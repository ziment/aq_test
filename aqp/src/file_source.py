import os
from abc import ABC, abstractmethod
from typing import Iterable


class FileSource(ABC):
    @abstractmethod
    def get_files(self) -> Iterable[os.PathLike]: ...


# todo fix path types from str


class DirFileSource(FileSource):
    def __init__(self, dir_path: str) -> None:
        super().__init__()
        self.dir_path = dir_path

    def get_files(self) -> Iterable[os.PathLike]:
        return (
            file
            for file in os.listdir(self.dir_path)
            if os.path.isfile(os.path.join(self.dir_path, file))
        )


class ListFileSource(FileSource):
    def __init__(self, files: Iterable[str]) -> None:
        super().__init__()
        self.dir_path = files

    def get_files(self) -> Iterable[os.PathLike]:
        return self.files
