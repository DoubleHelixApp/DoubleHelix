import logging
import typing
from collections import OrderedDict
from pathlib import Path

from helix.data.alignment_map.alignment_map_header_metadata import (
    AlignmentMapHeaderMetadata,
)
from helix.data.alignment_map.alignment_map_header_program import (
    AlignmentMapHeaderProgram,
)
from helix.data.alignment_map.alignment_map_header_read_group import (
    AlignmentMapHeaderReadGroup,
)
from helix.data.alignment_map.alignment_map_header_sequence import (
    AlignmentMapHeaderSequence,
)
from helix.data.chromosome_name_type import ChromosomeNameType
from helix.data.mitochondrial_name_type import MitochondrialNameType
from helix.data.sorting import Sorting


class AlignmentMapHeader:
    """Parse the output from `samtools view -H`"""

    def __init__(self, lines) -> None:
        self.metadata = None
        self.sequences: OrderedDict[str, AlignmentMapHeaderSequence] = OrderedDict()
        self.programs: list[AlignmentMapHeaderProgram] = []
        self.read_groups: list[AlignmentMapHeaderReadGroup] = []
        self.comments: list[str] = []

        self._handlers = {
            "@HD": self._metadata_process,
            "@SQ": self._sequence_process,
            "@PG": self._program_process,
            "@CO": self._comment_process,
            "@RG": self._read_group_process,
        }
        self._load(lines)

    def _program_process(self, parts: list[str]):
        program = AlignmentMapHeaderProgram()
        for part in parts:
            if part.startswith("ID"):
                program.id = part.split(":", 1)[1]
            elif part.startswith("PN"):
                program.id = part.split(":", 1)[1]
            elif part.startswith("CL"):
                program.id = part.split(":", 1)[1]
            elif part.startswith("PP"):
                program.previous = part.split(":", 1)[1]
                if program.previous in [x.id for x in self.programs]:
                    prev = [x for x in self.programs if x.id == program.previous]
                    program.previous = prev[0]
            elif part.startswith("DS"):
                program.description = part.split(":", 1)[1]
            elif part.startswith("VN"):
                program.program_version = part.split(":", 1)[1]
        self.programs.append(program)

    def _read_group_process(self, parts: list[str]):
        read_group = AlignmentMapHeaderReadGroup()
        for part in parts:
            if part.startswith("ID"):
                read_group.id = part.split(":", 1)[1]
            elif part.startswith("BC"):
                read_group.barcode = part.split(":", 1)[1]
            elif part.startswith("CN"):
                read_group.sequencing_center = part.split(":", 1)[1]
            elif part.startswith("DS"):
                read_group.description = part.split(":", 1)[1]
            elif part.startswith("DT"):
                read_group.date = part.split(":", 1)[1]
            elif part.startswith("FO"):
                read_group.flow_order = part.split(":", 1)[1]
            elif part.startswith("KS"):
                read_group.key_sequence = part.split(":", 1)[1]
            elif part.startswith("LB"):
                read_group.library = part.split(":", 1)[1]
            elif part.startswith("PG"):
                read_group.programs = part.split(":", 1)[1]
            elif part.startswith("PI"):
                read_group.predicted_median_insert_size = part.split(":", 1)[1]
            elif part.startswith("PL"):
                read_group.platform = part.split(":", 1)[1]
            elif part.startswith("PM"):
                read_group.platform_model = part.split(":", 1)[1]
            elif part.startswith("PU"):
                read_group.platform_unit = part.split(":", 1)[1]
            elif part.startswith("SM"):
                read_group.sample = part.split(":", 1)[1]
        self.read_groups.append(read_group)

    def _comment_process(self, parts: list[str]):
        self.comments.append(" ".join(parts))
        return

    def _metadata_process(self, parts: list[str]):
        metadata = AlignmentMapHeaderMetadata()
        for part in parts:
            if part.startswith("VN"):
                metadata.version = part.split(":", 1)[1]
            elif part.startswith("SO:"):
                metadata.sorted = self._sorted(part)
            elif part.startswith("GO:"):
                metadata.grouping = part.split(":", 1)[1]
            elif part.startswith("SS:"):
                metadata.subsorting = part.split(":", 1)[1]
        self.metadata = metadata

    def _sequence_process(self, parts: typing.List[str]):
        entry = AlignmentMapHeaderSequence()

        for part in parts:
            if part.startswith("SN"):
                entry.name = part.split(":", 1)[1]
            elif part.startswith("LN"):
                entry.length = int(part.split(":", 1)[1])
            elif part.startswith("M5"):
                entry.md5 = part.split(":", 1)[1]
            elif part.startswith("UR"):
                entry.uri = part.split(":", 1)[1]
            elif part.startswith("AH"):
                entry.alternate_locus = part.split(":", 1)[1]
            elif part.startswith("AN"):
                entry.alternative_names = part.split(":", 1)[1].split(",")
            elif part.startswith("AS"):
                entry.genome_assembly_identifier = part.split(":", 1)[1]
            elif part.startswith("DS"):
                entry.description = part.split(":", 1)[1]
            elif part.startswith("SP"):
                entry.species = part.split(":", 1)[1]
            elif part.startswith("TP"):
                entry.molecule_topology = part.split(":", 1)[1]
        if entry.name is None:
            raise RuntimeError("Unable to find the name of the sequence.")
        if entry.length is None:
            raise RuntimeError("Unable to find the length of the sequence.")

        self.sequences[entry.name] = entry

    def _load(self, lines):
        for index, line in enumerate(lines):
            line = line.strip()
            if line == "":
                continue
            parts = line.split("\t")
            line_type = parts[0].strip()
            if line_type in self._handlers:
                self._handlers[line_type](parts)
            else:
                logging.debug(
                    f"Skipping line {index} in dictionary because unrecognized type {line_type}."
                )

    def load_from_file(path: Path) -> "AlignmentMapHeader":
        if path is None:
            raise ValueError("path cannot be None.")
        if not path.exists():
            raise FileNotFoundError(f"Unable to find file: {str(path)}")

        with path.open("rt") as f:
            return AlignmentMapHeader(f)

    def _sorted(self, value: str) -> Sorting:
        value = value.split(":")[1].strip().lower()
        if "coordinate" in value:
            return Sorting.Coordinate
        elif "unsorted" in value:
            return Sorting.Unsorted
        elif "unknown" in value:
            return Sorting.Unknown
        elif "queryname" in value:
            return Sorting.QueryName
        logging.debug(f"Unable to recognize the sorting header {value}")
        return Sorting.Unknown

    def chromosome_name_type(self):
        patterns_type = {
            ChromosomeNameType.GenBank: ["CM0", "CP", "J0", "NC_"],
            ChromosomeNameType.Chr: ["chr"],
            ChromosomeNameType.Number: ["1"],
        }

        for type, patterns in patterns_type.items():
            for sequence in self.sequences.keys():
                if any([x in sequence for x in patterns]):
                    return type
        return ChromosomeNameType.Unknown

    def mtdna_name_type(self):
        patterns_type = {
            MitochondrialNameType.chrMT: ["chrMT"],
            MitochondrialNameType.MT: ["MT"],
            MitochondrialNameType.chrM: ["chrM"],
            MitochondrialNameType.M: ["M"],
        }

        for type, patterns in patterns_type.items():
            if any([x in self.sequences.keys() for x in patterns]):
                return type

        if self.chromosome_name_type() == ChromosomeNameType.GenBank:
            return MitochondrialNameType.Accession
        return MitochondrialNameType.Unknown

    def sequence_count(self):
        return len(self.sequences)
