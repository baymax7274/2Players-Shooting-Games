import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG, COLOR_PLAYER1, COLOR_PLAYER2
from src.scenes.base import Scene
from src.ui.button import Button


MAP_LIST = ["training_yard", "city_ruins", "underground_fortress", "space_station", "forest_maze"]
MAP_NAMES = ["训练靶场", "城市废墟", "地下堡垒", "太空站", "密林迷宫"]
GAME_MODES = ["elimination", "deathmatch"]


class LobbyScene(Scene):
    def __init__(self, game, vs_ai=False):
        super().__init__(game)
        self.vs_ai = vs_ai
        self.font_title = pygame.font.Font(None, 50)
        self.font_text = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.font_map = pygame.font.Font(None, 38)
        self.selected_map = 0
        self.selected_mode = 0

        bw = 260
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.start_btn = Button(cx, 570, bw, 50, "开始战斗", self._start_battle)
        self.back_btn = Button(cx, 635, bw, 50, "返回", self._go_back)

    def _start_battle(self):
        from src.scenes.battle import BattleScene
        map_name = MAP_LIST[self.selected_map]
        self.next_scene = BattleScene(
            self.game, map_name,
            p1_color=COLOR_PLAYER1, p2_color=COLOR_PLAYER2,
            vs_ai=self.vs_ai,
            game_mode=GAME_MODES[self.selected_mode],
        )

    def _go_back(self):
        from src.scenes.menu import MenuScene
        self.next_scene = MenuScene(self.game)

    def handle_event(self, event):
        self.start_btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_map = (self.selected_map - 1) % len(MAP_LIST)
            elif event.key == pygame.K_RIGHT:
                self.selected_map = (self.selected_map + 1) % len(MAP_LIST)
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.selected_mode = (self.selected_mode + 1) % len(GAME_MODES)

    def render(self, screen):
        screen.fill(COLOR_BG)
        t = self.font_title.render("选择地图与模式", True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 30))

        # Map selection
        map_label = self.font_text.render("地图:", True, (150, 150, 150))
        screen.blit(map_label, (SCREEN_WIDTH // 2 - map_label.get_width() // 2, 100))

        map_name = MAP_NAMES[self.selected_map]
        m = self.font_map.render(f"《{map_name}》", True, (255, 200, 60))
        screen.blit(m, (SCREEN_WIDTH // 2 - m.get_width() // 2, 180))

        nav = self.font_small.render("← → 切换地图", True, (150, 150, 150))
        screen.blit(nav, (SCREEN_WIDTH // 2 - nav.get_width() // 2, 230))

        # Mode selection
        mode_label = self.font_text.render("模式:", True, (150, 150, 150))
        screen.blit(mode_label, (SCREEN_WIDTH // 2 - mode_label.get_width() // 2, 280))

        mode_names = ["回合淘汰 (BO7)", "死斗 (15击杀)"]
        mode_text = mode_names[self.selected_mode]
        mode_surf = self.font_map.render(mode_text, True, (100, 255, 100))
        screen.blit(mode_surf, (SCREEN_WIDTH // 2 - mode_surf.get_width() // 2, 320))

        mode_nav = self.font_small.render("↑ ↓ 切换模式", True, (150, 150, 150))
        screen.blit(mode_nav, (SCREEN_WIDTH // 2 - mode_nav.get_width() // 2, 370))

        # Player info
        if self.vs_ai:
            p1 = self.font_text.render("玩家 (蓝方)  vs  AI Bot (红方)", True, COLOR_TEXT)
        else:
            p1 = self.font_text.render("玩家1 (蓝方)  vs  玩家2 (红方)", True, COLOR_TEXT)
        screen.blit(p1, (SCREEN_WIDTH // 2 - p1.get_width() // 2, 440))

        # Map preview mini
        self._draw_minimap(screen)

        self.start_btn.render(screen)
        self.back_btn.render(screen)

    def _draw_minimap(self, screen):
        px, py = SCREEN_WIDTH // 2 - 100, 490
        pygame.draw.rect(screen, (50, 50, 60), (px, py, 200, 60))
        pygame.draw.rect(screen, (100, 100, 100), (px, py, 200, 60), 1)
        preview = self.font_small.render(f"地图预览: {MAP_NAMES[self.selected_map]}", True, (150, 150, 150))
        screen.blit(preview, (px + 10, py + 20))
