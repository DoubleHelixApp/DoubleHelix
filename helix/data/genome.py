import hashlib
import typing
from pathlib import Path

from helix.data.build import Build
from helix.data.sequence import Sequence


class Genome:
    def __init__(
        self,
        fasta_url: str,
        fai_url: str = None,
        gzi_url: str = None,
        suffix: str = None,
        build: str = None,
        source: str = None,
        sequences: typing.List[Sequence] = None,
        description: str = None,
        download_size: int = None,
        decompressed_size: int = None,
        bgzip_size: int = None,
        downloaded_md5: str = None,
        decompressed_md5: str = None,
        bgzip_md5: str = None,
        mitochondrial_model=None,
        parent_folder=Path("."),
    ) -> None:
        self.fasta_url = fasta_url
        self.fai_url = fai_url
        self.gzi_url = gzi_url
        self.suffix = suffix
        self.build = build
        self.source = source
        self.sequences = sequences
        self.description = description
        self.download_size = download_size
        self.decompressed_size = decompressed_size
        self.bgzip_size = bgzip_size
        self.downloaded_md5 = downloaded_md5
        self.decompressed_md5 = decompressed_md5
        self.bgzip_md5 = bgzip_md5
        self.mitochondrial_model = mitochondrial_model
        # Not serialized as it depends on the config
        self.__parent_folder = parent_folder
        # Not serialized as it's populated at runtime
        self.__parent: Build = None

    @property
    def parent_folder(self):
        return self.__parent_folder

    @parent_folder.setter
    def parent_folder(self, parent: Path):
        if isinstance(parent, str):
            parent = Path(parent)
        self.__parent_folder = parent

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @property
    def url_hash(self) -> str:
        url = bytes(self.fasta_url, encoding="utf8")
        return hashlib.md5(url).hexdigest()

    @property
    def all(self) -> typing.List[Path]:
        return [
            self.fasta,
            self.gzi,
            self.nbin,
            self.nbuc,
            self.bed,
            self.fai,
            self.dict,
        ]

    @property
    def name_only(self) -> str:
        if self.suffix is not None:
            filename = f"{self.build}_{self.suffix}_{self.source}_{self.url_hash[0:8]}"
        else:
            filename = f"{self.build}_{self.source}_{self.url_hash[0:8]}"
        return filename

    @property
    def no_extensions(self) -> Path:
        return self.__parent_folder.joinpath(self.name_only)

    @property
    def fasta(self) -> Path:
        return Path(str(self.no_extensions) + ".fa.gz")

    @property
    def decompressed(self) -> Path:
        return Path(str(self.no_extensions) + ".fa")

    @property
    def gzi(self) -> Path:
        return Path(str(self.fasta) + ".gzi")

    @property
    def fai(self) -> Path:
        return Path(str(self.fasta) + ".fai")

    @property
    def nbin(self) -> Path:
        return Path(str(self.no_extensions) + "_nbin.csv")

    @property
    def nbuc(self) -> Path:
        return Path(str(self.no_extensions) + "_nbuc.csv")

    @property
    def bed(self) -> Path:
        return Path(str(self.no_extensions) + "_nreg.bed")

    @property
    def dict(self) -> Path:
        return Path(str(self.no_extensions) + ".dict")

    def __repr__(self) -> str:
        return self.name_only

    def __str__(self) -> str:
        return self.__repr__()
