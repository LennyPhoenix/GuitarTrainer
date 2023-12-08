from pyglet.app import run
from pyglet.clock import schedule_once, unschedule
from pyglet.graphics import Batch
from pyglet.math import Vec2
from pyglet.window import Window
from framework import Frame, Size, Pin, Position
from framework.components import Rectangle, Container
from framework.mat2 import Mat2
from interface import MenuBar, SettingsPage
from interface.style import Colours, Sizing


class Root(Frame):
    def __init__(self):
        self.window = Window(resizable=True)
        self.window.push_handlers(self)
        self.batch = Batch()

        super().__init__(
            Size(constant=Vec2(self.window.width, self.window.height)),
            Position(pin=Pin.bottom_left()),
            None,
        )

        self.fill = Rectangle(
            colour=Colours.BACKGROUND,
            batch=self.batch,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
            behind_parent=True,
        )

        self.menu = MenuBar(self.batch, self, self.window)

        self.content_container = Container(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(0.0, -Sizing.TOP_BAR),
            ),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

        self.settings = SettingsPage(
            batch=self.batch,
            parent=self.content_container,
        )

        self.reindex_tree()

    def resize(self, _: float, width, height):
        self.size.constant = Vec2(width, height)

    def on_resize(self, width, height):
        unschedule(self.resize)
        schedule_once(self.resize, 1 / 10, width, height)

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def run(self):
        run()


class Stave(Frame):
    def __init__(
        self,
        batch: Batch,
        size: Size,
        position: Position,
        parent: Frame | None,
        behind_parent: bool = False,
        num_rows: int = 4,
    ):
        super().__init__(size, position, parent, behind_parent)
        self.left = Rectangle(
            colour=(255, 255, 255, 255),
            batch=batch,
            size=Size(matrix=Mat2((0, 0, 0, 1)), constant=Vec2(5, 0)),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

        self.rows = [
            Rectangle(
                colour=(255, 255, 255, 255),
                batch=batch,
                size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
                          constant=Vec2(0.0, 5.0)),
                position=Position(
                    pin=Pin(
                        local_anchor=Vec2(0.0, i / num_rows),
                        remote_anchor=Vec2(0.0, i / num_rows),
                    )
                ),
                parent=self,
            )
            for i in range(num_rows + 1)
        ]


if __name__ == "__main__":
    app = Root()
    app.run()
