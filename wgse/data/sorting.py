import enum
from enum import auto


class Sorting(enum.Enum):
    Coordinate = auto()
    Unsorted = auto()
    Unknown = auto()
    QueryName = auto()
