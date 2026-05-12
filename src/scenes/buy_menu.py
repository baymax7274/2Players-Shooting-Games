import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG, BUY_TIME, COLOR_MONEY
from src.scenes.base import Scene
from src.ui.button import Button
from src.entities.weapon import load_weapons
from src.entities.item import ITEM_DEFS


class BuyMenuScene(Scene):
    def __init__(self, game, economy, battle_scene):
        super().__init__(game)
        self.economy = economy
        self.battle_scene = battle_scene
        self.buyer_id = 1

        self.owned_weapons = {
            1: list(battle_scene.p1_owned_weapons),
            2: list(battle_scene.p2_owned_weapons),
        }

        self.weapon_defs = load_weapons()
        self.font_title = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
        self.font_buy = pygame.font.Font(None, 20)
        self.time_left = BUY_TIME

        self.buy_buttons = []
        self._build_buy_buttons()

    def _build_buy_buttons(self):
        self.buy_buttons = []
        y = 140

        # Weapon buttons
        for wdef in self.weapon_defs:
            if wdef.price == 0:
                continue
            owned = wdef.weapon_id in self.owned_weapons[self.buyer_id]
            label = f"{wdef.name} - ${wdef.price}"
            if owned:
                label += " [Owned]"
            btn = Button(50, y, 340, 42, label,
                         lambda wid=wdef.weapon_id: self._buy_weapon(wid),
                         font_size=22, color=(60, 60, 80) if not owned else (40, 80, 40))
            self.buy_buttons.append((btn, wdef))
            y += 46

        # Item buttons
        y += 10
        self.item_buttons = []
        for item_id, defn in ITEM_DEFS.items():
            label = f"{defn['name']} - ${defn['price']}"
            btn = Button(50, y, 340, 42, label,
                         lambda iid=item_id: self._buy_item(iid),
                         font_size=22)
            self.item_buttons.append((btn, item_id, defn))
            y += 46

        self.done_btn = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 200, 50,
            "Done", self._done_buying
        )

    def _buy_weapon(self, weapon_id):
        wdef = next(w for w in self.weapon_defs if w.weapon_id == weapon_id)
        if self.economy.spend(self.buyer_id, wdef.price):
            if weapon_id not in self.owned_weapons[self.buyer_id]:
                self.owned_weapons[self.buyer_id].append(weapon_id)

    def _buy_item(self, item_id):
        defn = ITEM_DEFS[item_id]
        if self.economy.spend(self.buyer_id, defn["price"]):
            player = self._get_player(self.buyer_id)
            if player:
                player.items.append(item_id)

    def _get_player(self, pid):
        if pid == 1:
            return self.battle_scene.player1
        return self.battle_scene.player2

    def _done_buying(self):
        if self.buyer_id == 1:
            self.buyer_id = 2
            self.time_left = BUY_TIME
            self._build_buy_buttons()
        else:
            self.battle_scene.start_new_round(
                self.owned_weapons[1],
                self.owned_weapons[2]
            )
            self.next_scene = self.battle_scene

    def handle_event(self, event):
        self.done_btn.handle_event(event)
        for btn, _ in self.buy_buttons:
            btn.handle_event(event)
        for btn, _, _ in self.item_buttons:
            btn.handle_event(event)

    def update(self, dt):
        self.time_left -= dt
        if self.time_left <= 0:
            self._done_buying()

    def render(self, screen):
        screen.fill(COLOR_BG)
        money = self.economy.get_money(self.buyer_id)

        buyer_label = f"Player {self.buyer_id} Buy Phase"
        t = self.font_title.render(buyer_label, True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 15))

        timer_color = (255, 100, 100) if self.time_left < 10 else COLOR_TEXT
        timer = self.font_title.render(f"{int(self.time_left)}s", True, timer_color)
        screen.blit(timer, (SCREEN_WIDTH // 2 - timer.get_width() // 2, 60))

        money_text = self.font_small.render(
            f"Balance: ${money}",
            True, COLOR_MONEY
        )
        screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 105))

        # Sections
        wp_section = self.font_small.render("--- Weapons ---", True, (150, 150, 150))
        screen.blit(wp_section, (60, 120))
        item_section = self.font_small.render("--- Items ---", True, (150, 150, 150))
        screen.blit(item_section, (60, 140 + 46 * (len(self.weapon_defs) - 1)))

        for btn, wdef in self.buy_buttons:
            can_buy = self.economy.can_afford(self.buyer_id, wdef.price)
            btn.enabled = can_buy and wdef.weapon_id not in self.owned_weapons[self.buyer_id]
            btn.render(screen)

        for btn, item_id, defn in self.item_buttons:
            can_buy = self.economy.can_afford(self.buyer_id, defn["price"])
            btn.enabled = can_buy
            btn.render(screen)

        # Owned weapons list
        y = 140 + 46 * (len(self.weapon_defs) - 1 + len(ITEM_DEFS)) + 20
        owned = self.owned_weapons[self.buyer_id]
        own_text = self.font_small.render("Owned: " + ", ".join(owned), True, (160, 160, 160))
        screen.blit(own_text, (50, y))

        # Instructions
        inst = self.font_small.render("Press E/Num2 to switch weapons | Click to buy | Done to continue", True, (120, 120, 120))
        screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, SCREEN_HEIGHT - 130))

        self.done_btn.render(screen)
