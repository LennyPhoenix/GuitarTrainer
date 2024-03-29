from engine import Pitch

from framework import Frame, Size, Position, Pin, Vec2, Mat2
from framework.components import Rectangle

from .style import Colours


class Fretboard(Frame):
    """A visualisation of the fretboard on the screen.

    Works for any number of strings and frets.

    Allows individual frets or whole pitches to be highlighted.
    """

    FRET_MIN_WIDTH = 32.0
    FRET_MAX_WIDTH = 64.0
    STRING_MIN_HEIGHT = 32.0
    STRING_MAX_HEIGHT = 64.0

    highlights: dict[tuple[int, int], Rectangle]

    def __init__(
        self,
        strings: list[Pitch],
        frets: int,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        self.highlights = {}
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
                        constant=Vec2(8.0, 0.0),
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
                        matrix=Mat2((1 / (3 * frets), 0.0, 0.0, 1.0)),
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
        """Removes all highlighted frets."""
        self.highlights.clear()

    def highlight_fret(
        self,
        string: int,
        fret: int,
        colour: tuple[int, int, int, int] = (255, 0, 0, 255),
    ):
        """Highlights a given fret with a colour."""
        # Check position is available
        if 0 <= string < len(self.string_pitches) and 0 <= fret <= self.fret_count:
            # Convert to anchor
            x_pos = fret / self.fret_count
            y_pos = string / (len(self.string_pitches) - 1)
            if (string, fret) in self.highlights.keys():
                # Override old colour if already highlighted
                self.highlights[(string, fret)].colour = colour
            else:
                # Otherwise add a new highlight
                self.highlights[(string, fret)] = Rectangle(
                    colour=colour,
                    size=Size(constant=Vec2(32, 32)),
                    position=Position(
                        pin=Pin(
                            local_anchor=Vec2(0.75, 0.5),
                            remote_anchor=Vec2(x_pos, y_pos),
                        )
                    ),
                    parent=self.highlights_container,
                )

    def highlight_pitch(
        self,
        pitch: Pitch,
        colour: tuple[int, int, int, int] = (255, 0, 0, 255),
    ):
        """Highlights every instance of a pitch on the fretboard."""
        offset = pitch.offset
        for i, string in enumerate(self.string_pitches):
            string_offset = string.offset
            difference = offset - string_offset
            self.highlight_fret(i, difference, colour)

    def highlight_octaves(self, pitch: Pitch):
        """Highlights all octaves of a pitch on the fretboard."""
        # Try a range of octave 0 to 6, as no instruments are higher than this
        # right now
        for i in range(0, 6):
            if i != pitch.octave:
                self.highlight_pitch(
                    Pitch(pitch.note, i),
                    colour=(0, 0, 255, 255),
                )
