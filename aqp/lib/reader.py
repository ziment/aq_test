from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import StringIO
from typing import TextIO


class Reader(ABC):
    """
    An abstraction over an IO. Keeps track of character position and line number, which can be
    retrieved with ``get_file_pos``.
    """

    EOF = "\0"
    NEW_LINE = "\n"

    def __init__(self) -> None:
        self._position = 0
        self._line = 0

    def forward(self, offset: int = 1) -> None:
        """Moves the internal pointer ``offset`` symbols forward"""

        chars = self.prefix(offset)

        newline_count = chars.count(Reader.NEW_LINE)

        if newline_count > 0:
            last_newline = chars.rfind(Reader.NEW_LINE)
            self._line += newline_count
            self._position = len(chars) - (last_newline + 1)
        else:
            self._position += offset

        self._forward_impl(offset)

    def get_file_pos(self) -> "FilePosition":
        """Returns the current ``FilePosition``"""

        return FilePosition(self._position, self._line)

    @abstractmethod
    def _forward_impl(self, offset: int = 1) -> None: ...

    @abstractmethod
    def prefix(self, length: int) -> str:
        """Returns the next ``length`` characters"""

    @abstractmethod
    def peek(self, offset: int = 0) -> str:
        """Returns a character with the given ``offset``"""

    @abstractmethod
    def eof(self, offset: int = 0) -> bool:
        """Checks if there's EOF in ``offset`` characters"""

    def check(self, string: str) -> bool:
        """Check if the next characters are equal to the ``string``. Automatically forwards if the check is successful."""
        str_len = len(string)

        if self.prefix(str_len) == string:
            self.forward(str_len)
            return True

        return False


class IoReader(Reader):
    def __init__(self, text_io: TextIO) -> None:
        super().__init__()
        self.text_io = text_io
        self.buffer = ""

    def _fill_buffer(self, length: int) -> None:
        while len(self.buffer) < length:
            chunk = self.text_io.read(length - len(self.buffer))
            if not chunk:
                break
            self.buffer += chunk

    def _forward_impl(self, length: int = 1) -> None:
        self._fill_buffer(length)
        self.buffer = self.buffer[length:]

    def prefix(self, length: int) -> str:
        self._fill_buffer(length)
        return self.buffer[:length]

    def peek(self, position: int = 0) -> str:
        self._fill_buffer(position + 1)
        if position < len(self.buffer):
            return self.buffer[position]
        return Reader.EOF

    def eof(self, offset: int = 0) -> bool:
        self._fill_buffer(offset + 1)
        return len(self.buffer) < (offset + 1)


class StringReader(IoReader):
    def __init__(self, string: str) -> None:
        super().__init__(StringIO(string))


@dataclass
class FilePosition:
    """Represents a position inside a text file"""

    position: int = -1
    line: int = -1

    def __str__(self) -> str:
        return f"line {self.line if self.line != -1 else 'unknown'} char {self.line if self.line != -1 else 'unknown'}"
