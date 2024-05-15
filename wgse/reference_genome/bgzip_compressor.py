from pathlib import Path

from wgse.utility.external import External
from wgse.reference_genome.genome_metadata_loader import Genome


class BGZIPCompressor:
    def __init__(self, external: External = External()) -> None:
        self._external = external

    def perform(self, genome: Genome, file: Path) -> Path:
            return self._external.bgzip_wrapper(file, genome.fasta)