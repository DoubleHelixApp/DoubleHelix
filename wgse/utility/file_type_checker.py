import enum
from pathlib import Path

from wgse.utility.external import External


class Type(enum.Enum):
    ZIP = 0
    BZIP = 1
    SEVENZIP = 2
    # GZIP is not used ATM as it's not reliable.
    GZIP = 3
    BGZIP = 4
    RAZF_GZIP = 5
    DECOMPRESSED = 6


class FileTypeChecker:

    _EXT_TO_TYPE = {
        ".7z": Type.SEVENZIP,
        ".zip": Type.ZIP,
        ".bz2": Type.BZIP,
        ".bz": Type.BZIP,
        ".gz": Type.RAZF_GZIP,
        ".fa": Type.DECOMPRESSED,
        ".fasta": Type.DECOMPRESSED,
        ".fna": Type.DECOMPRESSED
    }
    
    _TYPE_TO_EXT = {
        Type.SEVENZIP: ".7z",
        Type.ZIP : ".zip",
        Type.BZIP: ".bz2",
        Type.RAZF_GZIP:".fa.gz",
        Type.GZIP:".fa.gz",
        Type.DECOMPRESSED: ".fa"
    }

    _HTSFILE_TO_TYPE = {
        "BGZF": Type.BGZIP,
        "gzip": Type.RAZF_GZIP,
        "RAZF": Type.RAZF_GZIP,
        "FASTA": Type.DECOMPRESSED,
    }

    def __init__(self, external: External=External()) -> None:
        self._external = external

    def get_type(self, file: Path) -> Type:
        """Get a Type starting from a file path.

        Args:
            file (Path): Path of the file to analyze.

        Returns:
            Type | None: Type or None if the type is unknown.
        """
        # Extensions can be wrong or misleading; Use htsfile and
        # eventually fallback on extension.

        file_type = self._external.get_file_type(file)
        for key, value in FileTypeChecker._HTSFILE_TO_TYPE.items():
            if key in file_type:
                return value

        # TODO: starting from .gz in _EXT_TO_TYPE, htsfile should really
        # be able to give something useful. If it isn't the case, it could
        # mean the file is corrupted. Unsure what's the best logic here.
        extension = file.suffix
        if extension in FileTypeChecker._EXT_TO_TYPE:
            return FileTypeChecker._EXT_TO_TYPE[extension]
        return None

    def get_extension(self, file: Path) -> str:
        type = self.get_type(file)
        matches = [x for x in FileTypeChecker._EXT_TO_TYPE.items() if x[1] == type]
        if len(matches) > 0:
            return matches[0][0]
        return None