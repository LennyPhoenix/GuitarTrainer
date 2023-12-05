from . import Container
from framework import Size, Position, Frame, Mat2, Vec2, Pin

from pyglet.window import Window


class ScrollContainer(Frame):
    SCROLL_BAR_SIZE = 24

    def __init__(
        self,
        size: Size,
        position: Position,
        parent: "Frame | None",
        behind_parent: bool = False,
    ):
        super().__init__(size, position, parent, behind_parent)

        self.content = Container(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(0.0, -self.SCROLL_BAR_SIZE),
            ),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

    def add_child(self, other: Frame):
        other.parent = self.content
        other.propagate_size()
        other.propagate_position()

    def register(self, window: Window):
        window.push_handlers(self)

    def on_mouse_scroll(self, x: float, y: float, _scroll_x: float, scroll_y: float):
        print(scroll_y)
        if self.aabb.check_point(Vec2(x, y)):
            self.content.position.offset.y -= scroll_y * 20
            self.propagate_position()
