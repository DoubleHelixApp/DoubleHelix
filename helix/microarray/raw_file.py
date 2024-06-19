import gzip
import json
import logging
from pathlib import Path

from parse import parse
from pydantic import BaseModel


class RawEntry(BaseModel):
    id: str
    chromosome: str
    position: int
    format: str
    result: str = None

    @property
    def template_entry(self):
        return f"{self.id}\t{self.chromosome}\t{self.position}\n"

    def __str__(self) -> str:
        return f"{self.id},{self.chromosome},{self.position},{self.result}"

    def __repr__(self) -> str:
        return self.__str__()


class RawFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.meta = None
        self._logger = logging.getLogger(__name__)
        if self.path.suffix == ".gz":
            self.open_file = lambda: gzip.open(self.path, "rt")
        else:
            self.open_file = lambda: self.path.open("rt")

    def load_meta(self, line: str):
        if self.meta is not None:
            self._logger.warning(f"Found two metadata line in {self.path!s}")
            return
        line = line.removeprefix("##")
        self.meta = json.loads(line)

    def __iter__(self):
        with self.open_file() as file:
            for line in file:
                if line.startswith("##"):
                    self.load_meta(line)
                    continue
                if "#" in line:
                    yield line
                    continue
                parsed = parse(self.meta["format"], line)
                if parsed is None:
                    yield None
                    continue
                yield RawEntry(
                    id=parsed["id"],
                    chromosome=parsed["chromosome"],
                    position=parsed["position"],
                    format=self.meta["format"],
                )
