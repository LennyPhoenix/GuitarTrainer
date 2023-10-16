from pyglet.event import EventDispatcher
from dataclasses import dataclass


class UpdateHook(EventDispatcher):
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.dispatch_event("on_update")


UpdateHook.register_event_type("on_update")


class TestUpdateHook:
    @dataclass
    class Object(UpdateHook):
        thing: int = 0

    thing: int = 100

    def test_update_hook(self):
        test = self.Object()

        def hook():
            self.thing = test.thing

        test.set_handler("on_update", hook)

        test.thing = 100

        assert self.thing == 100
