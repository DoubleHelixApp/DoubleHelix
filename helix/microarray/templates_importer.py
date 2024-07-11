import glob
import gzip
from pathlib import Path
import sys
from typing import Callable

from helix.microarray.raw_file import RawFile
from helix.naming.converter import Converter


class TemplatesImporter:
    def __init__(self, target_folder=Path(__file__).parent) -> None:
        self.target_folder = target_folder

    def ingest(self, input: Path, progress: Callable[[str, float], None] = None):
        name_noext = input.name.removesuffix("".join(input.suffixes))
        target = self.target_folder.joinpath(name_noext).with_suffix(".txt.gz")

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


if __name__ == "__main__":
    import tqdm

    if len(sys.argv) < 2:
        print(
            "This script can import a microarray template file and do som basic checks on it."
        )
        print("")
        print(f"Usage: python {Path(__file__).name} pattern1 pattern2 ...")
        print(f"Example: python {Path(__file__).name} directory\\*.txt")
        exit()
    importer = TemplatesImporter()
    files = []
    for file in sys.argv[1:]:
        files.extend(glob.glob(file))
    files = [Path(x) for x in files if Path(x).is_file()]
    print(f"Found {len(files)} files.")
    for index, file in enumerate(tqdm.tqdm(files)):
        try:
            importer.ingest(file)
        except Exception as e:
            print(f"Error while import {file}: {e!s}")
    print("Done!")
