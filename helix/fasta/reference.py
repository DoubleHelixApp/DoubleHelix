import enum
import logging
from collections import OrderedDict

from helix.data.genome import Genome
from helix.data.sequence import Sequence


class ReferenceStatus(enum.Enum):
    Available = enum.auto()
    Downloadable = enum.auto()
    Buildable = enum.auto()
    Ambiguous = enum.auto()
    Unknown = enum.auto()


class Reference:
    """This class represent a reference genome."""

    def __init__(
        self,
        reference_map: OrderedDict[Sequence, list[Sequence]],
        logger=logging.getLogger(__name__),
    ):
        self._logger = logger
        self.reference_map = reference_map
        self._genome_map = self._index_by_genome()
        self.matching: list[Genome] = self._get_matching_genomes()
        sorted = list([x for x in self._genome_map.keys() if x is not None])
        sorted.sort(
            key=lambda x: len(
                [y for y in self._genome_map[x].values() if y is not None]
            )
        )
        self.build = []
        if len(self.matching) > 0:
            self.build = set(x.build for x in self.matching)
        elif len(sorted) > 0:
            self.build = [f"Likely {sorted[-1].build}"]

        if len(self.build) > 1:
            self._logger.warn(
                "Found more than one valid builds for the reference of the file. "
                + "This is likely an issue with the reference genome metadata. "
                + "Please open a bug report."
            )
        self.build = " ".join(self.build)
        self.ready_reference = None
        for match in self.matching:
            if match.fasta.exists():
                self.ready_reference = match
                break
        if self.ready_reference is not None:
            self.status = ReferenceStatus.Available
        elif len(self.matching) > 0:
            self.status = ReferenceStatus.Downloadable
        # There's a possibility to build it only if every sequence has a
        # match in the metadata.
        elif all([True if len(x) > 0 else False for x in self.reference_map.values()]):
            self.status = ReferenceStatus.Buildable
        else:
            self.status = ReferenceStatus.Unknown

    def _md5_available(self):
        """Return True if MD5 is available for every input sequence.

        Returns:
            bool: True if MD5 available.
        """
        return all([x.md5 is not None for x in self.reference_map.keys()])

    def _index_by_genome(self) -> dict[Genome, dict[Sequence, Sequence]]:
        """For every genome that has at least one match in the input sequence,
        return a map between its sequences and input sequences.

        Returns:
            dict[Genome, dict[Sequence, Sequence]]: Map Genome <-> Sequences.
        """
        parents: set[Genome] = set(
            x.parent for y in self.reference_map.values() for x in y
        )
        genome_map = {x: {y: None for y in x.sequences} for x in parents}
        for parent in parents:
            genome_map[parent][None] = []
            for sequence in parent.sequences:
                for query_sequence, match_sequences in self.reference_map.items():
                    if sequence in match_sequences:
                        genome_map[parent][sequence] = query_sequence
                        break
            for query_sequence in self.reference_map.keys():
                if query_sequence not in genome_map[parent].values():
                    genome_map[parent][None].append(query_sequence)
        return genome_map

    def _get_matching_genomes(self):
        """Return a list of genomes that are guaranteed to match the input sequence
        by name, length or MD5 (if available in the input sequence).

        Returns:
            list[Genome]: list of matching genomes.
        """
        match_list = []
        # None is a special key for all the sequences
        # that have 0 matches among all the known references.
        # If None is in _genome_map means we didn't find a
        # reference.
        for genome, matches in self._genome_map.items():
            if len(matches[None]) > 0:
                continue
            matching = True
            for genome_sequence, query_sequence in matches.items():
                if genome_sequence is None:
                    continue
                if query_sequence is None:
                    matching = False
                    break
                if genome_sequence.name != query_sequence.name:
                    matching = False
                    break
                if query_sequence.md5 is not None:
                    if genome_sequence.md5 != query_sequence.md5:
                        matching = False
                        break
                if genome_sequence.length != query_sequence.length:
                    matching = False
                    break
            if matching:
                self._logger.info(f"{genome!s} is a perfect match.")
                match_list.append(genome)
        return match_list

    def __str__(self) -> str:
        return f"{self.build} ({self.status.name})"

    def __repr__(self) -> str:
        return self.__str__()
