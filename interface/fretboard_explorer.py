from pyglet.window import Window
from engine import GUITAR_STRINGS, BASS_STRINGS, frequency_to_offset, Pitch, Note

from framework import Frame, Size, Pin, Position, Mat2, Vec2
from framework.components import Label, Text

from engine import SoundManager

from .fretboard import Fretboard
from .dropdown import Dropdown
from .style import Colours
from .bordered_rect import BorderedRectangle


class FretboardExplorer(BorderedRectangle):
    shown_pitch: Pitch | None = None
    last_pitch: Pitch | None = None
    last_pitch_count: int = 0

    def __init__(
        self,
        window: Window,
        sound_manager: SoundManager,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        super().__init__(size, position, parent, behind_parent)

        sound_manager.push_handlers(self)

        self.dropdown = Dropdown(
            default="Guitar",
            window=window,
            size=Size(
                constant=Vec2(256, 64),
            ),
            position=Position(
                pin=Pin.top_left(),
                offset=Vec2(18.0, -18.0),
            ),
            parent=self,
            elements=lambda: ["Guitar", "Bass"],
        )
        self.dropdown.set_handler("on_picked", self.on_dropdown_picked)

        self.help_label = Text(
            """Play a note to see it on the fretboard:
Red - Enharmonic
Blue - Octave""",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin.top_right(),
                offset=Vec2(-18.0, -18.0),
            ),
            size=Size(
                constant=Vec2(256, 0.0),
            ),
            parent=self,
            font_size=16,
        )

        self.note_label = Label(
            "Note: N/A",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    remote_anchor=Vec2(0.5, 1.0),
                    local_anchor=Vec2(0.5, 1.0),
                ),
                offset=Vec2(0.0, -18.0),
            ),
            parent=self,
            font_size=32,
        )

        self.construct_fretboard(GUITAR_STRINGS)

    def construct_fretboard(self, strings: list[Pitch]):
        self.fretboard = Fretboard(
            strings=strings,
            frets=24,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                constant=Vec2(0.0, -64.0),
            ),
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 0.0),
                    remote_anchor=Vec2(0.5, 0.0),
                )
            ),
            parent=self,
        )

    def on_dropdown_picked(self, option: str):
        match option:
            case "Guitar":
                self.construct_fretboard(GUITAR_STRINGS)
            case "Bass":
                self.construct_fretboard(BASS_STRINGS)

    def on_frequency_change(self, frequency: float | None):
        # Convert frequency to pitch
        if frequency is not None:
            offset = frequency_to_offset(frequency)
            pitch = Pitch.from_offset(offset, Note.Mode.SHARPS)
        else:
            pitch = None

        # Increment counter if pitch is the same as last pitch
        if pitch == self.last_pitch:
            self.last_pitch_count += 1
        # Reset counter id pitch is different from last pitch
        else:
            self.last_pitch = pitch
            self.last_pitch_count = 0

        # Only update the fretboard if the pitch has been the same for 3
        # frames, and is different from the currently shown pitch.
        if self.last_pitch_count >= 3 and self.last_pitch != self.shown_pitch:
            self.shown_pitch = self.last_pitch

            self.fretboard.clear_highlight()
            if self.shown_pitch is None:
                self.note_label.text = "Note: N/A"
                return

            self.note_label.text = f"Note: {self.shown_pitch}"

            self.fretboard.highlight_pitch(self.shown_pitch)
            self.fretboard.highlight_octaves(self.shown_pitch)
            self.rebuild()
