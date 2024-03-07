from dataclasses import dataclass
from enum import Enum, auto

from .note import Pitch, Note
from .instrument import Instrument
from .scale import Scale


@dataclass
class Exercise:
    """An individual exercise for a lesson.

    All exercises have a `type` and `hint` field.

    Also, for note name:
    - `pitch`
    - `string`

    For stave:
    - `pitch`

    For scale:
    - `scale`
    - `starting_fret`
    """

    class Type(Enum):
        """The type of exercise."""

        NOTE_NAME = auto()
        STAVE_NOTE = auto()
        SCALE = auto()

    type: Type
    hint: bool

    # Note to request (Note name or stave note only)
    pitch: Pitch | None = None

    # Note name only
    string: Pitch | None = None

    # Scale only
    scale: Scale | None = None
    starting_fret: int | None = None

    def __hash__(self) -> int:
        return hash(
            (
                self.type,
                self.hint,
                self.pitch,
                self.string,
                self.scale,
            )
        )

    @staticmethod
    def new_frets(
        last_note: int | None,
        target_note: int | None,
        string: Pitch,
        teaching: bool,
    ) -> "list[Exercise]":
        """Constructs a new list of exercises for a range of frets."""
        if target_note is None:
            return []

        # If testing or string is new, then quiz on all frets
        if last_note is None or not teaching:
            last_note = -1

        # Build range:
        # e.g. last_note = 5 and target_note = 9, then test 6-9
        notes = range(last_note + 1, target_note + 1)

        # Construct an exercise for every fret
        # We do this twice: once for sharps and once for flats.
        # After building the list, we convert to and from a set to remove
        # duplicates.
        to_add = list(
            set(
                [
                    Exercise(
                        type=Exercise.Type.NOTE_NAME,
                        hint=teaching,
                        pitch=Pitch.from_offset(
                            string.offset + i,
                            Note.Mode.SHARPS,
                        ),
                        string=string,
                    )
                    for i in notes
                ]
                + [
                    Exercise(
                        type=Exercise.Type.NOTE_NAME,
                        hint=teaching,
                        pitch=Pitch.from_offset(
                            string.offset + i,
                            Note.Mode.FLATS,
                        ),
                        string=string,
                    )
                    for i in notes
                ]
            )
        )

        # Repeat every exercise 3 times
        to_add *= 3

        return to_add

    @staticmethod
    def new_stave(
        last_note: int | None,
        aim: int | None,
        instrument: Instrument,
        teaching: bool = True,
    ) -> "list[Exercise]":
        """Constructs a new list of exercises for a range of stave notes."""
        if aim is None:
            return []

        # If testing or new to stave, then quiz on all notes
        if last_note is None or not teaching:
            last_note = -1

        # Build range
        notes = range(last_note + 1, aim + 1)

        # Construct an exercises for every stave note in the range
        # See `new_frets` for why we do this twice.
        to_add = list(
            set(
                [
                    Exercise(
                        type=Exercise.Type.STAVE_NOTE,
                        hint=teaching,
                        pitch=Pitch.from_offset(
                            i + instrument.value.lowest_pitch.offset,
                            Note.Mode.SHARPS,
                        ),
                    )
                    for i in notes
                ]
                + [
                    Exercise(
                        type=Exercise.Type.STAVE_NOTE,
                        hint=teaching,
                        pitch=Pitch.from_offset(
                            i + instrument.value.lowest_pitch.offset,
                            Note.Mode.FLATS,
                        ),
                    )
                    for i in notes
                ]
            )
        )

        # Repeat 3 times
        to_add *= 3

        return to_add

    @staticmethod
    def new_scale(scale: Scale, teaching: bool = True) -> "list[Exercise]":
        """Constructs a new list of exercises for a scale."""

        # One exercise per fret (up to fret 12)
        return [
            Exercise(
                type=Exercise.Type.SCALE,
                hint=teaching,
                scale=scale,
                starting_fret=i,
            )
            for i in range(12)
        ]
