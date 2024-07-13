import enum
import time
from typing import Callable


class ComputeOn(enum.Enum):
    Read = enum.auto()
    Write = enum.auto()
    Proxy = enum.auto()


class BaseProgressCalculator:
    """Provide a way to calculate the progress and an ETA."""

    def __init__(
        self,
        progress: Callable[[str, float], None],
        total_bytes: int,
        compute_on: ComputeOn,
        op_name="",
    ) -> None:
        self._previous_bytes = None
        self._previous_time = None
        self._bytes_per_second = [None] * 100
        self._average_writes_index = 0
        self._op_name = op_name
        self._progress = progress
        self._total_bytes = total_bytes
        self._compute_on = compute_on
        self.compute = None
        if compute_on == ComputeOn.Read:
            self.compute = lambda r, _: self._compute(r)
        elif compute_on == ComputeOn.Write:
            self.compute = lambda _, w: self._compute(w)
        elif compute_on == ComputeOn.Proxy:
            self.compute = self._compute
        else:
            raise ValueError("Invalid progress_on parameter")

    def _compute(self, current_bytes):
        if current_bytes is None:
            self._progress(None, None)
            return
        current_time = time.time()
        delta_time = 0
        delta_bytes = 0
        if self._previous_bytes is not None and self._previous_time is not None:
            delta_bytes = current_bytes - self._previous_bytes
            delta_time = current_time - self._previous_time
        else:
            self._previous_bytes = current_bytes
            self._previous_time = current_time
            return
        # Let's say the delta is null, just don't update anything and
        # let's try on next iteration to get some proper stats.
        # Delta time and delta bytes should never decrease, so we'll
        # have another change to compute stats later.
        if delta_bytes == 0 or delta_time == 0:
            return

        self._previous_bytes = current_bytes
        self._previous_time = current_time

        current_bytes_to_completion = self._total_bytes - current_bytes
        current_bytes_per_second = delta_bytes / delta_time
        if self._average_writes_index == len(self._bytes_per_second):
            self._average_writes_index = 0

        self._bytes_per_second[self._average_writes_index] = current_bytes_per_second
        self._average_writes_index += 1
        non_none_bytes_per_second = [x for x in self._bytes_per_second if x is not None]
        average_bytes_per_second = None
        if len(non_none_bytes_per_second) == 0:
            return
        average_bytes_per_second = sum(non_none_bytes_per_second) / len(
            non_none_bytes_per_second
        )
        if average_bytes_per_second == 0:
            return

        second_to_completion = current_bytes_to_completion / average_bytes_per_second

        # Set a threshold to not have the ETA jumping around
        threshold = len(non_none_bytes_per_second) < 10
        if threshold:
            formatted_delta = "Calculating, please stand-by."
        else:
            if second_to_completion != 0:
                hours, remainder = divmod(second_to_completion, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_delta = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            else:
                formatted_delta = "Unavailable"

        percentage = current_bytes * 100 / self._total_bytes

        formatted_label = f"{self._op_name}, ETA: {formatted_delta}"
        self._progress(formatted_label, percentage)
