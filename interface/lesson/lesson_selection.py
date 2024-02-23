from interface import ScrollContainer, Dropdown
from .lesson_button import LessonButton

from framework import Size, Mat2, Position, Frame, Vec2, Pin
from engine import Instrument, StorageManager, Lesson, Progress

from pyglet.event import EventDispatcher
from pyglet.window import Window


class LessonSelection(ScrollContainer, EventDispatcher):
    def __init__(
        self,
        parent: Frame | None,
        window: Window,
        storage_manager: StorageManager,
        instrument: Instrument | None = None,
    ):
        self.lessons = []
        self.storage = storage_manager
        self.window = window

        self.register(window)

        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )

        if instrument is None:
            instrument = self.storage.default_instrument

        self.dropdown = Dropdown(
            default=instrument.value.name,
            window=window,
            size=Size(
                constant=Vec2(128, 64),
            ),
            position=Position(
                pin=Pin.top_left(),
                offset=Vec2(18.0, -18.0),
            ),
            parent=self.content,
            elements=lambda: [i.value.name for i in Instrument],
        )
        self.dropdown.set_handler("on_picked", self.on_dropdown_picked)

        self.generate_lessons(instrument)

    def on_dropdown_picked(self, instrument: str):
        instrument_member = filter(
            lambda i: i.value.name == instrument,
            Instrument,
        ).__next__()
        self.generate_lessons(instrument_member)
        self.dispatch_event("on_instrument_change", instrument_member)

    def generate_lessons(self, instrument: Instrument):
        self.lessons.clear()

        instrument_progress = self.storage.get_instrument_progress(instrument)

        for i, progress_snapshot in enumerate(instrument_progress):
            if i == 0:
                parent = self.content
                position = Position(
                    pin=Pin(
                        local_anchor=Vec2(0.5, 1.0),
                        remote_anchor=Vec2(0.5, 1.0),
                    ),
                    offset=Vec2(0.0, -128.0),
                )
                matrix = Mat2((0.7, 0.0, 0.0, 0.0))
            else:
                parent = self.lessons[i - 1]
                position = Position(
                    pin=Pin(
                        local_anchor=Vec2(0.5, 1.0),
                        remote_anchor=Vec2(0.5, 0.0),
                    ),
                    offset=Vec2(0.0, -128.0),
                )
                matrix = Mat2((1.0, 0.0, 0.0, 0.0))

            complete = i < len(instrument_progress) - 1
            if not complete:
                target_progress = Progress.next_target(
                    progress_snapshot,
                    instrument,
                )
            else:
                target_progress = instrument_progress[i + 1]

            lesson = Lesson.new_from_progress(
                i,
                progress_snapshot,
                target_progress,
                instrument,
            )

            lesson_button = LessonButton(
                position=position,
                parent=parent,
                size=Size(
                    matrix=matrix,
                    constant=Vec2(0, 196),
                ),
                window=self.window,
                lesson=lesson,
                complete=complete,
            )
            lesson_button.set_handler("on_started", self.on_lesson_started)
            self.lessons.append(lesson_button)

        # Padding
        self.lessons.append(
            Frame(
                size=Size(constant=Vec2(0, 64)),
                position=Position(
                    pin=Pin(
                        local_anchor=Vec2(0.0, 1.0),
                        remote_anchor=Vec2(0.0, 0.0),
                    )
                ),
                parent=self.lessons[-1],
            )
        )

        self.rebuild()

    def on_lesson_started(self, lesson: Lesson, complete: bool):
        self.dispatch_event("on_started", lesson, complete)


EventDispatcher.register_event_type("on_instrument_change")
EventDispatcher.register_event_type("on_started")
