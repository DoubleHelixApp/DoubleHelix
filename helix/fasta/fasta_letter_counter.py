import collections
import gzip
import logging
import re
import sys
import typing

from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.fasta.letter_run_collection import LetterRunCollection

try:
    import tqdm
except Exception:
    tqdm = None

from helix.reference.genome_metadata_loader import Genome


class FASTALetterCounter:
    def __init__(self, genome: Genome):
        self._bases_progressbar = None
        self.genome = genome
        self._sequences_progressbar = None
        self._bases_progressbar = None
        if not self.genome.dict.exists():
            raise RuntimeError(f"Unable to find dictionary in {self.genome.dict.name}.")
        self._dict: AlignmentMapHeader = AlignmentMapHeader.load_from_file(
            self.genome.dict
        )
        self._support_multiline_progress = "win32" == sys.platform

    @property
    def model_name(self):
        return self.genome.fasta

    def _progress(
        self, name, current_sequence, total_sequences, current_position, total_position
    ):
        if tqdm is not None:
            # Windows Prompt does not support nested progress bar and there's nothing
            # that can be done about that. On Windows, just keep only one progress bar.
            if self._sequences_progressbar is None and self._support_multiline_progress:
                self._sequences_progressbar = tqdm.tqdm(
                    total=total_sequences, desc="Sequences"
                )
            if self._bases_progressbar is None:
                self._bases_progressbar = tqdm.tqdm(
                    total=total_position, desc=f"{name}"
                )

            if current_sequence != 0 and self._support_multiline_progress:
                self._sequences_progressbar.update(current_sequence)
            if current_position != 0:
                self._bases_progressbar.update(current_position)

    def _sequence_from_line(self, line: str) -> LetterRunCollection:
        # Processing the opening of a new sequence in a FASTA file.
        # It's usually a line that begins with '>' followed by the name
        # of the sequence.
        sequence_name = line.split()[0][1:]
        if sequence_name not in self._dict.sequences:
            raise ValueError(f"Sequence {sequence_name} is not present in dictionary.")
        sequence_length = self._dict.sequences[sequence_name].length
        return LetterRunCollection(sequence_name, sequence_length)

    def _process_file(
        self,
        fp: typing.TextIO,
        letter: str,
        progress: typing.Callable[[int, int, int, int], None],
    ) -> typing.List[LetterRunCollection]:
        sequences = collections.OrderedDict()
        pattern = re.compile(rf"{letter}+")

        position = None
        current_sequence = None

        for line in fp:
            line = line.rstrip("\n")

            # Comment: skip
            if len(line) == 0 or line[0] == "#":
                continue

            # Check if processing a .fastq file by mistake.
            if line[0] == "+":
                raise RuntimeError(
                    "Expected a FASTA reference model, got a FASTQ sequencer data."
                )

            if line[0] == ">":
                if self._bases_progressbar is not None:
                    self._bases_progressbar.close()
                    self._bases_progressbar = None
                # New sequence found. Close old sequence if open.
                if current_sequence is not None:
                    current_sequence.end(position)

                current_sequence = self._sequence_from_line(line)
                if current_sequence.name in sequences:
                    raise RuntimeError(
                        f"Found a duplicated sequence: {current_sequence.name}"
                    )
                logging.debug(
                    f"{self.genome.fasta.name}: Processing sequence {current_sequence.name}"
                )
                sequences[current_sequence.name] = current_sequence
                if progress is not None:
                    progress(
                        current_sequence.name,
                        1,
                        len(self._dict.sequences),
                        0,
                        current_sequence.length,
                    )
                position = 0
                continue

            matches = list(pattern.finditer(line))

            # No Ns found in this line: close the open run (if any).
            if len(matches) == 0:
                if current_sequence.is_run_open():
                    current_sequence.close_run(position)

            for match in matches:
                if match.start() == 0:
                    # The Ns starts at the beginning of the line.
                    # If a run is open, keep open: is continuing from the previous line.
                    # Otherwise open a new one.
                    if not current_sequence.is_run_open():
                        current_sequence.open_run(position)
                else:
                    # There are Ns but they don't start at the beginning of the line.
                    # Close the run (if open) and re-open it: this is a new run of Ns.
                    if current_sequence.is_run_open():
                        current_sequence.close_run(position)
                    current_sequence.open_run(match.start() + position)

                # The run is ending before the end of the line. Close the open run (if any).
                if match.end() < len(line):
                    current_sequence.close_run(match.end() + position)
            position += len(line)
            if progress is not None:
                progress(
                    current_sequence.name,
                    0,
                    len(self._dict.sequences),
                    len(line),
                    current_sequence.length,
                )

        # File is terminated: close the current sequence and the open run (if any).
        if current_sequence is None:
            raise RuntimeError("Found the end of the file but no sequences found.")
        current_sequence.end(position)
        return list(sequences.values())

    def count_letters(
        self,
        letter: str = "N",
        progress: typing.Callable[[str, int, int, int, int], None] = False,
    ) -> typing.List[LetterRunCollection]:
        if progress is False:
            progress = self._progress

        with gzip.open(self.genome.fasta, "rt") as f:
            sequences = self._process_file(f, letter, progress)
        return sequences
