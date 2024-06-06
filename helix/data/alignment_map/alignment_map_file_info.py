from pathlib import Path

from helix.data.coverage_stats import CoverageStats
from helix.alignment_map.index_stats_calculator import SequenceStatistics
from helix.data.alignment_stats import AlignmentStats
from helix.data.chromosome_name_type import ChromosomeNameType
from helix.data.file_type import FileType
from helix.data.gender import Gender
from helix.data.mitochondrial_model_type import MitochondrialModelType
from helix.data.mitochondrial_name_type import MitochondrialNameType
from helix.data.sequence_type import SequenceType
from helix.data.sorting import Sorting
from helix.reference.reference import Reference


class AlignmentMapFileInfo:
    def __init__(self) -> None:
        self.path: Path = None
        self.sorted: Sorting = None
        self.indexed: bool = None
        self.file_type: FileType = None
        self.reference_genome: Reference = None
        self.content: SequenceType = None
        self.mitochondrial_dna_model: MitochondrialModelType = None
        self.build: int = None
        self.name_type_chromosomes: ChromosomeNameType = None
        self.name_type_mtdna: MitochondrialNameType = None
        self.sequence_count: int = None
        self.alignment_stats: AlignmentStats = None
        self.index_stats: list[SequenceStatistics] = None
        self.coverage_stats: CoverageStats = None
        self.gender: Gender = None
