from dataclasses import dataclass
from enum import Enum

from .note import Pitch, Note, Name
from .clef import Clef
from .scale import Scale


@dataclass
class InstrumentData:
    """The data that defines each unique instrument."""

    # Pretty printed name
    name: str
    # Open pitch for each string, low to high
    strings: list[Pitch]
    # Clef used in the stave
    clef: Clef
    # Lowest pitch that can be played
    lowest_pitch: Pitch
    # All defined scales for the instrument
    scales: list[Scale]
    # How much to transpose the instrument's stave by
    transposition: int = 0


class Instrument(Enum):
    """Each available instrument and their corresponding definitions."""

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
        scales=[
            Scale(
                "Major",
                [
                    (0, 0),
                    (0, 2),
                    (1, -1),
                    (1, 0),
                    (1, 2),
                    (2, -1),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 1),
                    (3, 2),
                    (4, 0),
                    (4, 2),
                    (5, -1),
                    (5, 0),
                ],
            ),
            Scale(
                "Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (1, 3),
                    (2, 0),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                    (4, 0),
                    (4, 1),
                    (4, 3),
                    (5, 0),
                ],
            ),
            Scale(
                "Melodic Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (2, -1),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                    (4, 0),
                    (4, 2),
                    (5, -1),
                    (5, 0),
                ],
            ),
            Scale(
                "Harmonic Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (1, 3),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                    (4, 0),
                    (4, 1),
                    (5, -1),
                    (5, 0),
                ],
            ),
            Scale(
                "Pentatonic Major",
                [
                    (0, 0),
                    (0, 2),
                    (1, -1),
                    (1, 2),
                    (2, -1),
                    (2, 2),
                    (3, -1),
                    (3, 1),
                    (4, 0),
                    (4, 2),
                    (5, 0),
                ],
            ),
            Scale(
                "Pentatonic Minor",
                [
                    (0, 0),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (2, 0),
                    (2, 2),
                    (3, 0),
                    (3, 2),
                    (4, 0),
                    (4, 3),
                    (5, 0),
                ],
            ),
            Scale(
                "Blues",
                [
                    (0, 0),
                    (0, 3),
                    (1, 0),
                    (1, 1),
                    (1, 2),
                    (2, 0),
                    (2, 2),
                    (3, 0),
                    (3, 2),
                    (3, 3),
                    (4, 0),
                    (4, 3),
                    (5, 0),
                ],
            ),
        ],
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
        scales=[
            Scale(
                "Major",
                [
                    (0, 0),
                    (0, 2),
                    (1, -1),
                    (1, 0),
                    (1, 2),
                    (2, -1),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 1),
                    (3, 2),
                ],
            ),
            Scale(
                "Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (1, 3),
                    (2, 0),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                ],
            ),
            Scale(
                "Melodic Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (2, -1),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                ],
            ),
            Scale(
                "Harmonic Minor",
                [
                    (0, 0),
                    (0, 2),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (1, 3),
                    (2, 1),
                    (2, 2),
                    (3, -1),
                    (3, 0),
                    (3, 2),
                ],
            ),
            Scale(
                "Pentatonic Major",
                [
                    (0, 0),
                    (0, 2),
                    (1, -1),
                    (1, 2),
                    (2, -1),
                    (2, 2),
                    (3, -1),
                    (3, 1),
                ],
            ),
            Scale(
                "Pentatonic Minor",
                [
                    (0, 0),
                    (0, 3),
                    (1, 0),
                    (1, 2),
                    (2, 0),
                    (2, 2),
                    (3, 0),
                    (3, 2),
                ],
            ),
        ],
        transposition=12,
    )
