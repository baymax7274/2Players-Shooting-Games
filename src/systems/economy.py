from config import (
    STARTING_MONEY, KILL_REWARD, ROUND_WIN_REWARD,
    ROUND_LOSS_REWARD, LOSS_STREAK_BONUS
)


class Economy:
    def __init__(self):
        self.money = {1: STARTING_MONEY, 2: STARTING_MONEY}
        self.loss_streak = {1: 0, 2: 0}

    def add_kill_reward(self, player_id):
        self.money[player_id] += KILL_REWARD

    def add_round_result(self, winner_id, loser_id):
        if winner_id:
            self.money[winner_id] += ROUND_WIN_REWARD
            self.loss_streak[winner_id] = 0
        if loser_id:
            self.money[loser_id] += ROUND_LOSS_REWARD
            self.loss_streak[loser_id] += 1
            self.money[loser_id] += LOSS_STREAK_BONUS * self.loss_streak[loser_id]

    def can_afford(self, player_id, price):
        return self.money[player_id] >= price

    def spend(self, player_id, amount):
        if self.can_afford(player_id, amount):
            self.money[player_id] -= amount
            return True
        return False

    def reset_for_match(self):
        self.money = {1: STARTING_MONEY, 2: STARTING_MONEY}
        self.loss_streak = {1: 0, 2: 0}

    def get_money(self, player_id):
        return self.money[player_id]
