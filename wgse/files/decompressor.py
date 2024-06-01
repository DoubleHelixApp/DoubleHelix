import gzip
import hashlib
import logging
import shutil
import typing
import zipfile
from pathlib import Path

from wgse.files.bgzip import BGzip, BgzipAction
from wgse.reference.genome_metadata_loader import Genome
from wgse.utility.external import External
from wgse.files.file_type_checker import FileType, FileTypeChecker


class Decompressor:
    def __init__(
        self,
        type_checker: FileTypeChecker = FileTypeChecker(),
        external: External = External(),
        bgzip_compressor=BGzip(),
    ) -> None:
        self._bgzip_compressor = bgzip_compressor
        self._external = external
        self._type_checker = type_checker

        self._handlers: typing.Dict[FileType, typing.Callable[[Path, Path], None]] = {
            FileType.GZIP: Decompressor.razf_gzip,
            FileType.RAZF_GZIP: Decompressor.razf_gzip,
            FileType.ZIP: Decompressor.zip,
            FileType.SEVENZIP: Decompressor.sevenzip,
            FileType.BZIP: Decompressor.bzip,
        }

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
                    "More than one file found inside the .zip, unable to proceed."
                )
            extracted = Path(f.extract(files[0], output_file.parent))
            if extracted != output_file:
                extracted.rename(output_file)

    def razf_gzip(self, input_file: Path, output_file: Path):
        self._bgzip_compressor.bgzip_wrapper(
            input_file, output_file, BgzipAction.Decompress
        )

    def calculate_md5_hash(self, filename: Path, chunk_size=4096):
        md5_hash = hashlib.md5()
        with filename.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def decompression_needed(self, genome: Genome, file: Path):
        if not file.exists():
            return True

        type = self._type_checker.get_type(file)
        # Shortcut in case we're dealing with a BGZIP file
        if type == FileType.BGZIP:
            if genome.bgzip_size is None:
                genome.bgzip_size = file.stat().st_size
                return False
            if file.stat().st_size == genome.bgzip_size:
                return False
        # Shortcut in case we're dealing with a FASTA file
        elif type == FileType.DECOMPRESSED:
            if genome.decompressed_size is None:
                return True
            if file.stat().st_size == genome.decompressed_size:
                return False
        return True

    def perform(self, genome: Genome, downloaded: Path = None):
        if not self.decompression_needed(genome, downloaded):
            return downloaded

        target = downloaded.with_suffix(".fa")
        if not self.decompression_needed(genome, target):
            return target

        if not downloaded.exists():
            raise FileNotFoundError(f"Unable to find file {downloaded.name}")

        type = self._type_checker.get_type(downloaded)
        if type not in self._handlers:
            raise RuntimeError(
                f"Trying to decompress a file with an unknown type: {downloaded.name}"
            )

        handler = self._handlers[type]
        logging.debug(
            f"Decompressing {genome.fasta.name}. {type.name} compression detected."
        )
        handler(self, downloaded, target)
        if not target.exists():
            raise RuntimeError(
                f"Error during the decompression of {str(genome)}. Decompressed file is not present."
            )

        if genome.decompressed_size is None:
            genome.decompressed_size = target.stat().st_size
        elif genome.decompressed_size != target.stat().st_size:
            raise RuntimeError(
                f"Error during the decompression of {str(genome)}. Size mismatch."
            )

        if genome.decompressed_md5 is None:
            genome.decompressed_md5 = self.calculate_md5_hash(target)
        elif genome.decompressed_md5 != self.calculate_md5_hash(target):
            raise RuntimeError(
                f"Error during the decompression of {str(genome)}. MD5 mismatch."
            )

        return target
