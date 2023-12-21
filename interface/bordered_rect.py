from framework.components import Rectangle
from framework import Frame, Mat2, Size, Vec2, Position

from interface.style import Colours, Sizing


class BorderedRectangle(Rectangle):
    def __init__(
        self,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        super().__init__(
            size=size,
            position=position,
            colour=Colours.ELEMENT_BACKGROUND,
            parent=parent,
            behind_parent=behind_parent,
        )

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
