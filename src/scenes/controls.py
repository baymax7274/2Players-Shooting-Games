import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class ControlsScene(Scene):
    def __init__(self, game, map_name, p1_color, p2_color, vs_ai, game_mode):
        super().__init__(game)
        self.map_name = map_name
        self.p1_color = p1_color
        self.p2_color = p2_color
        self.vs_ai = vs_ai
        self.game_mode = game_mode

        self.font_title = pygame.font.Font(None, 48)
        self.font_header = pygame.font.Font(None, 34)
        self.font_key = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 18)

        bw, bh = 260, 50
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.start_btn = Button(cx, SCREEN_HEIGHT - 80, bw, bh, "Start Battle", self._start)

    def _start(self):
        from src.scenes.battle import BattleScene
        self.next_scene = BattleScene(
            self.game, self.map_name,
            p1_color=self.p1_color, p2_color=self.p2_color,
            vs_ai=self.vs_ai, game_mode=self.game_mode,
        )

    def handle_event(self, event):
        self.start_btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._start()

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(COLOR_BG)

        title = self.font_title.render("Controls", True, COLOR_TEXT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))

        p1_x, p2_x = 80, SCREEN_WIDTH // 2 + 20
        y = 70

        # Player 1 header
        p1_h = self.font_header.render("Player 1", True, self.p1_color)
        screen.blit(p1_h, (p1_x, y))
        # Player 2 header
        p2_label = "AI Bot" if self.vs_ai else "Player 2"
        p2_h = self.font_header.render(p2_label, True, self.p2_color)
        screen.blit(p2_h, (p2_x, y))

        y += 45

        p1_keys = [
            ("Move", "W A S D"),
            ("Shoot", "U"),
            ("Switch Weapon", "I"),
            ("Item / Ability", "Q"),
            ("Reload", "R"),
            ("Sprint", "L-Shift"),
            ("Dodge", "Space"),
        ]
        p2_keys = [
            ("Move", "Arrow Keys"),
            ("Shoot", "Numpad 1"),
            ("Switch Weapon", "Numpad 2"),
            ("Item / Ability", ". (Period)"),
            ("Sprint", "R-Shift"),
            ("Dodge", "R-Ctrl"),
        ]

        for i in range(max(len(p1_keys), len(p2_keys))):
            if i < len(p1_keys):
                label, k = p1_keys[i]
                self._draw_key_line(screen, label, k, p1_x, y + i * 32)
            if i < len(p2_keys) and not self.vs_ai:
                label, k = p2_keys[i]
                self._draw_key_line(screen, label, k, p2_x, y + i * 32)

        # Hint
        hint = self.font_small.render("Press Enter or click Start to begin", True, (120, 120, 120))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 120))

        self.start_btn.render(screen)

    def _draw_key_line(self, screen, label, key_text, x, y):
        label_surf = self.font_key.render(label + ":", True, (150, 150, 150))
        screen.blit(label_surf, (x, y))
        key_surf = self.font_key.render(key_text, True, COLOR_TEXT)
        screen.blit(key_surf, (x + 170, y))
