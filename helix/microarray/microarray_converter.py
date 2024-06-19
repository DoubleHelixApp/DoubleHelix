import gzip
from pathlib import Path
from typing import Callable

from helix.configuration import MANAGER_CFG
from helix.data.microarray_converter import MicroarrayConverterTarget
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

    def _null_result(self, target: MicroarrayConverterTarget):
        if target in [
            MicroarrayConverterTarget.Ancestry_v1,
            MicroarrayConverterTarget.Ancestry_v2,
        ]:
            return "00"
        return "--"

    def ingest(self, input: Path, progress: Callable[[str, float], None] = None):
        name_noext = input.name.removesuffix("".join(input.suffixes))
        target = self._template_folder.joinpath(name_noext).with_suffix(".txt.gz")

        if target == input:
            raise ValueError(f"Input file is the same as the target: {input!s}")

        if not input.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {input!s}"
            )

        rawfile = RawFile(input)
        template = rawfile.load()

        entries = []
        with gzip.open(target, "wt") as file:
            if template.meta is not None:
                file.write(f"##{template.meta.model_dump_json()}\n")
            file.writelines(template.comments)
            for chromosome in Converter.sort(list(template.grouped_entries.keys())):
                ordered_positions = list(template.grouped_entries[chromosome].keys())
                ordered_positions.sort()
                for position in ordered_positions:
                    entries = template.grouped_entries[chromosome][position]
                    for entry in entries:
                        file.write(template.meta.input_format.format(**entry.__dict__))
        return target

    def convert(self, input: Path, target: Path):
        if not target.exists():
            raise FileNotFoundError(
                f"Unable to find body file for microarray template at {target!s}"
            )

        template = RawFile(target).load()
        query_entries = RawFile(input).load()

        lines = []
        for chromosome in template.grouped_entries:
            for position in template.grouped_entries[chromosome]:
                template_entries: set[RawEntry] = template.grouped_entries[chromosome][
                    position
                ]
                query_entry = None
                if chromosome not in query_entries.grouped_entries:
                    query_entry = template.meta.undetermined
                elif position not in query_entries.grouped_entries[chromosome]:
                    query_entry = template.meta.undetermined
                else:
                    if len(query_entries.grouped_entries[chromosome][position]) == 0:
                        raise RuntimeError(
                            f"Bug: could not find a query entry for {chromosome} {position}"
                        )
                    entries = query_entries.grouped_entries[chromosome][position]
                    entries = list(entries)
                    query_entry = entries[0].result

                for template_entry in template_entries:
                    output_line = template.meta.output_format.format(
                        id=template_entry.id,
                        chromosome=template_entry.chromosome,
                        position=template_entry.position,
                        result=query_entry,
                    )
                    lines.append(output_line)

        suffix = template.meta.file_extension
        stem = input.stem.replace("_CombinedKit", "")
        output = input.with_name(f"{stem}_{target.name}{suffix}")

        with output.open("a", newline="\n") as f:
            f.writelines(template.comments)
            f.writelines(lines)
        return output
