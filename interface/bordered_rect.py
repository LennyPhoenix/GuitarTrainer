from framework.components import Rectangle
from framework import Frame, Mat2, Size, Vec2, Position

from interface.style import Colours, Sizing

from pyglet.graphics import Batch


class BorderedRectangle(Rectangle):
    def __init__(
        self,
        size: Size,
        position: Position,
        batch: Batch,
        parent: Frame | None,
    ):
        super().__init__(
            size=size,
            position=position,
            colour=Colours.ELEMENT_BACKGROUND,
            batch=batch,
            parent=parent,
        )

        self.border = Rectangle(
            colour=Colours.BORDER,
            batch=batch,
            size=Size(
                matrix=Mat2(),
                constant=Vec2(Sizing.BORDER_SIZE, Sizing.BORDER_SIZE) * 2,
            ),
            position=Position(),
            parent=self,
            behind_parent=True,
        )
