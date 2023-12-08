from pyglet.graphics import Batch
from pyglet.math import Vec2
from pyglet.resource import image
from pyglet.window import Window

from framework import Frame, Size, Pin, Position
from framework.mat2 import Mat2
from framework.components import Rectangle, Label, Image

from .image_button import ImageButton
from .style import Colours, Sizing
from .bordered_rect import BorderedRectangle


class MenuBar(BorderedRectangle):
    def __init__(self, batch: Batch, parent: Frame | None, window: Window):
        super().__init__(
            batch=batch,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)), constant=Vec2(0.0, Sizing.TOP_BAR)
            ),
            position=Position(pin=Pin.top_left()),
            parent=parent,
        )

        self.title = Label(
            text="Guitar Trainer",
            colour=Colours.FOREGROUND,
            batch=batch,
            position=Position(pin=Pin.centre()),
            parent=self,
            font_size=32,
        )

        self.settings_button = ImageButton(
            image("assets/cog.png"),
            batch=batch,
            size=Size(
                matrix=Mat2((0.0, 1.0, 0.0, 1.0)),
                constant=Vec2(Sizing.PADDING, Sizing.PADDING) * -2,
            ),
            position=Position(
                pin=Pin(local_anchor=Vec2(1.0, 0.5),
                        remote_anchor=Vec2(1.0, 0.5)),
                offset=Vec2(-Sizing.PADDING, 0.0),
            ),
            parent=self,
            window=window,
            size_mode=Image.SizeMode.STRETCH,
            position_mode=Image.PositionMode.CENTRE,
        )
