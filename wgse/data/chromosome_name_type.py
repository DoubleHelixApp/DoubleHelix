import enum


class ChromosomeNameType(enum.Enum):
    Chr = enum.auto()
    Number = enum.auto()
    GenBank = enum.auto()
    RefSeq = enum.auto()
    GenBankT2T = enum.auto()
    RefSeqT2T = enum.auto()
    Unknown = enum.auto()
