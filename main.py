import gc

from pyglet.app import run
from pyglet.clock import schedule_once, unschedule
from pyglet.math import Vec2
from pyglet.window import Window
from pyglet import resource

from framework import Frame, Size, Pin, Position
from framework.components import Rectangle, Container
from framework.mat2 import Mat2

from interface import MenuBar, SettingsPage, View, Tuner, FretboardExplorer, Stave, Clef
from interface.style import Colours, Sizing

from engine import SoundManager, StorageManager, Pitch, Note


class Root(Frame):
    def __init__(self):
        resource.add_font("assets/NotoSans-RegularMusic.ttf")

        self.storage_manager = StorageManager()

        self.sound_manager = SoundManager()
        if self.storage_manager.input_device is not None:
            try:
                self.sound_manager.connect(self.storage_manager.input_device)
            except ValueError:
                print("Audio device unavailable, go to settings.")

        self.window = Window(resizable=True)
        self.window.push_handlers(self)

        super().__init__(
            Size(constant=Vec2(self.window.width, self.window.height)),
            Position(pin=Pin.bottom_left()),
            None,
        )

        self.fill = Rectangle(
            colour=Colours.BACKGROUND,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        self.menu = MenuBar(self, self.window)
        self.menu.set_handler("on_view", self.on_view)

        self.content_container = Container(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(
                    -Sizing.CONTENT_PADDING * 2,
                    -(Sizing.CONTENT_PADDING * 2 + Sizing.TOP_BAR),
                ),
            ),
            position=Position(
                pin=Pin.centre(),
                offset=Vec2(0.0, -Sizing.TOP_BAR / 2),
            ),
            parent=self,
        )

        self.stave = Stave(
            clef=Clef.BASS,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self.content_container,
        )

        self.sound_manager.set_handler(
            "on_new_offset",
            lambda offset: self.stave.show_pitch(
                Pitch.from_offset(
                    offset,
                    Note.Mode.FLATS,
                )
                if offset is not None
                else None,
            ),
        )

        self.rebuild_groups()
        gc.collect()

    def on_view(self, view: View):
        if view == View.SETTINGS:
            self.settings_page = SettingsPage(
                window=self.window,
                parent=self.content_container,
                sound_manager=self.sound_manager,
                storage_manager=self.storage_manager,
            )
        else:
            self.settings_page = None

        if view == View.TUNER:
            self.tuner = Tuner(
                sound_manager=self.sound_manager,
                parent=self.content_container,
            )
        else:
            self.tuner = None

        if view == View.FRETBOARD:
            self.fretboard = FretboardExplorer(
                window=self.window,
                sound_manager=self.sound_manager,
                parent=self.content_container,
            )
        else:
            self.fretboard = None

        self.rebuild()

    def resize(self, _: float, width, height):
        self.size.constant = Vec2(width, height)

    def on_resize(self, width, height):
        unschedule(self.resize)
        schedule_once(self.resize, 1 / 10, width, height)

    def on_draw(self):
        self.window.clear()
        self.propagate_draw()

    def run(self):
        run()


if __name__ == "__main__":
    app = Root()
    app.run()
