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
    """The actual mid-lesson interface.

    Handles each individual exercise.
    """

    # Specific to the scales exercises
    scale_notes: list[tuple[int, int]] | None = None
    scale_notes_index: int | None = None
    scale_question: Text | None = None

    fretboard: Fretboard | None = None

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

        # We have different frames available for different possible layouts,
        # reducing code repetition later
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
        """Displays the current exercise."""
        # Reset from last exercise
        self.scale_question = None
        self.scale_notes = None
        self.scale_notes_index = None
        self.fretboard = None

        self.content.clear()
        exercise = self.lesson.exercises[self.exercise]

        self.question_number.text = f"{self.exercise + 1}/{len(self.lesson.exercises)}"
        match exercise.type:
            case Exercise.Type.NOTE_NAME:
                self.setup_note_name(exercise)
            case Exercise.Type.STAVE_NOTE:
                self.setup_stave(exercise)
            case Exercise.Type.SCALE:
                self.setup_scale(exercise)

        self.rebuild()

    def setup_note_name(self, exercise: Exercise):
        """Displays the note name exercise on the screen."""
        # Make sure we have the necessary exercise details
        assert exercise.string is not None
        assert exercise.pitch is not None

        question = Text(
            text=f"Play the following note on the {exercise.string} string: {exercise.pitch}",
            colour=Colours.FOREGROUND,
            size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0))),
            position=Position(),
            align="center",
            parent=(self.question_hint if exercise.hint else self.question_no_hint),
            font_size=48,
        )
        # Make sure we have the necessary exercise details
        self.content.append(question)
        if exercise.hint:
            # If it is a hinted exercise (teaching, NOT testing) then display
            # fretboard on the screen.
            max_fret = -1
            for fret in self.lesson.target_progress.string_progress:
                if fret[0] is not None:
                    max_fret = max(max_fret, fret[0])
            self.fretboard = Fretboard(
                self.instrument.value.strings,
                frets=max_fret,
                size=Size(matrix=Mat2()),
                position=Position(),
                parent=self.hint,
            )
            self.fretboard.highlight_fret(
                string=self.instrument.value.strings.index(
                    exercise.string,
                ),
                fret=exercise.pitch.offset - exercise.string.offset,
            )
            self.content.append(self.fretboard)

    def setup_stave(self, exercise: Exercise):
        """Displays the stave exercise on the screen."""
        # Ensure we have the necessary fields
        assert exercise.pitch is not None

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
            parent=(self.question_hint if exercise.hint else self.question_no_hint),
        )

        # Transpose the instrument's stave if applicable
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

        if exercise.hint:
            if exercise.pitch.note.name in [Name.A, Name.E, Name.F]:
                determinant = "an"
            else:
                determinant = "a"

            hint = Label(
                text=f"(It is {determinant} {exercise.pitch})",
                colour=Colours.FOREGROUND,
                position=Position(),
                parent=self.hint,
                font_size=64,
            )
            self.content.append(hint)

    def setup_scale(self, exercise: Exercise):
        """Displays a scale exercise on the screen."""
        # Ensure we have the necessary fields
        assert exercise.scale is not None
        assert exercise.starting_fret is not None

        # If exercise has not yet been started
        if self.scale_notes is None or self.scale_notes_index is None:
            # Initialise scale notes with scale's pitches with reversal
            trimmed = exercise.scale.shape.copy()[:-1]
            trimmed.reverse()
            self.scale_notes = exercise.scale.shape.copy() + trimmed
            self.scale_notes_index = 0

        self.scale_question = Text(
            text="",
            colour=Colours.FOREGROUND,
            size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0))),
            position=Position(),
            align="center",
            parent=(self.question_hint if exercise.hint else self.question_no_hint),
            font_size=48,
        )
        self.content.append(self.scale_question)

        if exercise.hint:
            self.fretboard = Fretboard(
                self.instrument.value.strings,
                frets=15,
                size=Size(matrix=Mat2()),
                position=Position(),
                parent=self.hint,
            )
            self.content.append(self.fretboard)

        self.update_scale()

    def update_scale(self):
        """Should be called when a note in the scale is played."""
        assert self.scale_question is not None
        assert self.scale_notes_index is not None
        assert self.scale_notes is not None

        exercise = self.lesson.exercises[self.exercise]
        assert exercise.scale is not None
        assert exercise.starting_fret is not None

        # Scale's starting pitch
        pitch = Pitch.from_offset(
            exercise.starting_fret + self.instrument.value.strings[0].offset,
            Note.Mode.SHARPS,
        )

        self.scale_question.text = f"""Play the {exercise.scale.name} scale starting on {pitch}.

{self.scale_notes_index} / {len(self.scale_notes)}"""

        if exercise.hint:
            # Update fretboard if applicable
            assert self.fretboard is not None

            # Highlight every note in the scale
            for i, (string, fret) in enumerate(exercise.scale.shape):
                fret = exercise.starting_fret + fret
                # Ensure playable, move down the strings until the fret is in
                # range:
                while fret < 0:
                    offset = self.instrument.value.strings[string].offset + fret
                    string -= 1
                    fret = offset - self.instrument.value.strings[string].offset

                # `i` is only from the initial scale, unreversed, so we need to
                # check against the reversed scale as well:
                is_highlighted = i in [
                    self.scale_notes_index,  # original
                    len(self.scale_notes) - self.scale_notes_index - 1,  # reversed
                ]

                self.fretboard.highlight_fret(
                    string,
                    fret,
                    (255, 0, 0, 255) if is_highlighted else (0, 0, 255, 255),
                )

    def on_new_offset(self, offset: int):
        """Update the exercise."""
        match self.lesson.exercises[self.exercise].type:
            case Exercise.Type.NOTE_NAME | Exercise.Type.STAVE_NOTE:
                # Check note is correct
                pitch = self.lesson.exercises[self.exercise].pitch
                if pitch is not None and offset == pitch.offset:
                    # Move onto the next exercise
                    self.exercise += 1
                    if self.exercise < len(self.lesson.exercises):
                        self.dispatch_event("on_next_exercise", self.exercise)
                        self.show()
                    else:
                        self.sound.remove_handlers(self)
                        self.dispatch_event("on_finished")
            case Exercise.Type.SCALE:
                assert self.scale_notes is not None
                assert self.scale_notes_index is not None

                starting_fret = self.lesson.exercises[self.exercise].starting_fret
                assert starting_fret is not None

                target_string, target_fret = self.scale_notes[self.scale_notes_index]
                target_offset = (
                    self.instrument.value.strings[target_string].offset
                    + target_fret
                    + starting_fret
                )
                if offset == target_offset:
                    # Check for next note in the scale
                    self.scale_notes_index += 1

                    if self.scale_notes_index == len(self.scale_notes):
                        # Next exercise
                        self.exercise += 1
                        if self.exercise < len(self.lesson.exercises):
                            self.dispatch_event(
                                "on_next_exercise",
                                self.exercise,
                            )
                            self.show()
                        else:
                            self.sound.remove_handlers(self)
                            self.dispatch_event("on_finished")
                    else:
                        self.update_scale()

    def on_close_button_pressed(self):
        """Forward close event to parent."""
        self.sound.remove_handlers(self)
        self.dispatch_event("on_close")


LessonInterface.register_event_type("on_finished")
LessonInterface.register_event_type("on_next_exercise")
LessonInterface.register_event_type("on_close")
