""" Framework is a modular UI system for pyglet.

Each UI element is considered a frame, and each frame can have any number of
children. A frame's size and position can be dependent on its parent, or it can
be absolute. This allows you to easily create complex GUIs that can scale with
the window dimensions as little or as much as necessary.

Contents:
- `Pin`: A pin describes how a frame is anchored to its parent.
- `Aabb`: An axis-aligned bounding box. Used to describe the position and size
  of a frame.
- `Size`: A size describes how a frame's size is calculated.
- `Position`: A position describes how a frame's position is calculated.
- `Frame`: A frame is a UI element. It has a position, size, and children.
- `Mat2`: A 2x2 matrix. Used to describe how a frame's size is calculated.
- `Vec2`: A 2D vector. Reimported from `pyglet.math`.

Developed by Lenny Critchley for Guitar Trainer.
"""


from .pin import Pin
from .aabb import Aabb
from .size import Size
from .position import Position
from .frame import Frame
from .mat2 import Mat2
from pyglet.math import Vec2
from . import components

__all__ = [
    "Pin",
    "Aabb",
    "Size",
    "Position",
    "Frame",
    "Mat2",
    "Vec2",
    "components",
]
