from dataclasses import dataclass

from pyglet.math import Vec2


@dataclass
class Aabb:
    position: Vec2
    size: Vec2

    def check_point(self, point: Vec2) -> bool:
        return (
            self.position.x < point.x < self.position.x + self.size.x
            and self.position.y < point.y < self.position.y + self.size.y
        )
