from framework.components import Container, Rectangle, Button
from framework import Size, Position, Frame, Mat2, Vec2, Pin
from .style import Colours

from pyglet.window import Window
from pyglet.graphics import Batch


class ScrollContainer(Container):
    SCROLL_BAR_SIZE = 24

    content: Frame | None = None

    def __init__(
        self,
        size: Size,
        position: Position,
        parent: "Frame | None",
        batch: Batch,
        behind_parent: bool = False,
    ):
        super().__init__(size, position, parent, behind_parent)

        self.content = Frame(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(0.0, -self.SCROLL_BAR_SIZE),
            ),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
            behind_parent=True,
        )

        self.scroll_bar = Rectangle(
            size=Size(
                matrix=Mat2((0.0, 0.0, 0.0, 1.0)),
                constant=Vec2(self.SCROLL_BAR_SIZE, 0.0),
            ),
            position=Position(pin=Pin.top_right()),
            parent=self,
            batch=batch,
            colour=Colours.ELEMENT_BACKGROUND,
        )

        self.scroll_button = Button(
            size=Size(
                matrix=Mat2(
                    (
                        1.0,
                        0.0,
                        0.0,
                        min(
                            1.0,
                            self.content.broad_phase_aabb.size.y
                            / self.content.aabb.size.y,
                        ),
                    )
                )
            ),
            parent=self.scroll_bar,
            position=Position(pin=Pin.top_left()),
        )

        self.scroll_button_bg = Rectangle(
            size=Size(matrix=Mat2()),
            position=Position(),
            colour=Colours.FOREGROUND,
            batch=batch,
            parent=self.scroll_button,
        )

    def refresh_bar(self):
        if self.content is not None:
            self.scroll_button.size.matrix = Mat2(
                (
                    1.0,
                    0.0,
                    0.0,
                    min(
                        1.0,
                        self.content.aabb.size.y / self.content.broad_phase_aabb.size.y,
                    ),
                )
            )
            factor = self.content.position.offset.y / (
                self.content.broad_phase_aabb.size.y - self.content.aabb.size.y
            )
            self.scroll_button.position.pin = Pin(
                local_anchor=Vec2(0.0, 1.0 - factor),
                remote_anchor=Vec2(0.0, 1.0 - factor),
            )

    def propagate_position(self):
        val = super().propagate_position()
        self.refresh_bar()
        return val

    def add_child(self, other: Frame):
        other.parent = self.content
        other.propagate_size()
        other.propagate_position()
        self.refresh_bar()

    def register(self, window: Window):
        window.push_handlers(self)

    def on_mouse_scroll(self, x: float, y: float, _scroll_x: float, scroll_y: float):
        if self.aabb.check_point(Vec2(x, y)) and self.content is not None:
            self.content.position.offset = Vec2(
                0.0,
                min(
                    max(self.content.position.offset.y - scroll_y * 20, 0.0),
                    self.content.broad_phase_aabb.size.y - self.content.aabb.size.y,
                ),
            )
            self.refresh_bar()
