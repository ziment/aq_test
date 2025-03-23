from typing import Collection, Literal, Optional, overload

from . import tokens
from .reader import Reader

_NEW_LINE = "\n"
_NEW_STATEMENT_CHAR = "#"
_STRING_ESCAPE_CHAR = "\\"
_ESCAPABLE_CHARS = "#\\"


class Lexer:
    """A lexer for AQC files"""

    def __init__(self, reader: Reader) -> None:
        self._reader = reader
        self._skip_current_token = False

    def tokenise(self) -> list[tokens.Token]:
        """Returns a ``list`` of all tokens"""

        token_list = []

        while True:
            token = self.next_token()
            if not token:
                break
            token_list.append(token)

        return token_list

    def next_token(self) -> Optional[tokens.Token]:
        """Returns the next token, or ``None`` if at EOF."""

        if self._skip_current_token:
            self._read_until(_NEW_STATEMENT_CHAR)
            self._skip_current_token = False

        self._skip_whitespace()

        if self._reader.eof():
            return None

        if not self._reader.check(_NEW_STATEMENT_CHAR):
            self._skip_current_token = True
            return tokens.ErrorToken("Missing a new statement character")

        if self._is_potential_id_char() or self._reader.check("id:"):
            self._skip_whitespace()
            string = ""
            while self._is_potential_id_char():
                ch = self._reader.peek()
                string += ch
                self._reader.forward()

            id_value = int(string)
            return tokens.Id(int(id_value), self._reader.get_file_pos())

        if self._reader.check("mode:"):
            self._skip_whitespace()
            value = self._read_until((_NEW_STATEMENT_CHAR, _NEW_LINE))
            return tokens.Mode(value, self._reader.get_file_pos())

        if self._reader.check("path:"):
            self._skip_whitespace()
            value = self._read_escaped_string()
            return tokens.Path(value, self._reader.get_file_pos())

        if self._reader.check("action:"):
            self._skip_whitespace()
            value = self._read_until((_NEW_STATEMENT_CHAR, _NEW_LINE))
            return tokens.Action(value, self._reader.get_file_pos())

        return tokens.ErrorToken("unknown token", self._reader.get_file_pos())

    @overload
    def _read_until(
        self, terminators: Collection[str] | str, return_string: Literal[True] = True
    ) -> str: ...
    @overload
    def _read_until(
        self, terminators: Collection[str] | str, return_string: Literal[False]
    ) -> None: ...

    def _read_until(
        self, terminators: Collection[str] | str, return_string: bool = True
    ) -> Optional[str]:
        string = ""

        if isinstance(terminators, str):
            terminators = (terminators,)

        while not self._reader.eof():
            ch = self._reader.peek()

            if ch in terminators:
                break

            if return_string:
                string += ch
            self._reader.forward()

        if return_string:
            return string.strip()
        return None

    def _read_escaped_string(self) -> str:
        string = ""

        while not self._reader.eof():
            ch = self._reader.peek()

            if ch == _NEW_STATEMENT_CHAR:
                break

            if ch == _STRING_ESCAPE_CHAR:
                next_ch = self._reader.peek(1)
                if next_ch in _ESCAPABLE_CHARS:
                    ch = next_ch
                    self._reader.forward()

            string += ch
            self._reader.forward()

        return string.strip()

    def _is_potential_id_char(self) -> bool:
        return str.isnumeric(self._reader.peek())

    def _skip_whitespace(self) -> None:
        while self._reader.peek().isspace():
            self._reader.forward()
