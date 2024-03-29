from pyglet.image import AbstractImage
from pyglet.sprite import Sprite
from pyglet.math import Vec2
from pyglet.graphics import Group
from framework import Size, Position, Frame

from enum import Enum, auto


class Image(Frame):
    """A pyglet sprite as a UI component."""

    class SizeMode(Enum):
        # Stretches the image to fit the UI AABB
        STRETCH = auto()
        # Makes the image as big as possible while maintaining aspect ratio
        FIT = auto()

    class PositionMode(Enum):
        # Places the image in the center of the AABB
        CENTRE = auto()
        # Weights the position based on the local anchor of the pin
        PIN = auto()

    _size_mode: SizeMode
    _position_mode: PositionMode
    _image: AbstractImage

    def __init__(
        self,
        image: AbstractImage,
        size: Size,
        position: Position,
        parent: Frame | None,
        size_mode: SizeMode = SizeMode.FIT,
        position_mode: PositionMode = PositionMode.CENTRE,
        behind_parent: bool = False,
    ):
        self._image = image
        self.sprite = Sprite(
            self.image,
        )

        self._size_mode = size_mode
        self._position_mode = position_mode
        super().__init__(size, position, parent, behind_parent)

    @property
    def size_mode(self) -> SizeMode:
        return self._size_mode

    @size_mode.setter
    def size_mode(self, size_mode: SizeMode):
        self.set_size()
        self.set_position()
        self._size_mode = size_mode

    @property
    def position_mode(self) -> PositionMode:
        return self._position_mode

    @position_mode.setter
    def position_mode(self, position_mode: PositionMode):
        self._position_mode = position_mode
        self.set_position()

    @property
    def image(self) -> AbstractImage:
        return self._image

    @image.setter
    def image(self, image: AbstractImage):
        self._image = image
        self.sprite.image = image

    @property
    def colour(self) -> tuple:
        return (*self.sprite.color, self.sprite.opacity)

    @colour.setter
    def colour(self, new_colour: tuple[int, int, int, int]):
        self.sprite.color, self.sprite.opacity = new_colour[:3], new_colour[3]

    def draw(self):
        self.sprite.draw()

    def set_size(self):
        # Reset size
        self.sprite.update(scale=1.0, scale_x=1.0, scale_y=1.0)
        # Different size modes
        match self.size_mode:
            case Image.SizeMode.STRETCH:
                # Stretch to match AABB
                self.sprite.width = self.aabb.size.x
                self.sprite.height = self.aabb.size.y
            case Image.SizeMode.FIT:
                # Maintain aspect ratio
                self.sprite.scale = min(
                    self.aabb.size.x / self.sprite.width,
                    self.aabb.size.y / self.sprite.height,
                )

    def set_position(self):
        # Calculate base offset
        diff = Vec2(
            self.aabb.size.x - self.sprite.width, self.aabb.size.y - self.sprite.height
        )
        # Different position modes
        match self.position_mode:
            case Image.PositionMode.CENTRE:
                # Centre the image
                self.sprite.update(
                    x=self.aabb.position.x + diff.x / 2,
                    y=self.aabb.position.y + diff.y / 2,
                )
            case Image.PositionMode.PIN:
                # Offset based on local anchor
                self.sprite.update(
                    x=self.aabb.position.x + diff.x * self.position.pin.local_anchor.x,
                    y=self.aabb.position.y + diff.y * self.position.pin.local_anchor.y,
                )

    def set_group(self, group: Group | None):
        self.sprite.group = group
