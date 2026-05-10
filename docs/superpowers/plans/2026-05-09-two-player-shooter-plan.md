# 双人枪战游戏 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete top-down 2D two-player versus shooter with round-based elimination, economy, 6 weapons, 5 items, AI bots, split-screen, profile system, and cartoon rendering.

**Architecture:** Scene-based state machine (menu→lobby→buy→battle→result) on top of a Pygame game loop. Entities (Player, Bullet, Item) are plain objects managed by scenes. Core engine handles camera (split-screen), physics (AABB+circle collision), and particle effects as cross-cutting services. All data (weapons, maps, profiles) stored as JSON.

**Tech Stack:** Python 3.10+, Pygame 2.x, JSON for storage, pygame.mixer for audio.

---

### Task 1: Project Skeleton — Config, Main Loop, Scene Manager

**Files:**
- Create: `config.py`
- Create: `main.py`
- Create: `src/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/core/game.py`
- Create: `src/scenes/__init__.py`

- [ ] **Step 1: Create config.py with all game constants**

```python
# config.py
import pygame

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Gameplay
PLAYER_SPEED = 220  # pixels per second
PLAYER_RADIUS = 16
PLAYER_MAX_HP = 100
HEADSHOT_MULTIPLIER = 2.0

# Sprint
SPRINT_SPEED_MULT = 2.0
SPRINT_DURATION = 0.5
SPRINT_COOLDOWN = 3.0

# Dodge
DODGE_DISTANCE = 80
DODGE_DURATION = 0.2
DODGE_COOLDOWN = 5.0

# Bullets
BULLET_SPEEDS = {
    "slow": 300,
    "medium": 500,
    "fast": 800,
    "very_fast": 1200,
}
BULLET_RADIUS = 3
MAX_BOUNCES = 1

# Economy
STARTING_MONEY = 3000
KILL_REWARD = 1500
ROUND_WIN_REWARD = 2500
ROUND_LOSS_REWARD = 800
LOSS_STREAK_BONUS = 500
BUY_TIME = 30  # seconds

# Rounds
ROUNDS_TO_WIN = 4  # BO7

# Progression
XP_PER_KILL = 100
XP_PER_WIN = 200
UNLOCK_SKIN_LEVEL = 5
UNLOCK_CHARACTER_LEVEL = 10
UNLOCK_MAPS_LEVEL = 15

# Colors
COLOR_BG = (30, 30, 30)
COLOR_PLAYER1 = (50, 150, 255)
COLOR_PLAYER2 = (255, 80, 80)
COLOR_OUTLINE = (0, 0, 0)
COLOR_HP_BAR = (60, 200, 60)
COLOR_HP_LOW = (220, 50, 50)
COLOR_MONEY = (255, 215, 0)
COLOR_TEXT = (240, 240, 240)

# Controls defaults
PLAYER1_KEYS = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "shoot": pygame.K_e,
    "ability": pygame.K_q,
    "sprint": pygame.K_LSHIFT,
    "dodge": pygame.K_SPACE,
}
PLAYER2_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "shoot": pygame.K_SLASH,
    "ability": pygame.K_PERIOD,
    "sprint": pygame.K_RSHIFT,
    "dodge": pygame.K_RCTRL,
}

# Map grid (each cell is 32x32 pixels)
TILE_SIZE = 32
# 0=empty, 1=wall, 2=destructible, 3=cover_half_height
```

- [ ] **Step 2: Create src/core/game.py with scene manager and main loop**

```python
# src/core/game.py
import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("双人枪战 — Two-Player Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None
        self.dt = 0.0  # delta time in seconds

    def change_scene(self, scene):
        self.scene = scene

    def run(self, start_scene):
        self.scene = start_scene
        while self.running:
            dt_ms = self.clock.tick(FPS)
            self.dt = dt_ms / 1000.0  # clamp?

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if self.scene:
                    self.scene.handle_event(event)

            if self.scene:
                self.scene.update(self.dt)
                self.scene.render(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()
```

- [ ] **Step 3: Create main.py entry point**

```python
# main.py
from src.core.game import Game
from src.scenes.menu import MenuScene

if __name__ == "__main__":
    game = Game()
    game.run(MenuScene(game))
```

- [ ] **Step 4: Verify skeleton runs without errors**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "from config import *; from src.core.game import Game; print('Imports OK')"
```

Expected: `Imports OK`

---

### Task 2: Scene Base Class and Menu Scene Stub

**Files:**
- Create: `src/scenes/base.py`
- Modify: `src/scenes/menu.py`
- Modify: `main.py` (if needed)

- [ ] **Step 1: Create base scene class**

```python
# src/scenes/base.py
class Scene:
    def __init__(self, game):
        self.game = game
        self.next_scene = None

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass

    def finished(self):
        return self.next_scene is not None
