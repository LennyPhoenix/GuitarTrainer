from dataclasses import dataclass
from enum import Enum, auto

from .note import Pitch


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
