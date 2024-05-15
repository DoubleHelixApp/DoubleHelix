import logging
import shutil
import time
from collections import OrderedDict
from pathlib import Path

from wgse.configuration import MANAGER_CFG
from wgse.data.microarray_converter import MicroarrayConverterTarget
from wgse.microarray.microarray_line_formatter import TARGET_FORMATTER_MAP
from wgse.microarray.raw_file import RawEntry, RawFile
from wgse.utility.sequence_orderer import SequenceOrderer


class MicroarrayConverter:
    def __init__(self, config= MANAGER_CFG.REPOSITORY) -> None:
        self._config = config
        self._template_folder = self._config.metadata.joinpath("microarray_templates")
        self._head_folder = self._template_folder.joinpath("head")
        self._body_folder = self._template_folder.joinpath("body")

        if not self._body_folder.exists():
            raise FileNotFoundError(
                f"Unable to find microarray template body folder at {self._body_folder!s}"
            )
        if not self._head_folder.exists():
            raise FileNotFoundError(
                f"Unable to find microarray template head folder at {self._head_folder!s}"
            )

    def _group_entries(
        self, path
    ) -> OrderedDict[str, OrderedDict[int, list[RawEntry]]]:
        grouped: OrderedDict[str, OrderedDict[int, list[RawEntry]]] = OrderedDict()
        for entry in RawFile(path):
            chromosome = SequenceOrderer.canonicalize(entry.chromosome)
            if chromosome not in grouped:
                grouped[chromosome] = OrderedDict()
            if entry.position not in grouped[chromosome]:
                grouped[chromosome][entry.position] = []
            grouped[chromosome][entry.position].append(entry)
        return grouped

    def _null_result(self, target: MicroarrayConverterTarget):
        if target in [
            MicroarrayConverterTarget.Ancestry_v1,
            MicroarrayConverterTarget.Ancestry_v2,
        ]:
            return "00"
        return "--"

    def ingest(self, target: MicroarrayConverterTarget):
        header_path = self._head_folder.joinpath(target.name).with_suffix(".txt")
        body_path = self._body_folder.joinpath(target.name).with_suffix(".txt.gz")

        if not header_path.exists():
            raise FileNotFoundError(
                f"Unable to find header file for microarray template at {header_path!s}"
            )
        if not body_path.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {body_path!s}"
            )

        template = self._group_entries(body_path)
        lines = []
        for _, chromosome in SequenceOrderer(template.keys()):
            ordered_positions = list(template[chromosome].keys())
            ordered_positions.sort()
            for position in ordered_positions:
                entries = set(x.template_entry for x in template[chromosome][position])
                lines.extend(entries)

        with body_path.with_name(body_path.stem).open("wt") as file:
            file.writelines(lines)

    def analyze(self, target: MicroarrayConverterTarget):
        header_path = self._head_folder.joinpath(target.name).with_suffix(".txt")
        body_path = self._body_folder.joinpath(target.name).with_suffix(".txt")
        duplicate_coords = self._body_folder.joinpath(
            target.name + "_duplicate_coordinates"
        ).with_suffix(".csv")
        non_sequential = self._body_folder.joinpath(
            target.name + "_non_sequential"
        ).with_suffix(".csv")
        same_rsid_different_c = self._body_folder.joinpath(
            target.name + "_same_rsid_different_coordinates"
        ).with_suffix(".csv")
        same_c_different_rsid = self._body_folder.joinpath(
            target.name + "_same_coordinate_different_rsid"
        ).with_suffix(".csv")

        if not header_path.exists():
            raise FileNotFoundError(
                f"Unable to find header file for microarray template at {header_path!s}"
            )
        if not body_path.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {body_path!s}"
            )
        template = self._group_entries(body_path)
        lines = []
        lines.append("# Duplicate coordinate report\n")
        lines.append("# Duplicates,Chromosome,Position\n")
        for chromosome, positions in template.items():
            position = 0
            for position, entry in positions.items():
                if len(entry) != 1:
                    lines.append(f"{len(entry)},{chromosome},{position}\n")
        print(f"Target {target.name} has a total of {len(lines)-2} duplicate coordinates.")

        with duplicate_coords.open("wt") as file:
            file.writelines(lines)

        lines = []
        lines.append("# Non sequential entries\n")
        lines.append("# RSID,Chromosome,Position\n")
        index_by_rsid = dict()
        index_by_coord = dict()
        last_chromosome = None
        last_position = None
        for entry in RawFile(body_path):
            chromosome = SequenceOrderer.canonicalize(entry.chromosome)
            if chromosome != last_chromosome:
                last_chromosome = chromosome
                last_position = 0

            if entry.id not in index_by_rsid:
                index_by_rsid[entry.id] = []
            index_by_rsid[entry.id].append(entry)
            coord = f"{entry.chromosome},{entry.position}"
            if coord not in index_by_coord:
                index_by_coord[coord] = []
            index_by_coord[coord].append(entry)

            if entry.position < last_position:
                lines.append(f"{entry.id},{entry.chromosome},{entry.position}\n")
            last_position = entry.position

        with non_sequential.open("wt") as file:
            file.writelines(lines)
        
        print(f"Target {target.name} has a total of {len(lines)-2} non sequential entries.")

        lines = []
        lines.append("# Same RSID different coordinates\n")
        lines.append("# RSID,Chromosome,Position\n")
        same_rsids: list[list[RawEntry]] = [
            index_by_rsid[x] for x in index_by_rsid if len(index_by_rsid[x]) > 1
        ]

        for same_rsid in same_rsids:
            first_element = same_rsid[0]
            broken_elements = set(
                x
                for x in same_rsid
                if x.chromosome != first_element.chromosome
                or x.position != first_element.position
            )
            if len(broken_elements) > 0:
                lines.append(
                    f"{first_element.id},{first_element.chromosome},{first_element.position}\n"
                )
            for broken_element in broken_elements:
                lines.append(
                    f"{broken_element.id},{broken_element.chromosome},{broken_element.position}\n"
                )

        with same_rsid_different_c.open("wt") as file:
            file.writelines(lines)

        print(f"Target {target.name} has a total of {len(lines)-2} entries with same rsID but different coordinates.")
        
        lines = []
        lines.append("# Same coordinates different RSID\n")
        lines.append("# RSID,Chromosome,Position\n")
        same_coords: list[list[RawEntry]] = [
            index_by_coord[x] for x in index_by_coord if len(index_by_coord[x]) > 1
        ]

        for same_coord in same_coords:
            first_element = same_coord[0]
            broken_elements = set(x for x in same_coord if x.id != first_element.id)
            if len(broken_elements) > 0:
                lines.append(
                    f"{first_element.id},{first_element.chromosome},{first_element.position}\n"
                )
            for broken_element in broken_elements:
                lines.append(
                    f"{broken_element.id},{broken_element.chromosome},{broken_element.position}\n"
                )
        
        with same_c_different_rsid.open("wt") as file:
            file.writelines(lines)
        
        print(f"Target {target.name} has a total of {len(lines)-2} entries with same coordinate but different rsIDs.")

    def convert(self, input: Path, target: MicroarrayConverterTarget):
        header_path = self._head_folder.joinpath(target.name).with_suffix(".txt")
        body_path = self._body_folder.joinpath(target.name).with_suffix(".txt.gz")

        if not header_path.exists():
            raise FileNotFoundError(
                f"Unable to find header file for microarray template at {header_path!s}"
            )
        if not body_path.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {body_path!s}"
            )

        template = self._group_entries(body_path)
        query_entries = self._group_entries(input)

        lines = []

        # TODO: this is easy to parallelize. Check if it's worth it
        for chromosome in template:
            for position in template[chromosome]:
                template_entries = template[chromosome][position]
                query_entry = None
                if chromosome not in query_entries:
                    query_entry = self._null_result(target)
                elif position not in query_entries[chromosome]:
                    query_entry = self._null_result(target)
                else:
                    if len(query_entries[chromosome][position]) == 0:
                        raise RuntimeError(
                            f"Bug: could not find a query entry for {chromosome} {position}"
                        )
                    query_entry = query_entries[chromosome][position][0].result
                    if len(query_entries[chromosome][position]) != 1:
                        # Sanity check: we've multiple entries for the same chromosome and the same position.
                        # The genotype should be the same. If it's not, warn the user and set a null value.
                        for entry in query_entries[chromosome][position]:
                            if entry.result != query_entry:
                                genomes = set(query_entries[chromosome][position])
                                logging.warn(
                                    f"Found different genotypes for the same position and the same chromosome: {genomes!s}."
                                )
                                query_entry = self._null_result(target)
                                break
                ids = set()
                for template_entry in template_entries:
                    if template_entry.id in ids:
                        # We've an entry with same chromosome/position.
                        # If we need to print it more than once it must at least
                        # have a different ID.
                        continue
                    ids.add(template_entry.id)
                    output_line = TARGET_FORMATTER_MAP[target][0](
                        template_entry.id,
                        template_entry.chromosome,
                        template_entry.position,
                        query_entry,
                    )
                    lines.append(output_line)

        suffix = TARGET_FORMATTER_MAP[target][1].value
        stem = input.stem.replace("_CombinedKit", "")
        output = input.with_name(f"{stem}_{target.name}{suffix}")

        shutil.copy(header_path, output)
        with output.open("a", newline="\n") as f:
            for line in lines:
                f.write(line)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    converter = MicroarrayConverter()

    for value in MicroarrayConverterTarget:
        start = time.time()
        print(f"Ingesting target: {value.name}")
        converter.ingest(value)
        end = time.time()
        print(f"Total: {end-start:.1f}s")
