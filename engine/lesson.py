from dataclasses import dataclass
from random import shuffle

from .exercise import Exercise
from .progress import Progress
from .instrument import Instrument


@dataclass
class Lesson:
    """A lesson is a collection of exercises alongside the intended progress
    once the lesson is complete.

    If the lesson is completed successfully, then this target progress has been
    achieved.
    """

    # The lesson index
    number: int
    # All exercises to be shown in the lesson
    exercises: list[Exercise]
    # Intended target progress
    target_progress: Progress

    @staticmethod
    def new_from_progress(
        index: int,
        last: Progress,
        target: Progress,
        instrument: Instrument,
    ) -> "Lesson":
        exercises = []

        # Fret exercises
        for string_index, string_target in enumerate(target.string_progress):
            string = instrument.value.strings[string_index]
            string_last = last.string_progress[string_index]

            # A string is to be taught
            # > Remember that [0] is whether it was taught, [1] is whether it
            # > was memorised.
            if string_target[0] != string_last[0]:
                exercises += Exercise.new_frets(
                    string_last[0],
                    string_target[0],
                    string,
                    teaching=True,
                )

            # A string is to be tested
            if string_target[1] != string_last[1]:
                exercises += Exercise.new_frets(
                    string_last[1],
                    string_target[1],
                    string,
                    teaching=False,
                )

        # Stave exercises
        if target.highest_note[0] != last.highest_note[0]:
            # A new note is to be taught
            exercises += Exercise.new_stave(
                last.highest_note[0],
                target.highest_note[0],
                instrument,
            )
        if target.highest_note[1] != last.highest_note[1]:
            # A new note is to be tested
            exercises += Exercise.new_stave(
                last.highest_note[1],
                target.highest_note[1],
                instrument,
                teaching=False,
            )

        for scale_name, target_progress in target.scales.items():
            # Find each actual scale by name
            # This next(filter(...), None) call is essentially a find(...) call
            scale = next(
                filter(
                    lambda scale: scale.name == scale_name,
                    instrument.value.scales,
                ),
                None,
            )
            if scale is None:
                # The scale is not available in the instrument
                print(
                    f"Scale {scale_name} found in save, but not in instrument.")
                continue

            last_progress = last.scales[scale_name]
            if target_progress is not None:
                # A new scale is to be taught
                if target_progress[0] and (
                    last_progress is None or not last_progress[0]
                ):
                    exercises += Exercise.new_scale(scale)

                # A new scale is to be tested
                if target_progress[1] and (
                    last_progress is None or not last_progress[1]
                ):
                    exercises += Exercise.new_scale(scale, teaching=False)

        # Shuffle lesson exercises, so we don't get the same order every time
        shuffle(exercises)

        return Lesson(
            number=index + 1,
            exercises=exercises,
            target_progress=target,
        )
