from collections.abc import Iterable
from typing import Self, overload

from pyglet.math import Vec2


class Mat2(tuple):
    """A 2x2 matrix, used to describe a frame's size relative to its parent."""

    def __new__(cls, values: Iterable[float] = (1.0, 0.0, 0.0, 1.0)) -> Self:
        new = super().__new__(Mat2, values)
        # Make sure we got passed the right number of values
        assert len(new) == 4
        return new

    @overload
    def __matmul__(self, other: Vec2) -> Vec2:
        # This overload is for multiplying the matrix with a Vec2
        ...

    @overload
    def __matmul__(self, other: Self) -> Self:
        # This overload is for multiplying the matrix with another Mat2
        ...

    def __matmul__(self, other):
        if isinstance(other, Vec2):
            # If dealing with a vector...
            return Vec2(
                self[0] * other.x + self[1] * other.y,
                self[2] * other.x + self[3] * other.y,
            )
        elif isinstance(other, Mat2):
            # If dealing with a matrix...
            return Mat2(
                (
                    self[0] * other[0] + self[1] * other[2],
                    self[0] * other[1] + self[1] * other[3],
                    self[2] * other[0] + self[3] * other[2],
                    self[2] * other[1] + self[3] * other[3],
                )
            )
        else:
            raise TypeError("Can only multiply with Mat2 or Vec2 types")
