import gc

from pyglet.image import Texture
from pyglet.gl import GL_NEAREST
from pyglet.app import run
from pyglet.clock import schedule_once, unschedule
from pyglet.math import Vec2
from pyglet.window import Window
from pyglet import resource

from framework import Frame, Size, Pin, Position
from framework.components import Rectangle, Container
from framework.mat2 import Mat2

from interface import (
    MenuBar,
    SettingsPage,
    View,
    Tuner,
    FretboardExplorer,
    Lessons,
)
from interface.style import Colours, Sizing

from engine import SoundManager, StorageManager


# Set the default texture filter to nearest neighbour instead of
# bilinear interpolation, the textures in use are low-resolution and
# this helps to keep them looking sharp.
Texture.default_mag_filter = GL_NEAREST
Texture.default_min_filter = GL_NEAREST


class Root(Frame):
    """The base component that all other elements are children of.

    Also contains the Pyglet window, and sound and storage managers.
    """

    def __init__(self):
        # Load our music font
        resource.add_font("assets/NotoSans-RegularMusic.ttf")

        # Instantiate our storage and sound managers
        self.storage_manager = StorageManager()
        self.sound_manager = SoundManager()

        # If the user has selected an input device, try to connect to it
        if self.storage_manager.input_device is not None:
            try:
                self.sound_manager.connect(self.storage_manager.input_device)
            except ValueError:
                print("Audio device unavailable, go to settings.")

        # Instantiate our pyglet window
        self.window = Window(resizable=True)
        # Make sure to subscribe to window events
        self.window.push_handlers(self)

        # Initialise our root frame for the GUI, using the window's dimensions
        super().__init__(
            Size(constant=Vec2(self.window.width, self.window.height)),
            # This doesn't really matter as long as the remote and local
            # anchors are the same
            Position(pin=Pin.bottom_left()),
            parent=None,  # No parent, as this is the root frame
        )

        # Background colour for the window
        self.fill = Rectangle(
            colour=Colours.BACKGROUND,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        # Menu bar at the top of the window
        self.menu = MenuBar(self, self.window)
        self.menu.set_handler("on_view", self.on_view)

        # Container for the main content of the window.
        # Cuts off anything that extends into the top bar to avoid overlapping
        # UI elements.
        self.content_container = Container(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(0.0, -Sizing.TOP_BAR),
            ),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

        # Start off with the lessons view
        self.lessons = Lessons(
            parent=self.content_container,
            window=self.window,
            storage_manager=self.storage_manager,
            sound_manager=self.sound_manager,
        )

        # Assign rendering groups recursively to all children
        self.rebuild_groups()
        # Delete any orphaned frames
        gc.collect()

    def on_view(self, view: View):
        """Called when the user selects a new view from the menu bar."""

        # Show the settings page if that is the intended view...
        if view == View.SETTINGS:
            self.settings_page = SettingsPage(
                window=self.window,
                parent=self.content_container,
                sound_manager=self.sound_manager,
                storage_manager=self.storage_manager,
            )
        # ...otherwise, hide it.
        else:
            self.settings_page = None

        # Same for the tuner
        if view == View.TUNER:
            self.tuner = Tuner(
                window=self.window,
                sound_manager=self.sound_manager,
                storage_manager=self.storage_manager,
                parent=self.content_container,
            )
        else:
            self.tuner = None

        # And the fretboard explorer
        if view == View.FRETBOARD:
            self.fretboard = FretboardExplorer(
                window=self.window,
                sound_manager=self.sound_manager,
                storage_manager=self.storage_manager,
                parent=self.content_container,
            )
        else:
            self.fretboard = None

        # The lesson element is persistent as it stores the user's progress
        # mid-lesson, so we just show or hide it without deleting and
        # reinstantiating.
        if view == View.APP:
            self.lessons.show()
        else:
            self.lessons.hide()

        # Rebuild the UI to reflect the changes
        self.rebuild()

    def resize(self, _: float, width, height):
        """Called 1/10th of a second after the window was resized."""
        # Update the size of the root frame
        self.size.constant = Vec2(width, height)

    def on_resize(self, width, height):
        """Called every time the window's size changes."""
        # Schedule a resize event to occur after the window has finished
        # resizing to avoid unnecessary rebuilds (and lag).
        unschedule(self.resize)
        schedule_once(self.resize, 1 / 10, width, height)

    def on_draw(self):
        """Called every frame."""
        # Clears the window and redraws the UI recursively.
        self.window.clear()
        self.propagate_draw()

    def run(self):
        """Starts the event loop."""
        run()  # Pyglet's app.run()


if __name__ == "__main__":
    app = Root()
    app.run()
