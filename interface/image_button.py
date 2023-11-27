from pyglet.image import AbstractImage
from pyglet.graphics import Batch
from pyglet.window import Window
from pyglet.event import EventDispatcher

from framework.components import Image, Button, Rectangle
from framework import Size, Position, Frame, Mat2, Vec2

from interface.style import Colors, Sizing


class ImageButton(Image, EventDispatcher):
    def __init__(
        self,
        image: AbstractImage,
        batch: Batch,
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
            batch,
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
        window.push_handlers(self)

        self.border = Rectangle(
            colour=Colors.BORDER,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * 2,
            ),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        self.button.set_handler("on_state_change", self.on_state_change)

    def on_state_change(self, old_state: Button.State, new_state: Button.State):
        match new_state:
            case Button.State.HOVER:
                self.border.colour = self.sprite.color = Colors.HOVER
            case Button.State.PRESSED:
                self.dispatch_event("on_pressed")
                self.border.colour = Colors.PRESSED
            case Button.State.NORMAL:
                self.border.colour = Colors.BORDER

        if old_state == Button.State.PRESSED:
            self.dispatch_event("on_released")


ImageButton.register_event_type("on_pressed")
ImageButton.register_event_type("on_released")
