import json
import re

from helix.configuration import MANAGER_CFG


class Sequencer:
    def __init__(self, name, sequencer_regex, coord_regex, coord_order, url) -> None:
        self.name = name
        self.sequencer_regex = re.compile(sequencer_regex)
        self.coord_regex = re.compile(coord_regex)
        self.coord_order = coord_order
        self.url = url


class Sequencers:
    def __init__(
        self,
        config=MANAGER_CFG.REPOSITORY,
    ) -> None:
        self._config = config
        self.data = self._load()

    def _load(self):
        content = None
        sequencer = self._config.metadata.joinpath("sequencers.json")
        with sequencer.open("rt") as p:
            content = json.load(p)
        return [Sequencer(**x) for x in content]

    def determine_sequencer(self, template_query):
        for sequencer in self.data:
            if sequencer.sequencer_regex.match(template_query):
                return sequencer.name
        return f"Unknown ({template_query})"
