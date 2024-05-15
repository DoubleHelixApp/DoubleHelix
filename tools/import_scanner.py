import shutil
from pathlib import Path

import pefile


class ImportScanner:
    def __init__(self, exe: Path):
        self.exe = exe

    def get_dlls(self):
        to_scan = [self.exe.name]
        scanned = []

        dependencies = set([self.exe])
        directory = self.exe.parent

        while len(to_scan) > 0:
            file = to_scan.pop()
            pe = pefile.PE(str(Path(directory, file)))
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dependency = entry.dll.decode("utf-8")
                if Path(directory, dependency).exists():
                    if dependency not in scanned and dependency not in to_scan:
                        to_scan.append(dependency)
                    dependencies.add(Path(directory, dependency))
            scanned.append(file)
        return dependencies


if __name__ == "__main__":
    cygwin_root = Path("cygwin64", "usr", "local", "bin")

    files = [
        cygwin_root.joinpath("bwa.exe"),
        cygwin_root.joinpath("bgzip.exe"),
        cygwin_root.joinpath("samtools.exe"),
        cygwin_root.joinpath("htsfile.exe"),
        cygwin_root.joinpath("bcftools.exe"),
        cygwin_root.joinpath("tabix.exe"),
        cygwin_root.joinpath("minimap2.exe"),
        cygwin_root.joinpath("fastp.exe"),
        cygwin_root.joinpath("gzip.exe"),
    ]

    destination_root = Path("bare_minimum")
    if not destination_root.exists():
        destination_root.mkdir()

    for file in files:
        scanner = ImportScanner(file)
        binaries = scanner.get_dlls()

        for source_binary in binaries:
            destination_binary = destination_root.joinpath(source_binary.name)
            if not destination_binary.exists():
                shutil.copy(source_binary, destination_binary)
