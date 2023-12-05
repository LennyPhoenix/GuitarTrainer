from pyglet.graphics import Batch, Group
from framework import Frame, Position, Size
from pyglet.text import Label
from pyglet.math import Vec2


class Text(Frame):
    def __init__(
        self,
        text: str,
        colour: tuple[int, int, int, int],
        batch: Batch,
        size: Size,
        position: Position,
        parent: "Frame | None",
        font_size: int = 12,
        behind_parent: bool = False,
    ):
        self.label = Label(
            text=text,
            x=0,
            y=0,
            batch=batch,
            color=colour,
            width=1,
            multiline=True,
            anchor_y="top",
            font_size=font_size,
        )
        super().__init__(size, position, parent, behind_parent)

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, new_text):
        self.label.text = new_text
        self.propagate_size()
        self.propagate_position()

    @property
    def colour(self) -> tuple[int, int, int, int]:
        return self.label.color

    @colour.setter
    def colour(self, colour: tuple[int, int, int, int]):
        self.label.color = colour

    def set_group(self, group: Group):
        self.label.group = group

    def set_size(self):
        self.label.width = self.aabb.size.x
        self.aabb.size.y = self.label.content_height

    def set_position(self):
        self.label.x, self.label.y = self.aabb.position + Vec2(
            0, self.label.content_height
        )
