from pyglet.graphics import Batch
from pyglet.math import Vec2
from pyglet.resource import image
from pyglet.window import Window

from framework import Frame, Size, Pin, Position
from framework.mat2 import Mat2
from framework.components import Rectangle, Label, Image, Button

from interface.style import Colors, Sizing


class MenuBar(Rectangle):
    def __init__(self, batch: Batch, parent: Frame | None, window: Window):
        super().__init__(
            colour=Colors.ELEMENT_BACKGROUND,
            batch=batch,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)), constant=Vec2(0.0, Sizing.TOP_BAR)
            ),
            position=Position(pin=Pin.top_left()),
            parent=parent,
        )

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

        self.title = Label(
            text="Guitar Trainer",
            color=Colors.FOREGROUND,
            batch=batch,
            position=Position(pin=Pin.centre()),
            parent=self,
            font_size=32,
        )

        self.settings_button = Button(
            size=Size(matrix=Mat2((0.0, 1.0, 0.0, 1.0)), constant=Vec2(-12, -12)),
            position=Position(pin=Pin.top_right(), offset=Vec2(-6, -6)),
            parent=self,
        )
        window.push_handlers(self.settings_button)

        self.settings_button_icon = Image(
            image("assets/cog.png"),
            batch=batch,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self.settings_button,
            size_mode=Image.SizeMode.STRETCH,
            position_mode=Image.PositionMode.CENTRE,
        )

        self.settings_button_border = Rectangle(
            colour=Colors.BORDER,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * 2,
            ),
            position=Position(),
            parent=self.settings_button,
            behind_parent=True,
        )

        def on_state_change(state: Button.State):
            match state:
                case Button.State.HOVER:
                    self.settings_button_border.colour = Colors.HOVER
                case Button.State.PRESSED:
                    self.settings_button_border.colour = Colors.PRESSED
                case Button.State.NORMAL:
                    self.settings_button_border.colour = Colors.BORDER

        self.settings_button.set_handler("on_state_change", on_state_change)
