import random
from config import (
    PICKUP_RESPAWN_HEALTH, PICKUP_RESPAWN_POWER, PICKUP_RESPAWN_SPEED,
    PICKUP_MAX_HEALTH, PICKUP_MAX_POWER, PICKUP_MAX_SPEED,
    POWER_DURATION, SPEED_DURATION, HEAL_AMOUNT,
)
from src.entities.pickup import Pickup, PICKUP_TYPES
from src.core.physics import circle_circle_collision


class PickupManager:
    def __init__(self):
        self.pickups = []
        self.spawn_timers = {}
        self.spawn_points = []
        self.map_name = ""

    def setup(self, map_name, spawn_points):
        self.map_name = map_name
        self.spawn_points = list(spawn_points)
        self.pickups.clear()
        self.spawn_timers = {
            "health": 0.0,
            "power": 0.0,
            "speed": 0.0,
        }

    def _count_active(self, pickup_type):
        return sum(1 for p in self.pickups
                   if p.pickup_type == pickup_type and p.alive)

    def _get_random_spawn(self):
        if not self.spawn_points:
            return None
        pt = random.choice(self.spawn_points)
        return (pt["x"] * 32 + 16, pt["y"] * 32 + 16)

    def update(self, dt, players, game_map):
        # 更新计时器并尝试刷新
        for ptype, defn in PICKUP_TYPES.items():
            self.spawn_timers[ptype] -= dt
            max_active = defn["max_active"]
            if self.spawn_timers[ptype] <= 0:
                if self._count_active(ptype) < max_active:
                    pos = self._get_random_spawn()
                    if pos is not None:
                        # 确保刷新点在空地上
                        tx = int(pos[0] // 32)
                        ty = int(pos[1] // 32)
                        if (0 <= ty < game_map.rows and 0 <= tx < game_map.cols
                                and game_map.tiles[ty][tx] == 0):
                            self.pickups.append(Pickup(ptype, pos))
                self.spawn_timers[ptype] = defn["respawn"]

        # 更新拾取物动画
        for p in self.pickups:
            p.update(dt)

        # 碰撞检测
        for player in players:
            if not player.alive:
                continue
            for p in self.pickups[:]:
                if not p.alive:
                    continue
                hit, _ = circle_circle_collision(
                    p.pos, p.radius,
                    player.pos, player.radius + 8
                )
                if hit:
                    self._apply(player, p)
                    p.alive = False
                    self.pickups.remove(p)

    def _apply(self, player, pickup):
        if pickup.pickup_type == "health":
            player.heal(HEAL_AMOUNT)
        elif pickup.pickup_type == "power":
            player.power_timer = POWER_DURATION
        elif pickup.pickup_type == "speed":
            player.speed_timer = SPEED_DURATION

    def render(self, screen, camera_offset):
        for p in self.pickups:
            if p.alive:
                p.render(screen, camera_offset)

    def reset(self):
        self.pickups.clear()
        self.spawn_timers = {
            "health": 0.0,
            "power": 0.0,
            "speed": 0.0,
        }
