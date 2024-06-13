import csv
import logging
import math
import statistics
import typing
from pathlib import Path

from helix.fasta.fasta_letter_counter import FASTALetterCounter
from helix.fasta.letter_run_buckets import LetterRunBuckets
from helix.fasta.letter_run_collection import LetterRunCollection


class FASTAStatsFiles:
    """Manage the creation of statistics files for Ns."""

    def __init__(
        self,
        fasta_file: FASTALetterCounter,
        long_run_threshold: int = 300,
        buckets_number: int = 1000,
    ) -> None:
        self._long_run_threshold = long_run_threshold
        self._buckets_number = buckets_number
        self._fasta_file = fasta_file

    def save_nbin(self, sequences: typing.List[LetterRunCollection]):
        lines = [
            "#WGS Extract runs of N: BIN definition file\n",
            (
                f"#Processing Ref Model: {self._fasta_file.model_name} "
                f"with >{self._long_run_threshold}bp of N runs\n"
            ),
            "#SN\tBinID\tStart\tSize\n",
        ]
        for sequence in sequences:
            for index, run in enumerate(
                sequence.filter(lambda x: x.length > self._long_run_threshold)
            ):
                row = f"{sequence.name}\t{index+1}\t{run.start:,}\t{run.length:,}\n"
                lines.append(row)
        return lines

    def load_bed(self):
        pass

    def save_bed(self, sequences: typing.List[LetterRunCollection]):
        lines = [
            "#WGS Extract runs of N: BED file of bin definitions\n",
            (
                f"#Processing Ref Model: {self._fasta_file.model_name} "
                f"with >{self._long_run_threshold}bp of N runs\n"
            ),
            "#SN\tStart\tStop\n",
        ]

        for sequence in sequences:
            for run in sequence.filter(lambda x: x.length > self._long_run_threshold):
                row = f"{sequence.name}\t{run.start}\t{run.start+run.length}\n"
                lines.append(row)
        return lines

    def load_nbuc(self):
        entries = list()
        with open(self._fasta_file.genome.nbuc, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                pass
                entries.append
                # sequence = LetterRunCollection(row[0], row[1])

                # n_count = row[0]
                # NumNreg = row[0]
                # NregSizeMean = row[0]
                # NregSizeStdDev = row[0]
                # SmlNreg = row[0]
                # BuckSize = row[0]

    def save_nbuc(self, sequences: typing.List[LetterRunCollection]):
        lines = [
            "#WGS Extract generated Sequence of N summary file\n",
            (
                f"#Model {self._fasta_file.model_name} with "
                f">{self._long_run_threshold}bp Sequence of N "
                f"and {self._buckets_number} buckets per sequence\n"
            ),
            (
                "#Seq\tNumBP\tNumNs\tNumNreg\tNregSizeMean\tNregSizeStdDev\t"
                "SmlNreg\tBuckSize\tBucket Sparse List (bp start, ln value) "
                "when nonzero\n"
            ),
        ]
        for sequence in sequences:
            bucket_length = int(math.floor(sequence.length / self._buckets_number))

            long_runs = sequence.filter(lambda x: x.length > self._long_run_threshold)
            short_runs = sequence.filter(lambda x: x.length <= self._long_run_threshold)

            long_run_lengths = [x.length for x in long_runs]
            short_run_lengths = [x.length for x in short_runs]

            long_runs_total = sum(long_run_lengths)
            short_runs_total = sum(short_run_lengths)

            long_run_avg = 0
            long_run_stdev = 0

            if len(long_run_lengths) > 1:
                long_run_avg = int(statistics.mean(long_run_lengths))
                long_run_stdev = int(statistics.stdev(long_run_lengths))

            row = (
                f"{sequence.name}\t{sequence.length}\t{long_runs_total}\t"
                f"{len(long_run_lengths)}\t{long_run_avg}\t{long_run_stdev}\t"
                f"{short_runs_total}\t{bucket_length}"
            )

            buckets = LetterRunBuckets(
                sequence, self._buckets_number, self._long_run_threshold
            )
            for index, bucket_count in buckets.buckets.items():
                val = round(math.log(bucket_count) if bucket_count > 1 else 0)
                start = index * bucket_length

                if val > 0:
                    row += f"\t{start}\t{val}"
            row += "\n"
            lines.append(row)
        return lines

    def _generate_file(self, path: Path, lines: typing.List[str]):
        with path.open("wt", encoding="utf8") as f:
            f.writelines(lines)

    def _generate_files(
        self, sequences: typing.Dict[str, typing.List[LetterRunCollection]]
    ):
        self._generate_file(self._fasta_file.genome.nbuc, self.save_nbuc(sequences))
        self._generate_file(self._fasta_file.genome.bed, self.save_bed(sequences))
        self._generate_file(self._fasta_file.genome.nbin, self.save_nbin(sequences))

    def _load_files(self):
        pass

    def generate_stats(self):
        logging.info(f"{self._fasta_file.genome!s}: Counting Ns.")
        sequences = self._fasta_file.count_letters("N")
        logging.info(f"{self._fasta_file.genome!s}: Finished counting Ns.")
        self._generate_files(sequences)
