from pyglet.app import run
from pyglet.clock import schedule_interval, schedule_once, unschedule
from pyglet.graphics import Batch
from pyglet.math import Vec2
from framework.components import Rectangle, Text, Container
from pyglet.window import key as kb
from framework import Frame, Size, Pin, Position

from pyglet.window import Window

from framework.mat2 import Mat2


class Root(Frame):
    def __init__(self):
        self.window = Window(resizable=True)
        self.window.push_handlers(self)
        self.batch = Batch()
        self.keys = kb.KeyStateHandler()
        self.window.push_handlers(self.keys)

        super().__init__(
            Size(constant=Vec2(self.window.width, self.window.height)),
            Position(pin=Pin.bottom_left()),
            None,
        )

        self.fill = Rectangle(
            color=(255, 255, 255, 255),
            batch=self.batch,
            size=Size(matrix=Mat2()),
            position=Position(),
            parent=self,
        )

        self.centrebox = Rectangle(
            color=(255, 100, 100, 255),
            batch=self.batch,
            size=Size(matrix=Mat2((0.5, 0, 0, 0.5))),
            position=Position(),
            parent=self.fill,
        )

        self.container = Container(
            size=Size(matrix=Mat2()), position=Position(), parent=self.centrebox
        )

        self.text = Text(
            text="Sample Text. " * 1000,
            batch=self.batch,
            color=(0, 0, 0, 255),
            size=Size(matrix=Mat2((1.0, 0, 0, 0.5)), constant=Vec2(-30, -30)),
            position=Position(pin=Pin.top_left(), offset=Vec2(15, -15)),
            parent=self.container,
        )

        self.reindex_tree()

        schedule_interval(self.update, 1/60)

    def update(self, dt: float):
        if self.keys[kb.UP]:
            self.text.position.offset += Vec2(0, 100) * dt
        if self.keys[kb.DOWN]:
            self.text.position.offset -= Vec2(0, 100) * dt

    def resize(self, dt: float, width, height):
        print("Resize")
        self.size.constant = Vec2(width, height)

    def on_resize(self, width, height):
        unschedule(self.resize)
        schedule_once(self.resize, 1/10, width, height)

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
            color=(255, 255, 255, 255),
            batch=batch,
            size=Size(matrix=Mat2((0, 0, 0, 1)), constant=Vec2(5, 0)),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

        self.rows = [
            Rectangle(
                color=(255, 255, 255, 255),
                batch=batch,
                size=Size(matrix=Mat2((1.0, 0.0, 0.0, 0.0)), constant=Vec2(0.0, 5.0)),
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
