from typing import Self

from framework.aabb import Aabb
from framework.node import Node
from framework.position import Position
from framework.size import Size

from pyglet.math import Vec2
from pyglet.graphics import Group
from pyglet import clock

import gc


class Frame(Node):
    """The base class that all UI components must inherit from."""

    size: Size
    position: Position

    aabb: Aabb
    # The union AABB containing every child's AABB
    broad_phase_aabb: Aabb
    # The draw index (depth of the node)
    index: int = 0
    # Whether to draw behind or in front of the parent
    behind_parent: bool

    _group: Group | None = None

    def __init__(
        self,
        size: Size,
        position: Position,
        parent: "Frame | None",
        behind_parent: bool = False,
    ):
        super().__init__()
        self.size = size
        self.size.set_handler("on_update", self.on_size_update)

        self.position = position
        self.position.set_handler("on_update", self.on_position_update)

        self.behind_parent = behind_parent
        self.aabb = Aabb(Vec2(), Vec2())
        self.broad_phase_aabb = Aabb(Vec2(), Vec2())

        self.parent = parent
        self.propagate_size()
        self.propagate_position()

    def add_child(self, other: Self):
        """Override Node's `add_child` to update the size and position of the
        child."""
        super().add_child(other)
        other.propagate_size()
        other.propagate_position()

    def rebuild_groups(self):
        """Rebuilds groups by travelling to the top of the tree, then
        propagating groups downwards recursively."""
        if self.parent is not None:
            # Get to the top...
            self.parent.rebuild_groups()
        else:
            # ...then rebuild downwards.
            self.propagate_groups(None)

    def rebuild(self):
        """Schedule a garbage collection then rebuild groups."""
        # This is a lovely side-effect of the way the garbage collector works
        # and deals with cyclic references.
        # Calling gc.collect() directly here will not work as the callstack
        # will still contain a reference to the selection box.
        clock.schedule_once(lambda _: gc.collect(), 0)
        self.rebuild_groups()

    def draw(self):
        """Draw any drawables."""

    def set_size(self):
        """Update any drawables to use the newly assigned size."""

    def set_position(self):
        """Update any drawables to use the newly assigned position."""

    def build_group(self, parent: Group | None) -> Group | None:
        """Transform the group that this and all children will inherit from.

        Default behaviour is simply an identity that returns the parent group.
        """
        return parent

    def set_group(self, group: Group | None):
        """Update any drawables to use the newly assigned group."""

    def propagate_draw(self):
        """Recursively draw all frames in the tree.

        Draws children behind the frame, then self, then the children in front
        of the frame.
        """
        for child in self.children:
            if child.behind_parent:
                child.propagate_draw()

        self.draw()

        for child in self.children:
            if not child.behind_parent:
                child.propagate_draw()

    def propagate_size(self):
        """Recursively propagate size calculations down the tree."""
        # Ignore parent size if there is no parent
        if self.parent is not None:
            parent_size = self.parent.aabb.size
        else:
            parent_size = None

        # Calculate absolute size
        self.aabb.size = self.size.calc_size(parent_size)
        self.set_size()

        for child in self.children:
            child.propagate_size()

    def propagate_position(self):
        """Recursively propagate position calculations down the tree."""
        # Ignore parent AABB if there is no parent
        if self.parent is not None:
            parent_aabb = self.parent.aabb
        else:
            parent_aabb = None

        # Calculate absolute position
        self.aabb.position = self.position.calc_position(
            parent_aabb,
            self.aabb.size,
        )
        self.set_position()

        # Calculate broad phase by unioning every aabb
        self.broad_phase_aabb = self.aabb
        for child in self.children:
            child.propagate_position()
            self.broad_phase_aabb = self.broad_phase_aabb.union(
                child.broad_phase_aabb,
            )

    def propagate_groups(self, parent_group: Group | None):
        """Recursively propagate pyglet groups."""
        group = self.build_group(parent_group)
        self._group = group
        self.set_group(group)

        for child in self.children:
            child.propagate_groups(group)

    # Propagate update hooks
    def on_size_update(self):
        self.propagate_size()
        self.propagate_position()

    def on_position_update(self):
        self.propagate_position()
