from .scroll_container import ScrollContainer
from .style import Colours
from .bordered_rect import BorderedRectangle

from framework import Frame, Size, Position, Pin, Mat2, Vec2
from framework.components import Button, Label, Text

from pyglet.window import Window


class DropDown(BorderedRectangle):
    def __init__(
        self,
        elements: list[str],
        size: Size,
        position: Position,
        parent: "Frame | None",
        window: Window,
    ):
        super().__init__(size, position, parent)

        self.label = Label(
            text="Test",
            colour=Colours.FOREGROUND,
            position=Position(pin=Pin.centre()),
            parent=self,
        )

        self.selection_box = BorderedRectangle(
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=Vec2(0.0, 256.0),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
            ),
            parent=self,
        )

        self.scroll_container = ScrollContainer(
            size=Size(matrix=Mat2(), min=Vec2(0.0, 0.0)),
            position=Position(),
            parent=self.selection_box,
        )
        self.scroll_container.register(window)

        self.child = Text(
            text="Test 2\n" * 100,
            colour=(0, 0, 0, 255),
            parent=self,  # tmp
            size=Size(matrix=Mat2()),
            position=Position(pin=Pin.top_left()),
            font_size=32,
        )
        self.scroll_container.add_child(self.child)
