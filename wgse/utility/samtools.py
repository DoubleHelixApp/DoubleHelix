from pathlib import Path

from wgse.configuration import MANAGER_CFG
from wgse.data.file_type import FileType
from wgse.utility.external import External


class Samtools:
    def __init__(
        self, external: External = External(), config=MANAGER_CFG.EXTERNAL
    ) -> None:
        self._external = external
        self._config = config

    def fasta_index(self, path: Path, output: Path = None):
        if output is None:
            output = Path(str(path) + ".fai")

        self._external.samtools(["faidx", path, "-o", output], wait=True)

    def header(self, file: Path, *args):
        return (
            self._external.samtools(["view", "-H", "--no-PG", *args, file], wait=True)
            .decode()
            .split("\n")
        )

    def make_dictionary(self, path: Path, output: Path = None):
        if output is None:
            output = Path(path.parent, path.name + ".dict")
        self._external.samtools(["dict", str(path), "-o", str(output)], wait=True)

    def index(self, path: Path, wait=True, io=None):
        self._external.samtools(
            ["index", "-@", self._config.threads, "-b", str(path)], wait=wait, io=io
        )

    def view(
        self,
        file: Path,
        target_format=FileType.SAM,
        output=None,
        region=None,
        subsample=None,
        cram_reference=None,
    ):
        options = []
        if target_format == FileType.BAM:
            options.append("-b")
        elif target_format == FileType.CRAM:
            options.append("-C")
        elif target_format == FileType.SAM:
            pass
        else:
            raise ValueError("Cannot view in format %s" % (target_format.name))

        if output is not None:
            options.append("-o")
            options.append(output)

        self._external.samtools(
            ["view", "-H", "--no-PG", file], wait=True
        ).decode().split("\n")

    def idxstats(self, input: Path):
        """Generate BAM index statistics"""
        self._external.samtools(["idxstat", input], wait=True)
