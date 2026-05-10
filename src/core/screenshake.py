import random
from src.core.vector import Vec2


class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0
        self.offset = Vec2(0, 0)

    def shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.timer = duration

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            decay = self.timer / self.duration if self.duration > 0 else 0
            current = self.intensity * decay
            self.offset = Vec2(
                random.uniform(-current, current),
                random.uniform(-current, current),
            )
        else:
            self.offset = Vec2(0, 0)
