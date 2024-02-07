from copy import deepcopy
from enum import Enum, auto
from random import shuffle

from pyglet.event import EventDispatcher
from engine import (
    Instrument,
    StorageManager,
    Lesson,
    Progress,
    Exercise,
    SoundManager,
    fret_exercises,
    stave_exercises,
)

from framework import Frame, Position, Size, Mat2, Vec2, Pin
from framework.components import Text, Label

from pyglet.window import Window
from pyglet.resource import image

from .style import Colours
from .bordered_rect import BorderedRectangle
from .scroll_container import ScrollContainer
from .image_button import ImageButton
from .dropdown import Dropdown
from .lesson_interface import LessonInterface


def determine_next_target(
    current: Progress,
    instrument: Instrument,
) -> Progress:
    target = deepcopy(current)

    # Test Knowledge
    for i, progress in enumerate(current.string_progress):
        if progress[0] is not None:
            if progress[1] is None or progress[0] > progress[1]:
                target.string_progress[i] = (progress[0], progress[0])
    if current.highest_note[0] is not None:
        if (
            current.highest_note[1] is None
            or current.highest_note[0] > current.highest_note[1]
        ):
            target.highest_note = (
                current.highest_note[0],
                current.highest_note[0],
            )
    for scale, progress in current.scales.items():
        if progress is not None and progress[0] and not progress[1]:
            target.scales[scale] = (progress[0], progress[0])

    new_topic = False

    # Teach Stave
    highest_note_offset = -1
    for i, progress in enumerate(current.string_progress):
        if progress[1] is not None:
            highest_note_offset = max(
                highest_note_offset,
                progress[1]
                + instrument.value.strings[i].offset
                - instrument.value.lowest_pitch.offset,
            )
    if highest_note_offset != -1:
        if (
            current.highest_note[0] is None
            or current.highest_note[0] < highest_note_offset
        ):
            target.highest_note = (highest_note_offset, None)
            new_topic = True

    # Teach Note Names
    fret_target = 5
    while not new_topic and fret_target < 24:
        for i, progress in enumerate(current.string_progress):
            if i == 0:
                prev_string_learnt = True
            else:
                prev_progress = current.string_progress[i - 1][1]
                prev_string_learnt = (
                    prev_progress is not None and prev_progress >= fret_target
                )

            if progress[0] is None and prev_string_learnt:
                target.string_progress[i] = (fret_target, None)
                new_topic = True
                break
        fret_target += 2

    # Teach Scales
    top_string = current.string_progress[-1][1]
    if not new_topic and top_string is not None and top_string >= 12:
        for scale, progress in current.scales.items():
            if progress is None or not progress[0]:
                target.scales[scale] = (True, False)
                new_topic = True
                break

    return target


def determine_lesson_from_progress(
    index: int,
    last: Progress,
    target: Progress,
    instrument: Instrument,
) -> Lesson:
    exercises = []

    # Fret exercises
    for string_index, string_target in enumerate(target.string_progress):
        string = instrument.value.strings[string_index]
        string_last = last.string_progress[string_index]
        if string_target[0] != string_last[0]:
            # A string was taught
            exercises += fret_exercises(
                string_last[0],
                string_target[0],
                string,
                teaching=True,
            )

        if string_target[1] != string_last[1]:
            # A string was tested
            exercises += fret_exercises(
                string_last[1],
                string_target[1],
                string,
                teaching=False,
            )

    # Stave exercises
    if target.highest_note[0] != last.highest_note[0]:
        # A new note was taught
        exercises += stave_exercises(
            last.highest_note[0],
            target.highest_note[0],
            instrument,
        )
    if target.highest_note[1] != last.highest_note[1]:
        # A new note was tested
        exercises += stave_exercises(
            last.highest_note[1],
            target.highest_note[1],
            instrument,
            teaching=False,
        )

    for scale_name, scale_progress in target.scales.items():
        last_progress = last.scales[scale_name]
        if scale_progress is not None and last_progress is not None:
            if scale_progress[0] != last_progress[0]:
                # A new scale was taught
                pass
            if scale_progress[1] != last_progress[1]:
                # A new scale was tested
                pass

    shuffle(exercises)

    return Lesson(
        number=index + 1,
        exercises=exercises,
        target_progress=target,
    )


