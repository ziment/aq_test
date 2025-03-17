from abc import ABC, abstractmethod

from src.file_source import FileSource


class Action(ABC):
    @abstractmethod
    def execute(self) -> None: ...


class StringAction(Action):
    def __init__(self, file_src: FileSource) -> None:
        self.file_src = file_src

    def execute(self) -> None: ...  # todo impl


class CountAction(Action):
    def __init__(self, file_src: FileSource) -> None:
        self.file_src = file_src

    def execute(self) -> None: ...  # todo impl


class ReplaceAction(Action):
    def __init__(self, file_src: FileSource) -> None:
        self.file_src = file_src

    def execute(self) -> None: ...  # todo impl
