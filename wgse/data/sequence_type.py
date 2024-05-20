import enum


class SequenceType(enum.Flag):
    Autosome = enum.auto()
    X = enum.auto()
    Y = enum.auto()
    Mitochondrial = enum.auto()
    Other = enum.auto()
    Unmapped = enum.auto()