```

- [ ] **Step 2: Write stub MenuScene that shows blank screen with title text**

```python
# src/scenes/menu.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.Font(None, 72)
        self.font_item = pygame.font.Font(None, 36)

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(COLOR_BG)
        title = self.font_title.render("双人枪战", True, COLOR_TEXT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
```

- [ ] **Step 3: Run main.py to verify window opens with title**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && timeout 2 python main.py 2>&1 || true
```

Expected: Window appears briefly with "双人枪战" title, no crash.

---

### Task 3: Vector Math Utility and Basic Physics Module

**Files:**
- Create: `src/core/vector.py`
- Create: `src/core/physics.py`

- [ ] **Step 1: Create Vec2 class for 2D vector math**

```python
# src/core/vector.py
import math


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, s):
        return Vec2(self.x * s, self.y * s)

    def __truediv__(self, s):
        return Vec2(self.x / s, self.y / s)

    def __iter__(self):
        yield self.x
        yield self.y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vec2(0, 0)
        return Vec2(self.x / length, self.y / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        return (self - other).length()

    def rotate(self, angle_rad):
        cos = math.cos(angle_rad)
        sin = math.sin(angle_rad)
        return Vec2(self.x * cos - self.y * sin, self.x * sin + self.y * cos)

    def to_tuple(self):
        return (self.x, self.y)
```

- [ ] **Step 2: Create physics.py with circle-wall and circle-circle collision**

```python
# src/core/physics.py
from config import TILE_SIZE, BULLET_RADIUS


def circle_rect_collision(circle_center, radius, rect):
    """Circle vs AABB rect collision. Returns (hit, normal_vec, penetration)."""
    cx, cy = circle_center.x, circle_center.y
    rx, ry, rw, rh = rect

    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))

    dx = cx - closest_x
    dy = cy - closest_y
    dist_sq = dx * dx + dy * dy

    if dist_sq < radius * radius:
        dist = (dist_sq) ** 0.5
        if dist == 0:
            # Center is inside rect; push along nearest edge
            overlap_left = cx - rx
            overlap_right = (rx + rw) - cx
            overlap_top = cy - ry
            overlap_bottom = (ry + rh) - cy
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_overlap == overlap_left:
                return (True, (-1, 0), radius)
            elif min_overlap == overlap_right:
                return (True, (1, 0), radius)
            elif min_overlap == overlap_top:
                return (True, (0, -1), radius)
            else:
                return (True, (0, 1), radius)
        penetration = radius - dist
        if dist > 0.001:
            nx = dx / dist
            ny = dy / dist
        else:
            nx, ny = 1, 0
        return (True, (nx, ny), penetration)
    return (False, (0, 0), 0)


def circle_circle_collision(c1, r1, c2, r2):
    """Returns (hit, overlap_distance)."""
    dist = c1.distance_to(c2)
    overlap = (r1 + r2) - dist
    if overlap > 0:
        return (True, overlap)
    return (False, 0)


def point_in_rect(px, py, rect):
    rx, ry, rw, rh = rect
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def ray_cast_grid(start, direction, max_dist, grid, tile_size=TILE_SIZE):
    """Walk along a ray through a tile grid. Returns (hit_point, hit_normal, tile_coord) or None."""
    step = direction.normalized() * (tile_size * 0.5)
    pos = start
    traveled = 0.0
    steps = int(max_dist / (tile_size * 0.5)) + 1
    for _ in range(steps):
        pos = pos + step
        traveled += tile_size * 0.5
        if traveled > max_dist:
            return None
        tx = int(pos.x // tile_size)
        ty = int(pos.y // tile_size)
        if tx < 0 or ty < 0 or ty >= len(grid) or tx >= len(grid[0]):
            return (pos, Vec2(0, 0), (tx, ty))
        if grid[ty][tx] != 0:
            return (pos, Vec2(0, 0), (tx, ty))
    return None
```

- [ ] **Step 4: Verify imports and Vec2 operations**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
from src.core.vector import Vec2
v1 = Vec2(3, 4)
assert v1.length() == 5.0
v2 = v1.normalized()
assert abs(v2.length() - 1.0) < 0.001
print('Vec2 OK')
from src.core.physics import circle_circle_collision
hit, overlap = circle_circle_collision(Vec2(0,0), 10, Vec2(5,0), 10)
assert hit
print('Physics OK')
"
```

Expected: `Vec2 OK` `Physics OK`

---

### Task 4: Player Entity — Movement, Rotation, Cartoon Rendering

**Files:**
- Create: `src/entities/__init__.py`
- Create: `src/entities/player.py`

- [ ] **Step 1: Create Player class with movement and cartoon-style rendering**

```python
# src/entities/player.py
import math
import pygame
from config import (
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_MAX_HP,
    SPRINT_SPEED_MULT, SPRINT_DURATION, SPRINT_COOLDOWN,
    DODGE_DISTANCE, DODGE_DURATION, DODGE_COOLDOWN,
    COLOR_OUTLINE,
)
from src.core.vector import Vec2


class Player:
    def __init__(self, player_id, position, color, key_config):
        self.id = player_id
        self.pos = Vec2(*position)
        self.vel = Vec2(0, 0)
        self.color = color
        self.keys = key_config  # dict of action->pygame key constant
        self.radius = PLAYER_RADIUS
        self.aim_angle = 0.0  # radians, points toward mouse or aim direction
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.money = 0
        self.current_weapon = None  # set by weapon system later
        self.items = []

        # Sprint state
        self.sprint_timer = 0.0
        self.sprint_cooldown_timer = 0.0
        self.is_sprinting = False

        # Dodge state
        self.dodge_timer = 0.0
        self.dodge_cooldown_timer = 0.0
        self.dodge_dir = Vec2(0, 0)
        self.is_dodging = False
        self.dodge_invincible = False

    def handle_input(self, keys_pressed):
        if not self.alive:
            return
        if self.is_dodging:
            return

        # Sprint
        if keys_pressed.get(self.keys["sprint"], False):
            if self.sprint_timer <= 0 and self.sprint_cooldown_timer <= 0:
                self.is_sprinting = True
                self.sprint_timer = SPRINT_DURATION
                self.sprint_cooldown_timer = SPRINT_COOLDOWN

        # Dodge
        if keys_pressed.get(self.keys["dodge"], False):
            if self.dodge_cooldown_timer <= 0 and not self.is_sprinting:
                move_x = 0
                move_y = 0
                if keys_pressed.get(self.keys["left"], False):
                    move_x -= 1
                if keys_pressed.get(self.keys["right"], False):
                    move_x += 1
                if keys_pressed.get(self.keys["up"], False):
                    move_y -= 1
                if keys_pressed.get(self.keys["down"], False):
                    move_y += 1
                if move_x != 0 or move_y != 0:
                    self.dodge_dir = Vec2(move_x, move_y).normalized()
                else:
                    self.dodge_dir = Vec2(
                        math.cos(self.aim_angle), math.sin(self.aim_angle)
                    )
                self.is_dodging = True
                self.dodge_timer = DODGE_DURATION
                self.dodge_cooldown_timer = DODGE_COOLDOWN
                self.dodge_invincible = True

    def update(self, dt, keys_pressed, walls):
        if not self.alive:
            return

        # Update timers
        self.sprint_timer = max(0, self.sprint_timer - dt)
        self.sprint_cooldown_timer = max(0, self.sprint_cooldown_timer - dt)
        self.dodge_cooldown_timer = max(0, self.dodge_cooldown_timer - dt)

        if self.is_sprinting and self.sprint_timer <= 0:
            self.is_sprinting = False

        if self.is_dodging:
            self.dodge_timer -= dt
            speed = DODGE_DISTANCE / DODGE_DURATION
            new_pos = self.pos + self.dodge_dir * speed * dt
            # Simple wall collision during dodge
            if not self._collides_wall(new_pos, walls):
                self.pos = new_pos
            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.dodge_invincible = False
            return

        # Movement
        speed = PLAYER_SPEED
        if self.is_sprinting:
            speed *= SPRINT_SPEED_MULT

        move_x = 0
        move_y = 0
        if keys_pressed.get(self.keys["left"], False):
            move_x -= 1
        if keys_pressed.get(self.keys["right"], False):
            move_x += 1
        if keys_pressed.get(self.keys["up"], False):
            move_y -= 1
        if keys_pressed.get(self.keys["down"], False):
            move_y += 1

        if move_x != 0 or move_y != 0:
            move_vec = Vec2(move_x, move_y).normalized()
            new_pos = self.pos + move_vec * speed * dt
            # Resolve wall collision
            if not self._collides_wall(new_pos, walls):
                self.pos = new_pos
            else:
                # Try separate axes
                px = self.pos + Vec2(move_vec.x * speed * dt, 0)
                py = self.pos + Vec2(0, move_vec.y * speed * dt)
                if not self._collides_wall(px, walls):
                    self.pos = px
                elif not self._collides_wall(py, walls):
                    self.pos = py

    def _collides_wall(self, pos, walls):
        """Check circle vs all wall rects."""
        from src.core.physics import circle_rect_collision
        for wall_rect in walls:
            hit, _, _ = circle_rect_collision(pos, self.radius, wall_rect)
            if hit:
                return True
        return False

    def take_damage(self, amount, is_headshot=False):
        if self.dodge_invincible:
            return 0
        dmg = amount * 2 if is_headshot else amount
        self.hp = max(0, self.hp - dmg)
        if self.hp <= 0:
            self.alive = False
        return dmg

    def heal(self, amount):
        self.hp = min(PLAYER_MAX_HP, self.hp + amount)

    def set_aim(self, target_x, target_y):
        dx = target_x - self.pos.x
        dy = target_y - self.pos.y
        self.aim_angle = math.atan2(dy, dx)

    def render(self, screen, camera_offset=Vec2(0, 0)):
        """Cartoon-style rendering with outline and body."""
        if not self.alive:
            return
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)

        # Outline (slightly larger dark circle)
        pygame.draw.circle(screen, COLOR_OUTLINE, (sx, sy), self.radius + 2)
        # Body
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # Inner highlight (lighter shade)
        lighter = tuple(min(c + 60, 255) for c in self.color)
        pygame.draw.circle(screen, lighter, (sx - 3, sy - 3), self.radius - 6)

        # Aim indicator line
        end_x = sx + (self.radius + 10) * math.cos(self.aim_angle)
        end_y = sy + (self.radius + 10) * math.sin(self.aim_angle)
        pygame.draw.line(screen, (255, 255, 200), (sx, sy), (end_x, end_y), 3)

        # Direction dot (front of player)
        front_x = sx + self.radius * 0.6 * math.cos(self.aim_angle)
        front_y = sy + self.radius * 0.6 * math.sin(self.aim_angle)
        pygame.draw.circle(screen, (255, 255, 255), (int(front_x), int(front_y)), 3)
```

- [ ] **Step 2: Verify player module imports**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
from src.entities.player import Player
p = Player(1, (100, 100), (50, 150, 255), {})
assert p.hp == 100
assert p.alive
p.take_damage(60)
assert p.hp == 40
p.heal(20)
assert p.hp == 60
print('Player OK')
"
```

Expected: `Player OK`

---

### Task 5: Weapon Data and Bullet Entity

**Files:**
- Create: `data/weapons.json`
- Create: `src/entities/weapon.py`
- Create: `src/entities/bullet.py`

- [ ] **Step 1: Create weapons.json data file**

```json
[
  {
    "name": "手枪",
    "id": "pistol",
    "body_damage": 15,
    "head_damage": 25,
    "fire_rate": 0.4,
    "mag_size": 12,
    "reload_time": 1.2,
    "bullet_speed": "fast",
    "bullet_count": 1,
    "spread_angle": 3,
    "price": 0,
    "color": [180, 180, 180]
  },
  {
    "name": "冲锋枪",
    "id": "smg",
    "body_damage": 10,
    "head_damage": 18,
    "fire_rate": 0.1,
    "mag_size": 30,
    "reload_time": 1.8,
    "bullet_speed": "medium",
    "bullet_count": 1,
    "spread_angle": 10,
    "price": 1200,
    "color": [200, 150, 50]
  },
  {
    "name": "霰弹枪",
    "id": "shotgun",
    "body_damage": 8,
    "head_damage": 15,
    "fire_rate": 0.8,
    "mag_size": 6,
    "reload_time": 2.0,
    "bullet_speed": "fast",
    "bullet_count": 5,
    "spread_angle": 18,
    "price": 1800,
    "color": [200, 100, 50]
  },
  {
    "name": "突击步枪",
    "id": "rifle",
    "body_damage": 22,
    "head_damage": 38,
    "fire_rate": 0.15,
    "mag_size": 25,
    "reload_time": 1.5,
    "bullet_speed": "fast",
    "bullet_count": 1,
    "spread_angle": 5,
    "price": 2500,
    "color": [100, 180, 100]
  },
  {
    "name": "狙击枪",
    "id": "sniper",
    "body_damage": 65,
    "head_damage": 100,
    "fire_rate": 1.5,
    "mag_size": 5,
    "reload_time": 2.5,
    "bullet_speed": "very_fast",
    "bullet_count": 1,
    "spread_angle": 0,
    "price": 3500,
    "color": [80, 80, 200]
  },
  {
    "name": "火箭筒",
    "id": "rocket",
    "body_damage": 80,
    "head_damage": 80,
    "fire_rate": 2.0,
    "mag_size": 1,
    "reload_time": 3.0,
    "bullet_speed": "slow",
    "bullet_count": 1,
    "spread_angle": 2,
    "price": 4000,
    "color": [220, 50, 50],
    "explosive": true,
    "explosion_radius": 80,
    "explosion_push": 150
  }
]
```

- [ ] **Step 2: Create weapon.py to load and manage weapon definitions**

```python
# src/entities/weapon.py
import json
import math
import os
from config import BULLET_SPEEDS


class WeaponDef:
    """Read-only weapon definition loaded from JSON."""
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
    """Runtime weapon instance for a player."""
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


def load_weapons(path="data/weapons.json"):
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    full = os.path.join(base, path)
    with open(full, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [WeaponDef(d) for d in data]
```

- [ ] **Step 3: Create bullet.py with trajectory and bounce logic**

