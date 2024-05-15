from enum import Flag, auto
from wgse.configuration import MANAGER_CFG


class RegionType(Flag):
    Y = auto()
    MT = auto()
    WES = auto()


class Regions:
    def __init__(self, config=MANAGER_CFG.REPOSITORY) -> None:
        self._templates = config.metadata.joinpath("bed_templates")

    def get_regions(
        self, build: str, type: RegionType, autosome_name_type, mitochondrial_name_type
    ):
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

        template = file.read_text("utf-8")
