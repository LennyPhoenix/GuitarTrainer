from .bordered_rect import BorderedRectangle
from .dropdown import Dropdown
from .style import Colours, Sizing

from framework import Frame, Mat2, Size, Position, Vec2, Pin
from framework.components import Label, Text

from pyglet.window import Window

from engine import SoundManager, StorageManager, Note, Instrument


class SettingsPage(BorderedRectangle):
    components: list[tuple[BorderedRectangle, Label, Frame]]

    def __init__(
        self,
        window: Window,
        parent: Frame | None,
        sound_manager: SoundManager,
        storage_manager: StorageManager,
    ):
        self.components = []

        self.sound_manager = sound_manager
        self.storage_manager = storage_manager

        super().__init__(
            size=Size(
                matrix=Mat2(),
                constant=-Vec2(1.0, 1.0) * 2 * Sizing.CONTENT_PADDING,
            ),
            position=Position(),
            parent=parent,
        )

        in_device = storage_manager.input_device
        if in_device is None or in_device not in sound_manager.get_available_devices():
            in_device = "Please select"
        input_device = Dropdown(
            default=in_device,
            elements=sound_manager.get_available_devices,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                constant=Vec2(-64.0, -64.0),
            ),
            position=Position(),
            parent=None,
            window=window,
        )
        input_device.set_handler("on_picked", self.on_input_device_assigned)
        self.add_setting(
            "Input Device",
            input_device,
        )

        tuner_accidentals = Dropdown(
            default=storage_manager.tuner_accidentals.name,
            elements=lambda: list(Note.Mode.__members__.keys()),
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                constant=Vec2(-64.0, -64.0),
            ),
            position=Position(),
            parent=None,
            window=window,
        )
        tuner_accidentals.set_handler("on_picked", self.on_tuner_accidentals_assigned)
        self.add_setting("Tuner Accidentals", tuner_accidentals)

        default_instrument = Dropdown(
            default=storage_manager.default_instrument.name,
            elements=lambda: list(Instrument.__members__.keys()),
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 1.0)),
                constant=Vec2(-64.0, -64.0),
            ),
            position=Position(),
            parent=None,
            window=window,
        )
        default_instrument.set_handler("on_picked", self.on_default_instrument_assigned)
        self.add_setting("Default Instrument", default_instrument)

        self.help_text = Text(
            """The pitch tracker likes harmonics, turn your tone knob up!
P.S. Make sure to turn the volume of your mic/audio interface all the way up!""",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 0.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
                offset=Vec2(0.0, 24.0),
            ),
            size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0))),
            parent=self,
            font_size=24,
            align="center",
        )

    def on_input_device_assigned(self, option: str):
        self.sound_manager.connect(option)
        self.storage_manager.input_device = option

    def on_tuner_accidentals_assigned(self, option: str):
        acc = Note.Mode[option]
        self.storage_manager.tuner_accidentals = acc

    def on_default_instrument_assigned(self, option: str):
        instrument = Instrument[option]
        self.storage_manager.default_instrument = instrument

    def add_setting(self, label: str, component: Frame):
        position: Position
        parent: Frame
        size_constant: Vec2
        behind_parent: bool
        if len(self.components) >= 1:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 0.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            size_constant = Vec2(0.0, 64.0)
            parent = self.components[-1][0]
            behind_parent = True
        else:
            position = Position(
                pin=Pin(
                    local_anchor=Vec2(0.5, 1.0),
                    remote_anchor=Vec2(0.5, 1.0),
                ),
                offset=Vec2(0.0, -20.0),
            )
            size_constant = Vec2(-64.0, 64.0)
            parent = self
            behind_parent = False

        container = BorderedRectangle(
            position=position,
            parent=parent,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                constant=size_constant,
            ),
            behind_parent=behind_parent,
        )

        comp_label = Label(
            text=f"{label}:",
            colour=Colours.FOREGROUND,
            position=Position(
                pin=Pin(
                    local_anchor=Vec2(1.0, 0.5),
                    remote_anchor=Vec2(0.2, 0.5),
                ),
                offset=Vec2(-24.0, 0.0),
            ),
            parent=container,
            font_size=18,
        )

        component.size = Size(
            matrix=Mat2((0.8, 0.0, 0.0, 1.0)), constant=Vec2(-36.0, -12.0)
        )
        component.position = Position(
            pin=Pin(
                local_anchor=Vec2(0.0, 0.5),
                remote_anchor=Vec2(0.2, 0.5),
            ),
            offset=Vec2(24.0, 0.0),
        )
        component.parent = container
        component.propagate_size()
        component.propagate_position()

        self.components.append((container, comp_label, component))
