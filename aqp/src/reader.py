from abc import ABC, abstractmethod
from typing import TextIO


class Reader(ABC):
    EOF = "\0"

    def __init__(self: "Reader") -> None:
        self.position = 0
        self.line = 0

    def forward(self) -> None:
        if self.peek() == "\n":
            self.position = 0
            self.line += 1
        else:
            self.position += 1
        self._forward_impl()

    @abstractmethod
    def _forward_impl(self, length: int = 1) -> None: ...

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


class StringReader(Reader):
    def __init__(self, string: str) -> None:
        super().__init__()
        self.string = string
        self.index = 0

    def _forward_impl(self, length: int = 1) -> None:
        self.index += length

    def prefix(self, length: int) -> str:
        return self.string[self.index : self.index + length]

    def peek(self, position: int = 0) -> str:
        if self.eof(position):
            return Reader.EOF

        return self.string[self.index + position]

    def eof(self, offset: int = 0) -> bool:
        return self.index + offset >= len(self.string)


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
        # Remove the first `length` characters from the buffer.
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
