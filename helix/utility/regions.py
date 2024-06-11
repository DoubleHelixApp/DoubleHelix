from enum import Flag, auto
import uuid

from helix.configuration import MANAGER_CFG
from helix.data.sequence import Sequence
from helix.naming.converter import Converter


class RegionType(Flag):
    Y = auto()
    MT = auto()
    WES = auto()


class Regions:
    """Represent a region in a genome.

    This class loads and manipulate .bed file templates containing regions in a genome.
    Since the bed files need to change according to the specific sequence naming
    of the loaded file, this class take care of loading the templates for these
    .bed files and convert them to the correct sequence naming.
    """

    def __init__(self, config=MANAGER_CFG.REPOSITORY, converter=Converter()) -> None:
        self._templates = config.metadata.joinpath("bed_templates")
        self._temporary = config.temporary
        self._converter = converter

    def get_path(self, build: str, type: RegionType, sequences: list[Sequence]):
        """Return the path of a .bed file that is built for a specific genome.

        Args:
            build (str): The build number (currently only 37 or 38 are supported)
            type (RegionType): RegionType of the region the caller is looking for.
                Currently only Y or MT or WES are supported. Regions can be combined
                but only Y | MT is a valid combination.
            sequences (list[Sequence]): List of sequences from the input file.

        Raises:
            ValueError: An invalid combination of RegionTypes was provided.
            FileNotFoundError: Template file for the provided build was not found.

        Returns:
            pathlib.Path: Path to the.bed file that is built for a specific genome.
        """
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
        """Build and get the content of a .bed file.

        Args:
            build (str): Build name.
            type (RegionType): RegionType of the region.

        Returns:
            str: Content of the .bed file.
        """
        file = self.get_path(build, type)
        return file.read_text("utf-8")
