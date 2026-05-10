import math
import pygame
from config import (
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_MAX_HP,
    SPRINT_SPEED_MULT, SPRINT_DURATION, SPRINT_COOLDOWN,
    DODGE_DISTANCE, DODGE_DURATION, DODGE_COOLDOWN,
    COLOR_OUTLINE,
)
from src.core.vector import Vec2


class Player:
    def __init__(self, player_id, position, color, key_config):
        self.id = player_id
        self.pos = Vec2(*position)
        self.vel = Vec2(0, 0)
        self.color = color
        self.keys = key_config
        self.radius = PLAYER_RADIUS
        self.aim_angle = 0.0
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.money = 0
        self.current_weapon = None
        self.items = []
        self.kills = 0
        self.deaths = 0

        self.sprint_timer = 0.0
        self.sprint_cooldown_timer = 0.0
        self.is_sprinting = False

        self.dodge_timer = 0.0
        self.dodge_cooldown_timer = 0.0
        self.dodge_dir = Vec2(0, 0)
        self.is_dodging = False
        self.dodge_invincible = False

        self.blind_timer = 0.0
        self.shield_active = False
        self.shield_timer = 0.0
        self.effects = []

        # Power-up 状态 (v1.2.0)
        self.power_timer = 0.0
        self.speed_timer = 0.0

    def handle_input(self, keys_pressed):
        if not self.alive:
            return
        if self.is_dodging:
            return

        if keys_pressed.get(self.keys["sprint"], False):
            if self.sprint_timer <= 0 and self.sprint_cooldown_timer <= 0:
                self.is_sprinting = True
                self.sprint_timer = SPRINT_DURATION
                self.sprint_cooldown_timer = SPRINT_COOLDOWN

        if keys_pressed.get(self.keys["dodge"], False):
            if self.dodge_cooldown_timer <= 0 and not self.is_sprinting:
                move_x = 0
                move_y = 0
                if keys_pressed.get(self.keys["left"], False):
                    move_x -= 1
                if keys_pressed.get(self.keys["right"], False):
                    move_x += 1
                if keys_pressed.get(self.keys["up"], False):
                    move_y -= 1
                if keys_pressed.get(self.keys["down"], False):
                    move_y += 1
                if move_x != 0 or move_y != 0:
                    self.dodge_dir = Vec2(move_x, move_y).normalized()
                else:
                    self.dodge_dir = Vec2(
                        math.cos(self.aim_angle), math.sin(self.aim_angle)
                    )
                self.is_dodging = True
                self.dodge_timer = DODGE_DURATION
                self.dodge_cooldown_timer = DODGE_COOLDOWN
                self.dodge_invincible = True

    def update(self, dt, keys_pressed, walls):
        if not self.alive:
            return

        self.sprint_timer = max(0, self.sprint_timer - dt)
        self.sprint_cooldown_timer = max(0, self.sprint_cooldown_timer - dt)
        self.dodge_cooldown_timer = max(0, self.dodge_cooldown_timer - dt)
        self.blind_timer = max(0, self.blind_timer - dt)
        self.power_timer = max(0, self.power_timer - dt)
        self.speed_timer = max(0, self.speed_timer - dt)

        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False

        for eff in self.effects[:]:
            if not eff.update(dt):
                self.effects.remove(eff)

        if self.is_sprinting and self.sprint_timer <= 0:
            self.is_sprinting = False

        if self.is_dodging:
            self.dodge_timer -= dt
            speed = DODGE_DISTANCE / DODGE_DURATION
            new_pos = self.pos + self.dodge_dir * speed * dt
            if not self._collides_wall(new_pos, walls):
                self.pos = new_pos
            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.dodge_invincible = False
            return

        speed = PLAYER_SPEED
        if self.speed_timer > 0:
            speed *= 1.5
        if self.is_sprinting:
            speed *= SPRINT_SPEED_MULT

        move_x = 0
        move_y = 0
        if keys_pressed.get(self.keys["left"], False):
            move_x -= 1
        if keys_pressed.get(self.keys["right"], False):
            move_x += 1
        if keys_pressed.get(self.keys["up"], False):
            move_y -= 1
        if keys_pressed.get(self.keys["down"], False):
            move_y += 1

        if move_x != 0 or move_y != 0:
            move_vec = Vec2(move_x, move_y).normalized()
            new_pos = self.pos + move_vec * speed * dt
            if not self._collides_wall(new_pos, walls):
                self.pos = new_pos
            else:
                px = self.pos + Vec2(move_vec.x * speed * dt, 0)
                py = self.pos + Vec2(0, move_vec.y * speed * dt)
                if not self._collides_wall(px, walls):
                    self.pos = px
                elif not self._collides_wall(py, walls):
                    self.pos = py

    def _collides_wall(self, pos, walls):
        from src.core.physics import circle_rect_collision
        for wall_rect in walls:
            hit, _, _ = circle_rect_collision(pos, self.radius, wall_rect)
            if hit:
                return True
        return False

    def take_damage(self, amount, is_headshot=False):
        if self.dodge_invincible:
            return 0
        dmg = amount * 2 if is_headshot else amount
        if self.shield_active:
            dmg = int(dmg * 0.5)
        self.hp = max(0, self.hp - dmg)
        if self.hp <= 0:
            self.alive = False
        return dmg

    def heal(self, amount):
        self.hp = min(PLAYER_MAX_HP, self.hp + amount)

    @property
    def damage_multiplier(self):
        return 1.5 if self.power_timer > 0 else 1.0

    def set_aim(self, target_x, target_y):
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        self.aim_angle = math.atan2(dy, dx)

    def render(self, screen, camera_offset=None):
        if not self.alive:
            return
        if camera_offset is None:
            camera_offset = Vec2(0, 0)
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)

        # Shadow
        shadow_surf = pygame.Surface((self.radius * 2, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80),
                            (0, 0, self.radius * 2, 10))
        screen.blit(shadow_surf, (sx - self.radius, sy + 2))

        # Dodge invincibility glow
        if self.dodge_invincible:
            glow = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 100),
                               (self.radius * 3 // 2, self.radius * 3 // 2), self.radius + 4)
            screen.blit(glow, (sx - self.radius * 1.5, sy - self.radius * 1.5))

        # Shield ring
        if self.shield_active:
            shield_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 150, 255, 80),
                               (self.radius * 3 // 2, self.radius * 3 // 2), self.radius + 6, 3)
            screen.blit(shield_surf, (sx - self.radius * 1.5, sy - self.radius * 1.5))

        # Outline
        pygame.draw.circle(screen, COLOR_OUTLINE, (sx, sy), self.radius + 2)
        # Body
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # Inner highlight
        lighter = tuple(min(c + 60, 255) for c in self.color)
        pygame.draw.circle(screen, lighter, (sx - 3, sy - 3), self.radius - 6)

        # Aim indicator line
        end_x = sx + (self.radius + 12) * math.cos(self.aim_angle)
        end_y = sy + (self.radius + 12) * math.sin(self.aim_angle)
        pygame.draw.line(screen, (255, 255, 200), (sx, sy), (int(end_x), int(end_y)), 3)

        # Direction dot
        front_x = sx + self.radius * 0.6 * math.cos(self.aim_angle)
        front_y = sy + self.radius * 0.6 * math.sin(self.aim_angle)
        pygame.draw.circle(screen, (255, 255, 255), (int(front_x), int(front_y)), 3)

    def respawn(self, spawn_pos):
        self.pos = Vec2(*spawn_pos)
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.dodge_invincible = False
        self.is_dodging = False
        self.is_sprinting = False
        self.blind_timer = 0.0
        self.shield_active = False
        self.shield_timer = 0.0
        self.effects.clear()
        self.power_timer = 0.0
        self.speed_timer = 0.0
