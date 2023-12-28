from .bordered_rect import BorderedRectangle
from .dropdown import DropDown

from interface.style import Colours, Sizing
from framework import Frame, Mat2, Size, Position, Vec2, Pin
from framework.components import Label, Rectangle

from pyglet.window import Window


class SettingsPage(Frame):
    components: list[tuple[BorderedRectangle, Label, Frame]]

    def __init__(self, window: Window, parent: Frame | None):
        self.components = []

        super().__init__(
            size=Size(
                matrix=Mat2(), constant=Vec2(1.0, 1.0) * -2 * Sizing.CONTENT_PADDING
            ),
            position=Position(),
            parent=parent,
        )

        self.add_setting(
            "Input Device",
            DropDown(
                elements=["Test1", "Test2"],
                size=Size(
                    matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                    constant=Vec2(-64.0, -64.0),
                ),
                position=Position(),
                parent=None,
                window=window,
            ),
        )
        self.add_setting(
            "Mode",
            Rectangle(
                size=Size(
                    matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                    constant=Vec2(-64.0, -64.0),
                ),
                position=Position(),
                parent=None,
                colour=Colours.FOREGROUND,
            ),
        )
        self.add_setting(
            "Reset Progress",
            Rectangle(
                size=Size(
                    matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                    constant=Vec2(-64.0, -64.0),
                ),
                position=Position(),
                parent=None,
                colour=Colours.FOREGROUND,
            ),
        )

    def add_setting(self, label: str, component: Frame):
        position: Position
        parent: Frame
        size_constant: Vec2

        if len(self.components) >= 1:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            size_constant = Vec2(0.0, 64.0)
            parent = self.components[-1][0]
        else:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 1.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            size_constant = Vec2(-64.0, 64.0)
            parent = self

        container = BorderedRectangle(
            position=position,
            parent=parent,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=size_constant,
            ),
            behind_parent=True,
        )

        comp_label = Label(
            text=f"{label}:",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(1.0, 0.5),
                    remote_anchor=Vec2(0.2, 0.5),
                ),
                offset=Vec2(-24.0, 0.0),
            ),
            parent=container,
        )

        component.size = Size(
            matrix=Mat2((0.8, 0.0, 0.0, 1.0)), constant=Vec2(-36.0, -12.0)
        )
        component.position = Position(
            pin=Pin(
                local_anchor=Vec2(0.0, 0.5),
                remote_anchor=Vec2(0.2, 0.5),
            ),
            offset=Vec2(24.0, 0.0),
        )
        component.parent = container

        self.components.append((container, comp_label, component))
