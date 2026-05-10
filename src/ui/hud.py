import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_MONEY, COLOR_OUTLINE
from src.ui.health_bar import HealthBar, CooldownBar


class HUD:
    def __init__(self):
        self.health_bar = HealthBar()
        self.cooldown_bar = CooldownBar()
        self.font = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 16)
        self.font_large = pygame.font.Font(None, 36)

    def render(self, screen, player1, player2, p1_score, p2_score, round_timer,
               round_number, game_mode, match_active, split_screen, kill_feed):
        mid_x = SCREEN_WIDTH // 2

        # Score bar
        score_text = self.font_large.render(f"{p1_score} - {p2_score}", True, COLOR_TEXT)
        screen.blit(score_text, (mid_x - score_text.get_width() // 2, 6))

        timer_color = (255, 100, 100) if round_timer < 10 else COLOR_TEXT
        timer_text = self.font.render(f"{int(round_timer)}s", True, timer_color)
        screen.blit(timer_text, (mid_x - timer_text.get_width() // 2, 40))

        # Round number
        if game_mode == "elimination":
            rn_text = self.font_small.render(f"第{round_number}回合", True, (180, 180, 180))
            screen.blit(rn_text, (mid_x - rn_text.get_width() // 2, 58))

        # Player 1 HUD (left side when split, top-left when merged)
        if split_screen:
            self._render_player_hud(screen, player1, 10, 10, left_align=True)
            self._render_player_hud(screen, player2, SCREEN_WIDTH - 210, 10, left_align=False)
        else:
            self._render_player_hud(screen, player1, 10, 10, left_align=True)
            self._render_player_hud(screen, player2, SCREEN_WIDTH - 10, 10, left_align=False)

        # Kill feed
        self._render_kill_feed(screen, kill_feed, mid_x)

        # Mode indicator
        mode_text = self.font_small.render(
            "回合淘汰" if game_mode == "elimination" else "死斗", True, (120, 120, 120))
        screen.blit(mode_text, (mid_x - mode_text.get_width() // 2, SCREEN_HEIGHT - 20))

    def _render_player_hud(self, screen, player, x, y, left_align=True):
        w = 200
        if not left_align:
            x = x - w

        # Name
        name_text = self.font_small.render(f"P{player.id} 击杀:{player.kills}", True, COLOR_TEXT)
        screen.blit(name_text, (x, y))

        # HP
        self.health_bar.render(screen, x, y + 18, player.hp, 100, "")

        # Weapon info
        if player.current_weapon:
            wp = player.current_weapon
            wp_text = self.font_small.render(
                f"{wp.def_.name} | {wp.ammo}/{wp.def_.mag_size}",
                True, (200, 200, 200))
            screen.blit(wp_text, (x, y + 38))

            # Reload indicator
            if wp.is_reloading:
                reload_text = self.font_small.render("换弹中...", True, (255, 200, 50))
                screen.blit(reload_text, (x, y + 52))

        # Sprint cooldown
        self.cooldown_bar.render(screen, x, y + 68, player.sprint_cooldown_timer, 3.0, (100, 180, 255))
        # Dodge cooldown
        self.cooldown_bar.render(screen, x, y + 74, player.dodge_cooldown_timer, 5.0, (255, 180, 100))

        # Item count
        item_text = self.font_small.render(f"道具: {len(player.items)}", True, (200, 200, 200))
        screen.blit(item_text, (x, y + 82))

        # Effects
        if player.blind_timer > 0:
            blind_text = self.font_small.render("致盲!", True, (255, 255, 0))
            screen.blit(blind_text, (x, y + 96))
        if player.shield_active:
            shield_text = self.font_small.render("护盾", True, (100, 150, 255))
            screen.blit(shield_text, (x, y + 96))

    def _render_kill_feed(self, screen, kill_feed, mid_x):
        y = 80
        for text, _ in kill_feed:
            ks = self.font.render(text, True, (255, 220, 60))
            screen.blit(ks, (mid_x - ks.get_width() // 2, y))
            y += 24
