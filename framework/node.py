from typing import Self
from weakref import ref, WeakSet


class Node:
    """A single node in the component tree, helps with draw ordering."""

    # Use a weak reference here to avoid cyclic references
    _parent: ref[Self] | None = None

    # Weak reference here too
    children: WeakSet[Self]

    def __init__(self) -> None:
        self.children = WeakSet()

    def add_child(self, other: Self):
        """Adds a child to this node."""
        other.parent = self

    @property
    def parent(self) -> Self | None:
        if self._parent is not None:
            # Attempt to deref the weak reference
            return self._parent()
        else:
            return None

    @parent.setter
    def parent(self, new_parent: Self | None):
        # Removes self from old parent
        if self._parent is not None:
            p = self._parent()
            if p is not None:
                p.children.remove(self)

        # Adds self to new parent
        if new_parent is not None:
            self._parent = ref(new_parent)
            new_parent.children.add(self)
        else:
            self._parent = None
