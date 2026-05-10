import math
import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG,
    COLOR_PLAYER1, COLOR_PLAYER2, COLOR_TEXT,
    PLAYER1_KEYS, PLAYER2_KEYS,
    PLAYER_MAX_HP, ROUNDS_TO_WIN,
    KILL_REWARD, XP_PER_KILL, XP_PER_WIN,
    HEADSHOT_MULTIPLIER,
)
from src.scenes.base import Scene
from src.entities.player import Player
from src.entities.map import load_map
from src.entities.weapon import load_weapons, WeaponState
from src.entities.bullet import Bullet
from src.entities.item import ProjectileItem, ITEM_DEFS
from src.entities.ai_bot import AIBot
from src.core.camera import SplitCamera
from src.core.vector import Vec2
from src.core.particles import ParticleSystem
from src.core.screenshake import ScreenShake
from src.core.audio import AudioManager
from src.systems.economy import Economy
from src.ui.hud import HUD
from src.systems.pickup_manager import PickupManager
from src.systems.environment import Environment


class BattleScene(Scene):
    def __init__(self, game, map_name, p1_color=COLOR_PLAYER1, p2_color=COLOR_PLAYER2,
                 vs_ai=False, game_mode="elimination"):
        super().__init__(game)
        self.game_map = load_map(map_name)
        self._map_name = map_name
        self.vs_ai = vs_ai
        self.game_mode = game_mode

        weapon_defs = load_weapons()
        self.weapon_defs = {w.weapon_id: w for w in weapon_defs}
        pistol_def = self.weapon_defs["pistol"]

        p1_spawn = self.game_map.get_spawn(1)
        p2_spawn = self.game_map.get_spawn(2)
        self.player1 = Player(1, p1_spawn, p1_color, PLAYER1_KEYS)
        self.player2 = Player(2, p2_spawn, p2_color, PLAYER2_KEYS)

        self.p1_owned_weapons = ["pistol"]
        self.p2_owned_weapons = ["pistol"]
        self._equip_player(self.player1, "pistol")
        self._equip_player(self.player2, "pistol")

        self.bullets = []
        self.projectiles = []
        self.particles = ParticleSystem()
        self.shake = ScreenShake()
        self.audio = AudioManager()
        self.camera = SplitCamera(self.game_map.width, self.game_map.height)
        self.hud = HUD()

        self.economy = Economy()
        self.round_number = 0
        self.p1_score = 0
        self.p2_score = 0
        self.round_timer = 90
        self.round_active = True
        self._round_end_timer = 0.0
        self._buy_phase = False
        self._match_over = False
        self._respawn_queue = []

        self.kill_feed = []
        self.muzzle_flashes = []

        # Smoke clouds for smoke grenades
        self.smoke_clouds = []

        # v1.2.0 动态环境
        self.pickup_manager = PickupManager()
        self.pickup_manager.setup(
            map_name,
            self.game_map._original_data.get("pickup_spawns", [])
        )
        self.environment = Environment()
        self.environment.setup(
            map_name,
            self.game_map._original_data
        )
        self._debris_particles = []

        self.ai_bot = None
        if vs_ai:
            self.ai_bot = AIBot(self.player2, "normal")
            self.player2.keys = {
                "up": 0, "down": 0, "left": 0, "right": 0,
                "shoot": 0, "ability": 0, "sprint": 0, "dodge": 0,
            }

    def _equip_player(self, player, weapon_id):
        if weapon_id in self.weapon_defs:
            player.current_weapon = WeaponState(self.weapon_defs[weapon_id])

    def _add_kill_feed(self, killer_id, weapon_name, headshot=False):
        killer_name = f"Player {killer_id}"
        victim_name = f"Player {3 - killer_id}"
        hs = " HEADSHOT!" if headshot else ""
        text = f"{killer_name} [{weapon_name}] -> {victim_name}{hs}"
        self.kill_feed.insert(0, (text, 3.0))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from src.scenes.menu import MenuScene
                self.next_scene = MenuScene(self.game)
                return
            # Manual reload
            if event.key == pygame.K_r:
                if self.player1.current_weapon:
                    self.player1.current_weapon.start_reload()
            # Item use / cycle
            if event.key == pygame.K_q and self.player1.alive:
                self._use_item(self.player1)
            if event.key == pygame.K_PERIOD and self.player2.alive and not self.vs_ai:
                self._use_item(self.player2)
            # Switch weapon
            if event.key == pygame.K_1:
                self._switch_weapon(self.player1, 1)
            if event.key == pygame.K_2 and not self.vs_ai:
                self._switch_weapon(self.player2, 1)

    def _switch_weapon(self, player, slot):
        weapons = self.p1_owned_weapons if player.id == 1 else self.p2_owned_weapons
        if slot < len(weapons):
            self._equip_player(player, weapons[slot])

    def _use_item(self, player):
        if not player.items:
            return
        item_type = player.items.pop(0)
        if item_type in ("grenade", "flashbang", "smoke"):
            throw_vel = Vec2(math.cos(player.aim_angle), math.sin(player.aim_angle)) * 400
            spawn = player.pos + Vec2(math.cos(player.aim_angle), math.sin(player.aim_angle)) * player.radius
            self.projectiles.append(ProjectileItem(item_type, spawn.to_tuple(), throw_vel.to_tuple(), player.id))
        elif item_type == "medkit":
            player.heal(ITEM_DEFS["medkit"]["heal_amount"])
            self.audio.play("click")
        elif item_type == "shield":
            player.shield_active = True
            player.shield_timer = ITEM_DEFS["shield"]["duration"]

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # --- Round / Buy phase management ---
        if self._match_over:
            self._round_end_timer -= dt
            if self._round_end_timer <= 0:
                self._go_to_result()
            return

        if self._buy_phase:
            self._round_end_timer -= dt
            if self._round_end_timer <= 0:
                self._go_to_buy_menu()
            return

        if not self.round_active:
            self._round_end_timer -= dt
            if self._round_end_timer <= 0:
                self._start_next_round()
            # Still update particles
            self.particles.update(dt)
            self.shake.update(dt)
            return

        # --- AI Bot ---
        if self.ai_bot and self.player2.alive:
            self.ai_bot.update(dt, self.player1, self.game_map.width, self.game_map.height)
            move = self.ai_bot.get_movement(self.player1)
            fake_keys = {
                self.player2.keys["left"]: move.x < -0.2,
                self.player2.keys["right"]: move.x > 0.2,
                self.player2.keys["up"]: move.y < -0.2,
                self.player2.keys["down"]: move.y > 0.2,
                self.player2.keys["shoot"]: self.ai_bot.wants_to_shoot(self.player1),
                self.player2.keys["ability"]: False,
                self.player2.keys["sprint"]: self.ai_bot.state == 3 and random.random() < 0.1,
                self.player2.keys["dodge"]: False,
            }
            # AI item use
            item = self.ai_bot.wants_to_use_item()
            if item and self.economy.can_afford(2, ITEM_DEFS[item]["price"]):
                self.player2.items.append(item)
                self.economy.spend(2, ITEM_DEFS[item]["price"])
        else:
            fake_keys = None

        # --- Player input ---
        key_map1 = {}
        for action, k in self.player1.keys.items():
            key_map1[k] = keys[k]
        self.player1.handle_input(key_map1)

        if self.vs_ai:
            key_map2 = fake_keys or {}
        else:
            key_map2 = {}
            for action, k in self.player2.keys.items():
                key_map2[k] = keys[k]
        self.player2.handle_input(key_map2)

        # --- Player updates ---
        walls = self.game_map.wall_rects
        self.player1.update(dt, key_map1, walls)
        if self.vs_ai and fake_keys:
            self.player2.update(dt, fake_keys, walls)
        else:
            self.player2.update(dt, key_map2, walls)

        # --- Aim ---
        if self.player1.alive:
            self.player1.set_aim(self.player2.pos.x, self.player2.pos.y)
        if self.player2.alive:
            self.player2.set_aim(self.player1.pos.x, self.player1.pos.y)

        # --- Shooting ---
        self._handle_shooting(dt, keys)

        # --- Update bullets ---
        for bullet in self.bullets[:]:
            bullet.update(dt, walls)
            if not bullet.alive:
                self.bullets.remove(bullet)
                continue
            if (bullet.pos.x < -50 or bullet.pos.x > self.game_map.width + 50 or
                    bullet.pos.y < -50 or bullet.pos.y > self.game_map.height + 50):
                self.bullets.remove(bullet)
                continue
            self._check_bullet_hits(bullet)

        # --- Update projectiles ---
        for proj in self.projectiles[:]:
            proj.update(dt, walls)
            if not proj.alive:
                self._trigger_item_effect(proj)
                self.projectiles.remove(proj)

        # --- Update weapon states ---
        if self.player1.current_weapon:
            self.player1.current_weapon.update(dt)
        if self.player2.current_weapon:
            self.player2.current_weapon.update(dt)

        # --- Update particles, shake, HUD timers ---
        self.particles.update(dt)
        self.shake.update(dt)

        # v1.2.0 动态环境更新
        if self.round_active:
            self.game_map.update(dt)
            self.pickup_manager.update(
                dt,
                [self.player1, self.player2],
                self.game_map
            )
            self.environment.update(
                dt,
                self.game_map,
                [self.player1, self.player2]
            )
            # 更新碎片粒子
            for dp in self._debris_particles[:]:
                dp["life"] -= dt
                dp["pos"] = (
                    dp["pos"][0] + dp["vel"][0] * dt,
                    dp["pos"][1] + dp["vel"][1] * dt + 200 * dt,
                )
                if dp["life"] <= 0:
                    self._debris_particles.remove(dp)

        for mf in self.muzzle_flashes[:]:
            mf[1] -= dt
            if mf[1] <= 0:
                self.muzzle_flashes.remove(mf)
        for kf in self.kill_feed[:]:
            kf_list = list(kf)
            kf_list[1] -= dt
            if kf_list[1] <= 0:
                self.kill_feed.remove(kf)
            else:
                idx = self.kill_feed.index(kf)
                self.kill_feed[idx] = (kf[0], kf_list[1])
        for sc in self.smoke_clouds[:]:
            sc["timer"] -= dt
            if sc["timer"] <= 0:
                self.smoke_clouds.remove(sc)

        # --- Respawn queue (deathmatch) ---
        for rq in self._respawn_queue[:]:
            rq["timer"] -= dt
            if rq["timer"] <= 0:
                rq["player"].respawn(self.game_map.get_spawn(rq["player"].id))
                self._respawn_queue.remove(rq)

        # --- Camera ---
        self.camera.update(self.player1.pos, self.player2.pos)

        # --- Round timer ---
        if self.round_active:
            self.round_timer -= dt
            if self.round_timer <= 0:
                self._end_round_timeout()

        # --- Auto-reload when empty ---
        for p in [self.player1, self.player2]:
            if p.current_weapon and p.current_weapon.ammo == 0 and not p.current_weapon.is_reloading:
                p.current_weapon.start_reload()

    # ========= Shooting =========
    def _handle_shooting(self, dt, keys):
        for player in [self.player1, self.player2]:
            if not player.alive:
                continue
            ws = player.current_weapon
            if ws is None:
                continue

            shoot_key = player.keys["shoot"]
            shooting = False
            try:
                shooting = bool(keys[shoot_key])
            except (TypeError, IndexError):
                pass

            if self.vs_ai and player.id == 2 and self.ai_bot:
                shooting = self.ai_bot.wants_to_shoot(self.player1)

            if shooting:
                if ws.can_fire():
                    ws.fire()
                    wdef = ws.def_
                    for i in range(wdef.bullet_count):
                        spread = 0
                        if wdef.spread_angle > 0:
                            spread = math.radians(random.uniform(-math.degrees(wdef.spread_angle), math.degrees(wdef.spread_angle)))
                        b_angle = player.aim_angle + spread
                        spawn_x = player.pos.x + player.radius * math.cos(b_angle)
                        spawn_y = player.pos.y + player.radius * math.sin(b_angle)
                        bullet = Bullet(
                            (spawn_x, spawn_y), b_angle, wdef.bullet_speed,
                            wdef.body_damage, player.id, wdef.color,
                            is_explosive=wdef.explosive,
                            explosion_radius=wdef.explosion_radius,
                            explosion_push=wdef.explosion_push,
                        )
                        self.bullets.append(bullet)

                    # Muzzle flash & particles
                    muzzle_pos = player.pos + Vec2(
                        player.radius * 0.9, 0
                    ).rotate(player.aim_angle)
                    self.muzzle_flashes.append([muzzle_pos, 0.06])
                    self.particles.emit_gun_flash(muzzle_pos, player.aim_angle)

                    # Sound
                    sound_name = wdef.weapon_id if wdef.weapon_id in ("pistol", "smg", "shotgun", "rifle", "sniper") else "rocket"
                    if wdef.weapon_id == "rocket":
                        sound_name = "rocket"
                    self.audio.play(sound_name)

                    # Screen shake for heavy weapons
                    if wdef.weapon_id in ("sniper", "rocket", "shotgun"):
                        intensity = 6 if wdef.weapon_id == "sniper" else (8 if wdef.weapon_id == "rocket" else 3)
                        self.shake.shake(intensity, 0.15 if wdef.weapon_id == "sniper" else 0.2)

    # ========= Bullet hits =========
    def _check_bullet_hits(self, bullet):
        target = self.player2 if bullet.owner_id == 1 else self.player1
        if not target.alive:
            return
        from src.core.physics import circle_circle_collision
        hit, _ = circle_circle_collision(bullet.pos, bullet.radius,
                                          target.pos, target.radius)
        if hit:
            is_headshot = random.random() < 0.12
            # 应用攻击方 power-up 伤害倍率
            attacker = self.player1 if bullet.owner_id == 1 else self.player2
            damage = bullet.damage
            if hasattr(attacker, 'damage_multiplier'):
                damage = int(damage * attacker.damage_multiplier)
            dmg = target.take_damage(damage, is_headshot)
            self.particles.emit_hit_spark(bullet.pos)
            self.audio.play("hit")

            if bullet.is_explosive:
                self._explosion(bullet)

            bullet.alive = False
            if not target.alive:
                self.particles.emit_death(target.pos)
                self._on_player_killed(bullet.owner_id, bullet)
            else:
                # Track damage
                pass

    def _explosion(self, bullet):
        from src.core.physics import circle_circle_collision
        self.particles.emit_explosion(bullet.pos)
        self.audio.play("explosion")
        self.shake.shake(12, 0.3)
        # 摧毁爆炸范围内的可破坏墙
        tiles_to_destroy = self.game_map.get_tiles_in_radius(
            bullet.pos.x, bullet.pos.y, bullet.explosion_radius
        )
        for tx, ty in tiles_to_destroy:
            debris = self.game_map.destroy_tile(tx, ty)
            self._debris_particles.extend(debris)
        for player in [self.player1, self.player2]:
            if not player.alive:
                continue
            hit, _ = circle_circle_collision(
                bullet.pos, bullet.explosion_radius,
                player.pos, player.radius
            )
            if hit:
                player.take_damage(30, False)
                push = (player.pos - bullet.pos).normalized() * bullet.explosion_push
                new_p = player.pos + push * 0.15
                if not player._collides_wall(new_p, self.game_map.wall_rects):
                    player.pos = new_p
                if not player.alive and bullet.owner_id != player.id:
                    self._on_player_killed(bullet.owner_id, bullet)

    def _trigger_item_effect(self, proj):
        if proj.item_type == "grenade":
            self.particles.emit_explosion(proj.pos)
            self.audio.play("explosion")
            self.shake.shake(10, 0.25)
            tiles_to_destroy = self.game_map.get_tiles_in_radius(
                proj.pos.x, proj.pos.y, ITEM_DEFS["grenade"]["explosion_radius"]
            )
            for tx, ty in tiles_to_destroy:
                debris = self.game_map.destroy_tile(tx, ty)
                self._debris_particles.extend(debris)
            from src.core.physics import circle_circle_collision
            for player in [self.player1, self.player2]:
                if not player.alive:
                    continue
                hit, _ = circle_circle_collision(proj.pos, ITEM_DEFS["grenade"]["explosion_radius"],
                                                  player.pos, player.radius)
                if hit:
                    dmg = player.take_damage(ITEM_DEFS["grenade"]["damage"])
                    if not player.alive:
                        killer = self.player1 if proj.owner_id == 1 else self.player2
                        self._on_player_killed(proj.owner_id, None)

        elif proj.item_type == "flashbang":
            for player in [self.player1, self.player2]:
                if player.alive and player.id != proj.owner_id:
                    dist = player.pos.distance_to(proj.pos)
                    if dist < ITEM_DEFS["flashbang"]["radius"]:
                        player.blind_timer = ITEM_DEFS["flashbang"]["blind_duration"]

        elif proj.item_type == "smoke":
            self.smoke_clouds.append({
                "pos": Vec2(proj.pos.x, proj.pos.y),
                "radius": ITEM_DEFS["smoke"]["radius"],
                "timer": ITEM_DEFS["smoke"]["duration"],
            })

    # ========= Kill / Round logic =========
    def _on_player_killed(self, killer_id, bullet_or_source=None):
        killer = self.player1 if killer_id == 1 else self.player2
        victim = self.player2 if killer_id == 1 else self.player1
        killer.kills += 1
        victim.deaths += 1
        self.economy.add_kill_reward(killer_id)

        weapon_name = "?"
        if bullet_or_source and hasattr(bullet_or_source, 'is_explosive') and bullet_or_source.is_explosive:
            weapon_name = "Rocket Launcher"
        elif killer.current_weapon:
            weapon_name = killer.current_weapon.def_.name
        self._add_kill_feed(killer_id, weapon_name)

        if self.game_mode == "deathmatch":
            if killer_id == 1:
                self.p1_score += 1
            else:
                self.p2_score += 1
            self._respawn_queue.append({"player": victim, "timer": 2.0})
            if self.p1_score >= 15 or self.p2_score >= 15:
                self._match_over = True
                self._round_end_timer = 2.0
        else:
            if killer_id == 1:
                self.p1_score += 1
            else:
                self.p2_score += 1
            self.round_active = False
            self._round_end_timer = 2.0

    def _end_round_timeout(self):
        self.round_active = False
        hp1 = self.player1.hp if self.player1.alive else 0
        hp2 = self.player2.hp if self.player2.alive else 0
        if hp1 > hp2:
            self.p1_score += 1
        elif hp2 > hp1:
            self.p2_score += 1
        self._round_end_timer = 2.0

    def _start_next_round(self):
        self.round_number += 1
        if self.p1_score >= ROUNDS_TO_WIN or self.p2_score >= ROUNDS_TO_WIN:
            self._match_over = True
            self._round_end_timer = 2.0
            return

        # Economy
        winner = 1 if self.p1_score > self.p2_score else (2 if self.p2_score > self.p1_score else None)
        # Determine who won the last round (simplified: check score change)
        self.economy.add_round_result(
            winner if winner else 1,
            2 if winner == 1 else 1
        )

        self._buy_phase = True
        self._round_end_timer = 1.5  # Brief pause before buy menu

    def _go_to_buy_menu(self):
        self._buy_phase = False
        from src.scenes.buy_menu import BuyMenuScene
        buy_scene = BuyMenuScene(self.game, self.economy, self)
        self.next_scene = buy_scene

    def start_new_round(self, p1_weapons, p2_weapons):
        """Called when returning from buy menu."""
        self.p1_owned_weapons = p1_weapons if p1_weapons else ["pistol"]
        self.p2_owned_weapons = p2_weapons if p2_weapons else ["pistol"]

        # Respawn players
        self.player1.respawn(self.game_map.get_spawn(1))
        self.player2.respawn(self.game_map.get_spawn(2))
        self.player1.kills = 0
        self.player2.kills = 0

        self._equip_player(self.player1, self.p1_owned_weapons[0])
        self._equip_player(self.player2, self.p2_owned_weapons[0])

        self.bullets.clear()
        self.projectiles.clear()
        self.muzzle_flashes.clear()
        self.smoke_clouds.clear()
        self.kill_feed.clear()

        self.pickup_manager.reset()
        self.pickup_manager.setup(
            self._map_name,
            self.game_map._original_data.get("pickup_spawns", [])
        )
        self.environment.reset()
        self._debris_particles.clear()
        # 恢复可破坏墙和移动墙
        self.game_map.tiles = [row[:] for row in self.game_map._original_tiles]
        self.game_map.rebuild_wall_rects()
        self.game_map._load_moving_walls(
            self.game_map._original_data.get("moving_walls", [])
        )

        self.round_timer = 90
        self.round_active = True
        self.next_scene = self

    def _go_to_result(self):
        from src.scenes.result import ResultScene
        xp = (self.p1_score + self.p2_score) * XP_PER_KILL
        winner_xp = XP_PER_WIN if (self.p1_score > self.p2_score or self.p2_score > self.p1_score) else 0
        self.next_scene = ResultScene(
            self.game, self.p1_score, self.p2_score,
            xp + winner_xp, self.vs_ai
        )

    # ========= Render =========
    def render(self, screen):
        screen.fill(COLOR_BG)

        # If returning from buy menu needs to be handled
        cameras = self.camera.get_cameras()
        for cam, owner_id in cameras:
            screen.set_clip(cam.vp)

            # Apply screen shake offset
            shake_off = self.shake.offset
            offset_draw = Vec2(cam.offset.x - cam.vp.x + shake_off.x, cam.offset.y - cam.vp.y + shake_off.y)

            self.game_map.render(screen, offset_draw)

            # Render smoke clouds
            for sc in self.smoke_clouds:
                sx = int(sc["pos"].x - offset_draw.x)
                sy = int(sc["pos"].y - offset_draw.y)
                smoke_surf = pygame.Surface((sc["radius"] * 2, sc["radius"] * 2), pygame.SRCALPHA)
                alpha = int(180 * (sc["timer"] / ITEM_DEFS["smoke"]["duration"]))
                for r in range(sc["radius"], 0, -20):
                    a = alpha * (r / sc["radius"])
                    pygame.draw.circle(smoke_surf, (140, 140, 140, min(a, 255)),
                                       (sc["radius"], sc["radius"]), r)
                screen.blit(smoke_surf, (sx - sc["radius"], sy - sc["radius"]))

            # v1.2.0 拾取物渲染
            self.pickup_manager.render(screen, offset_draw)

            # 碎片粒子渲染
            for dp in self._debris_particles:
                dsx = int(dp["pos"][0] - offset_draw.x)
                dsy = int(dp["pos"][1] - offset_draw.y)
                alpha = int(255 * (dp["life"] / 1.0))
                debris_color = (*dp["color"][:3], min(alpha, 255))
                debris_surf = pygame.Surface((dp["size"] * 2, dp["size"] * 2), pygame.SRCALPHA)
                pygame.draw.rect(
                    debris_surf, debris_color,
                    (0, 0, dp["size"] * 2, dp["size"] * 2)
                )
                screen.blit(debris_surf, (dsx - dp["size"], dsy - dp["size"]))

            # 环境灾害渲染
            for hazard in self.environment.get_active_hazards():
                if hazard["type"] == "poison":
                    hx = int(hazard["cx"] - offset_draw.x)
                    hy = int(hazard["cy"] - offset_draw.y)
                    hr = int(hazard["radius"])
                    fog = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
                    for ring_r in range(hr, 0, -20):
                        ring_alpha = int(80 * (ring_r / hr))
                        pygame.draw.circle(
                            fog, (50, 200, 50, ring_alpha),
                            (hr, hr), ring_r
                        )
                    screen.blit(fog, (hx - hr, hy - hr))
                elif hazard["type"] == "thorn":
                    hx = hazard["tx"] * 32 - int(offset_draw.x)
                    hy = hazard["ty"] * 32 - int(offset_draw.y)
                    blink = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 150)
                    thorn_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                    thorn_surf.fill((220, 40, 40, blink))
                    screen.blit(thorn_surf, (hx, hy))

            # Render projectiles
            for proj in self.projectiles:
                proj.render(screen, offset_draw)

            # Render entities
            self.player1.render(screen, offset_draw)
            self.player2.render(screen, offset_draw)

            for bullet in self.bullets:
                bullet.render(screen, offset_draw)

            # Render muzzle flashes
            for mf_pos, _ in self.muzzle_flashes:
                mx = int(mf_pos.x - offset_draw.x)
                my = int(mf_pos.y - offset_draw.y)
                pygame.draw.circle(screen, (255, 255, 150), (mx, my), 8)
                pygame.draw.circle(screen, (255, 200, 50), (mx, my), 5)

            # Render particles (on top)
            self.particles.render(screen, offset_draw)

            # Blind effect overlay (only for the player viewing this camera)
            if owner_id == 1 and self.player1.blind_timer > 0:
                white_surf = pygame.Surface((cam.vp.width, cam.vp.height), pygame.SRCALPHA)
                alpha = int(200 * (self.player1.blind_timer / 2.0))
                white_surf.fill((255, 255, 255, min(alpha, 255)))
                screen.blit(white_surf, (cam.vp.x, cam.vp.y))
            elif owner_id == 2 and self.player2.blind_timer > 0:
                white_surf = pygame.Surface((cam.vp.width, cam.vp.height), pygame.SRCALPHA)
                alpha = int(200 * (self.player2.blind_timer / 2.0))
                white_surf.fill((255, 255, 255, min(alpha, 255)))
                screen.blit(white_surf, (cam.vp.x, cam.vp.y))

            screen.set_clip(None)

        # Divider
        self.camera.render_divider(screen)

        # HUD
        split = not self.camera.merged
        self.hud.render(
            screen, self.player1, self.player2,
            self.p1_score, self.p2_score,
            self.round_timer, self.round_number,
            self.game_mode, not self._match_over,
            split, self.kill_feed
        )

        # Buy phase overlay
        if self._buy_phase:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 48)
            phase_text = font.render("Buy Phase...", True, COLOR_TEXT)
            screen.blit(phase_text, (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Match over overlay
        if self._match_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 64)
            if self.p1_score > self.p2_score:
                win_text = "Player 1 Wins!" if not self.vs_ai else "You Win!"
            else:
                win_text = "Player 2 Wins!" if not self.vs_ai else "AI Wins!"
            wt = font.render(win_text, True, (255, 200, 60))
            screen.blit(wt, (SCREEN_WIDTH // 2 - wt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