```python
# src/entities/bullet.py
import math
import pygame
from config import BULLET_RADIUS, MAX_BOUNCES, COLOR_OUTLINE
from src.core.vector import Vec2


class Bullet:
    def __init__(self, position, angle, speed, damage, owner_id, color,
                 is_explosive=False, explosion_radius=0, explosion_push=0):
        self.pos = Vec2(*position)
        self.vel = Vec2(math.cos(angle), math.sin(angle)) * speed
        self.speed = speed
        self.damage = damage
        self.owner_id = owner_id
        self.color = color
        self.radius = BULLET_RADIUS
        self.alive = True
        self.bounces_left = MAX_BOUNCES
        self.is_explosive = is_explosive
        self.explosion_radius = explosion_radius
        self.explosion_push = explosion_push
        self.gravity = 150 if is_explosive else 0  # rocket arcs

    def update(self, dt, walls):
        if not self.alive:
            return

        # Apply gravity (rocket)
        if self.gravity > 0:
            self.vel = self.vel + Vec2(0, self.gravity * dt)
            # Update angle to match velocity
            if self.vel.length() > 0.001:
                self.vel = self.vel.normalized() * self.speed

        new_pos = self.pos + self.vel * dt

        # Check wall collisions for bounce
        from src.core.physics import circle_rect_collision
        bounced = False
        for wall_rect in walls:
            hit, normal, penetration = circle_rect_collision(new_pos, self.radius, wall_rect)
            if hit:
                if self.bounces_left > 0:
                    nx, ny = normal
                    # Reflect velocity
                    dot = self.vel.x * nx + self.vel.y * ny
                    self.vel = Vec2(
                        self.vel.x - 2 * dot * nx,
                        self.vel.y - 2 * dot * ny,
                    )
                    # Push out of wall
                    new_pos = new_pos + Vec2(nx * penetration, ny * penetration)
                    self.bounces_left -= 1
                    bounced = True
                else:
                    self.alive = False
                    return
                break

        self.pos = new_pos

    def render(self, screen, camera_offset=Vec2(0, 0)):
        if not self.alive:
            return
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        # Outline
        pygame.draw.circle(screen, COLOR_OUTLINE, (sx, sy), self.radius + 1)
        # Body
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # Trail effect
        trail = self.pos - self.vel.normalized() * 6
        tx = int(trail.x - camera_offset.x)
        ty = int(trail.y - camera_offset.y)
        pygame.draw.line(screen, (*self.color, 128), (sx, sy), (tx, ty), 4)
```

- [ ] **Step 4: Verify weapon loading**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
import sys; sys.path.insert(0, '.')
from src.entities.weapon import load_weapons
weapons = load_weapons()
print(f'Loaded {len(weapons)} weapons:')
for w in weapons:
    print(f'  {w.name} - ${w.price}, dmg {w.body_damage}/{w.head_damage}')
"
```

Expected: Loaded 6 weapons listed.

---

### Task 6: Map System — Grid-Based Maps with JSON

**Files:**
- Create: `data/maps/__init__.py`
- Create: `data/maps/training_yard.json`
- Create: `src/entities/map.py`

- [ ] **Step 1: Create first map JSON (training yard)**

```json
{
  "name": "训练靶场",
  "width": 60,
  "height": 40,
  "player1_spawn": [5, 20],
  "player2_spawn": [55, 20],
  "gravity": 1.0,
  "tiles": [
  ]
}
```

Note: The tiles grid is enormous (60x40=2400 cells). Generate it programmatically in map.py instead of writing all tiles by hand. The JSON stores only wall definitions as rectangle regions.

- [ ] **Step 2: Create map.py with Map class**

```python
# src/entities/map.py
import json
import os
import pygame
from config import TILE_SIZE, COLOR_OUTLINE


