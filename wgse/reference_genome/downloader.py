import glob
import hashlib
import logging
import os
from pathlib import Path

import pycurl
from google.cloud import storage

from wgse.configuration import MANAGER_CFG
from wgse.reference_genome.genome_metadata_loader import Genome
from wgse.utility.file_type_checker import FileTypeChecker

logger = logging.getLogger(__name__)
# There libs are very chatty for everything less than WARNING
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)

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
        config = MANAGER_CFG.REPOSITORY,
        file_type_checker: FileTypeChecker = FileTypeChecker(),
    ) -> None:
        if file_type_checker is None:
            raise RuntimeError("FileTypeChecker cannot be None.")

        self._config = config
        self._progressbar = None
        self.file_type_checker = file_type_checker

    def size_pycurl(self, url: str):
        curl = pycurl.Curl()
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
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def pre_download_action(self, genome: Genome):
        # Until it's in the temporary directory, the file has
        # a known name but it may have an unknown extension.
        # The extension is assigned after the file is downloaded
        # based on the file content (as the URL can be misleading).
        # As a consequence, the only way to find a file is to
        # look at its size/MD5.

        target = self._config.temporary.joinpath(genome.url_hash)
        if target.exists():
            return target

        files = glob.glob(f"{target}.*")
        for file in files:
            file = Path(file)
            if file.stat().st_size == genome.download_size:
                return file
        return target

    @size_handler("https://storage.cloud.google.com")
    @size_handler("gs://")
    def size_google(self, genome : Genome):
        chunk_size = 1024*1024
        storage_client = storage.Client.create_anonymous_client()
        uri = genome.fasta_url.strip()
        if not uri.startswith("gs://"):
            uri = 'gs://' + uri.replace('https://storage.cloud.google.com/', '')

        blob = storage.Blob.from_string(uri, client=storage_client)
        blob.reload()
        return blob.size

    @uri_handler("https://storage.cloud.google.com")
    @uri_handler("gs://")
    def download_google(self, genome : Genome, callback : any):
        storage_client = storage.Client.create_anonymous_client()
        uri = genome.fasta_url.strip()
        if not uri.startswith("gs://"):
            uri = 'gs://' + uri.replace('https://storage.cloud.google.com/', '')

        blob = storage.Blob.from_string(uri, client=storage_client)
        blob.reload()
        if genome.download_size is None:
            genome.download_size = blob.size
        
        target = self.pre_download_action(genome)
        
        if target.exists():
            if target.stat().st_size == genome.download_size:
                return self.post_download_action(genome, target)

        blob.download_to_filename(target)
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
            downloaded.rename(target)
            downloaded = target
        return downloaded

    def perform(self, genome: Genome, callback: any = False) -> Path:
        for handler in HANDLERS.keys():
            if genome.fasta_url.startswith(handler):
                return HANDLERS[handler](self, genome, callback)
        return self.download_pycurl(genome, callback)

    def download_pycurl(self, genome: Genome, callback: any):
        if genome.download_size is None:
            genome.download_size = self.get_file_size(genome.fasta_url)
            if genome.download_size == None:
                raise RuntimeError(f"Unable to download file {genome.fasta_url}")
        
        target = self.pre_download_action(genome)
        
        resume_from = None
        if target.exists():
            if target.stat().st_size == genome.download_size:
                return self.post_download_action(genome, target)
            else:
                resume_from = target.stat().st_size

        with target.open("wb" if resume_from is None else "ab") as f:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, genome.fasta_url)
            curl.setopt(pycurl.WRITEDATA, f)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            if callback is not False or callback is not None:
                curl.setopt(pycurl.NOPROGRESS, False)

            if resume_from is not None:
                curl.setopt(pycurl.RESUME_FROM, resume_from)

            # TODO: find an easy way (if it exists) to load ca-bundle
            # on every platform. Or remove this TODO as we don't really
            # care about people MITM-ing our reference genome download.
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)

            if callback is not None and callback is not False:
                curl.setopt(
                    pycurl.PROGRESSFUNCTION,
                    lambda tot, n, tot_up, n_up: callback(tot, n),
                )

            curl.perform()
            curl.close()
            # Signal the download is done
            if callback is not None and callback is not False:
                callback(None, None)
        return self.post_download_action(genome, target)
