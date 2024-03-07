from dataclasses import dataclass
from pyglet.math import Vec2

from framework.update_hook import UpdateHook


@dataclass
class Pin(UpdateHook):
    """Represents the positional relationship between two frames."""

    # Fraction of the object's own size that position is anchored to
    local_anchor: Vec2
    # Fraction of the object's parent's size that position is anchored to
    remote_anchor: Vec2

    @staticmethod
    def centre() -> "Pin":
        return Pin(local_anchor=Vec2(0.5, 0.5), remote_anchor=Vec2(0.5, 0.5))

    @staticmethod
    def top_left() -> "Pin":
        return Pin(local_anchor=Vec2(0.0, 1.0), remote_anchor=Vec2(0.0, 1.0))

    @staticmethod
    def bottom_left() -> "Pin":
        return Pin(local_anchor=Vec2(0.0, 0.0), remote_anchor=Vec2(0.0, 0.0))

    @staticmethod
    def top_right() -> "Pin":
        return Pin(local_anchor=Vec2(1.0, 1.0), remote_anchor=Vec2(1.0, 1.0))
