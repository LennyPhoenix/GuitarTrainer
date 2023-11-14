from dataclasses import dataclass
from typing import Self

from pyglet.math import Vec2


@dataclass
class Aabb:
    position: Vec2
    size: Vec2

    @property
    def left(self) -> float:
        return self.position.x

    @property
    def right(self) -> float:
        return self.position.x + self.size.x

    @property
    def bottom(self) -> float:
        return self.position.y

    @property
    def top(self) -> float:
        return self.position.y + self.size.y

    @staticmethod
    def from_left_right_bottom_top(
        left: float, right: float, bottom: float, top: float
    ) -> "Aabb":
        return Aabb(Vec2(left, bottom), Vec2(right - left, top - bottom))

    def check_point(self, point: Vec2) -> bool:
        return (
            self.position.x < point.x < self.position.x + self.size.x
            and self.position.y < point.y < self.position.y + self.size.y
        )

    def union(self, other: Self) -> Self:
        return Aabb.from_left_right_bottom_top(
            min(self.left, other.left),
            max(self.right, other.right),
            min(self.bottom, other.bottom),
            max(self.top, other.top),
        )

    def __repr__(self) -> str:
        return f"Aabb({self.position}, {self.size})"
