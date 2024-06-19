import hashlib
import logging
import os
from pathlib import Path

import certifi
import pycurl
from google.cloud import storage

from helix.configuration import MANAGER_CFG
from helix.progress.base_progress_calculator import BaseProgressCalculator
from helix.progress.file_io_monitor import FileIOMonitor
from helix.reference.genome_metadata_loader import Genome
from helix.files.file_type_checker import FileTypeChecker
from helix.utility.unit_prefix import UnitPrefix

HANDLERS = {}
SIZE_HANDLERS = {}


def uri_handler(uri):
    def decorator(f):
        global HANDLERS
        HANDLERS[uri] = f
        return f

    return decorator


def size_handler(uri):
    def decorator(f):
        global SIZE_HANDLERS
        SIZE_HANDLERS[uri] = f
        return f

    return decorator


class Downloader:

    def __init__(
        self,
        config=MANAGER_CFG.REPOSITORY,
        file_type_checker: FileTypeChecker = FileTypeChecker(),
        curl_class=pycurl.Curl,
    ) -> None:
        if file_type_checker is None:
            raise RuntimeError("FileTypeChecker cannot be None.")

        self._config = config
        self._curl_class = curl_class
        self.file_type_checker = file_type_checker
        self._logger = logging.getLogger("downloader")

    def size_pycurl(self, url: str):
        curl = self._curl_class()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.NOBODY, 1)
        curl.perform()
        length = int(curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD))
        if length == -1:
            return None
        if length == 0:
            return None
        return length

    def get_file_size(self, url: str):
        for handler in SIZE_HANDLERS.keys():
            if url.startswith(handler):
                return SIZE_HANDLERS[handler](self, url)
        return self.size_pycurl(url)

    def calculate_md5_hash(self, filename: Path, chunk_size=4096):
        md5_hash = hashlib.md5()
        with filename.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @size_handler("https://storage.cloud.google.com")
    @size_handler("gs://")
    def size_google(self, genome: Genome):
        storage_client = storage.Client.create_anonymous_client()
        uri = genome.fasta_url.strip()
        if not uri.startswith("gs://"):
            uri = "gs://" + uri.replace("https://storage.cloud.google.com/", "")

        blob = storage.Blob.from_string(uri, client=storage_client)
        blob.reload()
        return blob.size

    @uri_handler("https://storage.cloud.google.com")
    @uri_handler("gs://")
    def download_google(self, genome: Genome, callback: any):
        storage_client = storage.Client.create_anonymous_client()
        uri = genome.fasta_url.strip()
        if not uri.startswith("gs://"):
            uri = "gs://" + uri.replace("https://storage.cloud.google.com/", "")

        blob = storage.Blob.from_string(uri, client=storage_client)
        blob.reload()
        if genome.download_size is None:
            genome.download_size = blob.size
        if genome.downloaded_md5 is None:
            genome.downloaded_md5 = blob.md5_hash

        target = self._config.temporary.joinpath(genome.name_only)

        if target.exists():
            if target.stat().st_size == genome.download_size:
                return self.post_download_action(genome, target)
        base_calc = BaseProgressCalculator(callback, genome.download_size, "Download")
        monitor = FileIOMonitor(
            target, base_calc.compute_on_write_bytes, genome.download_size
        )
        blob.download_to_filename(target)
        monitor.quit()
        return self.post_download_action(genome, target)

    def post_download_action(self, genome: Genome, downloaded: Path):
        md5 = self.calculate_md5_hash(downloaded)
        if genome.downloaded_md5 is None:
            genome.downloaded_md5 = md5
        elif genome.downloaded_md5 != md5:
            downloaded.unlink()
            raise RuntimeError(f"MD5 for {genome} is not matching and was deleted.")

        extension = self.file_type_checker.get_extension(downloaded)

        if extension is None:
            _, ext = os.path.splitext(genome.fasta_url)
            extension = ext.lower()

        if extension is None:
            raise RuntimeError(
                f"Format file for {genome} was not recognized. Aborting."
            )

        if downloaded.suffix != extension:
            target = downloaded.with_suffix(extension)
            if target.exists():
                target.unlink()
            downloaded.rename(target)
            downloaded = target
        return downloaded

    def perform(self, genome: Genome, progress: any = None) -> Path:
        for handler in HANDLERS.keys():
            if genome.fasta_url.startswith(handler):
                return HANDLERS[handler](self, genome, progress)
        return self.download_pycurl(genome, progress)

    def download_pycurl(self, genome: Genome, progress: any):
        if genome.download_size is None:
            genome.download_size = self.get_file_size(genome.fasta_url)
            if genome.download_size is None:
                raise RuntimeError(f"Unable to download file {genome.fasta_url}")

        target = self._config.temporary.joinpath(genome.name_only)

        resume_from = None
        if target is not None and target.exists():
            if target.stat().st_size == genome.download_size:
                return self.post_download_action(genome, target)
            else:
                resume_from = target.stat().st_size

        progress_calc = None
        if progress is not None:
            progress_calc = BaseProgressCalculator(
                progress, genome.download_size, "Download"
            )

        total = UnitPrefix.convert_bytes(genome.download_size)
        resume = UnitPrefix.convert_bytes(resume_from if resume_from is not None else 0)
        url = genome.fasta_url
        self._logger.info(
            "Downloading file from %s, resuming from %s (%s total)"
            % (url, resume, total)
        )

        self.download_file(genome.fasta_url, target, resume_from, progress_calc)
        return self.post_download_action(genome, target)

    def download_file(
        self,
        url: str,
        target: Path,
        resume_from: int = None,
        progress_calc: BaseProgressCalculator = None,
    ):
        curl = self._curl_class()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.CAINFO, certifi.where())

        if resume_from is not None:
            curl.setopt(pycurl.RESUME_FROM, resume_from)

        if progress_calc is not None:
            curl.setopt(pycurl.NOPROGRESS, False)
            curl.setopt(
                pycurl.PROGRESSFUNCTION,
                lambda _tot_down, down, _tot_up, _up: progress_calc.compute(down),
            )

        try:
            with target.open("wb" if resume_from is None else "ab") as f:
                curl.setopt(pycurl.WRITEDATA, f)
                curl.perform()
                curl.close()
        finally:
            if progress_calc is not None:
                progress_calc.compute(None)