class LessonButton(BorderedRectangle, EventDispatcher):
    def __init__(
        self,
        position: Position,
        size: Size,
        parent: Frame | None,
        window: Window,
        lesson: Lesson,
        complete: bool,
    ):
        super().__init__(
            position=position,
            size=size,
            parent=parent,
            behind_parent=True,
        )

        self.lesson = lesson
        self.complete = complete

        self.play_button = ImageButton(
            window=window,
            size=Size(
                matrix=Mat2((0.0, 1.0, 0.0, 1.0)),
            ),
            position=Position(pin=Pin.top_left()),
            parent=self,
            image=image("assets/play.png"),
        )
        self.play_button.set_handler("on_released", self.on_button_pressed)

        self.info = ScrollContainer(
            size=Size(
                matrix=Mat2((1.0, -1.0, 0.0, 1.0)),
            ),
            position=Position(pin=Pin.top_right()),
            parent=self,
        )
        self.info.register(window)

        self.title = Label(
            text=f"Lesson {lesson.number}",
            font_size=32,
            colour=Colours.FOREGROUND,
            position=Position(pin=Pin.top_left(), offset=Vec2(8, 0)),
            parent=self.info.content,
        )

        exercises: dict[tuple[Exercise.Type, bool], int] = {}

        for exercise in set(lesson.exercises):
            if (exercise.type, exercise.hint) not in exercises:
                exercises[(exercise.type, exercise.hint)] = 0
            exercises[(exercise.type, exercise.hint)] += 1

        pretty = ""
        for key, value in exercises.items():
            modifier = "NEW" if key[1] else "practice for"

            match key[0]:
                case Exercise.Type.NOTE_NAME:
                    name = "Note Names"
                case Exercise.Type.STAVE_NOTE:
                    name = "Stave Notes"
                case Exercise.Type.SCALE:
                    name = "Scales"

            pretty += f"- {value} {modifier} {name}\n"

        self.text = Text(
            text=pretty,
            colour=Colours.FOREGROUND,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
            ),
            position=Position(pin=Pin.top_left(), offset=Vec2(8, -48 - 18)),
            parent=self.info.content,
            font_size=24,
        )

    def on_button_pressed(self):
        self.dispatch_event("on_started", self.lesson, self.complete)


LessonButton.register_event_type("on_started")


class LessonSelection(ScrollContainer, EventDispatcher):
    DEFAULT_INSTRUMENT = Instrument.GUITAR

    def __init__(
        self,
        parent: Frame | None,
        window: Window,
        storage_manager: StorageManager,
        instrument: Instrument = DEFAULT_INSTRUMENT,
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

        self.dropdown = Dropdown(
            default=instrument.value.name,
            window=window,
            size=Size(
                constant=Vec2(256, 64),
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
                target_progress = determine_next_target(
                    progress_snapshot,
                    instrument,
                )
            else:
                target_progress = instrument_progress[i + 1]

            lesson = determine_lesson_from_progress(
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


class Lessons(Frame):
    class Mode(Enum):
        SELECTION = auto()
        LESSON = auto()

    current_mode: Mode = Mode.SELECTION
    content: LessonSelection | LessonInterface | None = None

    instrument: Instrument = LessonSelection.DEFAULT_INSTRUMENT

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

        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )
        self.show()

    def show(self):
        match self.current_mode:
            case self.Mode.SELECTION:
                self.content = LessonSelection(
                    self, self.window, self.storage, instrument=self.instrument
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
        self.content = None
        self.rebuild()

    def on_instrument_change(self, instrument: Instrument):
        self.instrument = instrument

    def on_lesson_started(self, lesson: Lesson, complete: bool):
        self.lesson = lesson
        self.complete = complete
        self.current_mode = self.Mode.LESSON
        self.show()

    def on_lesson_finished(self):
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
        self.exercise = exercise

    def on_lesson_closed(self):
        self.lesson = None
        self.exercise = 0
        self.current_mode = self.Mode.SELECTION
        self.show()
