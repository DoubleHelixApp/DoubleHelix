import gzip
import hashlib
import logging
import shutil
import typing
import zipfile
from pathlib import Path

from helix.files.gzip import GZip, GZipAction
from helix.reference.genome_metadata_loader import Genome
from helix.files.file_type_checker import FileType, FileTypeChecker


class Decompressor:
    def __init__(
        self,
        type_checker: FileTypeChecker = FileTypeChecker(),
        gzip_compressor=GZip(),
    ) -> None:
        self._gzip_compressor = gzip_compressor
        self._type_checker = type_checker

        self._handlers: typing.Dict[FileType, typing.Callable[[Path, Path], None]] = {
            FileType.GZIP: Decompressor.razf_gzip,
            FileType.RAZF_GZIP: Decompressor.razf_gzip,
            FileType.ZIP: Decompressor.zip,
            FileType.SEVENZIP: Decompressor.sevenzip,
            FileType.BZIP: Decompressor.bzip,
            FileType.DECOMPRESSED: Decompressor.dummy,
            FileType.BGZIP: Decompressor.dummy,
        }

    def dummy(self, input_file: Path, output_file: Path):
        # Dummy handler as the file it's either already compressed
        # in the target format or decompressed.
        if input_file != output_file:
            if output_file.exists():
                output_file.unlink()
            input_file.rename(output_file)

    def gz(self, input_file: Path, output_file: Path):
        # Not reliable with RAZF and currently not used.
        with gzip.open(str(input_file), "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    def sevenzip(self, input_file: Path, output_file: Path):
        raise NotImplementedError()

    def bzip(self, input_file: Path, output_file: Path):
        raise NotImplementedError()

    def zip(self, input_file: Path, output_file: Path):
        with zipfile.ZipFile(str(input_file), "r") as f:
            files = f.namelist()
            if len(files) > 1:
                raise RuntimeError(
                    f"Error decompressing {input_file!s}: zip contains more than 1 file"
                )
            extracted = Path(f.extract(files[0], output_file.parent))
            if extracted != output_file:
                extracted.rename(output_file)

    def razf_gzip(self, input_file: Path, output_file: Path):
        self._gzip_compressor.gzip(input_file, output_file, GZipAction.Decompress)

    def calculate_md5_hash(self, filename: Path, chunk_size=4096):
        md5_hash = hashlib.md5()
        with filename.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def perform(self, genome: Genome, downloaded: Path = None):
        if not downloaded.exists():
            raise FileNotFoundError(
                f"Error decompressing {str(genome)}: "
                f"unable to find input file {downloaded!s}"
            )

        no_ext = downloaded.name.removesuffix("".join(downloaded.suffixes))
        target = downloaded.with_name(no_ext + ".fa")
        type = self._type_checker.get_type(downloaded)
        if type not in self._handlers:
            raise RuntimeError(f"Error decompressing {str(genome)}: unknown type")

        handler = self._handlers[type]
        logging.debug(
            f"Decompressing {downloaded!s}. {type.name} compression detected."
        )
        handler(self, downloaded, target)
        if not target.exists():
            raise RuntimeError(
                f"Error decompressing {str(genome)}: Decompressed file not found"
            )

        type = self._type_checker.get_type(target)

        if type != FileType.DECOMPRESSED:
            # If we've a bgzip, the file is never decompressed.
            return target

        if genome.decompressed_size is None:
            genome.decompressed_size = target.stat().st_size
        elif genome.decompressed_size != target.stat().st_size:
            raise RuntimeError(f"Error decompressing {str(genome)}: size mismatch")

        if genome.decompressed_md5 is None:
            genome.decompressed_md5 = self.calculate_md5_hash(target)
        elif genome.decompressed_md5 != self.calculate_md5_hash(target):
            raise RuntimeError(f"Error decompressing {str(genome)}: MD5 mismatch")

        return target
