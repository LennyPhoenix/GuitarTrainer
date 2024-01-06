from dataclasses import dataclass
from enum import Enum

from .note import Pitch, Note, Name
from .clef import Clef


@dataclass
class InstrumentData:
    name: str
    strings: list[Pitch]
    clef: Clef
    lowest_pitch: Pitch
    transposition: int = 0


class Instrument(Enum):
    GUITAR = InstrumentData(
        name="Guitar",
        strings=[
            Pitch(Note(Name.E), 2),
            Pitch(Note(Name.A), 2),
            Pitch(Note(Name.D), 3),
            Pitch(Note(Name.G), 3),
            Pitch(Note(Name.B), 3),
            Pitch(Note(Name.E), 4),
        ],
        clef=Clef.BASS,
        lowest_pitch=Pitch(Note(Name.E), 2),
    )
    BASS = InstrumentData(
        name="Bass",
        strings=[
            Pitch(Note(Name.E), 1),
            Pitch(Note(Name.A), 1),
            Pitch(Note(Name.D), 2),
            Pitch(Note(Name.G), 2),
        ],
        clef=Clef.BASS,
        lowest_pitch=Pitch(Note(Name.E), 1),
        transposition=12,
    )
