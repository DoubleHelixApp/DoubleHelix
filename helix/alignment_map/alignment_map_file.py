import logging
import pickle
from pathlib import Path

from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.alignment_map.alignment_stats_calculator import AlignmentStatsCalculator
from helix.alignment_map.index_stats_calculator import (
    IndexStatsCalculator,
    SequenceStatistics,
)
from helix.configuration import MANAGER_CFG
from helix.data.alignment_map.alignment_map_file_info import AlignmentMapFileInfo
from helix.data.file_type import FileType
from helix.data.gender import Gender
from helix.data.mitochondrial_model_type import MitochondrialModelType
from helix.data.read_type import ReadType
from helix.data.sequence_type import SequenceType
from helix.data.sorting import Sorting
from helix.reference.reference import Reference, ReferenceStatus
from helix.progress.base_progress_calculator import BaseProgressCalculator
from helix.reference.repository import Repository
from helix.mtDNA.mt_dna import MtDNA
from helix.utility.samtools import Samtools

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
        ignore_meta: bool = False,
        samtools=Samtools(),
        repository: Repository = Repository(),
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
        self._ignore_meta = ignore_meta
        self.meta_file: Path = self.path.with_suffix(".pickle")
        self._repo = repository
        self._samtools = samtools
        self._mtdna = mtdna
        self._config = config
        self.header = self._load_header()
        self.file_info = self._initialize_file_info()

    def subset(self, percentage):
        """Returns a subset of the alignment map file based on the specified percentage.

        Args:
            percentage (float):
                The percentage of the original file to be subsetted. Must be between 0 and 1.

        Returns:
            An AlignmentMapFile object representing the subsetted file.

        Raises:
            ValueError if the input percentage is not within the valid range.
        """
        if percentage < 0.0 or percentage > 100.0:
            raise RuntimeError(
                f"Percentage needs to be between 0 and 100 to produce a subset but was {percentage}"
            )

        output = self.path.with_stem(f"{self.path.stem}_{percentage}_percent")
        percentage /= 100
        reference = None
        if self.file_info.file_type == FileType.CRAM:
            reference = self.file_info.reference_genome.ready_reference
            if reference is None:
                raise FileNotFoundError(
                    "Reference genome was not found but is mandatory for CRAM files"
                )

        self._samtools.view(
            self.path, output, subsample=percentage, reference=reference
        )
        self._samtools.index(output)

        if not output.exists():
            raise RuntimeError(f"Unable to find the subset file at {output}")
        return AlignmentMapFile(output)

    def _load_header(self) -> AlignmentMapHeader:
        return AlignmentMapHeader(self._samtools.header(self.path))

    def _to_fastq(self, io):
        options_fq = ["fastq"]
        if self.file_info.alignment_stats.read_type == ReadType.Paired:
            name_1 = self.path.stem + "_R1.fastq.gz"
            name_2 = self.path.stem + "_R2.fastq.gz"
            name_1 = self.path.parent.joinpath(name_1)
            name_2 = self.path.parent.joinpath(name_2)
            options_fq.extend(["-1", str(name_1), "-2", str(name_2)])
        elif self.file_info.alignment_stats.read_type == ReadType.Single:
            name = self.path.stem + ".fastq.gz"
            options_fq.extend(["-0", str(name)])
        else:
            raise RuntimeError("Unknown read type")
        options_fq.append("-n")
        options_fq.extend(["-@", self._config.threads])

        view = self._samtools.view(
            self.path,
            target_format=FileType.BAM,
            cram_reference=self.file_info.reference_genome.ready_reference,
            header=True,
            uncompressed=True,
            io=io,
        )

        # sort = self._samtools.sort(self.path)
        # fastq = self._samtools.fastq(self.path, )
        return view

    def _to_fasta(self, regions=None, progress=None):
        if self.file_info.reference_genome.ready_reference is None:
            raise RuntimeError("Unable to convert to FASTA without a valid reference.")
        input = self.path
        suffixes = self.path.suffixes.copy()
        suffixes[-1] = ".fasta"
        output = self.path.with_name(self.path.stem + "".join(suffixes))
        reference = str(  # noqa: F841
            self.file_info.reference_genome.ready_reference.fasta
        )

        io = None
        # TODO: get a percentage of input read file size according to region
        if progress is not None:
            io = BaseProgressCalculator(
                progress, self.path.stat().st_size, "Converting to FASTA"
            )
            io = io.compute_on_read_bytes

        # faidx = self._samtools.fasta_index(reference, regions=regions)
        consensus = self._samtools.consensus(input, output, io=io)
        return consensus

    def _to_alignment_map(self, target: FileType, regions, progress):
        suffixes = self.path.suffixes.copy()
        if len(suffixes) == 0:
            suffixes = [None]
        reference = None
        if target == FileType.BAM:
            suffixes[-1] = ".bam"
        elif target == FileType.CRAM:
            suffixes[-1] = ".cram"
            if self.file_info.reference_genome.ready_reference is None:
                raise RuntimeError(
                    "Reference genome was not found but is mandatory for CRAM files."
                )
            reference = self.file_info.reference_genome.ready_reference.fasta
        elif target == FileType.SAM:
            suffixes[-1] = ".sam"
        output = self.path.with_name(self.path.stem + "".join(suffixes))

        io = None
        # TODO: get a percentage of input read file size according to region
        if progress is not None:
            io = BaseProgressCalculator(
                progress, self.path.stat().st_size, f"Converting to {target.name}"
            )
            io = io.compute_on_read_bytes

        return self._samtools.view(
            self.path,
            target_format=target,
            output=output,
            regions=regions,
            cram_reference=reference,
            io=io,
            wait=False,
        )

    def convert(self, target: FileType, regions=None, progress=None):
        """
        Convert the input file to a different format.

        This function allows for converting a BAM file to other formats like FASTA or SAM.
        It also supports converting a BAM file with paired-end reads to FASTQ.

        Parameters
        ----------
        target : FileType
            The target file format to convert to. Can be one of the following:
            - FileType.BAM (default)
            - FileType.FASTA
            - FileType.SAM
            - FileType.CRAM

        regions : None or list of str
            A list of genomic regions that will be used for conversion.
            If None, all regions in the input file will be converted.

        progress : None or int
            The progress bar to display during the conversion process.
            If None, no progress bar will be displayed.

        Returns
        -------
        The converted file object.
        """

        if self.file_info.file_type == target:
            raise ValueError("Target and source file type for conversion are identical")
        if target == FileType.FASTA:
            return self._to_fasta(regions, progress)
        if target == FileType.FASTQ:
            return self._to_fastq(progress)
        return self._to_alignment_map(target, regions, progress)

    def load_meta(self):
        try:
            if self.meta_file.exists():
                with self.meta_file.open("rb") as f:
                    return pickle.load(f)
        except Exception as e:
            logger.error(
                f"Error when loading meta-information for {self.meta_file.name}: {e!s}"
            )
        return None

    def save_meta(self, file_info=None):
        try:
            if file_info is None:
                file_info = self.file_info
            with self.meta_file.open("wb") as f:
                pickle.dump(file_info, f)
        except Exception as e:
            logger.error(
                f"Error when saving meta-information for {self.meta_file.name}: {e!s}"
            )

    def _initialize_file_info(self):
        if not self._ignore_meta:
            meta = self.load_meta()
            if meta is not None:
                return meta
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
        file_info.mitochondrial_dna_model = self.get_mitochondrial_dna_type(
            file_info.reference_genome
        )

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
        self.save_meta(file_info)
        return file_info

    def get_mitochondrial_dna_type(self, reference: Reference):
        mitochondrial_dna_model = MitochondrialModelType.Unknown
        if reference.status == ReferenceStatus.Available:
            matching = reference.matching[0]
            if matching.mitochondrial_model is not None:
                mitochondrial_dna_model = MitochondrialModelType[
                    matching.mitochondrial_model
                ]
        return mitochondrial_dna_model

    def _indexed(self, type=None):
        if type is None:
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
