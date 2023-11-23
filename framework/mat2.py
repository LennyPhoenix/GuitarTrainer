from collections.abc import Iterable
from operator import mul
from typing import Self, overload

from pyglet.math import Vec2


class Mat2(tuple):
    def __new__(cls, values: Iterable[float] = (1.0, 0.0, 0.0, 1.0)) -> Self:
        new = super().__new__(Mat2, values)
        assert len(new) == 4
        return new

    @overload
    def __matmul__(self, other: Vec2) -> Vec2:
        ...

    @overload
    def __matmul__(self, other: Self) -> Self:
        ...

    def __matmul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(
                self[0] * other.x + self[1] * other.y,
                self[2] * other.x + self[3] * other.y,
            )
        elif isinstance(other, Mat2):
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
