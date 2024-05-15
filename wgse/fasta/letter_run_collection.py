import typing

from wgse.fasta.letter_run import LetterRun


class LetterRunCollection:
    """Represent a sequence containing runs of a specific letter."""

    def __init__(self, name: str, length: int) -> None:
        if length <= 0:
            raise IndexError("Length should be greater than zero.")
        self.runs: typing.List[LetterRun] = []
        self.name: str = name
        self.length: int = length
        self._current_run: LetterRun = None
        self._is_ended: bool = False

    def filter(self, criteria: typing.Callable[[LetterRun], bool]):
        return [x for x in self.runs if criteria(x)]

    def open_run(self, position: int) -> None:
        if self._is_ended:
            raise RuntimeError("Trying to open a run on an ended sequence.")
        if self._current_run is not None:
            raise RuntimeError("Trying to open a an already opened run of Ns.")
        if position < 0:
            raise IndexError("Trying to open a run with a negative position.")

        if len(self.runs) > 0:
            previous_end = self.runs[-1].start + self.runs[-1].length
            if position < previous_end + 1:
                raise ValueError("Trying to open a run overlapping with previous runs.")

        self._current_run = LetterRun()
        self._current_run.open(position)

    def is_run_open(self) -> bool:
        return self._current_run is not None

    def close_run(self, position: int) -> None:
        if self._current_run is None:
            raise RuntimeError("Trying to close an already closed run.")
        if position <= self._current_run.start:
            raise RuntimeError(
                f"Expected a position greater than start for closing a run: {position}<={self._current_run.start}"
            )
        if position > self.length:
            raise RuntimeError(
                f"Trying to close a run with a position {position}, that is greater than the whole length of the sequence {self.length}."
            )
        run_length = position - self._current_run.start
        self._current_run.close(run_length)
        self.runs.append(self._current_run)
        self._current_run = None

    def end(self, position: int) -> None:
        if self.is_run_open():
            self.close_run(position)
        self._is_ended = True

        if position != self.length:
            raise ValueError(
                f"Expected {self.length} base pairs in this sequence but processed {position}."
            )