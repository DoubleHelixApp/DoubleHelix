from collections import OrderedDict
import enum
import logging

from wgse.data.genome import Genome
from wgse.data.sequence import Sequence


logger = logging.getLogger(__name__)

class ReferenceStatus(enum.Enum):
    Available = enum.auto()
    Downloadable = enum.auto()
    Buildable = enum.auto()
    Unknown = enum.auto()


class Reference:
    """This class represent a reference genome."""

    def __init__(self, reference_map: OrderedDict[Sequence, list[Sequence]]):
        self.reference_map = reference_map
        self._genome_map = self._index_by_genome()
        self.matching: list[Genome] = self._get_matching_genomes()
        self.build = set(x.build for x in self.matching)
        if len(self.build) > 1:
            logger.warn(
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
        genome_map = {}
        for query, reference_match in self.reference_map.items():
            unique_parents: set[Genome] = set(x.parent for x in reference_match)
            for parent in unique_parents:
                if parent not in genome_map:
                    genome_map[parent] = {x: None for x in parent.sequences}
            for match in reference_match:
                genome_map[match.parent][match] = query

        # Remove genomes that match only by 1 sequence.
        # It's likely to be an mtDNA sequence and it can create
        # a lot of noise. We don't care about them anyway as
        # MtDNA sequences are shipped with the software itself.
        # TODO: improve this procedure to make sure we're really
        # removing an MtDNA sequence and not a random one.
        genome_map_no_mitochondrial = {}
        for key, value in genome_map.items():
            valid = len([x for x in value.values() if x is not None])
            if valid > 1:
                genome_map_no_mitochondrial[key] = value
        return genome_map_no_mitochondrial

    def _get_matching_genomes(self):
        """Return a list of genomes that are guaranteed to match the input sequence
        by name, length or MD5 (if available in the input sequence).

        Returns:
            list[Genome]: list of matching genomes.
        """
        match_list = []
        for genome, matches in self._genome_map.items():
            matching = True
            for genome_sequence, query_sequence in matches.items():
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
                if query_sequence.length != query_sequence.length:
                    matching = False
                    break
            if matching:
                logger.info(f"{genome!s} is a perfect match.")
                match_list.append(genome)
        return match_list
    
    def __str__(self) -> str:
        return f"{self.build} ({self.status.name})"
    
    def __repr__(self) -> str:
        return self.__str__()