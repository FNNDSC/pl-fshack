from dataclasses import dataclass
from typing import Collection, AnyStr, IO, ContextManager, TextIO, Iterable


@dataclass(frozen=True)
class MultiSink:
    """
    A writable file-like object which writes to multiple other file-like objects.
    """
    streams: Collection[IO]
    """Output streams"""

    def close(self) -> None:
        for s in self.streams:
            s.close()

    def write(self, data: AnyStr) -> None:
        for s in self.streams:
            s.write(data)

    def writable(self) -> bool:
        return all(s.writable() for s in self.streams)

    def writelines(self, lines: Iterable[AnyStr]) -> None:
        for s in self.streams:
            s.writelines(lines)

    def __enter__(self) -> IO[AnyStr]:
        for s in self.streams:
            s.__enter__()
        return self

    def __exit__(self, t, v, tb):
        for s in self.streams:
            s.__exit__(t, v, tb)


@dataclass()
class PrefixedSink(ContextManager):
    """
    A writable file-like object which prepends a prefix to every new line of text output.
    """
    sink: TextIO
    """Output stream"""
    prefix: str
    """Prefix to print before every line"""
    __first: bool = True
    """Whether or not it's necessary to print prefix before printing the next character"""

    def write(self, data: str):
        for char in data:
            self._write_char(char)

    def _write_char(self, char: str):
        """
        Write a single character to the wrapped output stream,
        printing out the prefix when necessary.
        """
        if self.__first:
            self.sink.write(self.prefix)
            self.__first = False
        self.sink.write(char)
        if char == '\n':
            self.__first = True

    def __enter__(self):
        self.sink.__enter__()

    def __exit__(self, t, v, tb):
        self.sink.__exit__(t, v, tb)
