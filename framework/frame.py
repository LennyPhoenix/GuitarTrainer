from typing import Self

from framework.aabb import Aabb
from framework.node import Node
from framework.position import Position
from framework.size import Size

from pyglet.math import Vec2
from pyglet.graphics import Group


class Frame(Node):
    size: Size
    position: Position

    aabb: Aabb
    broad_phase_aabb: Aabb
    index: int = 0
    behind_parent: bool

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
        super().add_child(other)
        other.propagate_size()
        other.propagate_position()

    def propagate_size(self):
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

    def set_size(self):
        """Update any drawables to use the newly assigned size."""

    def propagate_position(self):
        # Ignore parent AABB if there is no parent
        if self.parent is not None:
            parent_aabb = self.parent.aabb
        else:
            parent_aabb = None

        # Calculate absolute position
        self.aabb.position = self.position.calc_position(parent_aabb, self.aabb.size)
        self.set_position()

        self.broad_phase_aabb = self.aabb
        for child in self.children:
            child.propagate_position()
            self.broad_phase_aabb = self.broad_phase_aabb.union(child.broad_phase_aabb)
        print(self.broad_phase_aabb)

    def set_position(self):
        """Update any drawables to use the newly assigned position."""

    def on_size_update(self):
        self.propagate_size()
        self.propagate_position()

    def on_position_update(self):
        self.propagate_position()

    def set_group(self, parent: Group | None, index: int) -> Group | None:
        """Create a group and update any drawables to use the newly assigned group."""
        return Group(index, parent=parent)

    def propagate_indices(self, assigned_index: int) -> int:
        max_index = assigned_index - 1

        # Deal with reversed children first
        for child in self.children:
            if child.behind_parent:
                max_index = max(max_index, child.propagate_indices(assigned_index))

        # Should be `assigned_index` if no children are reversed
        max_index += 1
        self.index = max_index

        # Deal with "normal" children
        for child in self.children:
            if not child.behind_parent:
                max_index = max(
                    max_index,
                    # If no reversed children: `assigned_index + 1`
                    child.propagate_indices(self.index + 1),
                )

        return max_index

    def propagate_groups(self, parent_group: Group | None):
        group = self.set_group(parent_group, self.index)

        for child in self.children:
            child.propagate_groups(group)

    def reindex_tree(self):
        if self.parent is not None:
            self.parent.reindex_tree()
        else:
            self.propagate_indices(0)
            self.propagate_groups(None)
