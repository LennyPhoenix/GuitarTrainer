from dataclasses import dataclass
from enum import Enum, auto

from .note import Pitch, Note
from .instrument import Instrument


class Scale(Enum):
    MAJOR = auto()
    MINOR = auto()


@dataclass
class Exercise:
    class Type(Enum):
        NOTE_NAME = auto()
        STAVE_NOTE = auto()
        SCALE = auto()

    type: Type
    hint: bool

    # Either the actual note or the starting note of the scale
    pitch: Pitch

    # Note name only
    string: Pitch | None = None

    # Scale only
    scale: Scale | None = None

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


def fret_exercises(
    last_note: int | None,
    target_note: int | None,
    string: Pitch,
    teaching: bool,
) -> list[Exercise]:
    if target_note is None:
        return []

    if last_note is None or not teaching:
        last_note = -1

    notes = range(last_note + 1, target_note + 1)

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
    to_add *= 3
    return to_add


def stave_exercises(
    last_note: int | None,
    aim: int | None,
    instrument: Instrument,
    teaching: bool = True,
) -> list[Exercise]:
    if aim is None:
        return []

    if last_note is None or not teaching:
        last_note = -1

    notes = range(last_note + 1, aim + 1)
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
    to_add *= 3
    return to_add
