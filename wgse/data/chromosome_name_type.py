import enum


class ChromosomeNameType(enum.Enum):
    Chr = enum.auto()
    Number = enum.auto()
    Accession = enum.auto()
    Unknown = enum.auto()