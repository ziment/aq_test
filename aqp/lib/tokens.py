from abc import ABC
from typing import Any

from .reader import FilePosition

# since there is no way to copy another function's type signature out of the box,
# it's easier to spell out all the parameters in each constructor explicitly than
# using *args and **kwargs


class Token(ABC):
    def __init__(self, value: Any, position: FilePosition = FilePosition()) -> None:
        self.value = value
        self.text_pos = position


class Id(Token):
    def __init__(self, value: int, position: FilePosition = FilePosition()) -> None:
        super().__init__(value, position)


class Path(Token):
    def __init__(self, value: str, position: FilePosition = FilePosition()) -> None:
        super().__init__(value, position)


class Mode(Token):
    def __init__(self, value: str, position: FilePosition = FilePosition()) -> None:
        super().__init__(value, position)


class Action(Token):
    def __init__(self, value: str, position: FilePosition = FilePosition()) -> None:
        super().__init__(value, position)


class ErrorToken(Token):
    def __init__(
        self, error_message: str = "", position: FilePosition = FilePosition()
    ) -> None:
        super().__init__(None, position)
        self.error_message = error_message
