from .sound_manager import SoundManager
from .storage_manager import StorageManager

from .note import (
    Pitch,
    Note,
    Name,
    Accidental,
    frequency_to_offset,
    frequency_to_offset_unrounded,
    offset_to_octave,
    offset_to_frequency,
)

GUITAR_STRINGS = [
    Pitch(Note(Name.E, Accidental.NATURAL), 2),
    Pitch(Note(Name.A, Accidental.NATURAL), 2),
    Pitch(Note(Name.D, Accidental.NATURAL), 3),
    Pitch(Note(Name.G, Accidental.NATURAL), 3),
    Pitch(Note(Name.B, Accidental.NATURAL), 3),
    Pitch(Note(Name.E, Accidental.NATURAL), 4),
]

BASS_STRINGS = [
    Pitch(Note(Name.E, Accidental.NATURAL), 1),
    Pitch(Note(Name.A, Accidental.NATURAL), 1),
    Pitch(Note(Name.D, Accidental.NATURAL), 2),
    Pitch(Note(Name.G, Accidental.NATURAL), 2),
]


__all__ = [
    "SoundManager",
    "StorageManager",
    "Pitch",
    "Note",
    "Name",
    "Accidental",
    "frequency_to_offset",
    "frequency_to_offset_unrounded",
    "offset_to_octave",
    "offset_to_frequency",
    "GUITAR_STRINGS",
    "BASS_STRINGS",
]
