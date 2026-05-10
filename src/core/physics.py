from config import TILE_SIZE
from src.core.vector import Vec2


def circle_rect_collision(circle_center, radius, rect):
    cx, cy = circle_center.x, circle_center.y
    rx, ry, rw, rh = rect

    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))

    dx = cx - closest_x
    dy = cy - closest_y
    dist_sq = dx * dx + dy * dy

    if dist_sq < radius * radius:
        dist = dist_sq ** 0.5
        if dist == 0:
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
    dist = c1.distance_to(c2)
    overlap = (r1 + r2) - dist
    if overlap > 0:
        return (True, overlap)
    return (False, 0)


def point_in_rect(px, py, rect):
    rx, ry, rw, rh = rect
    return rx <= px <= rx + rw and ry <= py <= ry + rh
