from pyglet.event import EventDispatcher
from pyglet.math import Vec2
from pyglet.resource import image
from pyglet.window import Window

from framework import Frame, Size, Pin, Position
from framework.mat2 import Mat2
from framework.components import Label, Image

from enum import Enum, auto

from .image_button import ImageButton
from .style import Colours, Sizing
from .bordered_rect import BorderedRectangle


class View(Enum):
    APP = auto()
    SETTINGS = auto()
    TUNER = auto()
    FRETBOARD = auto()


class MenuBar(BorderedRectangle, EventDispatcher):
    current_view: View = View.APP

    def __init__(self, parent: Frame | None, window: Window):
        super().__init__(
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=Vec2(0.0, Sizing.TOP_BAR),
            ),
            position=Position(pin=Pin.top_left()),
            parent=parent,
        )

        self.title = Label(
            text="Guitar Trainer",
            colour=Colours.FOREGROUND,
            position=Position(pin=Pin.centre()),
            parent=self,
            font_size=32,
        )

        self.settings_button = ImageButton(
            image("assets/cog.png"),
            size=Size(
                matrix=Mat2((0.0, 1.0, 0.0, 1.0)),
                constant=Vec2(Sizing.PADDING, Sizing.PADDING) * -2,
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(1.0, 0.5),
                    remote_anchor=Vec2(1.0, 0.5),
                ),
                offset=Vec2(-Sizing.PADDING, 0.0),
            ),
            parent=self,
            window=window,
            size_mode=Image.SizeMode.STRETCH,
            position_mode=Image.PositionMode.CENTRE,
        )
        self.settings_button.set_handler("on_released", self.on_settings)

        self.tuner_button = ImageButton(
            image("assets/tuner.png"),
            # Copy size and position of settings
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(1.0, 0.5),
                    remote_anchor=Vec2(0.0, 0.5),
                ),
                offset=Vec2(-Sizing.PADDING * 2, 0.0),
            ),
            parent=self.settings_button,
            window=window,
            size_mode=Image.SizeMode.STRETCH,
            position_mode=Image.PositionMode.CENTRE,
        )
        self.tuner_button.set_handler("on_released", self.on_tuner)

    def on_settings(self):
        if self.current_view == View.SETTINGS:
            self.current_view = View.APP
        else:
            self.current_view = View.SETTINGS

        self.dispatch_event("on_view", self.current_view)

    def on_tuner(self):
        if self.current_view == View.TUNER:
            self.current_view = View.APP
        else:
            self.current_view = View.TUNER
        self.dispatch_event("on_view", self.current_view)


MenuBar.register_event_type("on_view")
