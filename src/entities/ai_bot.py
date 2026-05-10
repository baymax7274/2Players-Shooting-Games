import math
import random
from src.core.vector import Vec2

IDLE, PATROL, CHASE, ATTACK, RETREAT = range(5)


class AIBot:
    def __init__(self, player, difficulty="normal"):
        self.player = player
        self.difficulty = difficulty
        self.state = PATROL
        self.patrol_target = Vec2(0, 0)
        self.decision_timer = 0.0
        self.reaction_time = {"easy": 0.5, "normal": 0.2, "hard": 0.05}[difficulty]
        self.aim_error = {"easy": 15, "normal": 5, "hard": 1}[difficulty]
        self.shoot_range = {"easy": 300, "normal": 400, "hard": 500}[difficulty]
        self.shoot_chance = {"easy": 0.3, "normal": 0.55, "hard": 0.75}[difficulty]
        self.item_cooldown = 0.0
        self._pick_patrol()

    def _pick_patrol(self):
        self.patrol_target = self.player.pos + Vec2(
            random.uniform(-300, 300),
            random.uniform(-200, 200),
        )

    def update(self, dt, enemy, map_width, map_height):
        self.decision_timer -= dt
        self.item_cooldown = max(0, self.item_cooldown - dt)

        # Aim with error
        aim_x = enemy.pos.x + random.uniform(-self.aim_error, self.aim_error)
        aim_y = enemy.pos.y + random.uniform(-self.aim_error, self.aim_error)
        self.player.set_aim(aim_x, aim_y)

        if self.decision_timer > 0:
            return
        self.decision_timer = self.reaction_time

        dist = self.player.pos.distance_to(enemy.pos)
        hp_ratio = self.player.hp / 100.0

        if hp_ratio < 0.3 and self.difficulty != "easy":
            self.state = RETREAT
        elif dist < 200:
            self.state = ATTACK
        elif dist < 500:
            self.state = CHASE
        else:
            self.state = PATROL

    def get_movement(self, enemy):
        if self.state == RETREAT:
            away = self.player.pos - enemy.pos
            if away.length() > 0:
                return away.normalized()
            return Vec2(0, 1)

        elif self.state == CHASE:
            toward = enemy.pos - self.player.pos
            if toward.length() > 0:
                return toward.normalized()
            return Vec2(0, 0)

        elif self.state == ATTACK:
            toward = enemy.pos - self.player.pos
            if toward.length() > 0:
                perp = Vec2(-toward.y, toward.x)
                if perp.length() > 0:
                    perp = perp.normalized()
                if random.random() < 0.5:
                    perp = perp * -1
                strafe = perp * 0.7
                if toward.length() > 150:
                    strafe = strafe + toward.normalized() * 0.3
                elif toward.length() < 100:
                    strafe = strafe - toward.normalized() * 0.3
                return strafe.normalized()
            return Vec2(0, 0)

        elif self.state == PATROL:
            to_patrol = self.patrol_target - self.player.pos
            if to_patrol.length() < 30:
                self._pick_patrol()
            if to_patrol.length() > 0:
                return to_patrol.normalized()
            return Vec2(0, 0)

        return Vec2(0, 0)

    def wants_to_shoot(self, enemy):
        if self.state in (ATTACK, CHASE):
            dist = self.player.pos.distance_to(enemy.pos)
            return dist < self.shoot_range and random.random() < self.shoot_chance
        return False

    def wants_to_use_item(self):
        hp_ratio = self.player.hp / 100.0
        if self.item_cooldown > 0:
            return None
        if hp_ratio < 0.4 and self.difficulty in ("normal", "hard"):
            if random.random() < 0.3:
                self.item_cooldown = 3.0
                return "medkit"
        if self.difficulty == "hard" and random.random() < 0.03 and self.state == ATTACK:
            self.item_cooldown = 5.0
            return "grenade"
        return None
