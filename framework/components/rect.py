from pyglet.graphics import Group
from pyglet.shapes import Rectangle as PygletRectangle
from framework import Size, Position, Frame


class Rectangle(Frame):
    def __init__(
        self,
        colour: tuple[int, int, int, int],
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        self.rect = PygletRectangle(
            x=0,
            y=0,
            width=0,
            height=0,
            color=colour,
        )

        super().__init__(size, position, parent, behind_parent)

    @property
    def colour(self) -> tuple:
        return self.rect.color

    @colour.setter
    def colour(self, colour: tuple[int, int, int, int]):
        self.rect.color = colour

    def draw(self):
        self.rect.draw()

    def set_group(self, group: Group | None):
        self.rect.group = group

    def set_size(self):
        self.rect.width, self.rect.height = self.aabb.size

    def set_position(self):
        self.rect.x, self.rect.y = self.aabb.position
