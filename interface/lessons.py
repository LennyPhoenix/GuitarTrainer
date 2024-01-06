from engine import Instrument

from framework import Frame, Position, Size, Mat2, Vec2, Pin

from pyglet.window import Window

from .scroll_container import ScrollContainer
from .dropdown import Dropdown


class LessonSelection(ScrollContainer):
    DEFAULT_INSTRUMENT = Instrument.GUITAR

    def __init__(
        self,
        parent: Frame | None,
        window: Window,
    ):
        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )

        self.dropdown = Dropdown(
            default=self.DEFAULT_INSTRUMENT.value.name,
            window=window,
            size=Size(
                constant=Vec2(256, 64),
            ),
            position=Position(
                pin=Pin.top_left(),
                offset=Vec2(18.0, -18.0),
            ),
            parent=self,
            elements=lambda: [i.value.name for i in Instrument],
        )
        self.dropdown.set_handler("on_picked", self.on_dropdown_picked)

        self.generate_levels(self.DEFAULT_INSTRUMENT)

    def on_dropdown_picked(self, instrument: str):
        self.generate_levels(
            filter(
                lambda i: i.value.name == instrument,
                Instrument,
            ).__next__()
        )

    def generate_levels(self, instrument: Instrument):
        pass


class Lessons(Frame):
    current_mode: None = None
    content: LessonSelection | None = None

    def __init__(
        self,
        parent: Frame | None,
        window: Window,
    ):
        self.window = window

        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )
        self.show()

    def show(self):
        match self.current_mode:
            case None:
                self.content = LessonSelection(self, self.window)

    def hide(self):
        self.content = None
        self.rebuild()
