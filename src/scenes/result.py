import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class ResultScene(Scene):
    def __init__(self, game, p1_score, p2_score, xp_gained=0, vs_ai=False):
        super().__init__(game)
        self.p1_score = p1_score
        self.p2_score = p2_score
        self.xp_gained = xp_gained
        self.vs_ai = vs_ai
        self.font_large = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)

        bw = 260
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.buttons = [
            Button(cx, 500, bw, 50, "再来一局", self._rematch),
            Button(cx, 570, bw, 50, "返回主菜单", self._go_menu),
        ]
        self.display_timer = 0.0

    def _rematch(self):
        from src.scenes.lobby import LobbyScene
        self.next_scene = LobbyScene(self.game, vs_ai=self.vs_ai)

    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.next_scene = MenuScene(self.game)

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return

    def update(self, dt):
        self.display_timer += dt

    def render(self, screen):
        screen.fill(COLOR_BG)

        # Title with pulsing effect
        alpha = 0.7 + 0.3 * (1 + (self.display_timer * 2 % 6.283))

        if self.p1_score > self.p2_score:
            winner = "玩家1 获胜!" if not self.vs_ai else "你赢了!"
            color = (255, 200, 60)
        elif self.p2_score > self.p1_score:
            winner = "玩家2 获胜!" if not self.vs_ai else "AI 获胜!"
            color = (255, 120, 120)
        else:
            winner = "平局!"
            color = (200, 200, 200)

        t = self.font_large.render(winner, True, color)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 80))

        # Score
        p1_label = "玩家1" if not self.vs_ai else "你"
        p2_label = "玩家2" if not self.vs_ai else "AI"
        score_text = f"{p1_label} {self.p1_score} - {self.p2_score} {p2_label}"
        s = self.font_med.render(score_text, True, COLOR_TEXT)
        screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, 170))

        # XP
        xp = self.font_small.render(f"获得经验: +{self.xp_gained} XP", True, (100, 255, 100))
        screen.blit(xp, (SCREEN_WIDTH // 2 - xp.get_width() // 2, 230))

        # Stats
        stats = [
            "--- 比赛统计 ---",
            f"{p1_label}: {self.p1_score} 分",
            f"{p2_label}: {self.p2_score} 分",
        ]
        for i, line in enumerate(stats):
            st = self.font_small.render(line, True, (200, 200, 200))
            screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, 310 + i * 30))

        for btn in self.buttons:
            btn.render(screen)
