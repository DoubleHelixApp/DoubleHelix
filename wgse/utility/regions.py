from enum import Flag, auto
import uuid

from wgse.configuration import MANAGER_CFG
from wgse.data.sequence import Sequence
from wgse.naming.converter import Converter


class RegionType(Flag):
    Y = auto()
    MT = auto()
    WES = auto()


class Regions:
    def __init__(self, config=MANAGER_CFG.REPOSITORY, converter=Converter()) -> None:
        self._templates = config.metadata.joinpath("bed_templates")
        self._temporary = config.temporary
        self._converter = converter

    def get_path(self, build: str, type: RegionType, sequences: list[Sequence]):
        name_map = {x.canonic_name: x.name for x in sequences}

        suffix = ""
        if type & RegionType.Y and type & RegionType.WES:
            raise ValueError("Invalid combination: Y and WES")
        if type & RegionType.MT and type & RegionType.WES:
            raise ValueError("Invalid combination: MT and WES")

        if type & RegionType.Y:
            suffix += "_y"
        if type & RegionType.MT:
            suffix += "_mt"
        if type & RegionType.WES:
            suffix += "_wes"
        file_name = f"{build}{suffix}.csv"
        file = self._templates.joinpath(file_name)
        if not file.exists():
            raise FileNotFoundError(f"Unable to find BED template at: {file!s}")
        with file.open("r") as f:
            lines = f.readlines()
            rows = []
            for line in lines:
                line = line.split(",")
                sequence = line[0]
                begin = line[1]
                end = line[2].strip()
                if sequence in name_map:
                    sequence = name_map[sequence]
                rows.append(f"{sequence}\t{begin}\t{end}\n")
        temporary_file = self._temporary.joinpath(str(uuid.uuid4()))
        with temporary_file.open("w") as f:
            f.writelines(rows)
        return temporary_file

    def get_content(self, build: str, type: RegionType):
        file = self.get_path(build, type)
        return file.read_text("utf-8")
