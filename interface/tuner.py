from framework import Frame, Size, Position, Pin, Vec2, Mat2
from framework.components import Label, Rectangle, Text

from engine import (
    SoundManager,
    frequency_to_offset,
    Pitch,
    Note,
    offset_to_frequency,
    frequency_to_offset_unrounded,
)
from interface import BorderedRectangle
from interface.style import Colours


class Tuner(BorderedRectangle):
    def __init__(
        self,
        sound_manager: SoundManager,
        parent: Frame | None,
    ):
        super().__init__(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=parent,
        )
        sound_manager.push_handlers(self)

        self.guide = Text(
            # TODO: Generate based on current setting??? We have string
            # definitions in the engine
            """Standard tuning, low to high: (Bass)
1: E2 (E1)
2: A2 (A1)
3: D3 (D2)
4: G3 (G2)
5: B3
6: E4""",
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
                pin=Pin(remote_anchor=Vec2(0.5, 1.0),
                        local_anchor=Vec2(0.5, 0.0)),
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
                pin=Pin(local_anchor=Vec2(0.5, 0.5),
                        remote_anchor=Vec2(0.35, 0.5))
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

    def on_frequency_change(self, frequency: float | None):
        if frequency is None:
            self.note_label.text = "Note: N/A"
            self.actual_frequency_label.text = "0Hz"
            self.expected_frequency_label.text = "Target: 0Hz"
            self.indicator.colour = (255, 0, 0, 0)
            return

        offset = frequency_to_offset(frequency)
        difference = frequency_to_offset_unrounded(frequency) - offset
        pitch = Pitch.from_offset(offset, Note.Mode.SHARPS)

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
