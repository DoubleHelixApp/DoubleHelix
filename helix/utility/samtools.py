from pathlib import Path
import shlex
import subprocess

from helix.configuration import MANAGER_CFG
from helix.data.file_type import FileType
from helix.utility.external import External


class Samtools:
    def __init__(
        self,
        external: External = External(),
        config=MANAGER_CFG.EXTERNAL,
        repo=MANAGER_CFG.REPOSITORY,
    ) -> None:
        self._external = external
        self._config = config
        self._repository_config = repo

    def fasta_index(self, input: Path, output: Path = None, regions=None, io=None):
        faidx_opt = ["faidx", input]
        if regions is not None:
            faidx_opt.append(regions)
        if output is not None:
            faidx_opt.extend(["-o", output])
        return self._external.samtools(faidx_opt, stdout=subprocess.PIPE, io=io)

    def consensus(self, input: Path, output: Path, stdin=None, io=None):
        consensus_opt = f'consensus "{input!s}" -o "{output!s}"'
        consensus_opt = shlex.split(consensus_opt)
        return self._external.samtools(consensus_opt, stdin=stdin, io=io)

    def header(self, file: Path, *args):
        return self._external.samtools(
            ["view", "-H", "--no-PG", *args, file], wait=True, text=True
        ).split("\n")

    def make_dictionary(self, path: Path, output: Path = None):
        if output is None:
            output = Path(path.parent, path.name + ".dict")
        self._external.samtools(["dict", str(path), "-o", str(output)], wait=True)

    def index(self, path: Path, wait=True, io=None):
        self._external.samtools(
            ["index", "-@", self._config.threads, "-b", str(path)], wait=wait, io=io
        )

    def index_stats(self, path: Path, wait=True, io=None):
        self._external.samtools(
            ["idxstats", path, "-@", self._config.threads], wait=wait, io=io
        )

    def sort(
        self, file: Path, output: Path = None, format: FileType = FileType.SAM, io=None
    ):
        options = ["sort", "-T", self._repository_config.temporary, "-n"]
        options.extend(["-@", self._config.threads])
        if output is not None:
            options.extend(["-o", str(output)])
        if format == FileType.SAM:
            options.extend(["-O", "sam"])
        elif format == FileType.BAM:
            options.extend(["-O", "bam"])
        else:
            raise RuntimeError("Unsupported file type")

        options.append(str(file))
        return self._external.samtools(options, io=io)

    def view(
        self,
        file: Path,
        target_format=FileType.SAM,
        output: Path = None,
        regions: str = None,
        subsample: float = None,
        cram_reference: Path = None,
        header=False,
        uncompressed=False,
        io=None,
        wait=True,
    ):
        options = ["view", "--no-PG"]
        if target_format == FileType.BAM:
            options.append("-b")
        elif target_format == FileType.CRAM:
            options.extend(["-C", "-T", str(cram_reference)])
        elif target_format == FileType.SAM:
            pass
        else:
            raise ValueError("Cannot view in format %s" % (target_format.name))

        if header:
            options.append("-h")
        if uncompressed:
            options.append("-u")

        options.append(str(file))
        if output is not None:
            options.append("-o")
            options.append(output)

        if regions is not None:
            options.append(regions)

        if subsample is not None:
            options.extend(["-s", str(subsample)])

        options.extend(["-@", self._config.threads])

        return self._external.samtools(options, wait=wait, io=io, text=True)
