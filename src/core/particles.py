import random
import pygame
from src.core.vector import Vec2


class Particle:
    def __init__(self, pos, vel, color, lifetime, size=3):
        self.pos = Vec2(pos.x, pos.y)
        self.vel = Vec2(vel.x, vel.y)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.pos = self.pos + self.vel * dt
        self.vel = self.vel * 0.95

    def render(self, screen, camera_offset=None):
        if not self.alive:
            return
        if camera_offset is None:
            camera_offset = Vec2(0, 0)
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        c = (*self.color[:3], alpha) if len(self.color) >= 3 else (*self.color, alpha)
        pygame.draw.circle(surf, c, (size + 2, size + 2), size)
        screen.blit(surf, (sx - size, sy - size))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, pos, count, colors, speed_range, lifetime_range, size_range=(2, 5)):
        for _ in range(count):
            angle = random.uniform(0, 6.283)
            speed = random.uniform(*speed_range)
            vel = Vec2(speed, 0).rotate(angle)
            color = random.choice(colors)
            lifetime = random.uniform(*lifetime_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(pos, vel, color, lifetime, int(size)))

    def emit_explosion(self, pos):
        self.emit(pos, 30, [(255, 200, 50), (255, 100, 20), (255, 60, 10)],
                  (50, 250), (0.3, 0.8), (3, 8))
        self.emit(pos, 10, [(255, 255, 255), (255, 255, 200)],
                  (20, 80), (0.1, 0.3), (2, 4))

    def emit_gun_flash(self, pos, angle):
        for _ in range(5):
            vel_angle = angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(30, 80)
            vel = Vec2(speed, 0).rotate(vel_angle)
            self.particles.append(Particle(
                pos, vel, (255, 255, 200), random.uniform(0.05, 0.15), 4
            ))

    def emit_smoke(self, pos, count=15):
        self.emit(pos, count, [(160, 160, 160), (180, 180, 180), (140, 140, 140)],
                  (10, 50), (1.0, 3.0), (8, 20))

    def emit_hit_spark(self, pos):
        self.emit(pos, 8, [(255, 200, 50), (255, 255, 200), (255, 150, 30)],
                  (40, 150), (0.1, 0.4), (2, 5))

    def emit_death(self, pos):
        self.emit(pos, 40, [(255, 50, 50), (255, 20, 20), (200, 50, 50), (255, 100, 50)],
                  (30, 200), (0.3, 1.0), (3, 10))
        self.emit(pos, 10, [(255, 255, 255)],
                  (10, 50), (0.2, 0.5), (2, 6))

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def render(self, screen, camera_offset=None):
        if camera_offset is None:
            camera_offset = Vec2(0, 0)
        for p in self.particles:
            p.render(screen, camera_offset)
