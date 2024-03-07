from framework import Frame, Size, Position, Pin, Vec2, Mat2
from framework.components import Label, Rectangle, Text

from engine import (
    Instrument,
    SoundManager,
    StorageManager,
    frequency_to_offset,
    Pitch,
    offset_to_frequency,
    frequency_to_offset_unrounded,
)

from interface import BorderedRectangle, Dropdown
from interface.style import Colours, Sizing

from pyglet.window import Window


class Tuner(BorderedRectangle):
    """The instrument tuner page.

    Builds a string list from the instrument and displays the nearest note
    from the currently detected frequency, alongside the distance from that
    note.
    """

    def __init__(
        self,
        window: Window,
        sound_manager: SoundManager,
        storage_manager: StorageManager,
        parent: Frame | None,
    ):
        super().__init__(
            size=Size(
                matrix=Mat2(),
                constant=-Vec2(1.0, 1.0) * 2 * Sizing.CONTENT_PADDING,
            ),
            position=Position(),
            parent=parent,
        )
        sound_manager.push_handlers(self)

        self.storage_manager = storage_manager

        self.dropdown = Dropdown(
            default=self.storage_manager.default_instrument.value.name,
            window=window,
            size=Size(
                constant=Vec2(256, 64),
            ),
            position=Position(
                pin=Pin.top_left(),
                offset=Vec2(18.0, -18.0),
            ),
            parent=self,
            elements=lambda: [i.value.name for i in Instrument],
        )
        self.dropdown.set_handler("on_picked", self.on_dropdown_picked)

        self.guide = Text(
            """Standard tuning, low to high:""",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(1.0, 0.5),
                    remote_anchor=Vec2(1.0, 0.5),
                ),
            ),
            size=Size(matrix=Mat2((0.3, 0.0, 0.0, 0.0))),
            parent=self,
            font_size=18,
        )
        self.rebuild_guide(self.storage_manager.default_instrument.value.strings)

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

        self.expected_frequency_label = Label(
            "Target: 0Hz",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    remote_anchor=Vec2(0.5, 0.0),
                    local_anchor=Vec2(0.5, 0.0),
                ),
                offset=Vec2(0.0, 20.0),
            ),
            font_size=20,
            parent=self,
        )
        self.actual_frequency_label = Label(
            "0Hz",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(remote_anchor=Vec2(0.5, 1.0), local_anchor=Vec2(0.5, 0.0)),
                offset=Vec2(0.0, 20.0),
            ),
            font_size=20,
            parent=self.expected_frequency_label,
        )

        self.range = Rectangle(
            colour=Colours.FOREGROUND,
            size=Size(
                matrix=Mat2((0.6, 0.0, 0.0, 0.0)),
                constant=Vec2(0.0, 8.0),
            ),
            position=Position(
                pin=Pin(local_anchor=Vec2(0.5, 0.5), remote_anchor=Vec2(0.35, 0.5))
            ),
            parent=self,
        )
        self.edges = [
            Rectangle(
                colour=Colours.FOREGROUND,
                size=Size(
                    constant=Vec2(8.0, 48.0),
                ),
                position=Position(
                    pin=Pin(
                        remote_anchor=Vec2(0.0, 0.5),
                        local_anchor=Vec2(0.5, 0.5),
                    )
                ),
                parent=self.range,
            ),
            Rectangle(
                colour=Colours.FOREGROUND,
                size=Size(
                    constant=Vec2(8.0, 48.0),
                ),
                position=Position(
                    pin=Pin(
                        remote_anchor=Vec2(1.0, 0.5),
                        local_anchor=Vec2(0.5, 0.5),
                    )
                ),
                parent=self.range,
            ),
        ]
        self.centre = Rectangle(
            colour=Colours.FOREGROUND,
            size=Size(
                constant=Vec2(8.0, 32.0),
            ),
            position=Position(pin=Pin.centre()),
            parent=self.range,
        )

        self.indicator = Rectangle(
            colour=(255, 0, 0, 0),
            size=Size(
                constant=Vec2(12.0, 48.0),
            ),
            position=Position(pin=Pin.centre()),
            parent=self.range,
        )

    def on_dropdown_picked(self, option: str):
        """Called when the target instrument is updated."""
        match option:
            case Instrument.GUITAR.value.name:
                self.rebuild_guide(Instrument.GUITAR.value.strings)
            case Instrument.BASS.value.name:
                self.rebuild_guide(Instrument.BASS.value.strings)

    def rebuild_guide(self, strings: list[Pitch]):
        """Rebuilds the guide to show the strings for the selected pitches."""
        self.guide.text = "Standard tuning, low to high:"
        for i, string in enumerate(strings):
            self.guide.text += f"\n{i + 1}: {string}"

    def on_frequency_change(self, frequency: float | None):
        """Updates the tuner to the latest frequency."""

        if frequency is None:
            # Reset if silent
            self.note_label.text = "Note: N/A"
            self.actual_frequency_label.text = "0Hz"
            self.expected_frequency_label.text = "Target: 0Hz"
            self.indicator.colour = (255, 0, 0, 0)
            return

        # Get closest note and difference from target
        offset = frequency_to_offset(frequency)
        difference = frequency_to_offset_unrounded(frequency) - offset
        pitch = Pitch.from_offset(offset, self.storage_manager.tuner_accidentals)

        # Update visuals
        anchor = difference + 0.5

        self.note_label.text = f"Note: {pitch}"
        self.actual_frequency_label.text = f"{frequency:.2f}Hz"
        self.expected_frequency_label.text = (
            f"Target: {offset_to_frequency(offset):.2f}Hz"
        )

        self.indicator.colour = (255, 0, 0, 255)
        self.indicator.position.pin = Pin(
            local_anchor=Vec2(anchor, 0.5), remote_anchor=Vec2(anchor, 0.5)
        )
