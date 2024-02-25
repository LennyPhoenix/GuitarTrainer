from dataclasses import dataclass


# String, Fret Offset
# Define up to 6 strings
ScaleShape = list[tuple[int, int]]


@dataclass
class Scale:
    name: str
    shape: ScaleShape

    def __hash__(self) -> int:
        return hash(self.name)
