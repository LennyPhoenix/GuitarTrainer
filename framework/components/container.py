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
    _group: ScissorGroup

    def build_group(self, parent: Group | None) -> Group | None:
        return ScissorGroup(self.aabb, parent=parent)

    def set_size(self):
        if self._group is not None:
            self._group.aabb = self.aabb

    def set_postion(self):
        if self._group is not None:
            self._group.aabb = self.aabb
