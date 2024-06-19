import enum
from pathlib import Path

from helix.utility.external import External


class FileType(enum.Enum):
    ZIP = 0
    BZIP = 1
    SEVENZIP = 2
    # GZIP is not used ATM as it's not reliable.
    GZIP = 3
    BGZIP = 4
    RAZF_GZIP = 5
    DECOMPRESSED = 6


class FileTypeChecker:
    """Gets the type of a file trying to not relying on its extension (if possible)

    This class uses the utility `htsfile` to get the type of a file. If it fails to
    get the type of a file using `htsfile`, it will try to guess its type based on its
    extension.

    Examples:
        >>> input = Path("file.fasta")
        >>> checker = FileTypeChecker()
        >>> assert checker.get_type() == FileType.DECOMPRESSED
        >>> input = input.rename("file")
        >>> assert checker.get_ext() == ".fa"
    """

    _EXT_TO_TYPE = {
        ".7z": FileType.SEVENZIP,
        ".zip": FileType.ZIP,
        ".bz2": FileType.BZIP,
        ".bz": FileType.BZIP,
        ".gz": FileType.RAZF_GZIP,
        ".fa": FileType.DECOMPRESSED,
        ".fasta": FileType.DECOMPRESSED,
        ".fna": FileType.DECOMPRESSED,
    }

    _TYPE_TO_EXT = {
        FileType.SEVENZIP: ".7z",
        FileType.ZIP: ".zip",
        FileType.BZIP: ".bz2",
        FileType.RAZF_GZIP: ".fa.gz",
        FileType.GZIP: ".fa.gz",
        FileType.DECOMPRESSED: ".fa",
    }

    _HTSFILE_TO_TYPE = {
        "BGZF": FileType.BGZIP,
        "gzip": FileType.RAZF_GZIP,
        "RAZF": FileType.RAZF_GZIP,
        "FASTA": FileType.DECOMPRESSED,
    }

    def __init__(self, external: External = External()) -> None:
        self._external = external

    def get_type(self, file: Path) -> FileType:
        """Get a Type starting from a file path.

        Args:
            file (Path): Path of the file to analyze.

        Returns:
            Type | None: Type or None if the type is unknown.
        """
        # Extensions can be wrong or misleading; Use htsfile and
        # eventually fallback on extension.

        file_type = self._external.htsfile([str(file)], wait=True, text=True)
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
        """Get an extension based on the content of the file.

        NOTE: if the input file is gzipped/bgzipped, this function
        will assume the extension is .fa.gz

        Args:
            file (Path): Input file

        Returns:
            str: Extension
        """
        type = self.get_type(file)
        matches = [x for x in FileTypeChecker._EXT_TO_TYPE.items() if x[1] == type]
        if len(matches) > 0:
            return matches[0][0]
        return None
