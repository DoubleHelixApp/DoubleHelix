
import gzip
from pathlib import Path


class RawEntry:
    def __init__(self, id=None, chromosome=None, position=None, result=None) -> None:
        self.id : str = id
        self.chromosome: str = chromosome
        self.position: int = position
        self.result: str = result
    
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
        if self.path.suffix == ".gz":
            self.open_file = lambda:gzip.open(self.path, "rt")
        else:
            self.open_file = lambda:self.path.open("rt")

    def __iter__(self):
        with self.open_file() as file:
            for line in file:
                if "#" in line:
                    continue
                parts = line.split("\t")
                id = parts[0].strip()
                chromosome = parts[1].strip()
                position = int(parts[2])
                result = None
                if len(parts) > 3:
                    result = parts[3].strip()
                yield RawEntry(id, chromosome, position, result)