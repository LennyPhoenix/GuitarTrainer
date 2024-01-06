from dataclasses import dataclass

from .exercise import Exercise
from .progress import Progress


@dataclass
class Lesson:
    """A lesson is a collection of exercises."""

    number: int
    exercises: list[Exercise]
    target_progress: Progress
