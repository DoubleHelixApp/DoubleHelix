from enum import Enum
import subprocess

from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.sequence_naming.converter import Converter
from wgse.utility.external import External
from wgse.utility.regions import RegionType, Regions


class DepthBin(Enum):
    Zero = 0
    Between0And3 = 1
    Between3And7 = 2
    MoreThan7 = 3


class DepthStats:
    def __init__(self) -> None:
        self.sequence_name: str = None
        self.bin_entries: list[int] = None
        self.bin_sum: list[int] = None
        self.non_zero_percentage: float = 0
        self.non_zero_average: float = 0
        self.all_average: float = 0


class DepthAnalyzer:
    def __init__(self, external=External(), regions=Regions()) -> None:
        self._external = external
        self._regions = regions

    def analyze_aligned_file(self, file: AlignmentMapFile, region: RegionType = None):
        options = ["depth"]
        if region is not None:
            bed_path = self._regions.get_path(region)

        process = self._external.samtools(
            [
                "depth",
                "-aa",
                str(file.path),
            ],
            stdout=subprocess.PIPE,
        )
        self.analyze_depth_lines(iter(process.stdout.readline, b""), file)

    def analyze_depth_lines(self, lines, file: AlignmentMapFile):
        # Stats are organized in bins according to how many times
        # a specific position was read.
        entries_by_name = {}
        sums_by_name = {}

        entries_by_name = {x: [0] * 4 for x in file.header.sequences.keys()}
        sums_by_name = {x: [0] * 4 for x in file.header.sequences.keys()}

        # Format is: sequence name, position (unused), # reads
        for line in lines:
            line = line.decode().split()
            name = line[0]
            reads = int(line[2])

            if reads > 7:
                entries_by_name[name][DepthBin.MoreThan7] += 1
                sums_by_name[name][DepthBin.MoreThan7] += reads
            elif reads > 3:
                entries_by_name[name][DepthBin.Between3And7] += 1
                sums_by_name[name][DepthBin.Between3And7] += reads
            elif reads > 0:
                entries_by_name[name][DepthBin.Between0And3] += 1
                sums_by_name[name][DepthBin.Between0And3] += reads
            elif reads == 0:
                entries_by_name[name][DepthBin.Zero] += 1

        statistics = []
        for name in entries_by_name:
            current = DepthStats()
            current.sequence_name = Converter.canonicalize(name)
            current.bin_entries = entries_by_name[name]
            current.bin_sum = sums_by_name[name]

            zero_count = current.bin_entries[DepthBin.Zero]
            non_zero_count = sum(
                [
                    current.bin_entries[DepthBin.Between0And3],
                    current.bin_entries[DepthBin.Between3And7],
                    current.bin_entries[DepthBin.MoreThan7],
                ]
            )

            all_sums = sum(current.bin_sum)
            all_count = zero_count + non_zero_count

            current.non_zero_percentage = non_zero_count / (all_count + 1)
            current.non_zero_average = all_sums / non_zero_count
            current.all_average = all_sums / (all_count + 1)
            statistics.append(current)
        return statistics
