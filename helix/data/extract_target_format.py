import enum


class ExtractTargetFormat(enum.Enum):
    Microarray = enum.auto()
    SAM = enum.auto()
    BAM = enum.auto()
    CRAM = enum.auto()
    FASTA = enum.auto()
    FASTQ = enum.auto()
    HTML = enum.auto()
    VCF = enum.auto()
    Unknown = enum.auto()
