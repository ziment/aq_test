from typing import Optional, cast

from . import tokens
from .config import Action, Config, FileMode
from .error import AqpError
from .lexer import Lexer


class ParserError(AqpError): ...


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer
        self._configurations: dict[int, Config] = {}
        self._current_config: Optional[Config] = None

    def parse(self) -> dict:
        while True:
            tok = self._lexer.next_token()

            if not tok:
                break

            if isinstance(tok, tokens.Id):
                if self._current_config:
                    self._build_current_config()

                self._current_config = Config(config_id=tok.value)
                continue

            if self._current_config is None:
                raise ParserError("No valid configuration found")

            self._current_config = cast(Config, self._current_config)

            match tok:
                case tokens.Path():
                    self._current_config.action_path = tok.value.split(", ")

                case tokens.Mode():
                    self._current_config.mode = self._mode_from_string(tok.value)

                case tokens.Action():
                    self._current_config.action = self._action_from_string(tok.value)

                case tokens.ErrorToken():
                    raise ParserError(f"{tok.text_pos}: {tok.error_message}")

                case _:
                    raise ParserError(f"{tok.text_pos}: unknown token")

        self._build_current_config()
        return self._configurations

    def _mode_from_string(self, mode: str) -> FileMode:
        match mode:
            case "dir":
                return FileMode.DIR
            case "files":
                return FileMode.FILES
            case _:
                return FileMode.UNKNOWN

    def _action_from_string(self, action: str) -> Action:
        match action:
            case "string":
                return Action.STRING
            case "count":
                return Action.COUNT
            case "replace":
                return Action.REPLACE
            case _:
                return Action.UNKNOWN

    def _build_current_config(self) -> None:
        assert self._current_config is not None  # assert for mypy

        self._check_current_config()
        self._configurations[self._current_config.config_id] = self._current_config

    def _check_current_config(self) -> None:
        assert self._current_config is not None  # assert for mypy

        missing_keys = []

        if not self._current_config.action:
            missing_keys.append("action")

        if not self._current_config.mode:
            missing_keys.append("mode")

        if not self._current_config.action_path:
            missing_keys.append("path")

        if len(missing_keys) > 0:
            raise ParserError(f"Missing required keys: {', '.join(missing_keys)}")
