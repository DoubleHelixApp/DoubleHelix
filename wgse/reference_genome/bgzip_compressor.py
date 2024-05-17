from pathlib import Path

from wgse.utility.external import External
from wgse.reference_genome.genome_metadata_loader import Genome
from wgse.utility.file_type_checker import FileType, FileTypeChecker


class BGZIPCompressor:
    def __init__(self, external: External = External(), file_type_checker = FileTypeChecker()) -> None:
        self._type_checker = file_type_checker
        self._external = external

    def perform(self, genome: Genome, file: Path) -> Path:
        if self._type_checker.get_type(file) == FileType.BGZIP:
            if genome.fasta != file:
                if genome.fasta.exists():
                    genome.fasta.unlink()
                file.rename(genome.fasta)
            return genome.fasta
        return self._external.bgzip_wrapper(file, genome.fasta)