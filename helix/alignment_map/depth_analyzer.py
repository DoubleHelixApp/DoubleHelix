import subprocess
from threading import Thread
import time

from helix.data.coverage_stats import CoverageStats, DepthBin
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.data.file_type import FileType
from helix.data.sequence_type import SequenceType
from helix.reference.reference import ReferenceStatus
from helix.naming.converter import Converter
from helix.progress.base_progress_calculator import BaseProgressCalculator
from helix.utility.external import External
from helix.utility.regions import RegionType, Regions


class CoverageStatsCalculator(Thread):
    def __init__(
        self,
        file: AlignmentMapFile,
        region: RegionType = None,
        external=External(),
        regions=Regions(),
        progress=None,
    ) -> None:
        self._external = external
        self._progress = progress
        self._regions = regions
        self._progress_calc = None
        self._file = file
        self._region = region
        self._process: subprocess.Popen = None
        self._is_quitting = False
        self._result = None

    def run(self):
        self.get_stats()

    def get_stats(self):
        options = ["depth"]
        if self._region is not None:
            bed_path = self._regions.get_path(
                self._file.file_info.reference_genome.ready_reference.build,
                self._region,
                self._file.header.sequences.values(),
            )
            options.extend(["-b", str(bed_path)])
        else:
            options.append("-aa")

        if self._file.file_info.file_type == FileType.CRAM:
            if (
                self._file.file_info.reference_genome.status
                != ReferenceStatus.Available
            ):
                raise FileNotFoundError(
                    "Unable to find the reference genome for loaded file."
                )
            options.extend(
                ["-T", self._file.file_info.reference_genome.ready_reference]
            )

        options.append(str(self._file.path))

        if self._progress is not None:
            total_bases = sum(
                [
                    x.length
                    for x in self._file.header.sequences.values()
                    if x.type != SequenceType.Unmapped
                ]
            )
            self._progress_calc = BaseProgressCalculator(
                self._progress, total_bases, "Calculating depth"
            )
        self._process = self._external.samtools(
            options, stdout=subprocess.PIPE, text=True
        )
        self._result = self.analyze_depth_lines(
            iter(self._process.stdout.readline, ""), self._file
        )
        return self._result

    def analyze_depth_lines(self, lines, file: AlignmentMapFile):
        # Stats are organized in bins according to how many times
        # a specific position was read.
        entries_by_name = {}
        sums_by_name = {}

        for name, sequence in file.header.sequences.items():

            if sequence.type == SequenceType.Other:
                continue
            entries_by_name[name] = [0] * 4
            sums_by_name[name] = [0] * 4

        # Format is: sequence name, position (unused), # reads
        last_time = time.time()
        line_counter = 0
        for line in lines:
            if self._is_quitting:
                self._process.kill()
                return
            if self._progress_calc is not None:
                now = time.time()
                if (now - last_time) > 1:
                    self._progress_calc.compute(line_counter)
                    last_time = now
                line_counter += 1
            line = line.split()
            name = line[0]
            reads = int(line[2])

            if name not in entries_by_name:
                continue

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
            current = CoverageStats()
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
            current.non_zero_average = 0
            if non_zero_count != 0:
                current.non_zero_average = all_sums / non_zero_count

            current.all_average = all_sums / (all_count + 1)
            statistics.append(current)
        return statistics

    def kill(self):
        self._is_quitting = True
