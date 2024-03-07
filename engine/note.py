"""Definitions for the Note and Pitch classes, which represent a musical note
and pitch, respectively.

Also provides some handy functions for processing pitches.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Self

import numpy as np


class Name(Enum):
    """A note name, A through G.

    The value of each note corresponds to its offset from A.
    """

    # Standard pitch is centered around A, but the octave increments on C. This
    # is why the values here look a little odd.
    C = -9
    D = -7
    E = -5
    F = -4
    G = -2
    A = 0
    B = 2

    def __str__(self):
        return self.name


class Accidental(Enum):
    """A note's accidental.

    The value of each accidental corresponds to the semitone offset it adds.
    """

    DOUBLE_FLAT = -2
    FLAT = -1
    NATURAL = 0
    SHARP = 1
    DOUBLE_SHARP = 2

    def __str__(self) -> str:
        # Convert to renderable symbols
        match self:
            case Accidental.DOUBLE_FLAT:
                return "𝄫"
            case Accidental.FLAT:
                return "♭"
            case Accidental.NATURAL:
                return ""
            case Accidental.SHARP:
                return "♯"
            case Accidental.DOUBLE_SHARP:
                return "𝄪"


@dataclass
class Note:
    """A note is defined as a combination of a note name and an accidental.

    E.g. A natural, or B flat.
    """

    name: Name
    accidental: Accidental = Accidental.NATURAL

    class Mode(Enum):
        """Used when building a Note from a semitone offset, as each note could
        either be represented as a flat or sharp. We need some way to choose
        between them."""

        SHARPS = auto()
        FLATS = auto()

    # Mapping of offsets to natural notes
    NATURALS = {
        0: (Name.A, Accidental.NATURAL),
        2: (Name.B, Accidental.NATURAL),
        3: (Name.C, Accidental.NATURAL),
        5: (Name.D, Accidental.NATURAL),
        7: (Name.E, Accidental.NATURAL),
        8: (Name.F, Accidental.NATURAL),
        10: (Name.G, Accidental.NATURAL),
    }

    # Mapping of offsets to unique sharps
    SHARPS = {
        1: (Name.A, Accidental.SHARP),
        4: (Name.C, Accidental.SHARP),
        6: (Name.D, Accidental.SHARP),
        9: (Name.F, Accidental.SHARP),
        11: (Name.G, Accidental.SHARP),
    }

    # Mapping of offsets to unique flats
    FLATS = {
        1: (Name.B, Accidental.FLAT),
        4: (Name.D, Accidental.FLAT),
        6: (Name.E, Accidental.FLAT),
        9: (Name.G, Accidental.FLAT),
        11: (Name.A, Accidental.FLAT),
    }

    def __str__(self) -> str:
        return f"{self.name}{self.accidental}"

    def __hash__(self) -> int:
        return hash((self.name, self.accidental))

    @property
    def offset(self) -> int:
        """The offset of this note from A."""
        return self.name.value + self.accidental.value

    @classmethod
    def from_offset(cls, offset: int, mode: Mode) -> Self:
        """Returns a Note given its semitone offset from A4."""
        note = offset % 12

        if note in cls.NATURALS.keys():
            return cls(*cls.NATURALS[note])

        match mode:
            case cls.Mode.SHARPS:
                return cls(*cls.SHARPS[note])
            case cls.Mode.FLATS:
                return cls(*cls.FLATS[note])


@dataclass
class Pitch:
    """A pitch is defined as a note with an octave, for example A sharp 4."""

    note: Note
    octave: int

    def __str__(self) -> str:
        return f"{self.note}{self.octave}"

    def __hash__(self) -> int:
        return hash((self.note, self.octave))

    @property
    def offset(self) -> int:
        """The offset of this pitch from A4."""
        return self.note.offset + (self.octave - 4) * 12

    @classmethod
    def from_offset(cls, offset: int, mode: Note.Mode) -> Self:
        """Returns a Pitch given its semitone offset from A4."""
        return cls(Note.from_offset(offset, mode), offset_to_octave(offset))


def frequency_to_offset(frequency: float) -> int:
    """Returns the nearest semitone offset of a note from A4, given the note's
    frequency."""
    return round(frequency_to_offset_unrounded(frequency))


def frequency_to_offset_unrounded(frequency: float) -> int:
    """Returns the semitone offset of a note from A4, given the note's
    frequency."""
    return 12 * np.log2(frequency / 440)


def offset_to_frequency(offset: int) -> float:
    """Returns the frequency of a note, given the note's offset from A4."""
    return 440 * 2 ** (offset / 12)


def offset_to_octave(offset: int) -> int:
    """Returns the octave of a note (C incremented) given its semitone offset
    from A4."""
    C_OFFSET = Name.C.value  # Octaves start at C, not A.
    return (offset - C_OFFSET) // 12 + 4  # Offset zero is octave 4.


class TestNotes:
    def test_frequency_to_offset(self):
        # Test octave As
        assert frequency_to_offset(440) == 0
        assert frequency_to_offset(880) == 12
        assert frequency_to_offset(220) == -12
        assert frequency_to_offset(110) == -24

        # Test other notes
        assert frequency_to_offset(987.77) == 14

        # Test rounding
        assert frequency_to_offset(350) == -4
        assert frequency_to_offset(1180) == 17

    def test_offset_to_octave(self):
        assert offset_to_octave(0) == 4
        assert offset_to_octave(12) == 5

        # Octave boundary (B4 -> C5)
        assert offset_to_octave(2) == 4
        assert offset_to_octave(3) == 5

    def test_offset_to_note(self):
        assert Note.from_offset(0, Note.Mode.SHARPS) == Note(Name.A)

        # Enharmonic Test
        assert Note.from_offset(1, Note.Mode.SHARPS) == Note(
            Name.A,
            Accidental.SHARP,
        )
        assert Note.from_offset(1, Note.Mode.FLATS) == Note(
            Name.B,
            Accidental.FLAT,
        )

        # Random tests
        assert Note.from_offset(-8, Note.Mode.SHARPS) == Note(
            Name.C,
            Accidental.SHARP,
        )
        assert Note.from_offset(6, Note.Mode.SHARPS) == Note(
            Name.D,
            Accidental.SHARP,
        )
        assert Note.from_offset(11, Note.Mode.SHARPS) == Note(
            Name.G,
            Accidental.SHARP,
        )
        assert Note.from_offset(11, Note.Mode.FLATS) == Note(
            Name.A,
            Accidental.FLAT,
        )

    def test_frequency_to_note(self):
        assert Pitch.from_offset(
            frequency_to_offset(440),
            Note.Mode.SHARPS,
        ) == Pitch(Note(Name.A), 4)

        # Enharmonic Test
        assert Pitch.from_offset(
            frequency_to_offset(466),
            Note.Mode.SHARPS,
        ) == Pitch(
            Note(
                Name.A,
                Accidental.SHARP,
            ),
            4,
        )
        assert Pitch.from_offset(
            frequency_to_offset(466),
            Note.Mode.FLATS,
        ) == Pitch(
            Note(
                Name.B,
                Accidental.FLAT,
            ),
            4,
        )
