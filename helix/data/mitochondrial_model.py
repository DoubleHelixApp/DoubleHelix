from helix.configuration import MANAGER_CFG
from helix.data.mitochondrial_model_type import MitochondrialModelType
from helix.data.sequence import Sequence


class MitochondrialModel:
    def __init__(self, sequence, url, type, config=MANAGER_CFG.REPOSITORY) -> None:
        self.sequence: Sequence = sequence
        self.url = url
        self.type: MitochondrialModelType = type
        self.path = config.mtdna.joinpath(self.type.name + ".fasta")

    def get_data(self):
        with self.path.open("r") as f:
            return f.read()

    def __str__(self) -> str:
        return f"{self.type.name}"

    def __repr__(self) -> str:
        return f"{self.type.name}"
