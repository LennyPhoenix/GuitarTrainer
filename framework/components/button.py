from pyglet.window import mouse
from pyglet.event import EventDispatcher
from pyglet.math import Vec2
from pyglet.window import Window
from framework import Frame

from enum import Enum, auto


class Button(Frame, EventDispatcher):
    class State(Enum):
        NORMAL = auto()
        HOVER = auto()
        PRESSED = auto()

    _state: State = State.NORMAL

    def register(self, window: Window):
        window.push_handlers(self)

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, state: State):
        old = self._state
        self._state = state
        if state != old:
            self.dispatch_event("on_state_change", old, self._state)

    def on_mouse_motion(self, x, y, _dx, _dy):
        if self.state == Button.State.NORMAL and self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.HOVER)
        elif self.state == Button.State.HOVER and not self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.NORMAL)

    def on_mouse_press(self, x, y, button, _modifiers):
        if button == mouse.LEFT and self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.PRESSED)

    def on_mouse_release(self, x, y, button, _modifiers):
        if button == mouse.LEFT and self.state == Button.State.PRESSED:
            if self.aabb.check_point(Vec2(x, y)):
                self._set_state(Button.State.HOVER)
            else:
                self._set_state(Button.State.NORMAL)


Button.register_event_type("on_state_change")
