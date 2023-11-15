from framework import Frame, Position, Size
from pyglet.graphics import Batch, Group
from pyglet.text import Label as PygletLabel
from pyglet.math import Vec2


class Label(Frame):
    def __init__(
        self,
        text: str,
        color: tuple[int, int, int, int],
        batch: Batch,
        position: Position,
        parent: "Frame | None",
        font_size: int = 12,
        behind_parent: bool = False,
    ):
        self.label = PygletLabel(
            text=text,
            x=0,
            y=0,
            batch=batch,
            color=color,
            anchor_y="top",
            anchor_x="left",
            font_size=font_size,
        )
        super().__init__(Size(), position, parent, behind_parent)

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, new_text):
        self.label.text = new_text
        self.propagate_size()
        self.propagate_position()

    def set_group(self, parent: Group | None, index: int) -> Group | None:
        group = super().set_group(parent, index)
        self.label.group = group
        return group

    def set_size(self):
        self.aabb.size.x = self.label.content_width
        self.aabb.size.y = self.label.content_height

    def set_position(self):
        self.label.x, self.label.y = self.aabb.position + Vec2(
            0, self.label.content_height
        )
