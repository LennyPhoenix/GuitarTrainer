import gc
from typing import Callable

from pyglet import clock

from .scroll_container import ScrollContainer
from .style import Colours
from .bordered_rect import BorderedRectangle

from framework import Frame, Size, Position, Pin, Mat2, Vec2
from framework.components import Button, Label, Rectangle

from pyglet.window import Window
from pyglet.event import EventDispatcher


class DropdownElement(Rectangle, EventDispatcher):
    def __init__(
        self,
        option: str,
        position: Position,
        parent: Frame | None,
        window: Window,
        behind_parent: bool = False,
    ):
        self.option = option

        super().__init__(
            Colours.ELEMENT_BACKGROUND,
            Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0)), constant=Vec2(0.0, 32.0)),
            position,
            parent,
            behind_parent,
        )

        self.button = Button(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
        )
        self.button.register(window)

        self.label = Label(
            text=self.option,
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(local_anchor=Vec2(0.0, 0.5),
                        remote_anchor=Vec2(0.0, 0.5))
            ),
            parent=self.button,
            font_size=24,
        )

        self.button.set_handler("on_state_change", self.on_state_change)

    def on_state_change(
        self,
        old_state: Button.State,
        new_state: Button.State,
    ):
        match new_state:
            case Button.State.HOVER:
                self.colour = Colours.HOVER
                if old_state == Button.State.PRESSED:
                    self.dispatch_event("on_selected", self.option)
            case Button.State.PRESSED:
                self.colour = Colours.PRESSED
            case Button.State.NORMAL:
                self.colour = Colours.ELEMENT_BACKGROUND


DropdownElement.register_event_type("on_selected")


class SelectionBox(BorderedRectangle):
    def __init__(
        self,
        options: list[str],
        parent: Frame | None,
        window: Window,
        dropdown: "DropDown",
    ):
        super().__init__(
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=Vec2(0.0, 256.0),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
            ),
            parent=parent,
        )

        self.dropdown = dropdown

        self.scroll_container = ScrollContainer(
            size=Size(matrix=Mat2(), min=Vec2(0.0, 0.0)),
            position=Position(),
            parent=self,
        )
        self.scroll_container.register(window)

        self.elements = []
        for option in options:
            if len(self.elements) > 0:
                parent = self.elements[-1]
                position = Position(
                    pin=Pin(
                        local_anchor=Vec2(0.0, 1.0),
                        remote_anchor=Vec2(0.0, 0.0),
                    ),
                )
            else:
                parent = self.scroll_container.content
                position = Position(
                    pin=Pin.top_left(),
                )
            element = DropdownElement(
                option=option,
                window=window,
                position=position,
                parent=parent,
            )
            element.set_handler("on_selected", self.on_element_selected)
            self.elements.append(element)

    def on_element_selected(self, option: str):
        self.dropdown.dispatch_event("on_picked", option)


class DropDown(BorderedRectangle, EventDispatcher):
    selection_box: SelectionBox | None = None

    def __init__(
        self,
        elements: Callable[[], list[str]],
        size: Size,
        position: Position,
        parent: "Frame | None",
        window: Window,
    ):
        super().__init__(size, position, parent)

        self.window = window
        self.elements = elements

        self.button = Button(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
        )
        self.button.register(window)
        self.button.set_handler("on_state_change", self.on_button_state_change)

        self.label = Label(
            text="Test",
            colour=Colours.FOREGROUND,
            position=Position(pin=Pin.centre()),
            parent=self,
        )

    def on_button_state_change(
        self,
        old_state: Button.State,
        new_state: Button.State,
    ):
        if old_state == Button.State.PRESSED and new_state == Button.State.HOVER:
            if self.selection_box is not None:
                self.close_box()
            else:
                self.selection_box = SelectionBox(
                    self.elements(),
                    self,
                    self.window,
                    self,
                )
                self.rebuild_groups()

    def close_box(self):
        self.selection_box = None
        # This is a lovely side-effect of the way the garbage collector works
        # and deals with cyclic references.
        # Calling gc.collect() directly here will not work as the callstack
        # will still contain a reference to the selection box.
        clock.schedule_once(lambda _: gc.collect(), 0)

    def on_picked(self, option: str = "Hello"):
        self.label.text = option
        self.close_box()


DropDown.register_event_type("on_picked")
