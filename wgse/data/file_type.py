import enum


class FileType(enum.Enum):
    BAM = enum.auto()
    SAM = enum.auto()
    CRAM = enum.auto()
    FASTA = enum.auto()
    FASTQ = enum.auto()
    Unknown = enum.auto()
