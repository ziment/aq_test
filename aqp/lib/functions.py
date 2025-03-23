import os
from typing import Any, Callable, Iterable, Collection, TextIO

from .config import Action, Config, FileMode
from .error import AqpError
from .lexer import Lexer
from .parser import Parser
from .reader import IoReader, Reader, StringReader


def loads(string: str) -> dict[int, Config]:
    return _load(StringReader(string))


def load(text_io: TextIO) -> dict[int, Config]:
    return _load(IoReader(text_io))


def _get_files(config: Config) -> Collection[str | os.PathLike]:
    assert config.action_path is not None

    match config.mode:
        case FileMode.FILES:
            return config.action_path
        case FileMode.DIR:
            files = []
            for dir_path in config.action_path:
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    if os.path.isfile(file_path):
                        files.append(file_path)
            return files
        case _:
            raise AqpError(f"Unsupported file mode {config.mode}")


def execute_config(config: Config) -> dict:
    # todo: add better config checking
    if config.action_path is None:
        raise AqpError("Action path is not provided")

    json_dict: dict[str, Any] = {
        "configurationId": config.config_id,
        "configFile": config.path_to_config,
        "configurationData": {
            "mode": str(config.mode),
            "path": ", ".join((str(elem) for elem in config.action_path)),
        },
    }

    out: dict[int, dict[int, str]] = {}

    file_paths = _get_files(config)
    line_handler = _get_line_handler(config)

    file_count = len(file_paths)

    for file_ind, file_path in enumerate(file_paths, start=1):
        # todo: maybe return Sized?
        # counting files in a weird way since get_files returns an Iterable
        file_count = max(file_count, file_ind)

        with open(file_path) as file:
            for line_ind, line in enumerate(file, start=1):
                if line_ind not in out:
                    out[line_ind] = {}

                out[line_ind][file_ind] = line_handler(
                    line.removesuffix("\n"), file_ind
                )

    for line_ind in out:
        for file_ind in range(1, file_count + 1):
            if file_ind not in out[line_ind]:
                out[line_ind][file_ind] = line_handler("", file_ind)

    json_dict["out"] = out

    return json_dict


def _load(reader: Reader) -> dict[int, Config]:
    lexer = Lexer(reader)
    parser = Parser(lexer)
    return parser.parse()


def _string_handle_line(line: str, file_number: int) -> str:
    return line


def _count_handle_line(line: str, file_number: int) -> str:
    return str(len(line.split()))


def _replace_handle_line(line: str, file_number: int) -> str:
    replacements = {
        "a": f"1{file_number}",
        "b": f"2{file_number}",
        "c": f"3{file_number}",
    }
    result = ""
    for ch in line:
        result += replacements.get(ch, ch)
    return result


def _get_line_handler(config: Config) -> Callable[[str, int], str]:
    match config.action:
        case Action.STRING:
            return _string_handle_line
        case Action.REPLACE:
            return _replace_handle_line
        case Action.COUNT:
            return _count_handle_line
        case _:
            raise AqpError(f"Unsupported action {config.action}")
