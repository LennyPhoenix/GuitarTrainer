from operator import pos
from engine import Pitch

from framework import Frame, Size, Position, Pin, Vec2, Mat2
from framework.components import Rectangle

from .style import Colours


class Fretboard(Frame):
    FRET_MIN_WIDTH = 32.0
    FRET_MAX_WIDTH = 64.0
    STRING_MIN_HEIGHT = 32.0
    STRING_MAX_HEIGHT = 64.0

    def __init__(
        self,
        strings: list[Pitch],
        frets: int,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        self.highlights = []
        self.string_pitches = strings
        self.fret_count = frets

        super().__init__(size, position, parent, behind_parent)

        self.container = Frame(
            size=Size(
                matrix=Mat2((0.9, 0.0, 0.0, 0.9)),
                min=Vec2(
                    self.FRET_MIN_WIDTH * frets,
                    self.STRING_MIN_HEIGHT * len(strings),
                ),
                max=Vec2(
                    self.FRET_MAX_WIDTH * frets,
                    self.STRING_MAX_HEIGHT * len(strings),
                ),
            ),
            position=Position(pin=Pin.centre()),
            parent=self,
        )

        self.highlights_container = Frame(
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self.container,
        )

        self.strings = list(
            map(
                lambda x: Rectangle(
                    colour=Colours.FOREGROUND,
                    size=Size(
                        matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                        constant=Vec2(0.0, 6.0),
                    ),
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(0.0, x),
                            remote_anchor=Vec2(0.0, x),
                        )
                    ),
                    parent=self.container,
                ),
                map(lambda i: i / (len(strings) - 1), range(len(strings))),
            )
        )
        self.frets = list(
            map(
                lambda x: Rectangle(
                    colour=Colours.FOREGROUND,
                    size=Size(
                        matrix=Mat2((0.0, 0.0, 0.0, 1.0)),
                        constant=Vec2(2.0, 0.0),
                    ),
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(x, 0.5),
                            remote_anchor=Vec2(x, 0.5),
                        )
                    ),
                    parent=self.container,
                ),
                map(
                    lambda i: i / frets,
                    range(frets + 1),
                ),
            )
        )

        self.dotted_frets = list(
            map(
                lambda x: Rectangle(
                    colour=Colours.FOREGROUND,
                    size=Size(
                        matrix=Mat2((0.0, 0.0, 0.0, 1.0)),
                        constant=Vec2(4.0, 0.0),
                    ),
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(x, 0.5),
                            remote_anchor=Vec2(x, 0.5),
                        ),
                    ),
                    parent=self.container,
                ),
                map(
                    lambda i: i / frets,
                    filter(
                        lambda i: i % 12 in [0, 3, 5, 7, 9],
                        range(frets + 1),
                    ),
                ),
            )
        )

        self.double_dotted_frets = list(
            map(
                lambda x: Rectangle(
                    colour=(128, 128, 128, 255),
                    size=Size(
                        matrix=Mat2((1 / frets, 0.0, 0.0, 1.0)),
                    ),
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(1.0, 0.5),
                            remote_anchor=Vec2(x, 0.5),
                        )
                    ),
                    parent=self.container,
                    behind_parent=True,
                ),
                map(
                    lambda i: i / frets,
                    filter(
                        lambda i: i % 12 == 0,
                        range(frets + 1),
                    ),
                ),
            )
        )

    def clear_highlight(self):
        for highlight in self.highlights:
            highlight.parent = None
        self.highlights.clear()

    def highlight_pitch(
        self,
        pitch: Pitch,
        colour: tuple[int, int, int, int] = (255, 0, 0, 255),
    ):
        offset = pitch.offset
        for i, string in enumerate(self.string_pitches):
            string_offset = string.offset
            difference = offset - string_offset
            if 0 <= difference <= self.fret_count:
                x_pos = difference / self.fret_count
                y_pos = i / (len(self.string_pitches) - 1)
                self.highlights.append(
                    Rectangle(
                        colour=colour,
                        size=Size(constant=Vec2(32, 32)),
                        position=Position(
                            pin=Pin(
                                local_anchor=Vec2(0.5, 0.5),
                                remote_anchor=Vec2(x_pos, y_pos),
                            )
                        ),
                        parent=self.highlights_container,
                    )
                )

    def highlight_octaves(self, pitch: Pitch):
        for i in range(0, 8):
            if i != pitch.octave:
                self.highlight_pitch(
                    Pitch(pitch.note, i),
                    colour=(0, 0, 255, 255),
                )
