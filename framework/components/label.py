from framework import Frame, Position, Size
from pyglet.graphics import Group
from pyglet.text import Label as PygletLabel
from pyglet.math import Vec2


class Label(Frame):
    """Single line of text."""

    def __init__(
        self,
        text: str,
        colour: tuple[int, int, int, int],
        position: Position,
        parent: "Frame | None",
        font_size: int = 12,
        behind_parent: bool = False,
    ):
        self.label = PygletLabel(
            text=text,
            x=0,
            y=0,
            color=colour,
            anchor_y="top",
            anchor_x="left",
            font_size=font_size,
            font_name="Noto Sans",
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

    @property
    def colour(self) -> tuple[int, int, int, int]:
        return self.label.color

    @colour.setter
    def colour(self, colour: tuple[int, int, int, int]):
        self.label.color = colour

    def draw(self):
        self.label.draw()

    def set_group(self, group: Group | None):
        self.label.group = group

    def set_size(self):
        # Size set by the label's content, needs to fit the label
        self.aabb.size.x = self.label.content_width
        self.aabb.size.y = self.label.content_height

    def set_position(self):
        # Need to anchor weirdly because of the way labels work in Pyglet
        self.label.x, self.label.y = self.aabb.position + Vec2(
            0, self.label.content_height
        )
