from dataclasses import dataclass, field
from io import StringIO
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

    def flush(self) -> None:
        for s in self.streams:
            s.flush()

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
class PrefixedSink(ContextManager['PrefixedSink']):
    """
    A writable file-like object which prepends a prefix and appends a suffix
    to every new line of text output.

    Text is only written to the underlying sink when a line is complete, i.e. after
    '\n' is received, or when the ``flush`` method is called.
    """
    sink: TextIO
    """Output stream"""
    prefix: str
    """Prefix to print before every line"""
    suffix: str
    """Suffix to print after every line"""
    __buffer: StringIO = field(default_factory=StringIO)
    __empty: bool = True

    def write(self, data: str):
        for char in data:
            self._write_char(char)

    def _write_char(self, char: str):
        """
        Write a single character to the wrapped output stream,
        printing only after encountering '\n'.
        """
        if self.__empty:
            self.__empty = False
            self.__buffer.write(self.prefix)

        if char == '\n':
            self.__buffer.write(self.suffix)
            self.__buffer.write(char)
            self.__push()
            self.__empty = True
        else:
            self.__buffer.write(char)

    def __push(self) -> None:
        """Empty buffer into the sink."""
        self.sink.write(self.__buffer.getvalue())
        self.__buffer = StringIO()

    def flush(self) -> None:
        self.__push()
        self.sink.flush()

    def __enter__(self) -> 'PrefixedSink':
        self.sink.__enter__()
        return self

    def __exit__(self, t, v, tb):
        if not self.__empty:
            self.__buffer.write(self.suffix)
        self.__push()
        self.sink.__exit__(t, v, tb)
