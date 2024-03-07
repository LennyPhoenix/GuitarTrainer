from dataclasses import dataclass

from pyglet.math import Vec2


@dataclass
class Aabb:
    """An axis-aligned bounding box, used to describe the actual position and
    size of a frame in the window.

    Also has some helper methods for checking if a point is inside the box,
    and for finding the union and intersection of two boxes. These are useful
    for buttons and other layout calculations.
    """

    position: Vec2
    size: Vec2

    @property
    def left(self) -> float:
        return self.position.x

    @property
    def right(self) -> float:
        return self.position.x + self.size.x

    @property
    def bottom(self) -> float:
        return self.position.y

    @property
    def top(self) -> float:
        return self.position.y + self.size.y

    @staticmethod
    def from_left_right_bottom_top(
        left: float, right: float, bottom: float, top: float
    ) -> "Aabb":
        """Builds a new AABB using the left, right, bottom and top sides."""
        return Aabb(
            Vec2(left, bottom),
            Vec2(
                max(right - left, 0.0),
                max(top - bottom, 0.0),
            ),
        )

    def check_point(self, point: Vec2) -> bool:
        """Check if a point is inside the AABB."""
        return (
            self.position.x < point.x < self.position.x + self.size.x
            and self.position.y < point.y < self.position.y + self.size.y
        )

    def union(self, other: "Aabb") -> "Aabb":
        """Returns the smallest AABB that encloses both this and some other
        AABB."""
        return Aabb.from_left_right_bottom_top(
            min(self.left, other.left),
            max(self.right, other.right),
            min(self.bottom, other.bottom),
            max(self.top, other.top),
        )

    def intersection(self, other: "Aabb") -> "Aabb":
        """Returns the largest AABB that is enclosed by both this and some
        other AABB."""
        return Aabb.from_left_right_bottom_top(
            max(self.left, other.left),
            min(self.right, other.right),
            max(self.bottom, other.bottom),
            min(self.top, other.top),
        )

    def __repr__(self) -> str:
        # Just allows the AABB to be printed nicely.
        return f"Aabb({self.position}, {self.size})"
