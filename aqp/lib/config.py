from dataclasses import dataclass
from enum import StrEnum, auto
from os import PathLike
from typing import Iterable, Optional


class FileMode(StrEnum):
    UNKNOWN = auto()
    FILES = auto()
    DIR = auto()

    def __bool__(self) -> bool:
        return self != FileMode.UNKNOWN


class Action(StrEnum):
    UNKNOWN = auto()
    STRING = auto()
    COUNT = auto()
    REPLACE = auto()

    def __bool__(self) -> bool:
        return self != Action.UNKNOWN


@dataclass(kw_only=True)
class Config:
    config_id: int

    path_to_config: Optional[str | PathLike] = None
    mode: FileMode = FileMode.UNKNOWN
    action: Action = Action.UNKNOWN
    action_path: Optional[Iterable[str | PathLike]] = None
