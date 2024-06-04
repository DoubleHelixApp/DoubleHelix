import shutil
from pathlib import Path

import pefile


class ImportScanner:
    def __init__(self, paths: list[Path]):
        self.paths = paths

    def get_dlls(self, binary):
        to_scan = [binary]
        scanned = []

        dependencies = set([binary])
        while len(to_scan) > 0:
            file = to_scan.pop()
            pe = pefile.PE(str(file))
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dependency = entry.dll.decode("utf-8")
                for path in self.paths:
                    target = Path(path, dependency)
                    if target.exists():
                        if target not in scanned and target not in to_scan:
                            to_scan.append(target)
                        dependencies.add(target)
            scanned.append(file)
        return dependencies


if __name__ == "__main__":
    """This script will scan certain executables and
    recursively look for dependencies.
    """

    msys2_additional_path = Path("/", "usr", "bin")

    files = [
        Path("bwa", "bwa.exe"),
        Path("htslib", "bgzip.exe"),
        Path("htslib", "tabix.exe"),
        Path("htslib", "htsfile.exe"),
        Path("samtools", "samtools.exe"),
        Path("bcftools", "bcftools.exe"),
        Path("minimap2", "minimap2.exe"),
    ]

    destination_root = Path("helix", "third_party")
    if not destination_root.exists():
        destination_root.mkdir(parents=True, exist_ok=True)

    destination_root.joinpath("__init__.py").touch()

    for file in files:
        scanner = ImportScanner([msys2_additional_path])
        binaries = scanner.get_dlls(file)

        for source_binary in binaries:
            destination_binary = destination_root.joinpath(source_binary.name)
            if not destination_binary.exists():
                shutil.copy(source_binary, destination_binary)
