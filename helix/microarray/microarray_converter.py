import logging
from collections import OrderedDict
from pathlib import Path

from helix.configuration import MANAGER_CFG
from helix.data.microarray_converter import MicroarrayConverterTarget
from helix.microarray.microarray_line_formatter import TARGET_FORMATTER_MAP
from helix.microarray.raw_file import RawEntry, RawFile
from helix.naming.converter import Converter


class MicroarrayConverter:
    def __init__(self, config=MANAGER_CFG.REPOSITORY) -> None:
        self._config = config
        self._template_folder = self._config.metadata.joinpath("microarray_templates")
        self._comments = []

        if not self._template_folder.exists():
            raise FileNotFoundError(
                f"Unable to find microarray template body folder at {self._template_folder!s}"
            )

    def _group_entries(
        self, path
    ) -> OrderedDict[str, OrderedDict[int, list[RawEntry]]]:
        grouped: OrderedDict[str, OrderedDict[int, list[RawEntry]]] = OrderedDict()
        for entry in RawFile(path):
            if entry is None:
                continue
            elif isinstance(entry, str):
                continue
            chromosome = Converter.canonicalize(entry.chromosome)
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
        body_path = self._template_folder.joinpath(target.name).with_suffix(".txt.gz")

        if not body_path.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {body_path!s}"
            )

        template = self._group_entries(body_path)
        lines = []
        for chromosome in Converter.sort(template.keys()):
            ordered_positions = list(template[chromosome].keys())
            ordered_positions.sort()
            for position in ordered_positions:
                entries = set(x.template_entry for x in template[chromosome][position])
                lines.extend(entries)

        with body_path.with_name(body_path.stem).open("wt") as file:
            file.writelines(lines)

    def convert(self, input: Path, target: MicroarrayConverterTarget):
        templates = self._template_folder.joinpath(target.name).with_suffix(".txt.gz")

        if not templates.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {templates!s}"
            )

        template = self._group_entries(templates)
        query_entries = self._group_entries(input)

        lines = []

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
                        # Sanity check: we've multiple entries for the same chromosome
                        # and the same position. The genotype should be the same.
                        # If it's not, warn the user and set a null value.
                        for entry in query_entries[chromosome][position]:
                            if entry.result != query_entry:
                                genomes = set(query_entries[chromosome][position])
                                logging.warn(
                                    f"Found different genotypes for the same "
                                    f"position and the same chromosome: {genomes!s}."
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

        with output.open("a", newline="\n") as f:
            for line in lines:
                f.write(line)
