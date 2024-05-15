from pathlib import Path

from wgse.alignment_map.index_stats_calculator import SequenceStatistics
from wgse.data.chromosome_name_type import ChromosomeNameType
from wgse.data.file_type import FileType
from wgse.data.mitochondrial_name_type import MitochondrialNameType
from wgse.data.mitochondrial_model_type import MitochondrialModelType
from wgse.data.alignment_stats import AlignmentStats
from wgse.data.sequence_type import SequenceType
from wgse.data.gender import Gender
from wgse.data.sorting import Sorting
from wgse.fasta.reference import Reference


class AlignmentMapFileInfo:
    def __init__(self) -> None:
        self.path: Path = None
        self.sorted: Sorting = None
        self.indexed: bool = None
        self.file_type: FileType = None
        self.reference_genome: Reference = None
        self.content : SequenceType = None
        self.primary: bool = None
        self.mitochondrial_dna_model: MitochondrialModelType = None
        self.build: int = None
        self.name_type_chromosomes: ChromosomeNameType = None
        self.name_type_mtdna: MitochondrialNameType = None
        self.sequence_count: int = None
        self.alignment_stats: AlignmentStats = None
        self.index_stats: dict[SequenceType, list[SequenceStatistics]] = None
        self.gender: Gender = None
