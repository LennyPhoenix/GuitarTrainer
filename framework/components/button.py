from pyglet.event import EventDispatcher
from pyglet.math import Vec2
from framework import Frame

from enum import Enum, auto


class Button(Frame, EventDispatcher):
    class State(Enum):
        NORMAL = auto()
        HOVER = auto()
        PRESSED = auto()

    _state: State = State.NORMAL

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, state: State):
        self._state = state
        self.dispatch_event("on_state_change", self._state)

    def on_mouse_motion(self, x, y, _dx, _dy):
        # TODO
        pass

    def on_mouse_drag(self, x, y, _dx, _dy, buttons, _modifiers):
        # TODO
        pass

    def on_mouse_press(self, x, y, button, _modifiers):
        # TODO
        pass

    def on_mouse_release(self, x, y, button, _modifiers):
        # TODO
        pass


Button.register_event_type("on_state_change")
