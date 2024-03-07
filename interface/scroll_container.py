from framework.components import Container, Rectangle, Button
from framework import Size, Position, Frame, Mat2, Vec2, Pin
from .style import Colours

from pyglet.window import Window, mouse


class ScrollContainer(Container):
    """A container with a scroll bar, useful for long paragraphs of text or
    dropdown boxes.

    Children should be added with the `add_child` method or directly added to
    the scroll container's content field as children.

    Remember to register for input events with `.register(window)`.
    """

    SCROLL_BAR_SIZE = 24

    content: Frame | None = None
    dragging: bool = False

    def __init__(
        self,
        size: Size,
        position: Position,
        parent: "Frame | None",
        behind_parent: bool = False,
    ):
        super().__init__(size, position, parent, behind_parent)

        self.content = Frame(
            size=Size(
                matrix=Mat2(),
                constant=Vec2(-self.SCROLL_BAR_SIZE, 0.0),
            ),
            position=Position(pin=Pin.bottom_left()),
            parent=self,
        )

        self.scroll_bar = Rectangle(
            size=Size(
                matrix=Mat2((0.0, 0.0, 0.0, 1.0)),
                constant=Vec2(self.SCROLL_BAR_SIZE, 0.0),
            ),
            position=Position(pin=Pin.top_right()),
            parent=self,
            colour=Colours.ELEMENT_BACKGROUND,
        )

        self.scroll_button = Button(
            size=Size(
                matrix=Mat2(
                    (
                        1.0,
                        0.0,
                        0.0,
                        min(
                            1.0,
                            self.content.broad_phase_aabb.size.y
                            / self.content.aabb.size.y,
                        ),
                    )
                )
            ),
            parent=self.scroll_bar,
            position=Position(pin=Pin.top_left()),
        )

        self.scroll_button_bg = Rectangle(
            size=Size(matrix=Mat2()),
            position=Position(),
            colour=Colours.FOREGROUND,
            parent=self.scroll_button,
        )

    def refresh_bar(self):
        """Updates the scroll bar to reflect the position of the content."""
        if self.content is not None:
            self.scroll_button.size.matrix = Mat2(
                (
                    1.0,
                    0.0,
                    0.0,
                    min(
                        1.0,
                        self.content.aabb.size.y / self.content.broad_phase_aabb.size.y,
                    ),
                )
            )
            diff = self.content.broad_phase_aabb.size.y - self.content.aabb.size.y
            if diff != 0.0:
                factor = self.content.position.offset.y / diff
            else:
                factor = 0.0
            self.scroll_button.position.pin = Pin(
                local_anchor=Vec2(0.0, 1.0 - factor),
                remote_anchor=Vec2(0.0, 1.0 - factor),
            )

    def propagate_position(self):
        # Override position propagation to also update the scroll bar
        val = super().propagate_position()
        self.refresh_bar()
        return val

    def add_child(self, other: Frame):
        # Override the `add_child` method to add to the content instead
        if self.content is not None:
            self.content.add_child(other)
        self.refresh_bar()

    def register(self, window: Window):
        """Registers the scroll container to receive input events from the
        window."""
        window.push_handlers(self)

    def on_mouse_press(self, x, y, buttons, _modifiers):
        """Checks when the scroll button is grabbed."""
        if (
            buttons == mouse.LEFT
            and self.scroll_bar.aabb.check_point(Vec2(x, y))
            and self.content is not None
        ):
            self.dragging = True

    def on_mouse_release(self, *_args):
        """Releases the scroll button."""
        self.dragging = False

    def on_mouse_drag(
        self,
        _x: float,
        _y: float,
        _dx: float,
        dy: float,
        _buttons: int,
        _modifiers: int,
    ):
        """Scrolls the content window with the mouse movement."""
        if self.dragging and self.content is not None:
            self.content.position.offset = Vec2(
                0.0,
                min(
                    max(
                        # Find the fraction of the scroll bar movement, then
                        # multiply by the content height.
                        self.content.position.offset.y
                        - (dy / self.scroll_bar.aabb.size.y)
                        * self.content.broad_phase_aabb.size.y,
                        # Clamp to min and max values
                        0.0,
                    ),
                    self.content.broad_phase_aabb.size.y - self.content.aabb.size.y,
                ),
            )
            self.refresh_bar()

    def on_mouse_scroll(
        self,
        x: float,
        y: float,
        _scroll_x: float,
        scroll_y: float,
    ):
        """Scrolls the content window with the scroll buttons."""
        if self.aabb.check_point(Vec2(x, y)) and self.content is not None:
            self.content.position.offset = Vec2(
                0.0,
                min(
                    max(self.content.position.offset.y - scroll_y * 20, 0.0),
                    self.content.broad_phase_aabb.size.y - self.content.aabb.size.y,
                ),
            )
            self.refresh_bar()
