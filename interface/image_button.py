from pyglet.image import AbstractImage
from pyglet.window import Window
from pyglet.event import EventDispatcher

from framework.components import Image, Button, Rectangle
from framework import Size, Position, Frame, Mat2, Vec2

from interface.style import Colours, Sizing


class ImageButton(Image, EventDispatcher):
    def __init__(
        self,
        image: AbstractImage,
        size: Size,
        position: Position,
        parent: Frame | None,
        window: Window,
        size_mode: Image.SizeMode = Image.SizeMode.FIT,
        position_mode: Image.PositionMode = Image.PositionMode.CENTRE,
        behind_parent: bool = False,
    ):
        super().__init__(
            image,
            size,
            position,
            parent,
            size_mode,
            position_mode,
            behind_parent,
        )

        self.button = Button(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
        )
        self.button.register(window)

        self.border = Rectangle(
            colour=Colours.BORDER,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * 2,
            ),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        self.button.set_handler("on_state_change", self.on_state_change)

    def on_state_change(
        self,
        old_state: Button.State,
        new_state: Button.State,
    ):
        match new_state:
            case Button.State.HOVER:
                self.colour = Colours.HOVER
            case Button.State.PRESSED:
                self.dispatch_event("on_pressed")
                self.colour = Colours.PRESSED
            case Button.State.NORMAL:
                self.colour = Colours.ELEMENT_BACKGROUND

        if old_state == Button.State.PRESSED:
            self.dispatch_event("on_released")


ImageButton.register_event_type("on_pressed")
ImageButton.register_event_type("on_released")
