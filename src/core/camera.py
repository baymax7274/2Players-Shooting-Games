import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.vector import Vec2


class Camera:
    def __init__(self, map_width, map_height, viewport_rect):
        self.map_w = map_width
        self.map_h = map_height
        self.vp = viewport_rect
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
    def __init__(self, map_width, map_height):
        self.map_w = map_width
        self.map_h = map_height
        half_w = SCREEN_WIDTH // 2
        self.cam1 = Camera(map_width, map_height, pygame.Rect(0, 0, half_w, SCREEN_HEIGHT))
        self.cam2 = Camera(map_width, map_height, pygame.Rect(half_w, 0, half_w, SCREEN_HEIGHT))
        self.merged = False
        self.merge_cam = Camera(map_width, map_height, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def update(self, player1_pos, player2_pos):
        p1 = Vec2(*player1_pos) if not hasattr(player1_pos, 'x') else player1_pos
        p2 = Vec2(*player2_pos) if not hasattr(player2_pos, 'x') else player2_pos

        dist = p1.distance_to(p2)
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
            pygame.draw.line(screen, (60, 60, 60), (mid_x, 0), (mid_x, SCREEN_HEIGHT), 3)
