from pyglet.window import Window
from engine import GUITAR_STRINGS, BASS_STRINGS, frequency_to_offset, Pitch, Note

from framework import Frame, Size, Pin, Position, Mat2, Vec2
from framework.components import Label

from engine import SoundManager

from .fretboard import Fretboard
from .dropdown import Dropdown
from .style import Colours
from .bordered_rect import BorderedRectangle


class FretboardExplorer(BorderedRectangle):
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
            ),
            position=Position(pin=Pin.centre()),
            parent=self,
        )

    def on_dropdown_picked(self, option: str):
        match option:
            case "Guitar":
                self.construct_fretboard(GUITAR_STRINGS)
            case "Bass":
                self.construct_fretboard(BASS_STRINGS)

    def on_frequency_change(self, frequency: float | None):
        self.fretboard.clear_highlight()
        if frequency is None:
            self.note_label.text = "Note: N/A"
            return

        offset = frequency_to_offset(frequency)
        pitch = Pitch.from_offset(offset, Note.Mode.SHARPS)
        self.note_label.text = f"Note: {pitch}"

        self.fretboard.highlight_pitch(pitch)
        self.fretboard.highlight_octaves(pitch)
