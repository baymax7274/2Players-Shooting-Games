import pygame

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

# Map grid
TILE_SIZE = 32
# 0=empty, 1=wall, 2=destructible, 3=cover_half_height
