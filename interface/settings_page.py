from framework import Frame, Mat2, Size, Position, Vec2, Pin
from framework.components import Label
from framework.components.rect import Rectangle
from .bordered_rect import BorderedRectangle
from interface.style import Colours, Sizing

from pyglet.graphics import Batch


class SettingsPage(Frame):
    components: list[tuple[BorderedRectangle, Label, Frame]]

    def __init__(self, batch: Batch, parent: Frame | None):
        self.components = []
        self.batch = batch

        super().__init__(
            size=Size(
                matrix=Mat2(), constant=Vec2(1.0, 1.0) * -2 * Sizing.CONTENT_PADDING
            ),
            position=Position(),
            parent=parent,
        )

        self.add_setting(
            "Test",
            Rectangle(
                size=Size(constant=Vec2(100, 50)),
                position=Position(),
                parent=None,
                colour=Colours.FOREGROUND,
                batch=self.batch,
            ),
        )

    def add_setting(self, label: str, component: Frame):
        position: Position
        parent: Frame

        if len(self.components) >= 1:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            parent = self.components[-1][0]
        else:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 1.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            parent = self

        container = BorderedRectangle(
            position=position,
            parent=parent,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=Vec2(-64.0, 64.0),
            ),
            batch=self.batch,
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
            batch=self.batch,
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
