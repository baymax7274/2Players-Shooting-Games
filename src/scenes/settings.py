import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class SettingsScene(Scene):
    def __init__(self, game, return_scene):
        super().__init__(game)
        self.return_scene = return_scene
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)
        self.back_btn = Button(
            SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 80, 260, 50,
            "Back", self._go_back
        )

    def _go_back(self):
        self.next_scene = self.return_scene

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def render(self, screen):
        screen.fill(COLOR_BG)
        t = self.font_title.render("Settings", True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 30))

        # Controls section
        section_font = pygame.font.Font(None, 34)
        p1_header = section_font.render("--- Player 1 ---", True, (100, 160, 255))
        screen.blit(p1_header, (80, 100))
        p2_header = section_font.render("--- Player 2 ---", True, (255, 120, 120))
        screen.blit(p2_header, (SCREEN_WIDTH // 2 + 20, 100))

        lines_p1 = [
            "Move: W A S D",
            "Shoot: E",
            "Item: Q",
            "Sprint: Left Shift",
            "Dodge: Space",
        ]
        lines_p2 = [
            "Move: Arrow Keys",
            "Shoot: /",
            "Item: .",
            "Sprint: Right Shift",
            "Dodge: Right Ctrl",
        ]

        for i, line in enumerate(lines_p1):
            s = self.font_text.render(line, True, COLOR_TEXT)
            screen.blit(s, (80, 150 + i * 35))

        for i, line in enumerate(lines_p2):
            s = self.font_text.render(line, True, COLOR_TEXT)
            screen.blit(s, (SCREEN_WIDTH // 2 + 20, 150 + i * 35))

        hint = self.font_small.render("Key rebinding coming in a future update", True, (120, 120, 120))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 350))

        self.back_btn.render(screen)
