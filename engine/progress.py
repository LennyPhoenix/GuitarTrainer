from dataclasses import dataclass
from copy import deepcopy

from .instrument import Instrument


def test_user(target: "Progress", current: "Progress"):
    """Adjusts the target progress to test the user on knowledge from the
    current progress.

    **Mutates target.**
    """
    # Find any unmemorised strings
    for i, progress in enumerate(current.string_progress):
        if progress[0] is not None:
            if progress[1] is None or progress[0] > progress[1]:
                target.string_progress[i] = (progress[0], progress[0])

    # Find unmemorised stave notes
    if current.highest_note[0] is not None:
        if (
            current.highest_note[1] is None
            or current.highest_note[0] > current.highest_note[1]
        ):
            target.highest_note = (
                current.highest_note[0],
                current.highest_note[0],
            )

    # Find unmemorised scales
    for scale, progress in current.scales.items():
        if progress is not None and progress[0] and not progress[1]:
            target.scales[scale] = (progress[0], progress[0])


def teach_stave(
    target: "Progress", current: "Progress", instrument: Instrument
) -> bool:
    """Adds new notes on the stave to teach the user, returns True if any
    new notes are being taught.

    **Mutates target.**
    """

    # Find highest learnt note name on strings
    highest_note_offset = -1
    for i, progress in enumerate(current.string_progress):
        if progress[1] is not None:
            highest_note_offset = max(
                highest_note_offset,
                progress[1]
                + instrument.value.strings[i].offset
                - instrument.value.lowest_pitch.offset,
            )

    # If learnt any note names
    if highest_note_offset != -1:
        if (
            current.highest_note[0] is None
            or current.highest_note[0] < highest_note_offset
        ):
            # Teach all learnt frets on the stave
            target.highest_note = (highest_note_offset, None)
            return True

    return False


def teach_frets(target: "Progress", current: "Progress") -> bool:
    """Adds new frets to be taught to the user, returns True if any new notes
    are being taught.

    **Mutates target.**
    """

    # Start by teaching the first 5 frets on every string
    fret_target = 5
    # Only teach up to fret 24
    while fret_target < 24:
        for i, progress in enumerate(current.string_progress):
            if i == 0:
                # The first string's previous string does not exist, so treat
                # it like we've memorised it
                prev_string_learnt = True
            else:
                # Check if the previous string has been memorised up to the
                # fret target
                prev_progress = current.string_progress[i - 1][1]
                prev_string_learnt = (
                    prev_progress is not None and prev_progress >= fret_target
                )

            # Quit early if the previous string has not been memorised
            if not prev_string_learnt:
                return False

            # Teach this string up to the fret target if it has not yet been
            # taught
            if progress[0] is None or progress[0] < fret_target:
                target.string_progress[i] = (fret_target, None)
                return True
        # All strings are already learnt at this target, try a higher target
        fret_target += 2
    return False


def teach_scales(target: "Progress", current: "Progress") -> bool:
    """Adds new scales to be taught to the user, returns True if any new scales
    are being taught.

    **Mutates target.**
    """
    # Check whether all strings have been memorised up to fret 12
    strings_learnt = all(
        map(lambda p: p[1] is not None and p[1] >= 12, current.string_progress)
    )
    if strings_learnt:
        # Find the next untaught scale and attempt to teach it
        for scale, progress in current.scales.items():
            if not progress[0]:
                target.scales[scale] = (True, False)
                return True
    return False


@dataclass
class Progress:
    string_progress: list[tuple[int | None, int | None]]
    highest_note: tuple[int | None, int | None]
    scales: dict[str, tuple[bool, bool]]

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
