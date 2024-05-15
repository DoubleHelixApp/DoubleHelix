import subprocess
from pathlib import Path

import tqdm

from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.utility.external import External


class DepthStats:
    def __init__(self) -> None:
        self.zero_reads: int = 0
        self.max_3_reads: int = 0
        self.between_3_and_7_reads: int = 0
        self.greater_7_reads: int = 0
        self.read_count: int = 0


class DepthAnalyzer:
    def __init__(self, external: External = External()) -> None:
        self._external = external
        pass

    def analyze_aligned_file(self, path: Path):
        file = AlignmentMapFile(path, self._external)

        process = self._external.samtools(
            ["depth", "-a", "-b", "C:\\Users\\Marco\\Documents\\Bioinformatics\\WGSExtractv4-dev\\reference\\xgen_plus_spikein.GRCh38.bed", str(path)], stdout=subprocess.PIPE
        )
        self.analyze_depth_lines(iter(process.stdout.readline, b""), file)

    def analyze_depth_lines(self, lines, file: AlignmentMapFile):
        progress = tqdm.tqdm(
            lines, total=39009164, smoothing=0)
        
        stats = DepthStats()
        stats_by_name = {}
        sums_by_name = {}

        stats_by_name = {bytes(x, "utf-8"): [0] * 4 for x in file.header.sequences.keys()}
        sums_by_name = {bytes(x, "utf-8"): [0] * 4 for x in file.header.sequences.keys()}
        
        for line in lines:
            line = line.split()
            name = line[0]
            position = int(line[1])
            reads = int(line[2])
            progress.update(1)

            if reads > 7:
                stats_by_name[name][3] += 1
                sums_by_name[name][3] += reads
            elif reads > 3:
                stats_by_name[name][2] += 1
                sums_by_name[name][2] += reads
            elif reads > 0:
                stats_by_name[name][1] += 1
                sums_by_name[name][1] += reads
            elif reads == 0:
                stats_by_name[name][0] += 1

        for name, stats in stats_by_name.items():
            sums = sums_by_name[name]

            zero_count = stats[0]
            non_zero_count = sum([stats[1], stats[2], stats[3]])

            max_3_count = stats[1]
            between_3_7_count = stats[2]
            greater_7_count = stats[3]

            max_3_sum = sums[1]
            between_3_7_sum = sums[2]
            greater_7_sum = sums[3]

            all_sums = sum(sums)
            all_count = zero_count + non_zero_count + 1

            non_zero_average = non_zero_count / all_count

            max_3_coverage = max_3_sum / all_sums
            between_3_7_coverage = between_3_7_sum / all_sums
            greater_7_coverage = greater_7_sum / all_sums
