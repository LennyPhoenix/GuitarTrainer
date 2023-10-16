from dataclasses import dataclass, field
from pyglet.math import Vec2

from framework.mat2 import Mat2

from framework.update_hook import UpdateHook


@dataclass
class Size(UpdateHook):
    constant: Vec2 = field(default_factory=lambda: Vec2())
    matrix: Mat2 = Mat2((0,) * 4)
    max: None | Vec2 = None
    min: None | Vec2 = None

    def calc_size(self, remote_size: None | Vec2) -> Vec2:
        if remote_size is not None:
            actual_size = self.matrix @ remote_size
        else:
            actual_size = Vec2(0, 0)
        actual_size += self.constant

        if self.min is not None:
            actual_size = Vec2(
                max(self.min.x, actual_size.x), max(self.min.y, actual_size.y)
            )
        if self.max is not None:
            actual_size = Vec2(
                min(self.max.x, actual_size.x), min(self.max.y, actual_size.y)
            )

        return actual_size
