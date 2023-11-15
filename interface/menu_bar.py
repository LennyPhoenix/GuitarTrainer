from pyglet.graphics import Batch
from pyglet.math import Vec2

from framework import Frame, Size, Pin, Position
from framework.mat2 import Mat2
from framework.components import Rectangle, Label

from interface.style import Colors, Sizing


class MenuBar(Rectangle):
    def __init__(self, batch: Batch, parent: Frame | None):
        super().__init__(
            color=Colors.BORDER,
            batch=batch,
            size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                      constant=Vec2(0.0, 64.0)),
            position=Position(pin=Pin.top_left()),
            parent=parent,
        )
        self.fill = Rectangle(
            color=Colors.BACKGROUND,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * -2,
            ),
            position=Position(),
            parent=self,
        )

        self.title = Label(
            text="Guitar Trainer",
            color=Colors.FOREGROUND,
            batch=batch,
            position=Position(pin=Pin.centre()),
            parent=self.fill,
            font_size=32,
        )
