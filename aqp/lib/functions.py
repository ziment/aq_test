import os
from typing import Any, Callable, Collection, TextIO

from .config import Action, Config, FileMode
from .error import AqpError
from .lexer import Lexer
from .parser import Parser
from .reader import IoReader, Reader, StringReader

"""Collection of public functions for working with AQC configs"""


def loads(string: str) -> dict[int, Config]:
    """Loads a ``Config`` from ``string``.
    Will not set ``path_to_config`` field in the returned config, since it has no way of knowing it

    Returns:
        dict[int, Config]: ``dict`` of all loaded configs, indexed by id
    """

    return _load(StringReader(string))


def load(text_io: TextIO) -> dict[int, Config]:
    """Loads a ``Config`` from ``TextIO``
    Will not set ``path_to_config`` field in the returned config, since it has no way of knowing it

    Returns:
        dict[int, Config]: ``dict`` of all loaded configs, indexed by id
    """

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
    """Executes ``config``, writing the results to a ``dict``.

    Returns:
        dict: result of executing the config
    """

    if config.action_path is None:
        raise AqpError("Action path is not provided")

    file_paths = _get_files(config)
    line_handler = _get_line_handler(config)

    json_dict: dict[str, Any] = {
        "configurationId": config.config_id,
        "configFile": config.path_to_config,
        "configurationData": {
            "mode": str(config.mode),
            "path": ", ".join((str(elem) for elem in config.action_path)),
        },
    }

    out: dict[int, dict[int, str]] = {}

    file_count = len(file_paths)

    for file_ind, file_path in enumerate(file_paths, start=1):
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
