import math
import pygame
from src.core.vector import Vec2


ITEM_DEFS = {
    "grenade": {
        "name": "Grenade", "price": 400, "fuse_time": 2.0,
        "explosion_radius": 80, "damage": 80, "color": (60, 180, 60),
    },
    "flashbang": {
        "name": "Flashbang", "price": 300, "fuse_time": 1.5,
        "blind_duration": 2.0, "radius": 150, "color": (255, 255, 100),
    },
    "smoke": {
        "name": "Smoke", "price": 200, "fuse_time": 1.0,
        "duration": 5.0, "radius": 80, "color": (160, 160, 160),
    },
    "medkit": {
        "name": "Medkit", "price": 500, "heal_amount": 30,
        "use_time": 1.0, "color": (255, 50, 50),
    },
    "shield": {
        "name": "Shield", "price": 600, "duration": 8.0,
        "damage_reduction": 0.5, "color": (100, 150, 255),
    },
}


class ProjectileItem:
    def __init__(self, item_type, position, velocity, owner_id):
        self.item_type = item_type
        self.pos = Vec2(*position)
        self.vel = Vec2(*velocity)
        self.owner_id = owner_id
        defn = ITEM_DEFS[item_type]
        self.fuse_time = defn["fuse_time"]
        self.fuse_timer = self.fuse_time
        self.alive = True
        self.radius = 5
        self.color = defn["color"]
        self.defn = defn

    def update(self, dt, walls):
        self.fuse_timer -= dt
        if self.fuse_timer <= 0:
            self.alive = False
            return

        self.vel = self.vel + Vec2(0, 300 * dt)
        new_pos = self.pos + self.vel * dt

        from src.core.physics import circle_rect_collision
        for wall_rect in walls:
            hit, normal, penetration = circle_rect_collision(new_pos, self.radius, wall_rect)
            if hit:
                nx, ny = normal
                dot = self.vel.x * nx + self.vel.y * ny
                self.vel = Vec2(
                    self.vel.x - 2 * dot * nx,
                    self.vel.y - 2 * dot * ny,
                ) * 0.5
                new_pos = new_pos + Vec2(nx * penetration, ny * penetration)
                break

        self.pos = new_pos

    def render(self, screen, camera_offset=None):
        if not self.alive:
            return
        if camera_offset is None:
            camera_offset = Vec2(0, 0)
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        pygame.draw.circle(screen, (0, 0, 0), (sx, sy), self.radius + 1)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # Blink when about to explode
        if self.fuse_timer < 0.5:
            blink = int((self.fuse_timer * 10) % 2)
            if blink:
                warning_color = tuple(min(c + 100, 255) for c in self.color)
                pygame.draw.circle(screen, warning_color, (sx, sy), self.radius + 3, 1)


class PlayerEffect:
    def __init__(self, effect_type, duration, **kwargs):
        self.effect_type = effect_type
        self.duration = duration
        self.timer = duration
        self.params = kwargs

    def update(self, dt):
        self.timer -= dt
        return self.timer > 0

    def is_active(self):
        return self.timer > 0
