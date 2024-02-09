from interface import Fretboard, Stave, ImageButton
from interface.style import Colours

from engine import (
    Accidental,
    Name,
    Instrument,
    Lesson,
    SoundManager,
    Exercise,
    Note,
    Pitch,
)

from framework import Frame, Position, Mat2, Size, Pin, Vec2
from framework.components import Label, Text

from pyglet.event import EventDispatcher
from pyglet.window import Window
from pyglet.resource import image


class LessonInterface(Frame, EventDispatcher):
    def __init__(
        self,
        sound_manager: SoundManager,
        instrument: Instrument,
        lesson: Lesson,
        window: Window,
        parent: Frame | None,
        exercise: int = 0,
    ):
        self.sound = sound_manager
        self.instrument = instrument
        self.lesson = lesson
        self.exercise = exercise

        self.content = []

        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )

        self.close_button = ImageButton(
            image("assets/close.png"),
            position=Position(
                pin=Pin.top_right(),
                offset=Vec2(-18, -18),
            ),
            size=Size(constant=Vec2(64, 64)),
            window=window,
            parent=self,
        )
        self.close_button.set_handler("on_released", self.on_close_button_pressed)

        self.question_number = Label(
            text="",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin.top_left(),
                offset=Vec2(18, -18),
            ),
            font_size=24,
            parent=self,
        )

        self.question_no_hint = Frame(
            size=Size(
                matrix=Mat2((0.8, 0.0, 0.0, 0.8)),
            ),
            position=Position(pin=Pin.centre()),
            parent=self,
        )

        self.question_hint = Frame(
            size=Size(
                matrix=Mat2((0.8, 0.0, 0.0, 0.4)),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 0.5),
                    remote_anchor=Vec2(0.5, 0.75),
                )
            ),
            parent=self,
        )
        self.hint = Frame(
            size=Size(
                matrix=Mat2((0.8, 0.0, 0.0, 0.4)),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 0.5),
                    remote_anchor=Vec2(0.5, 0.25),
                )
            ),
            parent=self,
        )

        self.show()
        sound_manager.push_handlers(self.on_new_offset)

    def show(self):
        self.content.clear()
        exercise = self.lesson.exercises[self.exercise]

        self.question_number.text = f"{self.exercise + 1}/{len(self.lesson.exercises)}"
        match exercise.type:
            case Exercise.Type.NOTE_NAME:
                assert exercise.string is not None
                question = Text(
                    text=f"Play the following note on the {exercise.string} string: {exercise.pitch}",
                    colour=Colours.FOREGROUND,
                    size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0))),
                    position=Position(),
                    align="center",
                    parent=(
                        self.question_hint if exercise.hint else self.question_no_hint
                    ),
                    font_size=48,
                )
                self.content.append(question)
                if exercise.hint:
                    max_fret = -1
                    for fret in self.lesson.target_progress.string_progress:
                        if fret[0] is not None:
                            max_fret = max(max_fret, fret[0])
                    hint = Fretboard(
                        self.instrument.value.strings,
                        frets=max_fret,
                        size=Size(matrix=Mat2()),
                        position=Position(),
                        parent=self.hint,
                    )
                    hint.highlight_fret(
                        string=self.instrument.value.strings.index(
                            exercise.string,
                        ),
                        fret=exercise.pitch.offset - exercise.string.offset,
                    )
                    self.content.append(hint)
            case Exercise.Type.STAVE_NOTE:
                help_text = Text(
                    "Play the following note:",
                    colour=Colours.FOREGROUND,
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(0.5, 1.0),
                            remote_anchor=Vec2(0.5, 1.0),
                        ),
                        offset=Vec2(0.0, -32.0),
                    ),
                    size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0))),
                    align="center",
                    parent=self,
                    font_size=32,
                )
                question = Stave(
                    clef=self.instrument.value.clef,
                    size=Size(matrix=Mat2()),
                    position=Position(offset=Vec2(0.0, -32.0)),
                    parent=(
                        self.question_hint if exercise.hint else self.question_no_hint
                    ),
                )

                if exercise.pitch.note.accidental == Accidental.FLAT:
                    mode = Note.Mode.FLATS
                else:
                    mode = Note.Mode.SHARPS
                pitch = Pitch.from_offset(
                    exercise.pitch.offset + self.instrument.value.transposition,
                    mode,
                )
                question.show_pitch(pitch)

                self.content.append(question)
                self.content.append(help_text)

                if exercise.pitch.note.name in [Name.A, Name.E, Name.F]:
                    determinant = "an"
                else:
                    determinant = "a"

                if exercise.hint:
                    hint = Label(
                        text=f"(It is {determinant} {exercise.pitch})",
                        colour=Colours.FOREGROUND,
                        position=Position(),
                        parent=self.hint,
                        font_size=64,
                    )
                    self.content.append(hint)

        self.rebuild()

    def on_new_offset(self, offset: int):
        if offset == self.lesson.exercises[self.exercise].pitch.offset:
            self.exercise += 1
            if self.exercise < len(self.lesson.exercises):
                self.dispatch_event("on_next_exercise", self.exercise)
                self.show()
            else:
                self.sound.remove_handlers(self)
                self.dispatch_event("on_finished")

    def on_close_button_pressed(self):
        self.sound.remove_handlers(self)
        self.dispatch_event("on_close")


LessonInterface.register_event_type("on_finished")
LessonInterface.register_event_type("on_next_exercise")
LessonInterface.register_event_type("on_close")
