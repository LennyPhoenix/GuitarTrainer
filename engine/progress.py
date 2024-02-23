from dataclasses import dataclass
from copy import deepcopy

from .instrument import Instrument


def test_user(target: "Progress", current: "Progress"):
    """Adjusts the target progress to test the user on knowledge from the
    current progress.

    **Mutates target.**
    """
    for i, progress in enumerate(current.string_progress):
        if progress[0] is not None:
            if progress[1] is None or progress[0] > progress[1]:
                target.string_progress[i] = (progress[0], progress[0])
    if current.highest_note[0] is not None:
        if (
            current.highest_note[1] is None
            or current.highest_note[0] > current.highest_note[1]
        ):
            target.highest_note = (
                current.highest_note[0],
                current.highest_note[0],
            )
    for scale, progress in current.scales.items():
        if progress is not None and progress[0] and not progress[1]:
            target.scales[scale] = (progress[0], progress[0])


def teach_stave(
    target: "Progress", current: "Progress", instrument: Instrument
) -> bool:
    """Adds new notes on the stave to teach the user, returns True if any
    new notes are being taught.
    """
    highest_note_offset = -1
    for i, progress in enumerate(current.string_progress):
        if progress[1] is not None:
            highest_note_offset = max(
                highest_note_offset,
                progress[1]
                + instrument.value.strings[i].offset
                - instrument.value.lowest_pitch.offset,
            )
    if highest_note_offset != -1:
        if (
            current.highest_note[0] is None
            or current.highest_note[0] < highest_note_offset
        ):
            target.highest_note = (highest_note_offset, None)
            return True

    return False


def teach_frets(target: "Progress", current: "Progress") -> bool:
    """Adds new frets to be taught to the user, returns True if any new notes
    are being taught.
    """
    fret_target = 5
    while fret_target < 24:
        for i, progress in enumerate(current.string_progress):
            if i == 0:
                prev_string_learnt = True
            else:
                prev_progress = current.string_progress[i - 1][1]
                prev_string_learnt = (
                    prev_progress is not None and prev_progress >= fret_target
                )

            if not prev_string_learnt:
                return False

            if progress[0] is None or progress[0] < fret_target:
                target.string_progress[i] = (fret_target, None)
                return True
        fret_target += 2
    return False


def teach_scales(target: "Progress", current: "Progress") -> bool:
    """Adds new scales to be taught to the user, returns True if any new scales
    are being taught.
    """
    top_string = current.string_progress[-1][1]
    if top_string is not None and top_string >= 12:
        for scale, progress in current.scales.items():
            if progress is None or not progress[0]:
                target.scales[scale] = (True, False)
                return True
    return False


@dataclass
class Progress:
    string_progress: list[tuple[int | None, int | None]]
    highest_note: tuple[int | None, int | None]
    scales: dict[str, tuple[bool, bool] | None]

    @staticmethod
    def next_target(
        current: "Progress",
        instrument: Instrument,
    ) -> "Progress":
        """Determines the next progress to aim for based on the last, or
        current level of, progress.
        """
        target = deepcopy(current)

        test_user(target, current)

        new_topic = teach_stave(target, current, instrument)

        if not new_topic:
            new_topic = teach_frets(target, current)

        if not new_topic:
            new_topic = teach_scales(target, current)

        return target
