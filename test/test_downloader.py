from helix.configuration import RepositoryConfig
from helix.data.genome import Genome
from helix.files.downloader import Downloader
import pycurl

from test.utility import MockPath


class MockPycurl:
    def __init__(self, url, content="TEST DATA") -> None:
        self.url = url
        self.dict_opt = {}
        self.length = len(content)
        self.content = content

    def getinfo(self, info):
        if info == pycurl.CONTENT_LENGTH_DOWNLOAD:
            return self.length
        raise RuntimeError("Unsupported getinfo value")

    def setopt(self, opt, value):
        self.dict_opt[opt] = value

    def perform(self):
        self.dict_opt[pycurl.WRITEDATA].write(self.content)

    def close(self):
        pass


class FileTypeCheckerMock:
    def __init__(self, ext=".fa") -> None:
        self._ext = ext

    def get_extension(self, _):
        return self._ext


def test_downloader():
    reference_content = "foo\nbar"

    genome = Genome(
        "https://www.example.com/ref.fa", download_size=len(reference_content)
    )
    cfg = RepositoryConfig()
    cfg.temporary = MockPath(
        "temporary",
        content={genome.url_hash: MockPath(genome.url_hash, buffer=reference_content)},
    )
    type_check = FileTypeCheckerMock()
    pycurl = MockPycurl(genome.fasta_url, reference_content)
    downloader = Downloader(cfg, type_check, pycurl)
    downloader.perform(genome)
