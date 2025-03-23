from abc import ABC, abstractmethod
from typing import TextIO
from io import StringIO


class Reader(ABC):
    EOF = "\0"
    NEW_LINE = "\n"

    def __init__(self: "Reader") -> None:
        self._position = 0
        self._line = 0

    def forward(self, offset: int = 1) -> None:
        chars = self.prefix(offset)

        newline_count = chars.count(Reader.NEW_LINE)

        if newline_count > 0:
            last_newline = chars.rfind(Reader.NEW_LINE)
            self._line += newline_count
            self._position = len(chars) - (last_newline + 1)
        else:
            self._position += offset

        self._forward_impl(offset)

    @abstractmethod
    def _forward_impl(self, offset: int = 1) -> None: ...

    @abstractmethod
    def prefix(self, length: int) -> str: ...

    @abstractmethod
    def peek(self, position: int = 0) -> str: ...

    @abstractmethod
    def eof(self, offset: int = 0) -> bool: ...

    def check(self, string: str) -> bool:
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
