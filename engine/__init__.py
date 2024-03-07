"""The engine is responsible for determining the user's pitch, alongside
building lessons and exercises.

The `SoundManager` is where all the pitch tracking code resides, with the
`note` module containing most of the scientific pitch notation logic/maths.

User data is managed entirely by the `StorageManager`, which attempts to
provide a seamless interface with the filesystem, meaning data in RAM and the
filesystem should never fall out of sync.

`Instrument` and `Clef` are designed to be very easily extensible.

`Progress`, `Lesson`, and `Exercise` handle all of the logic behind giving
lessons to the user and tracking their knowledge. This is also fairly
extensible in theory, but more work must be done to streamline the process of
adding new knowledge goals.
"""

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

from .clef import Clef
from .instrument import Instrument

from .progress import Progress
from .lesson import Lesson
from .exercise import Exercise

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
    "Clef",
    "Instrument",
    "Progress",
    "Lesson",
    "Exercise",
]
