from typing import Callable, List
from helix.fasta.letter_run import LetterRun


class LetterRunCollection:
    """Represent a collection of letter's run in a specific sequence

    Example:
        The following example indicates the repetition of 10 identical letter
        in the chromosome "chr1" that starts at position 0 and ends in the
        position 10:
        >>> collection = LetterRunCollection(name="chr1", length=10000)
        >>> collection.open_run(0)
        >>> collection.close_run(10)
        >>> collection.end(10000)

        The exact letter the run indicates is not tracked inside this class.
    """

    def __init__(self, name: str, length: int) -> None:
        """Initialize the collection

        Args:
            name (str): Name of the sequence
            length (int): Length of the sequence

        Raises:
            IndexError: Length is less than or equal to zero
        """
        if length <= 0:
            raise IndexError("Length should be greater than zero.")
        self.runs: List[LetterRun] = []
        self.name: str = name
        self.length: int = length
        self._current_run: LetterRun = None
        self._is_ended: bool = False

    def filter(self, criteria: Callable[[LetterRun], bool]) -> List[LetterRun]:
        """Filter the runs

        Args:
            criteria (typing.Callable[[LetterRun], bool]): Criteria to filter the runs

        Returns:
            _type_: Filtered runs
        """
        return [x for x in self.runs if criteria(x)]

    def open_run(self, position: int) -> None:
        """Indicates the beginning of a new run.

        Args:
            position (int): Position of the beginning of the new run

        Raises:
            RuntimeError: open_run was called after end() is called, meaning
                the collection is closed because the sequence is finished.
            ValueError: open_run was called on a run that was already opened.
            RuntimeError: open_run was called when the caller did not call
                close_run() for the previous run.
            ValueError: If position is before the end of the previous run
        """
        if self._is_ended:
            raise RuntimeError("Trying to open a run after the sequence was closed")
        if self._current_run is not None:
            raise RuntimeError("Trying to open an already open run")
        if position < 0:
            raise ValueError("Trying to open a run with a negative position")

        if len(self.runs) > 0:
            previous_end = self.runs[-1].start + self.runs[-1].length
            if position < previous_end + 1:
                raise ValueError(
                    "Position cannot be before the end of the previous run"
                )

        self._current_run = LetterRun()
        self._current_run.open(position)

    def is_run_open(self) -> bool:
        """Checks whether a run was opened.

        Returns:
            bool: True if the run is open.
        """
        return self._current_run is not None

    def close_run(self, position: int) -> None:
        """Indicates the end of a run.

        Args:
            position (int): Position where the run ends.

        Raises:
            RuntimeError: close_run called before calling open_run first
            RuntimeError: Position cannot be less then the start of this run
            RuntimeError: Position is greater than the end of the sequence
        """
        if self._current_run is None:
            raise RuntimeError("Trying to close an already closed run.")
        if position <= self._current_run.start:
            raise ValueError(
                f"Position cannot be smaller than start: {position}<={self._current_run.start}"
            )
        if position > self.length:
            raise ValueError(
                "Position cannot be greater than the length of the sequence: "
                f"{position}>{self.length}."
            )
        run_length = position - self._current_run.start
        self._current_run.close(run_length)
        self.runs.append(self._current_run)
        self._current_run = None

    def end(self, position: int) -> None:
        """Indicated the end of a sequence.

        After this function is called, the sequence is closed
        and is not possible to add more runs to this collection.

        Args:
            position (int): Position where the sequence ends.

        Raises:
            ValueError: Position is not equal to length of the sequence.
        """
        if self.is_run_open():
            self.close_run(position)
        self._is_ended = True

        if position != self.length:
            raise ValueError(
                f"Expected {self.length} base pairs in this sequence but processed {position}."
            )
