import enum
from pathlib import Path

from helix.configuration import MANAGER_CFG
from helix.reference.genome_metadata_loader import Genome
from helix.utility.external import External
from helix.files.file_type_checker import FileType, FileTypeChecker


class BgzipAction(enum.Enum):
    Compress = 0
    Decompress = 1
    Reindex = 2


class BGzip:
    def __init__(
        self,
        external: External = External(),
        file_type_checker=FileTypeChecker(),
        config=MANAGER_CFG.EXTERNAL,
    ) -> None:
        self._type_checker = file_type_checker
        self._external = external
        self._config = config

    def perform(
        self,
        genome: Genome,
        file: Path,
    ) -> Path:
        file_type = self._type_checker.get_type(file)
        if file_type == FileType.BGZIP:
            if genome.fasta != file:
                if genome.fasta.exists():
                    genome.fasta.unlink()
                file.rename(genome.fasta)
            self.bgzip_wrapper(genome.fasta, None, BgzipAction.Reindex)
            return genome.fasta
        elif file_type == FileType.DECOMPRESSED:
            return self.bgzip_wrapper(file, genome.fasta)
        raise RuntimeError("Trying to compress a file that is not decompressed")

    def _gzip_filename(self, input: Path, action: BgzipAction):
        if action == BgzipAction.Compress:
            return Path(str(input) + ".gz")
        elif action == BgzipAction.Decompress:
            if len(input.suffixes) == 0:
                raise RuntimeError(
                    f"Unable to determine decompressed filename, invalid filename "
                    f"{str(input)} (no extensions)."
                )
            ext = "".join(input.suffixes[:-1])
            name = input.name.removesuffix("".join(input.suffixes))
            return input.with_name(name + ext)
        elif action == BgzipAction.Reindex:
            return Path(str(input) + ".gzi")
        else:
            raise RuntimeError(f"Action {action.name} not supported.")

    def bgzip_wrapper(
        self,
        input: Path,
        output: Path,
        action: BgzipAction = BgzipAction.Compress,
    ) -> Path:
        if action != BgzipAction.Reindex and output.exists():
            output.unlink()

        action_flags = {
            BgzipAction.Compress: "-if",
            BgzipAction.Decompress: "-d",
            BgzipAction.Reindex: "-r",
        }
        inferred_filename = self._gzip_filename(input, action)

        if action == BgzipAction.Reindex and output is None:
            output = inferred_filename

        self._external.bgzip(
            [action_flags[action], str(input), "-@", str(self._config.threads)],
            wait=True,
        )
        if not inferred_filename.exists():
            raise FileNotFoundError(
                "Inferred bgzip file name does not exist after bgzip compression."
            )

        if inferred_filename != output:
            inferred_filename.rename(output)
            if action == BgzipAction.Compress:
                target = Path(str(output) + ".gzi")
                inferred_gzi_filename = Path(str(inferred_filename) + ".gzi")
                if target.exists():
                    target.unlink()
                if not inferred_gzi_filename.exists():
                    raise FileNotFoundError(
                        f"BGZIP index not found for {inferred_gzi_filename.name}"
                    )
                inferred_gzi_filename.rename(target)
        return output
