import json

from helix.configuration import MANAGER_CFG
from helix.data.mitochondrial_model import MitochondrialModel
from helix.data.mitochondrial_model_type import MitochondrialModelType
from helix.data.sequence import Sequence


class MtDNA:
    def __init__(
        self,
        config=MANAGER_CFG.REPOSITORY,
    ) -> None:
        self._mtdna_json = config.metadata.joinpath("mtdna.json")
        self.data: list[MitochondrialModel] = self._load()

    def _load(self):
        json_models = None
        with self._mtdna_json.open("rt") as p:
            json_models = json.load(p)

        models = []
        for model in json_models:
            sequence = Sequence(
                name=model["name"], length=int(model["length"]), md5=model["md5"]
            )
            model = MitochondrialModel(
                sequence, model["url"], MitochondrialModelType[model["name"]]
            )
            models.append(model)

        return models

    def get_by_md5(self, md5):
        for model in self.data:
            if model.sequence.md5 == md5:
                return model
        return None

    def get_by_length(self, length: int):
        for model in self.data:
            if model.sequence.length == length:
                return model
        return None

    def get_by_type(self, type):
        for model in self.data:
            if model.type == type:
                return model
        return None
