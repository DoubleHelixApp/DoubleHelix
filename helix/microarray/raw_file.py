import gzip
import logging
from pathlib import Path
from typing import Optional

from parse import parse
from pydantic import BaseModel

from helix.naming.converter import Converter


class RawEntry(BaseModel, frozen=True):
    id: str
    chromosome: str
    position: int
    result: str = None

    @property
    def template_entry(self):
        return f"{self.id}\t{self.chromosome}\t{self.position}\n"

    def __str__(self) -> str:
        return f"{self.id},{self.chromosome},{self.position},{self.result}"

    def __repr__(self) -> str:
        return self.__str__()


class MicroarrayMeta(BaseModel):
    input_format: str = "{id}\t{chromosome}\t{position}\n"
    output_format: str = "{id}\t{chromosome}\t{position}\t{result}\n"
    file_extension: Optional[str] = None
    undetermined: str = "00"


class ParsedMicroarrayFile(BaseModel):
    grouped_entries: dict[str, dict[int, set[RawEntry]]]
    comments: Optional[list[str]] = None
    meta: Optional[MicroarrayMeta] = None


class RawFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.meta: MicroarrayMeta = MicroarrayMeta()
        self._logger = logging.getLogger(__name__)
        if self.path.suffix == ".gz":
            self.open_file = lambda: gzip.open(self.path, "rt")
        else:
            self.open_file = lambda: self.path.open("rt")

    def parse(self) -> ParsedMicroarrayFile:
        grouped: dict[str, dict[int, set[RawEntry]]] = dict()
        meta: MicroarrayMeta = MicroarrayMeta()
        comments = []

        with self.open_file() as file:
            for line in file:
                if line.startswith("##"):
                    line = line.removeprefix("##")
                    if meta is not None:
                        self._logger.warning(
                            f"Duplicate metadata line found in {self.path!s}"
                        )
                    meta = MicroarrayMeta.model_validate_json(line)
                    continue
                elif line.startswith("#"):
                    comments.append(line)
                    continue
                parsed = parse(self.meta.output_format, line)
                if parsed is None:
                    parsed = parse(self.meta.input_format, line)
                    if parsed is None:
                        self._logger.debug(
                            f"Found invalid line in {self.path!s}: {self.meta.input_format}!={line}"
                        )
                        continue

                entry = RawEntry(
                    id=parsed["id"],
                    chromosome=parsed["chromosome"],
                    position=parsed["position"],
                    result=parsed["result"] if "result" in parsed else None,
                )
                if isinstance(entry, str):
                    comments.append(entry)
                    continue
                chromosome = Converter.canonicalize(entry.chromosome)
                if chromosome not in grouped:
                    grouped[chromosome] = dict()
                if entry.position not in grouped[chromosome]:
                    grouped[chromosome][entry.position] = set()
                grouped[chromosome][entry.position].add(entry)

        if meta.file_extension is None:
            if len(self.path.suffixes) > 1 and self.path.suffixes[-1] == ".gz":
                meta.file_extension = self.path.suffixes[-2]
            elif len(self.path.suffixes) > 0:
                meta.file_extension = self.path.suffixes[-1]

        return ParsedMicroarrayFile(
            grouped_entries=grouped,
            comments=comments,
            meta=meta,
        )
