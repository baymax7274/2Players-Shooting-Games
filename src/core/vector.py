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

    def __neg__(self):
        return Vec2(-self.x, -self.y)

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
