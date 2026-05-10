import math
import pygame
from config import BULLET_RADIUS, MAX_BOUNCES, COLOR_OUTLINE, HEADSHOT_MULTIPLIER
from src.core.vector import Vec2


class Bullet:
    def __init__(self, position, angle, speed, damage, owner_id, color,
                 is_explosive=False, explosion_radius=0, explosion_push=0):
        self.pos = Vec2(*position)
        self.vel = Vec2(math.cos(angle), math.sin(angle)) * speed
        self.speed = speed
        self.damage = damage
        self.owner_id = owner_id
        self.color = color
        self.radius = BULLET_RADIUS
        self.alive = True
        self.bounces_left = MAX_BOUNCES
        self.is_explosive = is_explosive
        self.explosion_radius = explosion_radius
        self.explosion_push = explosion_push
        self.gravity = 180 if is_explosive else 0

    def update(self, dt, walls):
        if not self.alive:
            return

        if self.gravity > 0:
            self.vel = self.vel + Vec2(0, self.gravity * dt)
            if self.vel.length() > 0.001:
                self.vel = self.vel.normalized() * self.speed

        new_pos = self.pos + self.vel * dt

        from src.core.physics import circle_rect_collision
        bounced = False
        for wall_rect in walls:
            hit, normal, penetration = circle_rect_collision(new_pos, self.radius, wall_rect)
            if hit:
                if self.bounces_left > 0:
                    nx, ny = normal
                    dot = self.vel.x * nx + self.vel.y * ny
                    self.vel = Vec2(
                        self.vel.x - 2 * dot * nx,
                        self.vel.y - 2 * dot * ny,
                    )
                    new_pos = new_pos + Vec2(nx * penetration, ny * penetration)
                    self.bounces_left -= 1
                    bounced = True
                else:
                    self.alive = False
                    return
                break

        self.pos = new_pos

    def render(self, screen, camera_offset=None):
        if not self.alive:
            return
        if camera_offset is None:
            camera_offset = Vec2(0, 0)
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        pygame.draw.circle(screen, COLOR_OUTLINE, (sx, sy), self.radius + 1)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        trail = self.pos - self.vel.normalized() * 6
        tx = int(trail.x - camera_offset.x)
        ty = int(trail.y - camera_offset.y)
        bright = tuple(min(c + 100, 255) for c in self.color)
        pygame.draw.line(screen, bright, (sx, sy), (tx, ty), max(2, self.radius))
