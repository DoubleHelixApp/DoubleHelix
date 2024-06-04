import subprocess
from pathlib import Path

from helix.data.sequence_type import SequenceType
from helix.utility.external import External
from helix.naming.converter import Converter


class SequenceStatistics:
    def __init__(self, type, name, reference_length, mapped, unmapped) -> None:
        self.type: SequenceType = type
        self.name: str = name
        self.reference_length: int = reference_length
        self.unmapped: int = unmapped
        self.mapped: int = mapped


class IndexStatsCalculator:
    def __init__(self, file: Path, external=External()) -> None:
        if not file.exists():
            raise RuntimeError(f"Unable to find file {file.name}")

        self._file = file
        self._external = external

    def get_stats(self):
        stats: list[SequenceStatistics] = []

        stats_text = self._external.samtools(
            ["idxstats", self._file], stdout=subprocess.PIPE, wait=True
        )
        stats_text: list[str] = stats_text.decode().split("\n")
        for line in stats_text:
            # Line format is: name, length, # mapped, # unmapped
            # http://www.htslib.org/doc/samtools-idxstats.html
            chromosome_type = None
            line = line.strip()
            if line == "":
                continue
            elements = line.split("\t")
            name = elements[0]
            reference_length = int(elements[1])
            mapped = int(elements[2])
            unmapped = int(elements[3])

            chromosome_type = Converter.get_type(name)

            stats.append(
                SequenceStatistics(
                    chromosome_type, name, reference_length, mapped, unmapped
                )
            )

        return stats
