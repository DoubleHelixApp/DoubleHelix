import gzip
from math import sqrt
from pathlib import Path

from helix.utility.sequencers import Sequencers


class FASTQFile:
    def __init__(self, path: Path, sequencers: Sequencers = Sequencers()) -> None:
        self.path = path
        self._sequencers = sequencers

    def process_FASTQ(self, paired=True):
        line_count = 0
        char_count = 0
        sequencer_id = ""
        rcnt = 0
        rlen = 0
        rmean = 0
        rM2 = 0
        with gzip.open(self.path, "rt") as f:
            for line in f:
                if (
                    line_count % 4 == 2
                ):  # more common case; checking length of sequencer read
                    rlen += len(line)
                    if rlen > 1:
                        rcnt += 1
                        rdelta = rlen - rmean
                        rmean += rdelta / rcnt
                        rdelta2 = rlen - rmean
                        rM2 += rdelta * rdelta2
                elif (
                    line_count == 0
                ):  # Only at start; while skipping header or to read first sequncer ID
                    if (
                        line[0] == "#"
                    ):  # Skip header; do not count (new spec coming out with header)
                        continue
                    else:  # line[0] == '@':   # First line and sequencer label
                        sequencer = line.strip().split("\t")[0][1:]
                        sequencer_id = self._sequencers.determine_sequencer(sequencer)
                        line_count = 1
                elif (
                    line_count > 20000
                ):  # Only at end; Average first 5K segments (4 lines per segment)
                    line_count -= 1
                    break
                char_count += len(line)
                line_count += 1

        average_read_length = 0
        average_read_stddev = 0  # noqa: F841
        if rcnt > 2:
            rstd = sqrt(rM2 / (rcnt - 1))
            average_read_length = rmean
            average_read_stddev = rstd  # noqa: F841

        # Do a quick estimate based on the character count in the first 10,000 lines above
        # (2500 read segments) divided into the file size.
        segments = 0
        fastq_stats = self.path.stat()
        if fastq_stats.st_size > 0:
            segments = int(fastq_stats.st_size / (char_count / (line_count / 4)))
            segments *= 2 if paired else 1

        # e.g. return "Illumima", 660000000, 150
        return sequencer_id, segments, average_read_length
