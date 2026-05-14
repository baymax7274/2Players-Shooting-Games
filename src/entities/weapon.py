import json
import math
import os
from config import BULLET_SPEEDS


class WeaponDef:
    def __init__(self, data):
        self.name = data["name"]
        self.weapon_id = data["id"]
        self.body_damage = data["body_damage"]
        self.head_damage = data["head_damage"]
        self.fire_rate = data["fire_rate"]
        self.mag_size = data["mag_size"]
        self.reload_time = data["reload_time"]
        bullet_speed_key = data.get("bullet_speed", "medium")
        self.bullet_speed = BULLET_SPEEDS.get(bullet_speed_key, 500)
        self.bullet_count = data.get("bullet_count", 1)
        self.spread_angle = math.radians(data.get("spread_angle", 0))
        self.price = data.get("price", 0)
        self.color = tuple(data.get("color", [200, 200, 200]))
        self.explosive = data.get("explosive", False)
        self.explosion_radius = data.get("explosion_radius", 0)
        self.explosion_push = data.get("explosion_push", 0)


class WeaponState:
    def __init__(self, weapon_def):
        self.def_ = weapon_def
        self.ammo = weapon_def.mag_size
        self.fire_timer = 0.0
        self.reload_timer = 0.0
        self.is_reloading = False

    def can_fire(self):
        return (
            not self.is_reloading
            and self.ammo > 0
            and self.fire_timer <= 0
        )

    def fire(self):
        self.ammo -= 1
        self.fire_timer = self.def_.fire_rate
        if self.ammo == 0:
            self.start_reload()

    def start_reload(self):
        if not self.is_reloading and self.ammo < self.def_.mag_size:
            self.is_reloading = True
            self.reload_timer = self.def_.reload_time

    def update(self, dt):
        self.fire_timer = max(0, self.fire_timer - dt)
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.ammo = self.def_.mag_size
                self.is_reloading = False


def load_weapons():
    from config import get_base_dir
    base = get_base_dir()
    full = os.path.join(base, "data", "weapons.json")
    with open(full, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [WeaponDef(d) for d in data]
