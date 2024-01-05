from dataclasses import dataclass, field

from pyglet.math import Vec2
from framework.aabb import Aabb
from framework.pin import Pin
from framework.update_hook import UpdateHook


@dataclass
class Position(UpdateHook):
    """Position of a Frame relative to its parent. Defaults to the centre."""

    pin: Pin = field(default_factory=lambda: Pin.centre())
    offset: Vec2 = field(default_factory=lambda: Vec2())

    def __post_init__(self):
        self.pin.set_handler("on_update", self.on_pin_update)

    def on_pin_update(self):
        self.dispatch_event("on_update")

    def calc_position(self, parent: None | Aabb, size: Vec2) -> Vec2:
        if parent is not None:
            actual_pos = parent.position
            actual_pos += Vec2(
                parent.size.x * self.pin.remote_anchor.x,
                parent.size.y * self.pin.remote_anchor.y,
            )
        else:
            actual_pos = Vec2()

        actual_pos -= Vec2(
            size.x * self.pin.local_anchor.x, size.y * self.pin.local_anchor.y
        )
        actual_pos += self.offset

        return actual_pos


class TestPosition:
    def test_position(self):
        pos = Position(pin=Pin.centre(), offset=Vec2(1.0, 5.0))

        parent = Aabb(position=Vec2(50.0, 40.0), size=Vec2(100.0, 50.0))
        size = Vec2(50.0, 25.0)

        calculated = pos.calc_position(parent, size)
        assert calculated == Vec2(76.0, 57.5)
