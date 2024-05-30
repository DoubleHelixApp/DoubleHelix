from enum import IntEnum


class DepthBin(IntEnum):
    Zero = 0
    Between0And3 = 1
    Between3And7 = 2
    MoreThan7 = 3


class CoverageStats:
    def __init__(self) -> None:
        self.sequence_name: str = None
        self.bin_entries: dict[DepthBin, int] = None
        self.bin_sum: dict[DepthBin, int] = None
        self.non_zero_percentage: float = 0
        self.non_zero_average: float = 0
        self.all_average: float = 0
