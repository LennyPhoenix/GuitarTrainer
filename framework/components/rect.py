from pyglet.graphics import Batch, Group
from pyglet import shapes
from framework import Size, Position, Frame


class Rectangle(Frame):
    def __init__(
        self,
        color: tuple[int, int, int, int],
        batch: Batch,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        self.rect = shapes.Rectangle(
            0,
            0,
            0,
            0,
            color,
            batch,
        )

        super().__init__(size, position, parent, behind_parent)

    def set_group(self, parent: Group | None, index: int) -> Group | None:
        group = super().set_group(parent, index)
        self.rect.group = group
        return group

    def set_size(self):
        self.rect.width, self.rect.height = self.aabb.size

    def set_position(self):
        self.rect.x, self.rect.y = self.aabb.position
