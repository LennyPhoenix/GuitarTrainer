from typing import Self
from weakref import ref, WeakSet


class Node:
    _parent: ref[Self] | None = None

    children: WeakSet[Self]

    def __init__(self) -> None:
        self.children = WeakSet()

    def add_child(self, other: Self):
        other.parent = self

    @property
    def parent(self) -> Self | None:
        if self._parent is not None:
            return self._parent()
        else:
            return None

    @parent.setter
    def parent(self, new_parent: Self | None):
        if self._parent is not None:
            p = self._parent()
            if p is not None:
                p.children.remove(self)

        if new_parent is not None:
            self._parent = ref(new_parent)
            new_parent.children.add(self)
        else:
            self._parent = None
