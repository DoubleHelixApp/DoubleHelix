from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
    path: Optional[Path] = None
    sorted: Sorting = Sorting.Unknown
    indexed: Optional[bool] = None
    file_type: FileType = FileType.Unknown
    reference_genome: Optional[Reference] = None
    mitochondrial_dna_model: MitochondrialModelType = MitochondrialModelType.Unknown
    build: Optional[int] = None
    name_type_chromosomes: ChromosomeNameType = ChromosomeNameType.Unknown
    name_type_mtdna: MitochondrialNameType = MitochondrialNameType.Unknown
    sequence_count: Optional[int] = None
    alignment_stats: Optional[AlignmentStats] = None
    index_stats: list[SequenceStatistics] = []
    coverage_stats: Optional[CoverageStats] = None
    gender: Gender = Gender.Unknown
