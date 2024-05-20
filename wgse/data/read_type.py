from enum import Enum, auto


class ReadType(Enum):
    Single = auto()
    Paired = auto()
    Unknown = auto()
