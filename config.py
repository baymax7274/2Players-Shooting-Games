import os
import sys

import pygame


def get_base_dir():
    """获取项目根目录，兼容 PyInstaller 打包和开发环境。"""
    if getattr(sys, "frozen", False):
        # PyInstaller 6.x: 数据文件在 sys._MEIPASS (_internal/)
        # PyInstaller 旧版: 数据文件在 sys.executable 同级目录
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        # 如果 data/ 在 _MEIPASS 下就直接用，否则用 executable 的目录
        if os.path.isdir(os.path.join(base, "data")):
            return base
        return os.path.dirname(sys.executable)
    # 开发环境：config.py 位于项目根目录
    return os.path.dirname(__file__)


# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Gameplay
PLAYER_SPEED = 220
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
BUY_TIME = 30

# Rounds
ROUNDS_TO_WIN = 4

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
    "shoot": pygame.K_u,
    "ability": pygame.K_i,
    "sprint": pygame.K_LSHIFT,
    "dodge": pygame.K_SPACE,
}
PLAYER2_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "shoot": pygame.K_KP1,
    "ability": pygame.K_KP2,
    "sprint": pygame.K_RSHIFT,
    "dodge": pygame.K_RCTRL,
}

# Map grid
TILE_SIZE = 32
# 0=empty, 1=wall, 2=destructible, 3=cover_half_height

# ========== v1.2.0 动态环境 ==========

# 拾取物
PICKUP_RESPAWN_HEALTH = 20.0
PICKUP_RESPAWN_POWER = 45.0
PICKUP_RESPAWN_SPEED = 40.0
PICKUP_MAX_HEALTH = 3
PICKUP_MAX_POWER = 1
PICKUP_MAX_SPEED = 1
PICKUP_RADIUS = 12

# Power-up 持续时间
POWER_DURATION = 8.0
SPEED_DURATION = 6.0
HEAL_AMOUNT = 25

# 可破坏环境
DESTRUCTIBLE_FLASH_TIME = 0.1
SHOTGUN_DESTROY_RANGE = 100.0

# 移动墙
MOVING_WALL_SPEED_MIN = 60
MOVING_WALL_SPEED_MAX = 100
MOVING_WALL_PAUSE = 0.5

# 环境事件
COLLAPSE_INTERVAL_MIN = 25.0
COLLAPSE_INTERVAL_MAX = 35.0
POISON_START_TIME = 60.0
POISON_INITIAL_RADIUS = 2
POISON_EXPAND_INTERVAL = 15.0
POISON_EXPAND_STEP = 1
POISON_DPS = 5.0
GRAVITY_FLIP_INTERVAL = 15.0
THORN_ACTIVATE_INTERVAL = 20.0
THORN_ACTIVATE_COUNT = 3
THORN_DURATION = 5.0
THORN_DAMAGE = 15

# 移动墙推动玩家的力系数
WALL_PUSH_FORCE = 0.8
