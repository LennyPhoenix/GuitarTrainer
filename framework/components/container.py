from pyglet.graphics import Group
from pyglet import gl
from pyglet.gl import GLint
from framework import Frame, Aabb, Vec2


class ScissorGroup(Group):
    """Pyglet graphics group that only renderes within the bounds of its
    AABB."""

    # The state before this scissor group was applied
    previous_state: Aabb | None = None

    def __init__(self, aabb: Aabb, order=0, parent=None):
        super().__init__(order, parent)
        self.aabb = aabb

    def set_state(self):
        if gl.glIsEnabled(gl.GL_SCISSOR_TEST):
            # Save old state if there is already a scissor group applied as
            # the new scissorgroup will simply overwrite the old one.
            old_state = (GLint * 4)()
            gl.glGetIntegerv(gl.GL_SCISSOR_BOX, old_state)
            self.previous_state = Aabb(
                Vec2(*old_state[:2]),
                Vec2(*old_state[2:]),
            )
        else:
            self.previous_state = None

        # Turn on the OpenGL flag
        gl.glEnable(gl.GL_SCISSOR_TEST)
        if self.previous_state is None:
            # If there is no previous group, then apply the new AABB
            # directly...
            aabb = self.aabb
        else:
            # ...otherwise use the intersection between them to make sure we
            # combine the two scissor groups.
            aabb = self.previous_state.intersection(self.aabb)
        # Apply the new scissor group
        gl.glScissor(*round(aabb.position), *round(aabb.size))

    def unset_state(self):
        if self.previous_state is None:
            # Turn off the flag if there is no previous scissor group
            gl.glDisable(gl.GL_SCISSOR_TEST)
        else:
            # Change back to previous state
            gl.glScissor(
                *round(self.previous_state.position),
                *round(self.previous_state.size),
            )


class Container(Frame):
    _group: ScissorGroup | None

    # Constructs a new ScissorGroup
    def build_group(self, parent: Group | None) -> Group | None:
        return ScissorGroup(self.aabb, parent=parent)

    def set_size(self):
        # Resets the ScissorGroup's size to fit
        if self._group is not None:
            self._group.aabb = self.aabb

    def set_position(self):
        # Resets the ScissorGroup's position to match
        if self._group is not None:
            self._group.aabb = self.aabb
