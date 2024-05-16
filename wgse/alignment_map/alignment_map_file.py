import logging
import shlex
import subprocess
from pathlib import Path

from wgse.alignment_map.alignment_map_header import AlignmentMapHeader
from wgse.alignment_map.alignment_stats_calculator import AlignmentStatsCalculator
from wgse.alignment_map.index_stats_calculator import (
    IndexStatsCalculator,
    SequenceStatistics,
)
from wgse.configuration import MANAGER_CFG
from wgse.data.file_type import FileType
from wgse.data.mitochondrial_model_type import MitochondrialModelType
from wgse.data.alignment_map_file_info import (
    AlignmentMapFileInfo,
)
from wgse.data.sequence_type import SequenceType
from wgse.data.gender import Gender
from wgse.data.sorting import Sorting
from wgse.utility.external import External
from wgse.fasta.reference import Reference
from wgse.reference_genome.repository_manager import RepositoryManager
from wgse.utility.mt_dna import MtDNA
from wgse.utility.sequence_orderer import SequenceOrderer

logger = logging.getLogger(__name__)


class AlignmentMapFile:
    SUPPORTED_FILES = {
        ".bam": FileType.BAM,
        ".sam": FileType.SAM,
        ".cram": FileType.CRAM,
    }

    def __init__(
        self,
        path: Path,
        external: External = External(),
        repository: RepositoryManager = RepositoryManager(),
        mtdna: MtDNA = MtDNA(),
        config=MANAGER_CFG.EXTERNAL,
    ) -> None:
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Unable to find file {path.name}")
        if path.suffix.lower() not in AlignmentMapFile.SUPPORTED_FILES:
            raise RuntimeError(f"Unrecognized file extension: {path.name}")

        self.path: Path = path
        self._repo = repository
        self._external = external
        self._mtdna = mtdna
        self._config = config
        self.header = self._load_header()
        self.file_info = self._initialize_file_info()

    def subset(self, percentage):
        if percentage < 0.0 or percentage > 100.0:
            raise RuntimeError(
                f"Percentage needs to be between 0 and 100 to produce a subset but was {percentage}"
            )
        format_dependent_opt = ""
        if self.file_info.file_type == FileType.CRAM:
            reference = self.file_info.reference_genome.ready_reference
            if reference is None:
                raise FileNotFoundError(
                    f"Reference genome was not found but is mandatory for CRAM files"
                )
            format_dependent_opt = f'-C -T "{reference.fasta!s}"'
        elif self.file_info.file_type == FileType.BAM:
            format_dependent_opt = f"-b"

        output = self.path.with_stem(f"{self.path.stem}_{percentage}_percent")
        input = self.path

        percentage /= 100
        view_opt = shlex.split(
            f'view -bh -s {percentage:.1f} {format_dependent_opt} -@ {self._config.threads} -o "{output}" "{input}"'
        )
        index_opt = shlex.split(f'index "{output}"')

        self._external.samtools(view_opt, wait=True)
        self._external.samtools(index_opt, wait=True)

        if not output.exists():
            raise RuntimeError(f"Unable to find the subset file at {output}")
        return AlignmentMapFile(output)

    def _load_header(self) -> AlignmentMapHeader:
        lines = self._external.samtools(
            ["view", "-H", "--no-PG", self.path], stdout=subprocess.PIPE, wait=True
        )
        lines = lines.decode().split("\n")
        return AlignmentMapHeader(lines)

    def _to_fastq(self):
        pass

    def _to_fasta(self, regions=""):
        input = None
        output = None
        reference = str(self.file_info.reference_genome.ready_reference.fasta)
        faidx_opt = f"faidx {reference} {regions}"
        consensus_opt = f"consensus {input} -o {output}"

        faidx = self._external.samtools(faidx_opt, stdout=subprocess.PIPE)
        consensus = self._external.samtools(
            shlex.split(consensus_opt), stdin=faidx.stdout
        )
        consensus.communicate()
        return output

    def _to_alignment_map(self, target: FileType, region):
        suffixes = self.path.suffixes.copy()
        if len(suffixes) == 0:
            suffixes = [None]
        format_dependent_opt = ""
        if target == FileType.BAM:
            suffixes[-1] = ".bam"
            target_opt = "-b"
        elif target == FileType.CRAM:
            suffixes[-1] = ".cram"
            target_opt = "-C"
            if self.file_info.reference_genome.ready_reference is None:
                raise RuntimeError("Reference genome was not found but is mandatory for CRAM files.")
            reference = self.file_info.reference_genome.ready_reference.fasta
            format_dependent_opt = f'-T "{reference}"'
        elif target == FileType.SAM:
            suffixes[-1] = ".sam"
            target_opt = ""
        output = self.path.with_name(self.path.stem + "".join(suffixes))
        
        view_opt = f'view {target_opt} {format_dependent_opt} "{self.path!s}" {region} -o "{output}"'
        view_opt = shlex.split(view_opt)
        self._external.samtools(view_opt, wait=True)

    def convert(self, target: FileType, regions = ""):
        if self.file_info.file_type == target:
            raise ValueError("Target and source file type for conversion are identical")
        if target == FileType.FASTA:
            self._to_fasta()
        if target == FileType.FASTQ:
            self._to_fastq()
        self._to_alignment_map(target, regions)

    def _initialize_file_info(self):
        file_info = AlignmentMapFileInfo()
        file_info.path = self.path
        file_info.file_type = AlignmentMapFile.SUPPORTED_FILES[self.path.suffix.lower()]
        file_info.sorted = self.header.metadata.sorted
        file_info.name_type_mtdna = self.header.mtdna_name_type()
        file_info.name_type_chromosomes = self.header.chromosome_name_type()
        file_info.sequence_count = self.header.sequence_count()
        file_info.indexed = self._indexed(file_info.file_type)
        file_info.gender = Gender.Unknown
        file_info.reference_genome = self._repo.find(
            list(self.header.sequences.values())
        )
        file_info.mitochondrial_dna_model = self.get_mitochondrial_dna_type(file_info.reference_genome)

        # Compute IndexStats automatically only if it's inexpensive to do so.
        # Otherwise, let the caller explicitly request them.
        inexpensive_index_stats = file_info.indexed and file_info.file_type not in [
            FileType.CRAM,
            FileType.SAM,
        ]

        if inexpensive_index_stats:
            indexed_stats = IndexStatsCalculator(self.path)
            file_info.index_stats = indexed_stats.get_stats()
            file_info.gender = self.get_gender(file_info.index_stats)

        # If file is not sorted computing AlignmentStats is expensive.
        # Let the caller request them.
        if file_info.sorted == Sorting.Coordinate:
            is_cram = file_info.file_type == FileType.CRAM 
            has_reference = file_info.reference_genome.ready_reference is not None
            if is_cram and has_reference or not is_cram:
                calculator = AlignmentStatsCalculator(file_info)
                file_info.alignment_stats = calculator.get_stats()
        return file_info

    def get_mitochondrial_dna_type(self, reference: Reference):
        if self.header.sequences is None:
            return MitochondrialModelType.Unknown
        sequences = {
            SequenceOrderer.canonicalize(x.name): x
            for x in self.header.sequences.values()
        }
        if "M" not in sequences:
            return MitochondrialModelType.Unknown
        mito_md5 = None
        # If the sequence does not have MD5, we still have 
        # the chance to get it from the reference genome.
        # TODO: finish this thing
        # if sequences["M"].md5 is None:
        #     ref_sequences = [x.sequences for x in reference.matching]
        #     for sequence in ref_sequences:
        #         names = [x.name for x in SequenceOrderer(sequence) if names]

        model = self._mtdna.get_by_length(sequences["M"].length)
        if model is None:
            return MitochondrialModelType.Unknown
        return model.type

    def _indexed(self, type=None):
        if type == None:
            type = self.file_info.file_type

        file = str(self.path)
        if type == FileType.BAM:
            return Path(file + ".bai").exists()
        elif type == FileType.CRAM:
            return Path(file + ".crai").exists()
        return False

    def get_gender(self, stats: list[SequenceStatistics]):
        x_stats = [x for x in stats if x.type == SequenceType.X]
        y_stats = [x for x in stats if x.type == SequenceType.Y]
        x_length = 0
        y_length = 0

        if len(x_stats) != 0 and len(x_stats) != 1:
            return Gender.Unknown

        if len(y_stats) != 0 and len(y_stats) != 1:
            return Gender.Unknown

        if len(x_stats) == 1:
            x_length = x_stats[0].mapped + x_stats[0].unmapped
        if len(y_stats) == 1:
            y_length = y_stats[0].mapped + y_stats[0].unmapped

        if x_length == 0 and y_length == 0:
            return Gender.Unknown
        elif y_length == 0 or (x_length / y_length) > 20:
            return Gender.Female
        else:
            return Gender.Male
