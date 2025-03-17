from typing import TextIO

from src.action import CountAction, ReplaceAction, StringAction
from src.file_source import DirFileSource, ListFileSource
from src.lexer import Lexer
from src.reader import IoReader, Reader, StringReader
from src.tokens import Action, Id, Mode, Path


def loads(string: str) -> dict:
    return _load(StringReader(string))


def load(text_io: TextIO) -> dict:
    return _load(IoReader(text_io))


def _load(reader: Reader) -> dict:
    lexer = Lexer(reader)
    parser = Parser(lexer)
    return parser.parse()


class ParserError(Exception): ...


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.configurations = {}
        self.current_config = {}

    def parse(self) -> dict:
        tokens = self.lexer.tokenise()

        for tok in tokens:
            match tok:
                case Id():
                    if self.current_config:
                        self._build_current_config()
                    self.current_config["id"] = tok.value

                case Path():
                    self.current_config["path"] = tok.value

                case Mode():
                    self.current_config["mode"] = tok.value

                case Action():
                    self.current_config["action"] = tok.value

                case _:
                    raise ParserError("Unknown token")

        self._build_current_config()
        return self.configurations

    def _build_current_config(self) -> None:
        self._check_current_config()

        config_id = self.current_config["id"]
        path = self.current_config["path"]

        match self.current_config["mode"]:
            case "dir":
                file_source = DirFileSource(path)
            case "files":
                file_source = ListFileSource(path.split(","))
            case _:
                raise ParserError("Uknown mode")

        match self.current_config.get("action", "string"):
            case "string":
                action = StringAction(file_source)
            case "count":
                action = CountAction(file_source)
            case "string":
                action = ReplaceAction(file_source)
            case _:
                raise ParserError("Uknown action")

        self.configurations[config_id] = action

    def _check_current_config(self) -> None:
        required_keys = ("mode", "path")
        missing_keys = []

        for key in required_keys:
            if key not in self.current_config:
                missing_keys.append(key)

        if len(missing_keys) > 0:
            raise ParserError(f"Missing required keys: {', '.join(missing_keys)}")
