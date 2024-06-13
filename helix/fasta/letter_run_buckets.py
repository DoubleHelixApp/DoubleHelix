from collections import OrderedDict
import math
import typing

from helix.fasta.letter_run_collection import LetterRunCollection


class LetterRunBuckets:
    """Represent a collection of run of letters partitioned into
    subsequences of fixed length called buckets.
    """

    def __init__(
        self,
        sequence: LetterRunCollection,
        buckets_number: int,
        long_run_threshold: int,
        items: typing.OrderedDict[int, int] = None,
    ) -> None:
        self._buckets_number = buckets_number
        self._long_run_threshold: int = long_run_threshold
        self._sequence: LetterRunCollection = sequence
        self.buckets = items

        if self.buckets is None:
            self.buckets = self._make_buckets()

    def _make_buckets(self) -> typing.OrderedDict[int, int]:
        if self._buckets_number > self._sequence.length:
            # Can't have less than 1 N per bucket.
            # This can happen in short sequence (i.e., decoy).
            return OrderedDict()

        buckets = OrderedDict()
        bucket_size = int(math.floor(self._sequence.length / self._buckets_number))

        for run in self._sequence.filter(
            lambda x: x.length >= self._long_run_threshold
        ):
            # Determine how many buckets this run is spanning
            start = run.start
            end = run.start + run.length
            index_bucket_start = int(math.floor(start / bucket_size))
            index_bucket_end = int(math.floor(end / bucket_size))

            # Iterate over each bucket determining how many elements are in
            # each bucket.
            for bucket in range(index_bucket_start, index_bucket_end + 1):
                start_bucket_offset = max(bucket * bucket_size, start)
                end_bucket_offset = min(bucket * bucket_size + bucket_size - 1, end)
                runs_count = end_bucket_offset - start_bucket_offset
                if runs_count < 1:
                    continue
                if bucket not in buckets:
                    buckets[bucket] = 0
                buckets[bucket] += runs_count
        return buckets
