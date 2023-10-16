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
            r0 = self[0::2]
            r1 = self[1::2]
            return Vec2(sum(map(mul, r0, other)), sum(map(mul, r1, other)))
        elif isinstance(other, Mat2):
            r0 = self[0::2]
            r1 = self[1::2]

            c0 = other[0:2]
            c1 = other[2:4]

            return Mat2(
                (
                    sum(map(mul, c0, r0)),
                    sum(map(mul, c0, r1)),
                    sum(map(mul, c1, r0)),
                    sum(map(mul, c1, r1)),
                )
            )
        else:
            raise TypeError("Can only multiply with Mat2 or Vec2 types")
