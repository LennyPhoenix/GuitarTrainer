from engine import Pitch, Note, Name, Clef

from framework import Frame, Vec2, Size, Position
from framework.components import Label

from .style import Colours

SIZE = 128
NOTE_SPACE = 0.165


def note_position(note: Name) -> int:
    """Converts a note to a stave offset."""
    match note:
        case Name.C:
            return 0
        case Name.D:
            return 1
        case Name.E:
            return 2
        case Name.F:
            return 3
        case Name.G:
            return 4
        case Name.A:
            return 5
        case Name.B:
            return 6


class MusicSymbol(Label):
    """Helper class for drawing musical symbols to the screen."""

    def __init__(
        self,
        symbol: str,
        position: Position,
        parent: Frame | None,
    ):
        position.offset *= SIZE
        super().__init__(
            symbol,
            colour=Colours.FOREGROUND,
            position=position,
            parent=parent,
            font_size=SIZE,
        )


class Stave(Frame):
    """Draws a stave to the screen with a given clef and note."""

    def __init__(
        self,
        clef: Clef,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
    ):
        super().__init__(size, position, parent, behind_parent)

        # Builds a list of musical symbols to be drawn to the screen
        self.symbols = list(
            map(
                lambda s: MusicSymbol(
                    s[0],
                    position=Position(
                        offset=Vec2(s[1], 0.0),
                    ),
                    parent=self,
                ),
                # Symbol and position pair
                [
                    ("𝄃", -2),
                    ("𝄚", -1.5),
                    ("𝄚", -0.5),
                    ("𝄚", 0.5),
                    ("𝄚", 1.5),
                    ("𝄂", 2),
                ],
            )
        )

        match clef:
            # Treble and bass clef need different offsets and middle notes
            case Clef.TREBLE:
                self.middle_note = Pitch(Note(Name.B), 4)
                y = 0.0
            case Clef.BASS:
                self.middle_note = Pitch(Note(Name.D), 3)
                y = 0.125

        self.clef = MusicSymbol(
            clef.value,
            position=Position(offset=Vec2(-1.25, y)),
            parent=self,
        )

        self.note = MusicSymbol(
            "",
            position=Position(offset=Vec2(0, 0)),
            parent=self,
        )
        self.ledgers = []

    def show_pitch(self, pitch: Pitch | None):
        self.ledgers.clear()

        if pitch is None:
            self.note.text = ""
        else:
            # Render the note by offsetting from the middle note
            middle_note = note_position(self.middle_note.note.name)
            requested_note = note_position(pitch.note.name)
            difference = (middle_note - requested_note) + 7 * (
                self.middle_note.octave - pitch.octave
            )

            self.note.text = f"{pitch.note.accidental}𝅝"

            # Calculate the number of ledger lines required
            ledger_count = max(abs(difference) // 2 - 2, 0)
            ledger_direction = 1 if difference > 0 else -1

            # Render all required ledger lines
            for i in range(ledger_count):
                self.ledgers.append(
                    MusicSymbol(
                        "𝄖",
                        position=Position(
                            offset=Vec2(
                                0.5, -((i + 3) * ledger_direction * 2 * NOTE_SPACE)
                            )
                        ),
                        parent=self,
                    )
                )

            self.note.position.offset = Vec2(0.5, 0.5 - NOTE_SPACE * difference) * SIZE

        self.rebuild()
