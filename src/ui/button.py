import pygame
from config import COLOR_TEXT, COLOR_OUTLINE


class Button:
    def __init__(self, x, y, w, h, text, callback, font_size=32,
                 color=(60, 60, 80), hover_color=(80, 80, 110), text_color=COLOR_TEXT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def render(self, screen):
        c = self.hover_color if self.hovered else self.color
        if not self.enabled:
            c = tuple(max(0, x - 40) for x in c)
        pygame.draw.rect(screen, c, self.rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_OUTLINE, self.rect, 2, border_radius=6)
        text_surf = self.font.render(self.text, True,
                                     self.text_color if self.enabled else (100, 100, 100))
        tx = self.rect.centerx - text_surf.get_width() // 2
        ty = self.rect.centery - text_surf.get_height() // 2
        screen.blit(text_surf, (tx, ty))
