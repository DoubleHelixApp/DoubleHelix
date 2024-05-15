from enum import Enum, auto


class ReadType(Enum):
    SingleEnd = auto()
    PairedEnd = auto()
    Unknown = auto()