import random
import math
from config import (
    COLLAPSE_INTERVAL_MIN, COLLAPSE_INTERVAL_MAX,
    POISON_START_TIME, POISON_INITIAL_RADIUS,
    POISON_EXPAND_INTERVAL, POISON_EXPAND_STEP, POISON_DPS,
    GRAVITY_FLIP_INTERVAL,
    THORN_ACTIVATE_INTERVAL, THORN_ACTIVATE_COUNT,
    THORN_DURATION, THORN_DAMAGE,
    TILE_SIZE,
)


class Environment:
    def __init__(self):
        self.map_name = ""
        self.active = False
        self.collapse_timer = 0.0
        self._next_collapse_interval = 0.0
        self.poison_active = False
        self.poison_centers = []
        self.poison_radius = 0
        self.poison_expand_timer = 0.0
        self.gravity_flip_timer = 0.0
        self.gravity_inverted = False
        self.thorn_timer = 0.0
        self.thorn_patches = []
        self.thorn_spots = []
        self.active_hazards = []

    def setup(self, map_name, config_data):
        self.map_name = map_name
        self.active = True
        self._next_collapse_interval = random.uniform(
            COLLAPSE_INTERVAL_MIN, COLLAPSE_INTERVAL_MAX
        )
        self.collapse_timer = self._next_collapse_interval
        self.poison_active = False
        self.poison_centers = []
        self.poison_radius = POISON_INITIAL_RADIUS
        self.poison_expand_timer = POISON_START_TIME
        self.gravity_flip_timer = GRAVITY_FLIP_INTERVAL
        self.gravity_inverted = False
        self.thorn_timer = THORN_ACTIVATE_INTERVAL
        self.thorn_patches = []
        self.thorn_spots = config_data.get("thorn_spots", [])
        self.active_hazards = []

    def update(self, dt, game_map, players):
        if not self.active:
            return
        self.active_hazards = []
        self._update_collapse(dt, game_map)
        self._update_poison(dt, game_map, players)
        self._update_gravity(dt, game_map)
        self._update_thorns(dt, players)

    def _update_collapse(self, dt, game_map):
        if self.map_name != "city_ruins":
            return
        self.collapse_timer -= dt
        if self.collapse_timer <= 0:
            edge_tiles = []
            for ty in range(game_map.rows):
                for tx in range(game_map.cols):
                    if game_map.tiles[ty][tx] == 2:
                        if (tx < 8 or tx > game_map.cols - 9
                                or ty < 8 or ty > game_map.rows - 9):
                            edge_tiles.append((tx, ty))
            if edge_tiles:
                tx, ty = random.choice(edge_tiles)
                particles = game_map.destroy_tile(tx, ty)
                for p in particles:
                    self.active_hazards.append({
                        "type": "debris",
                        "pos": p["pos"],
                        "vel": p["vel"],
                        "size": p["size"],
                        "color": p["color"],
                        "life": p["life"],
                    })
            self._next_collapse_interval = random.uniform(
                COLLAPSE_INTERVAL_MIN, COLLAPSE_INTERVAL_MAX
            )
            self.collapse_timer = self._next_collapse_interval

    def _update_poison(self, dt, game_map, players):
        if self.map_name != "underground_fortress":
            return
        self.poison_expand_timer -= dt
        if self.poison_expand_timer <= 0 and not self.poison_active:
            self.poison_active = True
            self.poison_radius = POISON_INITIAL_RADIUS
            self.poison_expand_timer = POISON_EXPAND_INTERVAL
            margin = 5
            self.poison_centers = [
                (margin, margin),
                (game_map.cols - 1 - margin, margin),
                (margin, game_map.rows - 1 - margin),
                (game_map.cols - 1 - margin, game_map.rows - 1 - margin),
            ]
        elif self.poison_active:
            self.poison_expand_timer -= dt
            if self.poison_expand_timer <= 0:
                self.poison_radius += POISON_EXPAND_STEP
                self.poison_expand_timer = POISON_EXPAND_INTERVAL

        if self.poison_active:
            for player in players:
                if not player.alive:
                    continue
                for cx, cy in self.poison_centers:
                    pcx = cx * TILE_SIZE + TILE_SIZE // 2
                    pcy = cy * TILE_SIZE + TILE_SIZE // 2
                    dist = ((player.pos.x - pcx) ** 2 + (player.pos.y - pcy) ** 2) ** 0.5
                    if dist < self.poison_radius * TILE_SIZE:
                        player.hp = max(0, player.hp - POISON_DPS * dt)
                        if player.hp <= 0:
                            player.alive = False
                        break
            for cx, cy in self.poison_centers:
                self.active_hazards.append({
                    "type": "poison",
                    "cx": cx * TILE_SIZE + TILE_SIZE // 2,
                    "cy": cy * TILE_SIZE + TILE_SIZE // 2,
                    "radius": self.poison_radius * TILE_SIZE,
                })

    def _update_gravity(self, dt, game_map):
        if self.map_name != "space_station":
            return
        self.gravity_flip_timer -= dt
        if self.gravity_flip_timer <= 0:
            self.gravity_inverted = not self.gravity_inverted
            game_map.gravity_mod = -abs(game_map.gravity_mod) if self.gravity_inverted else abs(game_map.gravity_mod)
            self.gravity_flip_timer = GRAVITY_FLIP_INTERVAL

    def _update_thorns(self, dt, players):
        if self.map_name != "forest_maze":
            return
        self.thorn_timer -= dt

        for thorn in self.thorn_patches[:]:
            thorn["timer"] -= dt
            if thorn["timer"] <= 0:
                self.thorn_patches.remove(thorn)
                continue
            for player in players:
                if not player.alive:
                    continue
                tx = int(player.pos.x // TILE_SIZE)
                ty = int(player.pos.y // TILE_SIZE)
                if (tx, ty) == (thorn["tx"], thorn["ty"]):
                    player.hp = max(0, player.hp - THORN_DAMAGE * dt)
                    if player.hp <= 0:
                        player.alive = False

        if self.thorn_timer <= 0:
            if self.thorn_spots:
                chosen = random.sample(
                    self.thorn_spots,
                    min(THORN_ACTIVATE_COUNT, len(self.thorn_spots))
                )
                for spot in chosen:
                    self.thorn_patches.append({
                        "tx": spot["x"],
                        "ty": spot["y"],
                        "timer": THORN_DURATION,
                    })
            self.thorn_timer = THORN_ACTIVATE_INTERVAL

        for thorn in self.thorn_patches:
            self.active_hazards.append({
                "type": "thorn",
                "tx": thorn["tx"],
                "ty": thorn["ty"],
            })

    def get_active_hazards(self):
        return self.active_hazards

    def reset(self):
        self.setup(self.map_name, {
            "thorn_spots": self.thorn_spots,
        })
