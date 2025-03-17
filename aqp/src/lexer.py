from typing import Collection

import src.tokens as t
from src.reader import Reader

_NEW_LINE = "\n"
_NEW_STATEMENT_CHAR = "#"
_STRING_ESCAPE_CHAR = "\\"


class LexerError(Exception): ...


class Lexer:
    def __init__(self, reader: Reader) -> None:
        self.cfg = {}
        self.reader = reader

    def tokenise(self) -> list[t.Token]:
        tokens = []

        while True:
            token = self._next_token()
            if not token:
                break
            tokens.append(token)

        return tokens

    def _next_token(self) -> t.Token:
        self._skip_whitespace()

        if self.reader.eof():
            return None

        if not self.reader.check(_NEW_STATEMENT_CHAR):
            raise Exception  # todo: add error msg

        if self._is_potential_id_char() or self.reader.check("id:"):
            self._skip_whitespace()
            string = ""
            while self._is_potential_id_char():
                ch = self.reader.peek()
                string += ch
                self.reader.forward()

            id_value = int(string)
            return t.Id(int(id_value))

        if self.reader.check("mode:"):
            self._skip_whitespace()
            value = self._scan_until((_NEW_STATEMENT_CHAR, _NEW_LINE))
            return t.Mode(value)

        if self.reader.check("path:"):
            self._skip_whitespace()
            value = self._scan_escaped_string()
            return t.Path(value)

        if self.reader.check("action:"):
            self._skip_whitespace()
            value = self._scan_until((_NEW_STATEMENT_CHAR, _NEW_LINE))
            return t.Action(value)

        raise LexerError  # todo: add description

    def _scan_until(self, terminators: Collection[str] | str) -> str:
        string = ""

        if isinstance(terminators, str):
            terminators = (terminators,)

        while not self.reader.eof():
            ch = self.reader.peek()

            if ch in terminators:
                break

            string += ch
            self.reader.forward()

        return string.strip()

    def _scan_escaped_string(self) -> str:
        string = ""

        escaped = False

        while True:
            ch = self.reader.peek()

            if ch == _STRING_ESCAPE_CHAR:
                escaped = not escaped
                continue

            if ch == _NEW_STATEMENT_CHAR and not escaped:
                break

            string += ch
            self.reader.forward()

        return string.strip()

    def _is_potential_id_char(self) -> bool:
        return str.isnumeric(self.reader.peek())

    def _skip_whitespace(self) -> None:
        while self.reader.peek().isspace():
            self.reader.forward()
