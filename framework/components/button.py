from pyglet.window import mouse
from pyglet.event import EventDispatcher
from pyglet.math import Vec2
from pyglet.window import Window
from framework import Frame

from enum import Enum, auto


class Button(Frame, EventDispatcher):
    """A clickable button on the screen.

    Internally represented as a kind of finite state machine."""

    class State(Enum):
        """Represents the different possible states for the button."""

        NORMAL = auto()
        HOVER = auto()
        PRESSED = auto()

    _state: State = State.NORMAL

    def register(self, window: Window):
        """Assigns window events to be handled by this button."""
        window.push_handlers(self)

    @property
    def state(self) -> State:
        return self._state

    def _set_state(self, new_state: State):
        old_state = self._state
        self._state = new_state
        # Only dispatch the event if the state is different to the previous
        # state:
        if new_state != old_state:
            self.dispatch_event("on_state_change", old_state, new_state)

    def on_mouse_motion(self, x, y, _dx, _dy):
        """Called whenever the mouse moves on the window."""
        # Set to hover if mouse is over and state was `NORMAL`:
        if self.state == Button.State.NORMAL and self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.HOVER)
        # Set to normal if mouse isn't over and state was `HOVER`:
        elif self.state == Button.State.HOVER and not self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.NORMAL)

    def on_mouse_press(self, x, y, button, _modifiers):
        """Called when a mouse button is pressed in the window."""
        # Only change to pressed if mouse button was left and mouse is within
        # bounds of button.
        if button == mouse.LEFT and self.aabb.check_point(Vec2(x, y)):
            self._set_state(Button.State.PRESSED)

    def on_mouse_release(self, x, y, button, _modifiers):
        """Called whenever a mouse button is released."""

        # If mouse button is left, and was `PRESSED`:
        if button == mouse.LEFT and self.state == Button.State.PRESSED:
            # If within button, set to hover...
            if self.aabb.check_point(Vec2(x, y)):
                self._set_state(Button.State.HOVER)
            # ...otherwise set to normal.
            else:
                self._set_state(Button.State.NORMAL)


Button.register_event_type("on_state_change")
