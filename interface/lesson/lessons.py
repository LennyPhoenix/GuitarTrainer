from enum import Enum, auto

from engine import (
    Instrument,
    StorageManager,
    Lesson,
    SoundManager,
)

from framework import Frame, Position, Size, Mat2

from pyglet.window import Window

from .lesson_interface import LessonInterface
from .lesson_selection import LessonSelection


class Lessons(Frame):
    """The main view of the application, could be either the lesson selection
    menu or the in-lesson interface.

    Retains information about the current lesson, so should be kept alive.

    Has a `show` and `hide` method available which can be used instead of
    deleting.
    """

    class Mode(Enum):
        """The state of the lesson view."""

        SELECTION = auto()
        LESSON = auto()

    current_mode: Mode = Mode.SELECTION
    # The actual content of the view
    content: LessonSelection | LessonInterface | None = None

    # Details about the lesson interface
    lesson: Lesson | None = None
    complete: bool = True  # whether this is an old lesson or not
    exercise: int = 0

    def __init__(
        self,
        parent: Frame | None,
        window: Window,
        storage_manager: StorageManager,
        sound_manager: SoundManager,
    ):
        self.window = window
        self.storage = storage_manager
        self.sound = sound_manager
        self.instrument = self.storage.default_instrument

        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )
        self.show()

    def show(self):
        """Displays the current view by constructing the content."""
        match self.current_mode:
            case self.Mode.SELECTION:
                self.content = LessonSelection(
                    self,
                    self.window,
                    self.storage,
                    instrument=self.instrument,
                )
                self.content.set_handler(
                    "on_instrument_change",
                    self.on_instrument_change,
                )
                self.content.set_handler(
                    "on_started",
                    self.on_lesson_started,
                )
            case self.Mode.LESSON:
                assert self.lesson is not None
                self.content = LessonInterface(
                    sound_manager=self.sound,
                    instrument=self.instrument,
                    lesson=self.lesson,
                    exercise=self.exercise,
                    parent=self,
                    window=self.window,
                )
                self.content.set_handler(
                    "on_finished",
                    self.on_lesson_finished,
                )
                self.content.set_handler(
                    "on_next_exercise",
                    self.on_next_exercise,
                )
                self.content.set_handler("on_close", self.on_lesson_closed)

        self.rebuild()

    def hide(self):
        """Hides the current view."""
        self.content = None
        self.rebuild()

    def on_instrument_change(self, instrument: Instrument):
        """Called when a new instrument is selected."""
        self.instrument = instrument

    def on_lesson_started(self, lesson: Lesson, complete: bool):
        """Called when lesson selection reports that a lesson was chosen."""
        self.lesson = lesson
        self.complete = complete
        self.current_mode = self.Mode.LESSON
        self.show()

    def on_lesson_finished(self):
        """Called when a lesson reports that it was completed."""
        assert self.lesson is not None

        if not self.complete:
            progress = self.storage.get_instrument_progress(self.instrument)
            progress.append(self.lesson.target_progress)
            self.storage.set_instrument_progress(self.instrument, progress)

        self.lesson = None
        self.exercise = 0
        self.complete = True
        self.current_mode = self.Mode.SELECTION
        self.show()

    def on_next_exercise(self, exercise: int):
        """Called when the lesson interface reports that an exercise was
        complete."""
        self.exercise = exercise

    def on_lesson_closed(self):
        """Called when a lesson reports that it was exited without
        completion."""
        self.lesson = None
        self.exercise = 0
        self.current_mode = self.Mode.SELECTION
        self.show()