class GameMap:
    def __init__(self, map_path):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full = os.path.join(base, map_path)
        with open(full, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.name = data["name"]
        self.width = data["width"] * TILE_SIZE
        self.height = data["height"] * TILE_SIZE
        self.cols = data["width"]
        self.rows = data["height"]
        self.gravity_mod = data.get("gravity", 1.0)
        self.player1_spawn = data["player1_spawn"]
        self.player2_spawn = data["player2_spawn"]

        # Load walls from "walls" array of [x, y, w, h] in tile coords
        self.wall_rects = []
        for w in data.get("walls", []):
            self.wall_rects.append(pygame.Rect(
                w[0] * TILE_SIZE, w[1] * TILE_SIZE,
                w[2] * TILE_SIZE, w[3] * TILE_SIZE,
            ))

        # Build tile grid for rendering and collision lookups
        self.tiles = [[0] * self.cols for _ in range(self.rows)]
        for i, w in enumerate(data.get("walls", [])):
            tile_type = w[4] if len(w) > 4 else 1  # 1=wall, 2=destructible
            for ty in range(w[1], w[1] + w[3]):
                for tx in range(w[0], w[0] + w[2]):
                    if 0 <= ty < self.rows and 0 <= tx < self.cols:
                        self.tiles[ty][tx] = tile_type

    def get_spawn(self, player_id):
        if player_id == 1:
            return (self.player1_spawn[0] * TILE_SIZE + TILE_SIZE // 2,
                    self.player1_spawn[1] * TILE_SIZE + TILE_SIZE // 2)
        else:
            return (self.player2_spawn[0] * TILE_SIZE + TILE_SIZE // 2,
                    self.player2_spawn[1] * TILE_SIZE + TILE_SIZE // 2)

    def render(self, screen, camera_offset):
        """Render visible portion of map tiles."""
        ox, oy = camera_offset.x, camera_offset.y
        start_tx = max(0, int(ox // TILE_SIZE) - 1)
        start_ty = max(0, int(oy // TILE_SIZE) - 1)
        screen_w, screen_h = screen.get_size()
        end_tx = min(self.cols, int((ox + screen_w) // TILE_SIZE) + 1)
        end_ty = min(self.rows, int((oy + screen_h) // TILE_SIZE) + 1)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = self.tiles[ty][tx]
                if tile == 0:
                    continue
                rx = tx * TILE_SIZE - ox
                ry = ty * TILE_SIZE - oy
                if tile == 1:
                    color = (80, 80, 90)
                elif tile == 2:
                    color = (140, 100, 50)
                else:
                    color = (100, 100, 120)
                pygame.draw.rect(screen, color, (rx, ry, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, COLOR_OUTLINE, (rx, ry, TILE_SIZE, TILE_SIZE), 1)


def load_map(map_name):
    return GameMap(f"data/maps/{map_name}.json")
```

- [ ] **Step 3: Update training_yard.json with proper wall data**

```json
{
  "name": "训练靶场",
  "width": 80,
  "height": 45,
  "player1_spawn": [5, 22],
  "player2_spawn": [74, 22],
  "gravity": 1.0,
  "walls": [
    [0, 0, 80, 1],
    [0, 44, 80, 1],
    [0, 0, 1, 45],
    [79, 0, 1, 45],
    [25, 10, 2, 3],
    [53, 10, 2, 3],
    [38, 15, 4, 2],
    [30, 25, 4, 2],
    [46, 25, 4, 2],
    [18, 30, 3, 2],
    [59, 30, 3, 2],
    [38, 32, 4, 2],
    [10, 15, 13, 2],
    [57, 15, 13, 2]
  ]
}
```

- [ ] **Step 4: Verify map loading**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
from src.entities.map import load_map
m = load_map('training_yard')
print(f'Map: {m.name}, size: {m.width}x{m.height}')
print(f'P1 spawn: {m.get_spawn(1)}, P2 spawn: {m.get_spawn(2)}')
print(f'Walls: {len(m.wall_rects)}')
"
```

Expected: Map loaded with spawn points and walls.

---

### Task 7: Camera — Split-Screen System

**Files:**
- Create: `src/core/camera.py`

- [ ] **Step 1: Create camera.py with split-screen support**

```python
# src/core/camera.py
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.vector import Vec2


class Camera:
    """Tracks a target position and provides a camera offset for rendering."""
    def __init__(self, map_width, map_height, viewport_rect):
        self.map_w = map_width
        self.map_h = map_height
        self.vp = viewport_rect  # pygame.Rect of the viewport on screen
        self.target = Vec2(0, 0)
        self.offset = Vec2(0, 0)

    def set_target(self, pos):
        self.target = Vec2(pos.x, pos.y) if isinstance(pos, Vec2) else Vec2(*pos)

    def update(self):
        self.offset.x = self.target.x - self.vp.width // 2
        self.offset.y = self.target.y - self.vp.height // 2
        self.offset.x = max(0, min(self.offset.x, self.map_w - self.vp.width))
        self.offset.y = max(0, min(self.offset.y, self.map_h - self.vp.height))

    def world_to_screen(self, world_pos):
        x = world_pos.x - self.offset.x + self.vp.x
        y = world_pos.y - self.offset.y + self.vp.y
        return (int(x), int(y))


class SplitCamera:
    """Manages two cameras for split-screen or merges when players are close."""
    def __init__(self, map_width, map_height):
        self.map_w = map_width
        self.map_h = map_height
        half_w = SCREEN_WIDTH // 2
        import pygame
        self.cam1 = Camera(map_width, map_height, pygame.Rect(0, 0, half_w, SCREEN_HEIGHT))
        self.cam2 = Camera(map_width, map_height, pygame.Rect(half_w, 0, half_w, SCREEN_HEIGHT))
        self.merged = False
        self.merge_cam = Camera(map_width, map_height, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def update(self, player1_pos, player2_pos):
        import math
        p1 = Vec2(*player1_pos) if not hasattr(player1_pos, 'x') else player1_pos
        p2 = Vec2(*player2_pos) if not hasattr(player2_pos, 'x') else player2_pos

        dist = p1.distance_to(p2)
        # Merge if both players fit in one screen
        if dist < (SCREEN_WIDTH // 2) * 0.7:
            self.merged = True
            mid = Vec2((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
            self.merge_cam.set_target(mid)
            self.merge_cam.update()
        else:
            self.merged = False
            self.cam1.set_target(p1)
            self.cam2.set_target(p2)
            self.cam1.update()
            self.cam2.update()

    def get_cameras(self):
        if self.merged:
            return [(self.merge_cam, None)]
        return [(self.cam1, 1), (self.cam2, 2)]

    def render_divider(self, screen):
        if not self.merged:
            mid_x = SCREEN_WIDTH // 2
            import pygame
            pygame.draw.line(screen, (60, 60, 60), (mid_x, 0), (mid_x, SCREEN_HEIGHT), 2)
```

- [ ] **Step 2: Verify camera module**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
from src.core.camera import SplitCamera
sc = SplitCamera(2560, 1440)
sc.update((100, 100), (200, 200))
assert sc.merged == True
sc.update((100, 100), (2000, 2000))
assert sc.merged == False
print('Camera OK')
"
```

Expected: `Camera OK`

---

### Task 8: UI Components — Button, HealthBar, Text

**Files:**
- Create: `src/ui/__init__.py`
- Create: `src/ui/button.py`
- Create: `src/ui/health_bar.py`

- [ ] **Step 1: Create button.py**

```python
# src/ui/button.py
import pygame
from config import COLOR_TEXT, COLOR_OUTLINE

DEFAULT_FONT = None


def get_font(size):
    global DEFAULT_FONT
    if DEFAULT_FONT is None:
        DEFAULT_FONT = pygame.font.Font(None, size)
    return pygame.font.Font(None, size)


class Button:
    def __init__(self, x, y, w, h, text, callback, font_size=32,
                 color=(60, 60, 80), hover_color=(80, 80, 110), text_color=COLOR_TEXT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = get_font(font_size)
        self.hovered = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def render(self, screen):
        c = self.hover_color if self.hovered else self.color
        if not self.enabled:
            c = tuple(max(0, x - 40) for x in c)
        pygame.draw.rect(screen, c, self.rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_OUTLINE, self.rect, 2, border_radius=6)
        text_surf = self.font.render(self.text, True, self.text_color)
        tx = self.rect.centerx - text_surf.get_width() // 2
        ty = self.rect.centery - text_surf.get_height() // 2
        screen.blit(text_surf, (tx, ty))
```

- [ ] **Step 2: Create health_bar.py**

```python
# src/ui/health_bar.py
import pygame
from config import COLOR_HP_BAR, COLOR_HP_LOW, COLOR_OUTLINE


class HealthBar:
    def __init__(self, width=200, height=16):
        self.width = width
        self.height = height

    def render(self, screen, x, y, current_hp, max_hp, label=""):
        ratio = max(0, current_hp / max_hp)
        # Background
        pygame.draw.rect(screen, (40, 40, 40), (x, y, self.width, self.height))
        # Fill
        color = COLOR_HP_BAR if ratio > 0.3 else COLOR_HP_LOW
        fill_w = int(self.width * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, y, fill_w, self.height))
        # Outline
        pygame.draw.rect(screen, COLOR_OUTLINE, (x, y, self.width, self.height), 1)
        # Text
        font = pygame.font.Font(None, 20)
        text = font.render(f"{label} {current_hp}/{max_hp}", True, (255, 255, 255))
        screen.blit(text, (x + 4, y + 1))
```

- [ ] **Step 3: Verify UI components**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
import pygame
pygame.init()
from src.ui.button import Button
from src.ui.health_bar import HealthBar
b = Button(0, 0, 100, 40, 'Test', lambda: None)
assert b.text == 'Test'
h = HealthBar()
print('UI OK')
"
```

Expected: `UI OK`

---

### Task 9: Main Menu Scene

**Files:**
- Create/Modify: `src/scenes/menu.py`

- [ ] **Step 1: Implement full MenuScene with buttons**

```python
# src/scenes/menu.py
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

    def render(self, screen):
        screen.fill(COLOR_BG)
        title = self.font_title.render("双 人 枪 战", True, (255, 200, 60))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        sub = self.font_sub.render("Two-Player Shooter", True, COLOR_TEXT)
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 160))

        for btn in self.buttons:
            btn.render(screen)

        # Show current profile
        prof_font = pygame.font.Font(None, 20)
        prof_text = prof_font.render("存档: 未加载", True, (150, 150, 150))
        screen.blit(prof_text, (10, SCREEN_HEIGHT - 25))
```

- [ ] **Step 2: Test menu scene renders**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
import pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
from src.core.game import Game
from src.scenes.menu import MenuScene
# Just verify imports and construction
g = None
# Quick smoke test
print('MenuScene OK')
"
```

Expected: `MenuScene OK`

---

### Task 10: Settings Scene — Keybinding Display

**Files:**
- Create: `src/scenes/settings.py`

- [ ] **Step 1: Create settings scene with back button and key display**

```python
# src/scenes/settings.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class SettingsScene(Scene):
    def __init__(self, game, return_scene):
        super().__init__(game)
        self.return_scene = return_scene
        self.font_title = pygame.font.Font(None, 60)
        self.font_text = pygame.font.Font(None, 28)
        self.back_btn = Button(
            SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 80, 260, 50,
            "返回", self._go_back
        )

    def _go_back(self):
        self.next_scene = self.return_scene

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def render(self, screen):
        screen.fill(COLOR_BG)
        t = self.font_title.render("设置", True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 30))

        lines = [
            "玩家1: WASD 移动 | E 射击 | Q 道具 | Shift 冲刺 | Space 翻滚",
            "玩家2: ↑↓←→ 移动 | / 射击 | . 道具 | RShift 冲刺 | RCtrl 翻滚",
            "",
            "键位自定义功能将在后续版本开放",
        ]
        for i, line in enumerate(lines):
            s = self.font_text.render(line, True, COLOR_TEXT)
            screen.blit(s, (100, 120 + i * 35))

        self.back_btn.render(screen)
```

---

### Task 11: Lobby Scene — Map and Character Selection

**Files:**
- Create: `src/scenes/lobby.py`

- [ ] **Step 1: Create lobby scene**

```python
# src/scenes/lobby.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG, COLOR_PLAYER1, COLOR_PLAYER2
from src.scenes.base import Scene
from src.ui.button import Button


MAP_LIST = ["training_yard"]


class LobbyScene(Scene):
    def __init__(self, game, vs_ai=False):
        super().__init__(game)
        self.vs_ai = vs_ai
        self.font_title = pygame.font.Font(None, 50)
        self.font_text = pygame.font.Font(None, 28)
        self.selected_map = 0

        bw = 260
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.start_btn = Button(cx, 600, bw, 50, "开始战斗", self._start_battle)
        self.back_btn = Button(cx, 660, bw, 50, "返回", self._go_back)

    def _start_battle(self):
        from src.scenes.battle import BattleScene
        map_name = MAP_LIST[self.selected_map]
        self.next_scene = BattleScene(
            self.game, map_name,
            p1_color=COLOR_PLAYER1, p2_color=COLOR_PLAYER2,
            vs_ai=self.vs_ai
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

    def render(self, screen):
        screen.fill(COLOR_BG)
        t = self.font_title.render("选择地图", True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 30))

        # Map name display
        map_name = MAP_LIST[self.selected_map]
        m = self.font_text.render(f"《{map_name}》", True, (255, 200, 60))
        screen.blit(m, (SCREEN_WIDTH // 2 - m.get_width() // 2, 200))

        hint = self.font_text.render("← → 切换地图", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 250))

        # Player info
        p1 = self.font_text.render("玩家1 (蓝方)  vs  玩家2 (红方)", True, COLOR_TEXT)
        if self.vs_ai:
            p1 = self.font_text.render("玩家 (蓝方)  vs  AI (红方)", True, COLOR_TEXT)
        screen.blit(p1, (SCREEN_WIDTH // 2 - p1.get_width() // 2, 350))

        self.start_btn.render(screen)
        self.back_btn.render(screen)
```

---

### Task 12: Battle Scene — Core Gameplay Integration

**Files:**
- Create: `src/scenes/battle.py`

This is the largest and most complex scene. I'll implement it in layers.

- [ ] **Step 1: Create battle scene skeleton with player spawning and rendering**

```python
# src/scenes/battle.py
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG,
    COLOR_PLAYER1, COLOR_PLAYER2, COLOR_TEXT,
    PLAYER1_KEYS, PLAYER2_KEYS,
    PLAYER_MAX_HP,
)
from src.scenes.base import Scene
from src.entities.player import Player
from src.entities.map import load_map
from src.entities.weapon import load_weapons, WeaponState
from src.entities.bullet import Bullet
from src.core.camera import SplitCamera
from src.core.vector import Vec2
from src.ui.health_bar import HealthBar


class BattleScene(Scene):
    def __init__(self, game, map_name, p1_color=COLOR_PLAYER1, p2_color=COLOR_PLAYER2,
                 vs_ai=False, game_mode="elimination"):
        super().__init__(game)
        self.game_map = load_map(map_name)
        self.vs_ai = vs_ai
        self.game_mode = game_mode  # "elimination" or "deathmatch"

        # Load weapons
        weapon_defs = load_weapons()
        self.weapon_defs = {w.weapon_id: w for w in weapon_defs}
        pistol_def = self.weapon_defs["pistol"]

        # Create players
        p1_spawn = self.game_map.get_spawn(1)
        p2_spawn = self.game_map.get_spawn(2)
        self.player1 = Player(1, p1_spawn, p1_color, PLAYER1_KEYS)
        self.player2 = Player(2, p2_spawn, p2_color, PLAYER2_KEYS)
        self.player1.current_weapon = WeaponState(pistol_def)
        self.player2.current_weapon = WeaponState(pistol_def)

        self.bullets = []
        self.camera = SplitCamera(self.game_map.width, self.game_map.height)
        self.health_bar = HealthBar()

        # Round tracking
        self.round_active = True
        self.round_timer = 90  # seconds for elimination mode
        self.p1_score = 0
        self.p2_score = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.menu import MenuScene
            self.next_scene = MenuScene(self.game)
            return

    def update(self, dt):
        keys = pygame.key.get_pressed()
        key_map1 = {v: keys[v] for v in self.player1.keys.values()}
        key_map2 = {v: keys[v] for v in self.player2.keys.values()}

        self.player1.handle_input(key_map1)
        self.player2.handle_input(key_map2)

        walls = self.game_map.wall_rects
        self.player1.update(dt, key_map1, walls)
        self.player2.update(dt, key_map2, walls)

        # Aim toward each other (keyboard-only, aim in movement direction)
        # For now: each player aims toward the opponent
        if self.player1.alive:
            self.player1.set_aim(self.player2.pos.x, self.player2.pos.y)
        if self.player2.alive:
            self.player2.set_aim(self.player1.pos.x, self.player1.pos.y)

        # Shooting
        self._handle_shooting(dt, keys)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt, walls)
            if not bullet.alive:
                self.bullets.remove(bullet)
                continue
            # Out of bounds
            if (bullet.pos.x < -50 or bullet.pos.x > self.game_map.width + 50 or
                    bullet.pos.y < -50 or bullet.pos.y > self.game_map.height + 50):
                self.bullets.remove(bullet)
                continue
            # Hit players
            self._check_bullet_hits(bullet)

        # Update weapons
        if self.player1.current_weapon:
            self.player1.current_weapon.update(dt)
        if self.player2.current_weapon:
            self.player2.current_weapon.update(dt)

        # Camera
        self.camera.update(self.player1.pos, self.player2.pos)

        # Round timer
        if self.round_active:
            self.round_timer -= dt
            if self.round_timer <= 0:
                self._end_round_timeout()

    def _handle_shooting(self, dt, keys):
        for player in [self.player1, self.player2]:
            if not player.alive:
                continue
            ws = player.current_weapon
            if ws is None:
                continue
            if keys.get(player.keys["shoot"], False):
                if ws.can_fire():
                    ws.fire()
                    wdef = ws.def_
                    import math, random
                    angle = player.aim_angle
                    for i in range(wdef.bullet_count):
                        spread = 0
                        if wdef.spread_angle > 0:
                            spread = math.radians(random.uniform(-wdef.spread_angle, wdef.spread_angle))
                        b_angle = angle + spread
                        spawn_x = player.pos.x + player.radius * math.cos(b_angle)
                        spawn_y = player.pos.y + player.radius * math.sin(b_angle)
                        bullet = Bullet(
                            (spawn_x, spawn_y), b_angle, wdef.bullet_speed,
                            wdef.body_damage, player.id, wdef.color,
                            is_explosive=wdef.explosive,
                            explosion_radius=wdef.explosion_radius,
                            explosion_push=wdef.explosion_push,
                        )
                        self.bullets.append(bullet)
            # Reload on R key is automatic when empty, but manual reload here
            if keys.get(pygame.K_r, False):
                if ws:
                    ws.start_reload()

    def _check_bullet_hits(self, bullet):
        target = self.player2 if bullet.owner_id == 1 else self.player1
        if not target.alive:
            return
        from src.core.physics import circle_circle_collision
        hit, _ = circle_circle_collision(bullet.pos, bullet.radius,
                                          target.pos, target.radius)
        if hit:
            is_headshot = False  # Simplified: random 10% headshot
            import random
            if random.random() < 0.1:
                is_headshot = True
            dmg = target.take_damage(bullet.damage, is_headshot)
            if bullet.is_explosive:
                self._explosion(bullet)
            bullet.alive = False
            if not target.alive:
                self._on_player_killed(bullet.owner_id)

    def _explosion(self, bullet):
        # Damage nearby players, push them
        from src.core.physics import circle_circle_collision
        for player in [self.player1, self.player2]:
            if not player.alive:
                continue
            hit, _ = circle_circle_collision(
                bullet.pos, bullet.explosion_radius,
                player.pos, player.radius
            )
            if hit:
                player.take_damage(30)
                push = (player.pos - bullet.pos).normalized() * bullet.explosion_push
                new_p = player.pos + push * 0.1  # limited push
                if not player._collides_wall(new_p, self.game_map.wall_rects):
                    player.pos = new_p

    def _on_player_killed(self, killer_id):
        if self.game_mode == "elimination":
            if killer_id == 1:
                self.p1_score += 1
            else:
                self.p2_score += 1
            self.round_active = False
            # Wait 2 seconds then go to result or next round
            self._round_end_timer = 2.0

    def _end_round_timeout(self):
        self.round_active = False
        hp1 = self.player1.hp if self.player1.alive else 0
        hp2 = self.player2.hp if self.player2.alive else 0
        if hp1 > hp2:
            self.p1_score += 1
        elif hp2 > hp1:
            self.p2_score += 1
        self._round_end_timer = 2.0

    def render(self, screen):
        screen.fill(COLOR_BG)

        cameras = self.camera.get_cameras()
        for cam, owner_id in cameras:
            # Set clip rect to viewport
            screen.set_clip(cam.vp)
            self.game_map.render(screen, cam.offset)
            self.player1.render(screen, cam.offset)
            self.player2.render(screen, cam.offset)
            for bullet in self.bullets:
                bullet.render(screen, cam.offset)
            screen.set_clip(None)

        self.camera.render_divider(screen)

        # HUD at top
        self._render_hud(screen)

    def _render_hud(self, screen):
        # Score
        font = pygame.font.Font(None, 36)
        score = font.render(f"{self.p1_score} - {self.p2_score}", True, COLOR_TEXT)
        screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, 10))

        # Timer
        timer_text = font.render(f"{int(self.round_timer)}s", True, COLOR_TEXT)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 45))

        # Player HP bars
        self.health_bar.render(screen, 10, 10, self.player1.hp, PLAYER_MAX_HP, "P1")
        self.health_bar.render(screen, SCREEN_WIDTH - 210, 10, self.player2.hp, PLAYER_MAX_HP, "P2")
```

- [ ] **Step 2: Test battle scene renders basic map with two players**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && timeout 3 python main.py 2>&1 || true
```

Expected: Window opens, shows split-screen with two players and map. No crash.

---

### Task 13: Economy System

**Files:**
- Create: `src/systems/__init__.py`
- Create: `src/systems/economy.py`

- [ ] **Step 1: Create economy.py**

```python
# src/systems/economy.py
from config import (
    STARTING_MONEY, KILL_REWARD, ROUND_WIN_REWARD,
    ROUND_LOSS_REWARD, LOSS_STREAK_BONUS
)


class Economy:
    """Tracks money per player across rounds."""
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
```

---

### Task 14: Buy Menu Scene

**Files:**
- Create: `src/scenes/buy_menu.py`

- [ ] **Step 1: Create buy menu with weapon and item purchase**

```python
# src/scenes/buy_menu.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG, BUY_TIME, COLOR_MONEY
from src.scenes.base import Scene
from src.ui.button import Button
from src.entities.weapon import load_weapons, WeaponState
from src.systems.economy import Economy


class BuyMenuScene(Scene):
    def __init__(self, game, economy, player_weapons, return_scene):
        super().__init__(game)
        self.economy = economy  # Economy instance
        self.player_weapons = player_weapons  # dict of player_id -> list of WeaponState
        self.return_scene = return_scene
        self.buyer_id = 1  # Start with player 1 buying

        # Track purchased weapons per player (persist across rounds)
        self.owned_weapons = {1: ["pistol"], 2: ["pistol"]}

        self.weapon_defs = load_weapons()
        self.font_title = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 24)
        self.font_buy = pygame.font.Font(None, 20)
        self.time_left = BUY_TIME

        # Generate buy buttons for current buyer
        self._build_buy_buttons()

    def _build_buy_buttons(self):
        self.buy_buttons = []
        y = 160
        for wdef in self.weapon_defs:
            if wdef.price == 0:  # Pistol is free, skip
                continue
            btn = Button(50, y, 300, 40,
                         f"{wdef.name} - ${wdef.price}",
                         lambda wid=wdef.weapon_id: self._buy_weapon(wid),
                         font_size=22)
            self.buy_buttons.append((btn, wdef))
            y += 45

        # Done buying button
        self.done_btn = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 200, 50,
            "完成购买", self._done_buying
        )

    def _buy_weapon(self, weapon_id):
        wdef = next(w for w in self.weapon_defs if w.weapon_id == weapon_id)
        if self.economy.spend(self.buyer_id, wdef.price):
            if weapon_id not in self.owned_weapons[self.buyer_id]:
                self.owned_weapons[self.buyer_id].append(weapon_id)

    def _done_buying(self):
        if self.buyer_id == 1:
            self.buyer_id = 2
            self.time_left = BUY_TIME
            self._build_buy_buttons()
        else:
            # Both done, return to battle
            self.next_scene = self.return_scene
            # Attach owned weapons data for battle scene to use
            self.next_scene.p1_weapons = self.owned_weapons[1]
            self.next_scene.p2_weapons = self.owned_weapons[2]

    def handle_event(self, event):
        self.done_btn.handle_event(event)
        for btn, _ in self.buy_buttons:
            btn.handle_event(event)

    def update(self, dt):
        self.time_left -= dt
        if self.time_left <= 0:
            self._done_buying()

    def render(self, screen):
        screen.fill(COLOR_BG)
        buyer_label = f"玩家{self.buyer_id} 购买阶段"
        t = self.font_title.render(buyer_label, True, COLOR_TEXT)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 20))

        # Timer
        timer = self.font_title.render(f"{int(self.time_left)}s", True,
                                       (255, 100, 100) if self.time_left < 10 else COLOR_TEXT)
        screen.blit(timer, (SCREEN_WIDTH // 2 - timer.get_width() // 2, 70))

        # Money
        money = self.font_small.render(
            f"余额: ${self.economy.get_money(self.buyer_id)}",
            True, COLOR_MONEY
        )
        screen.blit(money, (SCREEN_WIDTH // 2 - money.get_width() // 2, 115))

        # Buy buttons
        for btn, wdef in self.buy_buttons:
            can_buy = self.economy.can_afford(self.buyer_id, wdef.price)
            btn.enabled = can_buy
            btn.render(screen)

        # Owned weapons
        y = 160
        owned = self.owned_weapons[self.buyer_id]
        own_text = self.font_small.render("已拥有: " + ", ".join(owned), True, (150, 150, 150))
        screen.blit(own_text, (400, y))

        self.done_btn.render(screen)
```

---

### Task 15: Result Scene

**Files:**
- Create: `src/scenes/result.py`

- [ ] **Step 1: Create result scene showing match outcome**

```python
# src/scenes/result.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_BG
from src.scenes.base import Scene
from src.ui.button import Button


class ResultScene(Scene):
    def __init__(self, game, p1_score, p2_score, xp_gained=None):
        super().__init__(game)
        self.p1_score = p1_score
        self.p2_score = p2_score
        self.xp_gained = xp_gained or 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)

        bw = 260
        cx = SCREEN_WIDTH // 2 - bw // 2
        self.buttons = [
            Button(cx, 500, bw, 50, "再来一局", self._rematch),
            Button(cx, 570, bw, 50, "返回主菜单", self._go_menu),
        ]

    def _rematch(self):
        from src.scenes.lobby import LobbyScene
        self.next_scene = LobbyScene(self.game)

    def _go_menu(self):
        from src.scenes.menu import MenuScene
        self.next_scene = MenuScene(self.game)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, screen):
        screen.fill(COLOR_BG)

        winner = "玩家1 获胜！" if self.p1_score > self.p2_score else "玩家2 获胜！"
        if self.p1_score == self.p2_score:
            winner = "平局！"

        t = self.font_large.render(winner, True, (255, 200, 60))
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 80))

        score_text = f"{self.p1_score} - {self.p2_score}"
        s = self.font_med.render(score_text, True, COLOR_TEXT)
        screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, 170))

        # XP gained
        xp = self.font_small.render(f"获得经验: +{self.xp_gained} XP", True, (100, 255, 100))
        screen.blit(xp, (SCREEN_WIDTH // 2 - xp.get_width() // 2, 250))

        # Stats
        stats_lines = [
            "--- 本场最佳 ---",
            f"玩家1: {self.p1_score} 回合",
            f"玩家2: {self.p2_score} 回合",
        ]
        for i, line in enumerate(stats_lines):
            st = self.font_small.render(line, True, (200, 200, 200))
            screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, 330 + i * 30))

        for btn in self.buttons:
            btn.render(screen)
```

---

### Task 16: Item System — Grenades, Flash, Smoke, Heal, Shield

**Files:**
- Create: `src/entities/item.py`

- [ ] **Step 1: Create item.py with all 5 item types**

```python
# src/entities/item.py
import math
import pygame
from src.core.vector import Vec2


ITEM_DEFS = {
    "grenade": {
        "name": "手雷", "price": 400, "fuse_time": 2.0,
        "explosion_radius": 80, "damage": 80, "color": (60, 180, 60),
    },
    "flashbang": {
        "name": "闪光弹", "price": 300, "fuse_time": 1.5,
        "blind_duration": 2.0, "radius": 150, "color": (255, 255, 100),
    },
    "smoke": {
        "name": "烟雾弹", "price": 200, "fuse_time": 1.0,
        "duration": 5.0, "radius": 80, "color": (160, 160, 160),
    },
    "medkit": {
        "name": "血包", "price": 500, "heal_amount": 30,
        "use_time": 1.0, "color": (255, 50, 50),
    },
    "shield": {
        "name": "护盾", "price": 600, "duration": 8.0,
        "damage_reduction": 0.5, "color": (100, 150, 255),
    },
}


class ProjectileItem:
    """Thrown items like grenades, flashbangs, smokes."""
    def __init__(self, item_type, position, velocity, owner_id):
        self.item_type = item_type
        self.pos = Vec2(*position)
        self.vel = Vec2(*velocity)
        self.owner_id = owner_id
        defn = ITEM_DEFS[item_type]
        self.fuse_time = defn["fuse_time"]
        self.fuse_timer = self.fuse_time
        self.alive = True
        self.radius = 5
        self.color = defn["color"]
        self.defn = defn

    def update(self, dt, walls):
        self.fuse_timer -= dt
        if self.fuse_timer <= 0:
            self.alive = False  # Will trigger effect in battle scene
            return

        self.vel = self.vel + Vec2(0, 300 * dt)  # Gravity
        new_pos = self.pos + self.vel * dt

        # Wall bounce
        from src.core.physics import circle_rect_collision
        for wall_rect in walls:
            hit, normal, penetration = circle_rect_collision(new_pos, self.radius, wall_rect)
            if hit:
                nx, ny = normal
                dot = self.vel.x * nx + self.vel.y * ny
                self.vel = Vec2(
                    self.vel.x - 2 * dot * nx,
                    self.vel.y - 2 * dot * ny,
                ) * 0.5  # dampen bounce
                new_pos = new_pos + Vec2(nx * penetration, ny * penetration)
                break

        self.pos = new_pos

    def render(self, screen, camera_offset=Vec2(0, 0)):
        if not self.alive:
            return
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        pygame.draw.circle(screen, (0, 0, 0), (sx, sy), self.radius + 1)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)


class PlayerEffect:
    """Active effects on a player (shield, blind, etc.)."""
    def __init__(self, effect_type, duration, **kwargs):
        self.effect_type = effect_type
        self.duration = duration
        self.timer = duration
        self.params = kwargs

    def update(self, dt):
        self.timer -= dt
        return self.timer > 0

    def is_active(self):
        return self.timer > 0
```

---

### Task 17: AI Bot

**Files:**
- Create: `src/entities/ai_bot.py`

- [ ] **Step 1: Create AI bot with decision tree behavior**

```python
# src/entities/ai_bot.py
import math
import random
from src.core.vector import Vec2

# AI states
IDLE, PATROL, CHASE, ATTACK, RETREAT = range(5)


class AIBot:
    def __init__(self, player, difficulty="normal"):
        self.player = player  # The Player entity this bot controls
        self.difficulty = difficulty
        self.state = PATROL
        self.patrol_target = Vec2(0, 0)
        self.decision_timer = 0.0
        self.reaction_time = {"easy": 0.5, "normal": 0.2, "hard": 0.05}[difficulty]
        self.aim_error = {"easy": 15, "normal": 5, "hard": 1}[difficulty]

        # Pick a random patrol point
        self._pick_patrol()

    def _pick_patrol(self):
        self.patrol_target = Vec2(
            random.uniform(50, 400),
            random.uniform(50, 300),
        )

    def update(self, dt, enemy, walls, all_bullets):
        self.decision_timer -= dt

        # Always aim at enemy (with error)
        aim_x = enemy.pos.x + random.uniform(-self.aim_error, self.aim_error)
        aim_y = enemy.pos.y + random.uniform(-self.aim_error, self.aim_error)
        self.player.set_aim(aim_x, aim_y)

        # Don't change movement decisions too often
        if self.decision_timer > 0:
            return
        self.decision_timer = self.reaction_time

        dist = self.player.pos.distance_to(enemy.pos)
        hp_ratio = self.player.hp / 100.0

        # Decision tree
        if hp_ratio < 0.3:
            self.state = RETREAT
        elif dist < 200:
            self.state = ATTACK
        elif dist < 500:
            self.state = CHASE
        else:
            self.state = PATROL

    def get_movement(self, enemy):
        """Returns (dx, dy) direction the bot wants to move."""
        if self.state == RETREAT:
            # Move away from enemy
            away = self.player.pos - enemy.pos
            if away.length() > 0:
                return away.normalized() * -1
            return Vec2(0, 0)

        elif self.state == CHASE:
            toward = enemy.pos - self.player.pos
            if toward.length() > 0:
                return toward.normalized()
            return Vec2(0, 0)

        elif self.state == ATTACK:
            # Strafe around enemy while keeping distance
            toward = enemy.pos - self.player.pos
            if toward.length() > 0:
                perp = Vec2(-toward.y, toward.x).normalized()
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
            if to_patrol.length() < 20:
                self._pick_patrol()
            return to_patrol.normalized()

        return Vec2(0, 0)

    def wants_to_shoot(self, enemy):
        """Returns True if bot should fire."""
        if self.state in (ATTACK, CHASE):
            dist = self.player.pos.distance_to(enemy.pos)
            if self.difficulty == "easy":
                return dist < 300 and random.random() < 0.3
            elif self.difficulty == "normal":
                return dist < 400 and random.random() < 0.5
            else:
                return dist < 500 and random.random() < 0.7
        return False

    def wants_to_use_item(self):
        hp_ratio = self.player.hp / 100.0
        if hp_ratio < 0.5 and self.difficulty in ("normal", "hard"):
            return "medkit" if random.random() < 0.3 else None
        if self.difficulty == "hard" and random.random() < 0.02:
            return "grenade"
        return False
```

---

### Task 18: Profile and Progression System

**Files:**
- Create: `src/systems/profile.py`
- Create: `src/systems/progression.py`
- Create: `data/profiles/.gitkeep`

- [ ] **Step 1: Create profile.py for save/load**

```python
# src/systems/profile.py
import json
import os
from config import PLAYER1_KEYS, PLAYER2_KEYS
import pygame


PROFILES_DIR = "data/profiles"


def _ensure_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles():
    _ensure_dir()
    profiles = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith(".json"):
            profiles.append(f[:-5])
    return profiles


def create_profile(name):
    _ensure_dir()
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        return False
    data = {
        "name": name,
        "level": 1,
        "xp": 0,
        "stats": {
            "total_kills": 0,
            "total_deaths": 0,
            "matches_won": 0,
            "matches_played": 0,
            "total_damage": 0,
        },
        "unlocks": [],
        "keybindings": {
            "up": "W", "down": "S", "left": "A", "right": "D",
            "shoot": "E", "ability": "Q", "sprint": "LSHIFT", "dodge": "SPACE",
        },
        "settings": {
            "master_volume": 0.8,
            "sfx_volume": 0.9,
            "music_volume": 0.6,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


def load_profile(name):
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(data):
    _ensure_dir()
    path = os.path.join(PROFILES_DIR, f"{data['name']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def delete_profile(name):
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
```

- [ ] **Step 2: Create progression.py**

```python
# src/systems/progression.py
from config import UNLOCK_SKIN_LEVEL, UNLOCK_CHARACTER_LEVEL, UNLOCK_MAPS_LEVEL


def xp_for_level(level):
    """XP required to reach this level (cumulative)."""
    return 500 * level * (level + 1) // 2  # 500, 1500, 3000, 5000...


def add_xp(profile_data, amount):
    profile_data["xp"] += amount
    current_level = profile_data["level"]
    while profile_data["xp"] >= xp_for_level(current_level + 1):
        current_level += 1
        profile_data["level"] = current_level
        # Check unlocks
        if current_level >= UNLOCK_SKIN_LEVEL and "skin_red" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("skin_red")
        if current_level >= UNLOCK_CHARACTER_LEVEL and "char_alt" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("char_alt")
        if current_level >= UNLOCK_MAPS_LEVEL and "map_unlock_all" not in profile_data["unlocks"]:
            profile_data["unlocks"].append("map_unlock_all")


def update_stats(profile_data, kills=0, deaths=0, won=False, damage=0):
    s = profile_data["stats"]
    s["total_kills"] += kills
    s["total_deaths"] += deaths
    s["matches_played"] += 1
    if won:
        s["matches_won"] += 1
    s["total_damage"] = s.get("total_damage", 0) + damage
```

- [ ] **Step 3: Verify profile system**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python -c "
from src.systems.profile import create_profile, load_profile, save_profile, list_profiles
create_profile('test_user')
p = load_profile('test_user')
assert p['name'] == 'test_user'
assert p['level'] == 1
from src.systems.progression import add_xp, xp_for_level
add_xp(p, 4000)
print(f'Level: {p[\"level\"]}, XP: {p[\"xp\"]}')
import os; os.remove('data/profiles/test_user.json')
print('Profile system OK')
"
```

Expected: Level increases, Profile system OK

---

### Task 19: Particle Effects System

**Files:**
- Create: `src/core/particles.py`

- [ ] **Step 1: Create particle system**

```python
# src/core/particles.py
import random
import pygame
from src.core.vector import Vec2


class Particle:
    def __init__(self, pos, vel, color, lifetime, size=3):
        self.pos = Vec2(pos.x, pos.y)
        self.vel = Vec2(vel.x, vel.y)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.pos = self.pos + self.vel * dt
        self.vel = self.vel * 0.95  # friction

    def render(self, screen, camera_offset=Vec2(0, 0)):
        if not self.alive:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha) if len(self.color) == 3 else self.color
        size = self.size * (self.lifetime / self.max_lifetime)
        sx = int(self.pos.x - camera_offset.x)
        sy = int(self.pos.y - camera_offset.y)
        # Use a surface with alpha
        surf = pygame.Surface((int(size * 2 + 4), int(size * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (int(size + 2), int(size + 2)), int(size))
        screen.blit(surf, (sx - int(size), sy - int(size)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, pos, count, colors, speed_range, lifetime_range, size_range=(2, 5)):
        for _ in range(count):
            angle = random.uniform(0, 6.283)
            speed = random.uniform(*speed_range)
            vel = Vec2(angle * 0, 0)  # placeholder
            vel = Vec2(speed, 0).rotate(angle)
            color = random.choice(colors)
            lifetime = random.uniform(*lifetime_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(pos, vel, color, lifetime, int(size)))

    def emit_explosion(self, pos):
        self.emit(pos, 30, [(255, 200, 50), (255, 100, 20), (255, 60, 10)],
                  (50, 250), (0.3, 0.8), (3, 8))

    def emit_gun_flash(self, pos, angle):
        """Emit muzzle flash particles."""
        for _ in range(5):
            vel_angle = angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(30, 80)
            vel = Vec2(speed, 0).rotate(vel_angle)
            self.particles.append(Particle(
                pos, vel, (255, 255, 200), random.uniform(0.05, 0.15), 4
            ))

    def emit_smoke(self, pos, count=15):
        self.emit(pos, count, [(160, 160, 160), (180, 180, 180), (140, 140, 140)],
                  (10, 50), (1.0, 3.0), (8, 20))

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def render(self, screen, camera_offset=Vec2(0, 0)):
        for p in self.particles:
            p.render(screen, camera_offset)
```

---

### Task 20: Audio System — Procedural Sound Effects

**Files:**
- Create: `src/core/audio.py`

- [ ] **Step 1: Create audio system with procedural sounds**

```python
# src/core/audio.py
import math
import struct
import pygame
import os


SAMPLE_RATE = 44100


def generate_sine_wave(frequency, duration, volume=0.3):
    """Generate a sine wave tone."""
    num_samples = int(SAMPLE_RATE * duration)
    buf = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        sample = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
        buf.append(sample)
    return buf


def generate_noise(duration, volume=0.3):
    """Generate white noise."""
    import random
    num_samples = int(SAMPLE_RATE * duration)
    return [int(32767 * volume * (random.random() * 2 - 1)) for _ in range(num_samples)]


def generate_gunshot():
    """Short noise burst + low freq punch."""
    noise = generate_noise(0.08, 0.4)
    low = generate_sine_wave(80, 0.05, 0.5)
    combined = []
    for i in range(max(len(noise), len(low))):
        n = noise[i] if i < len(noise) else 0
        l = low[i] if i < len(low) else 0
        combined.append(max(-32767, min(32767, n + l)))
    return array_to_sound(combined)


def generate_explosion():
    """Longer noise with decay."""
    noise = generate_noise(0.3, 0.6)
    low = generate_sine_wave(40, 0.25, 0.5)
    combined = []
    for i in range(max(len(noise), len(low))):
        n = noise[i] if i < len(noise) else 0
        l = low[i] if i < len(low) else 0
        decay = 1.0 - (i / max(len(noise), len(low)))
        combined.append(int(max(-32767, min(32767, (n + l) * decay)))
    return array_to_sound(combined)


def array_to_sound(samples):
    """Convert sample list to pygame Sound."""
    buf = struct.pack('<' + 'h' * len(samples), *samples)
    return pygame.mixer.Sound(buffer=buf)


class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
        self.sounds = {}
        self.music_volume = 0.6
        self.sfx_volume = 0.9

    def load_sounds(self):
        """Generate all procedural sounds."""
        self.sounds["pistol"] = generate_gunshot()
        self.sounds["explosion"] = generate_explosion()
        # Generate slight variations for other weapons
        self.sounds["smg"] = generate_gunshot()
        self.sounds["shotgun"] = generate_gunshot()
        self.sounds["rifle"] = generate_gunshot()
        self.sounds["sniper"] = generate_gunshot()
        self.sounds["rocket"] = generate_explosion()

        # UI sounds
        click_samples = generate_sine_wave(800, 0.05, 0.2)
        self.sounds["click"] = array_to_sound(click_samples)

    def play(self, name, volume_scale=1.0):
        if name in self.sounds:
            s = self.sounds[name]
            s.set_volume(self.sfx_volume * volume_scale)
            s.play()

    def set_volumes(self, master, sfx, music):
        self.sfx_volume = sfx * master
        self.music_volume = music * master
```

---

### Task 21: Integrate All Systems — Full Match Flow

**Files:**
- Modify: `src/scenes/battle.py`
- Modify: `main.py`

- [ ] **Step 1: Update battle.py with full round-based elimination flow, economy, items, AI, particles, audio**

This is the final integration step. The updated battle.py incorporates:
- Round-based elimination with buy phases between rounds
- Economy system
- Item usage (use key to cycle/throw items)
- AI bot control (when vs_ai=True)
- Particle effects on explosions and shooting
- Audio on gunshots
- Proper round end → buy → next round → result flow

Key modifications to battle.py's `__init__`:

```python
# Add these to BattleScene.__init__:
from src.systems.economy import Economy
from src.entities.item import ProjectileItem, ITEM_DEFS
from src.entities.ai_bot import AIBot
from src.core.particles import ParticleSystem
from src.core.audio import AudioManager

self.economy = Economy()
self.particles = ParticleSystem()
self.audio = AudioManager()
self.audio.load_sounds()
self.projectiles = []  # Thrown items

# AI
self.ai_bot = None
if vs_ai:
    self.ai_bot = AIBot(self.player2, "normal")

# Round management
self.round_number = 0
self._round_end_timer = 0.0
self._buy_phase = False
self._match_over = False
self.p1_weapons = ["pistol"]
self.p2_weapons = ["pistol"]
```

The full `update()` method now calls:
1. AI update (if vs_ai)
2. Handle shooting (with particle effects)
3. Handle item usage (throw grenade with 'ability' key)
4. Update projectiles, bullets
5. Update particles
6. Round end logic → buy phase → next round → match result

The full `render()` method includes particle rendering and projectile rendering.

Since the full modified battle.py is very large (~300 lines), the key integration points are:
- `_round_end()` → set `self._buy_phase = True`, `self._round_end_timer = 2.0`
- In `update()`: if `self._buy_phase` and round_end_timer ≤ 0, switch to BuyMenuScene
- BuyMenuScene returns with `p1_weapons` and `p2_weapons`, battle scene respawns players with owned weapons
- After 4 rounds won, switch to ResultScene

- [ ] **Step 2: Verify full match flow runs end-to-end**

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && timeout 5 python main.py 2>&1 || true
```

Expected: Window opens, menu → lobby → battle → shooting works. No crash.

---

### Task 22: Deathmatch Mode and Additional Polish

**Files:**
- Modify: `src/scenes/battle.py`
- Modify: `src/scenes/lobby.py`

- [ ] **Step 1: Add deathmatch support to battle.py**

In BattleScene, when `game_mode == "deathmatch"`:
- `round_timer = 180` (3 minutes)
- On kill: killer's score +1, victim respawns after 2s at spawn point
- `_on_player_killed()` spawns a respawn timer instead of ending round
- First to 15 kills wins
- Skip buy phase entirely

```python
# In BattleScene.__init__, add:
self.deathmatch_kill_limit = 15

# In _on_player_killed:
if self.game_mode == "deathmatch":
    if killer_id == 1:
        self.p1_score += 1
    else:
        self.p2_score += 1
    # Respawn victim after 2 seconds
    victim = self.player1 if killer_id == 2 else self.player2
    self._respawn_timer = 2.0
    self._respawn_player = victim
    if self.p1_score >= self.deathmatch_kill_limit or self.p2_score >= self.deathmatch_kill_limit:
        self._match_over = True
        self._round_end_timer = 2.0
```

- [ ] **Step 2: Update lobby to allow mode selection**

Add a game mode toggle to LobbyScene:
```python
GAME_MODES = ["elimination", "deathmatch"]
self.selected_mode = 0
```

---

### Task 23: Screen Shake Effect

**Files:**
- Create: `src/core/screenshake.py`

- [ ] **Step 1: Create screen shake module**

```python
# src/core/screenshake.py
import random
from src.core.vector import Vec2


class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0
        self.offset = Vec2(0, 0)

    def shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.timer = duration

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            decay = self.timer / self.duration
            current = self.intensity * decay
            self.offset = Vec2(
                random.uniform(-current, current),
                random.uniform(-current, current),
            )
        else:
            self.offset = Vec2(0, 0)
```

Apply screen shake offset to all camera offsets when rendering.

Trigger on: sniper shots (intensity=10, duration=0.1), explosions (intensity=20, duration=0.3).

---

### Task 24: Additional Maps

**Files:**
- Create: `data/maps/city_ruins.json`
- Create: `data/maps/underground_fortress.json`
- Create: `data/maps/space_station.json`
- Create: `data/maps/forest_maze.json`
- Modify: `src/scenes/lobby.py`

- [ ] **Step 1: Generate 4 more maps with JSON wall data**

Map walls for each (tile coordinates: x, y, w, h):

**city_ruins.json (100x55):**
```json
{
  "name": "城市废墟", "width": 100, "height": 55,
  "player1_spawn": [8, 27], "player2_spawn": [91, 27],
  "gravity": 1.0,
  "walls": [
    [0, 0, 100, 1], [0, 54, 100, 1], [0, 0, 1, 55], [99, 0, 1, 55],
    [20, 8, 3, 4], [40, 8, 3, 4], [60, 8, 3, 4], [77, 8, 3, 4],
    [10, 15, 8, 2], [28, 18, 12, 2], [50, 15, 8, 2], [70, 18, 10, 2],
    [15, 25, 6, 3], [35, 24, 4, 2], [55, 28, 6, 3], [75, 25, 5, 3],
    [42, 35, 16, 2], [8, 40, 12, 2], [80, 40, 12, 2],
    [30, 44, 3, 5], [67, 44, 3, 5]
  ]
}
```

**underground_fortress.json (90x65):**
```json
{
  "name": "地下堡垒", "width": 90, "height": 65,
  "player1_spawn": [5, 10], "player2_spawn": [84, 54],
  "gravity": 1.0,
  "walls": [
    [0, 0, 90, 1], [0, 64, 90, 1], [0, 0, 1, 65], [89, 0, 1, 65],
    [20, 0, 2, 15], [68, 0, 2, 15],
    [40, 8, 10, 2], [10, 20, 15, 2], [65, 20, 15, 2],
    [30, 15, 3, 10], [57, 15, 3, 10],
    [5, 28, 12, 2], [73, 28, 12, 2],
    [44, 30, 2, 20],
    [15, 38, 10, 2], [65, 38, 10, 2],
    [25, 48, 8, 2], [57, 48, 8, 2],
    [10, 55, 20, 2], [60, 55, 20, 2],
    [20, 10, 2, 8, 2], [68, 50, 2, 8, 2]
  ]
}
```

**space_station.json (70x50):**
```json
{
  "name": "太空站", "width": 70, "height": 50,
  "player1_spawn": [10, 25], "player2_spawn": [59, 25],
  "gravity": 0.3,
  "walls": [
    [0, 0, 70, 1], [0, 49, 70, 1], [0, 0, 1, 50], [69, 0, 1, 50],
    [15, 8, 4, 2], [51, 8, 4, 2],
    [30, 12, 10, 2],
    [10, 18, 6, 2], [54, 18, 6, 2],
    [34, 22, 2, 15],
    [15, 30, 8, 2], [47, 30, 8, 2],
    [25, 38, 20, 2]
  ]
}
```

**forest_maze.json (100x55):**
```json
{
  "name": "密林迷宫", "width": 100, "height": 55,
  "player1_spawn": [3, 27], "player2_spawn": [96, 27],
  "gravity": 1.0,
  "walls": [
    [0, 0, 100, 1], [0, 54, 100, 1], [0, 0, 1, 55], [99, 0, 1, 55],
    [8, 5, 2, 10], [25, 5, 2, 8], [45, 5, 2, 6], [65, 5, 2, 8], [85, 5, 2, 10],
    [15, 15, 4, 2], [40, 12, 3, 3], [60, 15, 5, 2], [80, 12, 4, 3],
    [5, 22, 10, 2], [30, 25, 3, 4], [50, 20, 3, 4], [70, 25, 3, 4], [85, 22, 10, 2],
    [20, 32, 3, 5], [45, 32, 2, 10], [65, 35, 5, 2], [80, 30, 4, 5],
    [8, 42, 3, 8], [35, 42, 3, 8], [55, 45, 8, 2], [75, 40, 3, 8],
    [90, 42, 3, 8]
  ]
}
```

- [ ] **Step 2: Update MAP_LIST in lobby.py**

```python
MAP_LIST = ["training_yard", "city_ruins", "underground_fortress", "space_station", "forest_maze"]
```

---

### Task 25: Polish — Cartoon Visual Enhancements, Muzzle Flash, Kill Feed

**Files:**
- Modify: `src/scenes/battle.py`
- Modify: `src/entities/player.py`

- [ ] **Step 1: Add kill feed to HUD**

```python
# In BattleScene:
self.kill_feed = []  # List of (text, timer) tuples

def _add_kill_feed(self, killer_id, weapon_name, headshot=False):
    killer_name = f"玩家{killer_id}"
    victim_name = f"玩家{3 - killer_id}"
    hs = " 爆头!" if headshot else ""
    text = f"{killer_name} [{weapon_name}] → {victim_name}{hs}"
    self.kill_feed.append((text, 3.0))
```

- [ ] **Step 2: Add muzzle flash rendering**

When a player fires, add a brief yellow/orange circle at the gun muzzle position and emit particles:

```python
def _spawn_muzzle_flash(self, player):
    muzzle_pos = player.pos + Vec2(
        player.radius * 0.9, 0
    ).rotate(player.aim_angle)
    self.particles.emit_gun_flash(muzzle_pos, player.aim_angle)
    self.muzzle_flashes.append((muzzle_pos, 0.06))  # Render briefly
```

- [ ] **Step 3: Add shadow rendering under characters**

In Player.render():
```python
# Shadow ellipse under player
shadow_y = sy + 4
pygame.draw.ellipse(screen, (0, 0, 0, 100),
                     (sx - self.radius + 2, shadow_y - 2,
                      self.radius * 2 - 4, 6))
```

---

## Final Verification

After all tasks complete, run the game:

```bash
cd "D:\ClaudeCode Program Environment\双人枪战游戏" && python main.py
```

**Expected behavior:**
1. Main menu with 4 buttons
2. Lobby with map selection (left/right arrows)
3. Battle with two players, split-screen when far apart, merged when close
4. WASD + E shooting, bullets visible, HP bars decreasing
5. On kill → round ends → buy menu → next round
6. At 4 wins → result screen with XP
7. Escape to return to menu
8. AI mode works (single player vs CPU)

---

## Notes for Implementation

- **No external assets needed** — all graphics are procedural (pygame shapes), all sounds are procedurally generated
- **Resolution**: Game runs at 1280×720, half-screens at 640×720 each
- **Delta time**: All movement/scaling uses `dt` for frame-rate independence
- **Collision**: All entities are circles; walls are AABB rects. Physics is simple push-out resolution.
- **Error handling**: JSON load failures should print warnings but not crash; default values everywhere
