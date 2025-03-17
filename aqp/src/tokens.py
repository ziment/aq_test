from abc import ABC
from typing import Any


class Token(ABC):
    def __init__(self, value: Any) -> None:
        self.value = value


class Id(Token):
    def __init__(self, value: int) -> None:
        super().__init__(value)


class Path(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Mode(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Action(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)
