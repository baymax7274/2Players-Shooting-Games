import math
import pygame
from config import PICKUP_RADIUS, COLOR_OUTLINE
from src.core.vector import Vec2


PICKUP_TYPES = {
    "health": {
        "color": (255, 50, 50),
        "respawn": 20.0,
        "max_active": 3,
    },
    "power": {
        "color": (180, 50, 220),
        "respawn": 45.0,
        "max_active": 1,
    },
    "speed": {
        "color": (50, 220, 50),
        "respawn": 40.0,
        "max_active": 1,
    },
}


class Pickup:
    def __init__(self, pickup_type, position):
        self.pickup_type = pickup_type
        self.pos = Vec2(*position)
        self.radius = PICKUP_RADIUS
        self.alive = True
        self.defn = PICKUP_TYPES[pickup_type]
        self.color = self.defn["color"]
        self.bob_phase = 0.0

    def update(self, dt):
        self.bob_phase += dt * 3.0

    def render(self, screen, camera_offset):
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y + math.sin(self.bob_phase) * 3)

        # 外圈光晕
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        alpha_pulse = int(50 + 30 * math.sin(self.bob_phase * 1.5))
        pygame.draw.circle(
            glow, (*self.color, alpha_pulse),
            (self.radius * 2, self.radius * 2), self.radius + 4
        )
        screen.blit(glow, (sx - self.radius * 2, sy - self.radius * 2))

        # 描边
        pygame.draw.circle(screen, COLOR_OUTLINE, (sx, sy), self.radius + 1)
        # 主体
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # 高光
        lighter = tuple(min(c + 80, 255) for c in self.color)
        pygame.draw.circle(screen, lighter, (sx - 2, sy - 3), self.radius - 5)

        # 类型图标：血包=十字，强力=星形，加速=箭头
        if self.pickup_type == "health":
            pygame.draw.rect(screen, (255, 255, 255),
                             (sx - 2, sy - 6, 4, 12))
            pygame.draw.rect(screen, (255, 255, 255),
                             (sx - 6, sy - 2, 12, 4))
        elif self.pickup_type == "power":
            for i in range(4):
                angle = math.pi / 2 * i + self.bob_phase
                ex = sx + int(math.cos(angle) * 6)
                ey = sy + int(math.sin(angle) * 6)
                pygame.draw.line(screen, (255, 255, 100), (sx, sy), (ex, ey), 2)
        elif self.pickup_type == "speed":
            pts = [
                (sx - 5, sy + 5), (sx, sy - 6), (sx + 5, sy + 5),
                (sx - 2, sy + 1), (sx + 2, sy + 1),
            ]
            pygame.draw.polygon(screen, (255, 255, 100), pts[:3])
            pygame.draw.polygon(screen, (255, 255, 100), pts[3:])
