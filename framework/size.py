from dataclasses import dataclass, field
from pyglet.math import Vec2

from framework.mat2 import Mat2

from framework.update_hook import UpdateHook


@dataclass
class Size(UpdateHook):
    """Size of a Frame. Defaults to 0x0."""

    constant: Vec2 = field(default_factory=lambda: Vec2())
    matrix: Mat2 = Mat2((0,) * 4)
    max: None | Vec2 = None
    min: None | Vec2 = None

    def calc_size(self, remote_size: None | Vec2) -> Vec2:
        """Calculate the absolute size of the frame.

        Takes the remote (parent's) size.
        """

        if remote_size is not None:
            # If remote size is passed, start with the relative size...
            actual_size = self.matrix @ remote_size
        else:
            # ...otherwise start with zero.
            actual_size = Vec2(0, 0)
        actual_size += self.constant

        # Clamp to min...
        if self.min is not None:
            actual_size = Vec2(
                max(self.min.x, actual_size.x), max(self.min.y, actual_size.y)
            )
        # ...and max.
        if self.max is not None:
            actual_size = Vec2(
                min(self.max.x, actual_size.x), min(self.max.y, actual_size.y)
            )

        return actual_size
