from pyglet.event import EventDispatcher
from dataclasses import dataclass


class UpdateHook(EventDispatcher):
    """Can be inherited from to emit an event every time an attribute is
    assigned to."""

    def __setattr__(self, name, value):
        """Called whenever a field is assigned to."""
        super().__setattr__(name, value)
        self.dispatch_event("on_update")


UpdateHook.register_event_type("on_update")


class TestUpdateHook:
    @dataclass
    class Object(UpdateHook):
        """Dummy object to test the update hook."""

        thing: int = 0

    test_output: int = 100

    def test_update_hook(self):
        test = self.Object()

        def hook():
            self.test_output = test.thing

        test.set_handler("on_update", hook)

        test.thing = 100

        assert self.test_output == 100
