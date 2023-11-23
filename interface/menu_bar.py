from pyglet.graphics import Batch
from pyglet.math import Vec2
from pyglet.resource import image

from framework import Frame, Size, Pin, Position
from framework.mat2 import Mat2
from framework.components import Rectangle, Label, Image

from interface.style import Colors, Sizing


class MenuBar(Rectangle):
    def __init__(self, batch: Batch, parent: Frame | None):
        super().__init__(
            color=Colors.ELEMENT_BACKGROUND,
            batch=batch,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)), constant=Vec2(0.0, Sizing.TOP_BAR)
            ),
            position=Position(pin=Pin.top_left()),
            parent=parent,
        )

        self.border = Rectangle(
            color=Colors.BORDER,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * 2,
            ),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        self.title = Label(
            text="Guitar Trainer",
            color=Colors.FOREGROUND,
            batch=batch,
            position=Position(pin=Pin.centre()),
            parent=self,
            font_size=32,
        )

        self.settings_button = Image(
            image("assets/cog.png"),
            batch=batch,
            size=Size(matrix=Mat2((0.0, 1.0, 0.0, 1.0)), constant=Vec2(-8, -8)),
            position=Position(pin=Pin.top_right(), offset=Vec2(-4, -4)),
            parent=self,
            size_mode=Image.SizeMode.STRETCH,
            position_mode=Image.PositionMode.CENTRE,
        )

        self.settings_button_border = Rectangle(
            color=Colors.BORDER,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE),
            ),
            position=Position(),
            parent=self.settings_button,
            behind_parent=True,
        )
