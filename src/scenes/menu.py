import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.Font(None, 80)
        self.font_sub = pygame.font.Font(None, 24)

        bw, bh = 260, 50
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.buttons = [
            Button(cx, 280, bw, bh, "开始对战", self._start_pvp),
            Button(cx, 350, bw, bh, "人机对战", self._start_vs_ai),
            Button(cx, 420, bw, bh, "设置", self._open_settings),
            Button(cx, 490, bw, bh, "退出", self._quit),
        ]
        self.bg_offset = 0.0

    def _start_pvp(self):
        from src.scenes.lobby import LobbyScene
        self.next_scene = LobbyScene(self.game, vs_ai=False)

    def _start_vs_ai(self):
        from src.scenes.lobby import LobbyScene
        self.next_scene = LobbyScene(self.game, vs_ai=True)

    def _open_settings(self):
        from src.scenes.settings import SettingsScene
        self.next_scene = SettingsScene(self.game, self)

    def _quit(self):
        self.game.running = False

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return

    def update(self, dt):
        self.bg_offset = (self.bg_offset + 30 * dt) % 40

    def render(self, screen):
        # Animated background grid
        screen.fill(COLOR_BG)
        for i in range(0, SCREEN_WIDTH, 40):
            x = i + int(self.bg_offset)
            for j in range(0, SCREEN_HEIGHT, 40):
                y = j + int(self.bg_offset * 0.7)
                pygame.draw.rect(screen, (35, 35, 42), (x % SCREEN_WIDTH, y % SCREEN_HEIGHT, 2, 2))

        # Title with shadow
        title_shadow = self.font_title.render("双 人 枪 战", True, (10, 10, 20))
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 83))
        title = self.font_title.render("双 人 枪 战", True, (255, 200, 60))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        sub = self.font_sub.render("Two-Player Shooter", True, COLOR_TEXT)
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 165))

        # Version
        ver_font = pygame.font.Font(None, 16)
        ver = ver_font.render("v1.0", True, (100, 100, 100))
        screen.blit(ver, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 20))

        for btn in self.buttons:
            btn.render(screen)

        # Profile hint
        prof_font = pygame.font.Font(None, 18)
        prof_text = prof_font.render("存档: 未加载", True, (120, 120, 120))
        screen.blit(prof_text, (10, SCREEN_HEIGHT - 22))
