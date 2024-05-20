import enum


class MitochondrialNameType(enum.Enum):
    Accession = enum.auto()
    chrM = enum.auto()
    chrMT = enum.auto()
    M = enum.auto()
    MT = enum.auto()
    Unknown = enum.auto()
