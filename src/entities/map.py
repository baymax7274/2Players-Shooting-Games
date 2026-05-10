import json
import math
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

        # 存储原始数据以便回合重置
        self._original_data = data
        self._original_tiles = [row[:] for row in self.tiles]
        # 移动墙数据
        self.moving_walls = []
        self._load_moving_walls(data.get("moving_walls", []))

    def _load_moving_walls(self, mw_data):
        self.moving_walls = []
        for mw in mw_data:
            self.moving_walls.append({
                "tile_x": mw["tile_x"],
                "tile_y": mw["tile_y"],
                "tile_w": mw["tile_w"],
                "tile_h": mw["tile_h"],
                "path": [(p["x"], p["y"]) for p in mw["path"]],
                "current_target": 0,
                "speed": mw.get("speed", 80),
                "pause": mw.get("pause", 0.5),
                "pause_timer": 0.0,
                "moving_forward": True,
            })
            # 在 tiles 中标记为 tile=4
            tx, ty = mw["tile_x"], mw["tile_y"]
            for dy in range(mw["tile_h"]):
                for dx in range(mw["tile_w"]):
                    if 0 <= ty + dy < self.rows and 0 <= tx + dx < self.cols:
                        self.tiles[ty + dy][tx + dx] = 4

    def destroy_tile(self, tx, ty):
        """摧毁指定瓦片，返回粒子数据列表"""
        if not (0 <= ty < self.rows and 0 <= tx < self.cols):
            return []
        if self.tiles[ty][tx] != 2:
            return []
        self.tiles[ty][tx] = 0
        self.rebuild_wall_rects()
        # 返回碎片粒子数据
        cx = tx * TILE_SIZE + TILE_SIZE // 2
        cy = ty * TILE_SIZE + TILE_SIZE // 2
        import random as rnd
        particles = []
        for _ in range(10):
            angle = rnd.uniform(0, 6.283)
            speed = rnd.uniform(60, 180)
            vx = cx + rnd.uniform(-8, 8)
            vy = cy + rnd.uniform(-8, 8)
            particles.append({
                "pos": (vx, vy),
                "vel": (math.cos(angle) * speed, math.sin(angle) * speed - 100),
                "size": rnd.randint(3, 8),
                "color": (140, 100, 50),
                "life": rnd.uniform(0.4, 1.0),
            })
        return particles

    def get_tiles_in_radius(self, cx, cy, radius):
        """返回圆形区域内 tile=2 的坐标列表"""
        tiles = []
        min_tx = max(0, int((cx - radius) // TILE_SIZE))
        max_tx = min(self.cols - 1, int((cx + radius) // TILE_SIZE))
        min_ty = max(0, int((cy - radius) // TILE_SIZE))
        max_ty = min(self.rows - 1, int((cy + radius) // TILE_SIZE))
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if self.tiles[ty][tx] == 2:
                    tile_cx = tx * TILE_SIZE + TILE_SIZE // 2
                    tile_cy = ty * TILE_SIZE + TILE_SIZE // 2
                    if (tile_cx - cx) ** 2 + (tile_cy - cy) ** 2 <= radius ** 2:
                        tiles.append((tx, ty))
        return tiles

    def rebuild_wall_rects(self):
        """根据当前 tiles 重建碰撞矩形列表"""
        self.wall_rects.clear()
        visited = [[False] * self.cols for _ in range(self.rows)]
        for ty in range(self.rows):
            for tx in range(self.cols):
                if self.tiles[ty][tx] in (1, 2, 3, 4) and not visited[ty][tx]:
                    # 查找水平连续段
                    end_tx = tx
                    while (end_tx + 1 < self.cols
                           and self.tiles[ty][end_tx + 1] in (1, 2, 3, 4)
                           and not visited[ty][end_tx + 1]):
                        end_tx += 1
                    # 垂直扩展
                    end_ty = ty
                    can_extend = True
                    while can_extend and end_ty + 1 < self.rows:
                        for x in range(tx, end_tx + 1):
                            if (self.tiles[end_ty + 1][x] not in (1, 2, 3, 4)
                                    or visited[end_ty + 1][x]):
                                can_extend = False
                                break
                        if can_extend:
                            end_ty += 1
                    # 标记已访问
                    for y in range(ty, end_ty + 1):
                        for x in range(tx, end_tx + 1):
                            visited[y][x] = True
                    w = (end_tx - tx + 1) * TILE_SIZE
                    h = (end_ty - ty + 1) * TILE_SIZE
                    self.wall_rects.append(pygame.Rect(
                        tx * TILE_SIZE, ty * TILE_SIZE, w, h
                    ))

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
