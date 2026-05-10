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
        self.map_width = data["width"]
        self.map_height = data["height"]
        self.width = self.map_width * TILE_SIZE
        self.height = self.map_height * TILE_SIZE
        self.cols = data["width"]
        self.rows = data["height"]
        self.gravity_mod = data.get("gravity", 1.0)
        self.player1_spawn = data["player1_spawn"]
        self.player2_spawn = data["player2_spawn"]

        self.wall_rects = []
        for w in data.get("walls", []):
            self.wall_rects.append(pygame.Rect(
                w[0] * TILE_SIZE, w[1] * TILE_SIZE,
                w[2] * TILE_SIZE, w[3] * TILE_SIZE,
            ))

        self.tiles = [[0] * self.cols for _ in range(self.rows)]
        for w in data.get("walls", []):
            tile_type = w[4] if len(w) > 4 else 1
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
        ox, oy = camera_offset.x, camera_offset.y
        start_tx = max(0, int(ox // TILE_SIZE) - 1)
        start_ty = max(0, int(oy // TILE_SIZE) - 1)
        screen_w, screen_h = screen.get_size()
        end_tx = min(self.cols, int((ox + screen_w) // TILE_SIZE) + 2)
        end_ty = min(self.rows, int((oy + screen_h) // TILE_SIZE) + 2)

        # Floor
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                rx = tx * TILE_SIZE - ox
                ry = ty * TILE_SIZE - oy
                # Checkerboard floor
                color = (45, 45, 50) if (tx + ty) % 2 == 0 else (40, 40, 45)
                pygame.draw.rect(screen, color, (rx, ry, TILE_SIZE, TILE_SIZE))

        # Walls
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
                # Subtle highlight on top edge
                pygame.draw.line(screen, (120, 120, 130), (rx, ry), (rx + TILE_SIZE, ry), 1)


def load_map(map_name):
    return GameMap(f"data/maps/{map_name}.json")
