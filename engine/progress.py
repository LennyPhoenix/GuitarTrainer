from dataclasses import dataclass


@dataclass
class Progress:
    string_progress: list[tuple[int | None, int | None]]
    highest_note: tuple[int | None, int | None]
    scales: dict[str, tuple[bool, bool] | None]
