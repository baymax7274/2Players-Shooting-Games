import pygame
from config import COLOR_HP_BAR, COLOR_HP_LOW, COLOR_OUTLINE


class HealthBar:
    def __init__(self, width=200, height=16):
        self.width = width
        self.height = height

    def render(self, screen, x, y, current_hp, max_hp, label=""):
        ratio = max(0, current_hp / max_hp)
        pygame.draw.rect(screen, (40, 40, 40), (x, y, self.width, self.height))
        color = COLOR_HP_BAR if ratio > 0.3 else COLOR_HP_LOW
        fill_w = int(self.width * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, y, fill_w, self.height))
            # Gradient highlight
            if fill_w > 2:
                lighter = tuple(min(c + 60, 255) for c in color)
                pygame.draw.rect(screen, lighter, (x, y, fill_w, self.height // 2))
        pygame.draw.rect(screen, COLOR_OUTLINE, (x, y, self.width, self.height), 1)
        font = pygame.font.Font(None, 18)
        text = font.render(f"{label} {int(current_hp)}/{max_hp}", True, (255, 255, 255))
        screen.blit(text, (x + 4, y + 1))


class CooldownBar:
    def __init__(self, width=80, height=6):
        self.width = width
        self.height = height

    def render(self, screen, x, y, current, max_val, color=(100, 180, 255)):
        ratio = max(0, min(1, current / max_val)) if max_val > 0 else 0
        pygame.draw.rect(screen, (40, 40, 40), (x, y, self.width, self.height))
        if ratio > 0:
            fill_w = int(self.width * ratio)
            pygame.draw.rect(screen, color, (x, y, fill_w, self.height))
        pygame.draw.rect(screen, COLOR_OUTLINE, (x, y, self.width, self.height), 1)
