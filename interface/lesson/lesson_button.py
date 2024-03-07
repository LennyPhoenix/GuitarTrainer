from ..style import Colours
from ..image_button import ImageButton
from ..bordered_rect import BorderedRectangle
from ..scroll_container import ScrollContainer

from framework import Position, Size, Frame, Mat2, Pin, Vec2
from framework.components import Label, Text
from engine import Lesson, Exercise

from pyglet.event import EventDispatcher
from pyglet.window import Window
from pyglet.resource import image


class LessonButton(BorderedRectangle, EventDispatcher):
    """A lesson start button for the lesson selection interface.

    Contains some information about the lesson and a play button to start it.
    """

    def __init__(
        self,
        position: Position,
        size: Size,
        parent: Frame | None,
        window: Window,
        lesson: Lesson,
        complete: bool,
    ):
        super().__init__(
            position=position,
            size=size,
            parent=parent,
            behind_parent=True,
        )

        self.lesson = lesson
        self.complete = complete

        self.play_button = ImageButton(
            window=window,
            size=Size(
                matrix=Mat2((0.0, 1.0, 0.0, 1.0)),
            ),
            position=Position(pin=Pin.top_left()),
            parent=self,
            image=image("assets/play.png"),
        )
        self.play_button.set_handler("on_released", self.on_button_pressed)

        self.info = ScrollContainer(
            size=Size(
                matrix=Mat2((1.0, -1.0, 0.0, 1.0)),
            ),
            position=Position(pin=Pin.top_right()),
            parent=self,
        )
        self.info.register(window)

        self.title = Label(
            text=f"Lesson {lesson.number}",
            font_size=32,
            colour=Colours.FOREGROUND,
            position=Position(pin=Pin.top_left(), offset=Vec2(8, 0)),
            parent=self.info.content,
        )

        exercises: dict[tuple[Exercise.Type, bool], int] = {}

        # Get number of each exercise
        for exercise in set(lesson.exercises):
            if (exercise.type, exercise.hint) not in exercises:
                exercises[(exercise.type, exercise.hint)] = 0
            exercises[(exercise.type, exercise.hint)] += 1

        # Pretty print the exercises and their counts
        pretty = ""
        for key, value in exercises.items():
            modifier = "NEW" if key[1] else "practice for"

            match key[0]:
                case Exercise.Type.NOTE_NAME:
                    name = "Note Names"
                case Exercise.Type.STAVE_NOTE:
                    name = "Stave Notes"
                case Exercise.Type.SCALE:
                    name = "Scales"

            pretty += f"- {value} {modifier} {name} exercises\n"

        self.text = Text(
            text=pretty,
            colour=Colours.FOREGROUND,
            size=Size(
                matrix=Mat2((1.0, 0.0, 0.0, 0.0)),
            ),
            position=Position(pin=Pin.top_left(), offset=Vec2(8, -48 - 18)),
            parent=self.info.content,
            font_size=24,
        )

    def on_button_pressed(self):
        """Called when the start button is pressed."""
        self.dispatch_event("on_started", self.lesson, self.complete)


LessonButton.register_event_type("on_started")
