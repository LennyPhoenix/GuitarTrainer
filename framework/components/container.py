from pyglet.graphics import Group
from pyglet import gl
from framework import Frame, Aabb


class ScissorGroup(Group):
    previous_state: Aabb | None = None

    def __init__(self, aabb: Aabb, order=0, parent=None):
        super().__init__(order, parent)
        self.aabb = aabb

    def set_state(self):
        if gl.glIsEnabled(gl.GL_SCISSOR_TEST):
            self.previous_state = Aabb(
                gl.glGetIntegerv(gl.GL_SCISSOR_BOX)[:2],
                gl.glGetIntegerv(gl.GL_SCISSOR_BOX)[2:],
            )
        else:
            self.previous_state = None

        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(*round(self.aabb.position), *round(self.aabb.size))

    def unset_state(self):
        if self.previous_state is None:
            gl.glDisable(gl.GL_SCISSOR_TEST)
        else:
            gl.glScissor(
                *round(self.previous_state.position),
                *round(self.previous_state.size),
            )


class Container(Frame):
    _parent_group: Group | None = None

    def set_group(self, parent: Group | None, index: int) -> Group | None:
        self._parent_group = parent
        return ScissorGroup(self.aabb, order=index, parent=parent)

    def set_size(self):
        self.set_group(self._parent_group, self.index)

    def set_postion(self):
        self.set_group(self._parent_group, self.index)
