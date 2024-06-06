import json
import typing

from helix.configuration import MANAGER_CFG
from helix.data.build import Build
from helix.data.genome import Genome
from helix.data.sequence import Sequence
from helix.data.source import Source


class MetadataLoader:
    class _CircularReferenceEncoder(json.JSONEncoder):
        """Helps with the serialization of metadata, ensuring
        that is serialized only what's really needed."""

        def __init__(self, **kwargs) -> None:
            self.seen = set()
            super().__init__()

        def default(self, obj):
            if hasattr(obj, "__dict__"):
                obj_dict = obj.__dict__.copy()
                self.seen.add(id(obj))
                for key, value in obj.__dict__.items():
                    if id(value) in self.seen:
                        del obj_dict[key]
                    elif value is None:
                        del obj_dict[key]
                    else:
                        # Trivial types (i.e., str) may share the same id()
                        # if they are identical. This will break the serialization
                        # process. Let's add to the seen set an object only if it is
                        # non trivial.
                        if hasattr(value, "__dict__"):
                            self.seen.add(id(value))
                return {k: v for k, v in obj_dict.items() if not k.startswith("_")}
            return super().default(obj)

    def __init__(self, config=MANAGER_CFG.REPOSITORY):
        self._config = config
        self.genome_root = self._config.genomes
        self.references_path = self._config.metadata.joinpath("references.json")
        self.sources_path = self._config.metadata.joinpath("sources.json")

        if not self.genome_root.is_dir():
            raise FileNotFoundError(
                f"Unable to find {str(self.genome_root)} or is not a directory."
            )
        if not self.references_path.is_file():
            raise FileNotFoundError(
                f"Unable to find {str(self.references_path)} or is not a file."
            )
        if not self.sources_path.is_file():
            raise FileNotFoundError(
                f"Unable to find {str(self.sources_path)} or is not a file."
            )

        self.source_meta: dict[str, Source] = self._load_sources()

    def _load_sources(self):
        with self.sources_path.open("rt") as f:
            decoded = json.load(f)
        sources = {}
        for item in decoded:
            source = Source(**item)
            sources[source.name] = source
            builds = {}
            if source.builds is None:
                continue
            for build in source.builds:
                build = Build(**build)
                builds[build.name] = build
            source.builds = builds
        return sources

    def load(self) -> typing.List[Genome]:
        with self.references_path.open("rt") as f:
            decoded = json.load(f)
        genomes = []
        for genome in [Genome(**x) for x in decoded]:
            genomes.append(genome)
            genome.parent_folder = self.genome_root

            if genome.source in self.source_meta:
                genome.parent = self.source_meta[genome.source]
            else:
                genome.parent = Source(
                    genome.source, [], [], "Metadata for this source is not available."
                )
            if genome.sequences is None:
                continue
            genome.sequences = [Sequence(**x) for x in genome.sequences]
            for sequence in genome.sequences:
                sequence.parent = genome
        return genomes

    def save(self, source: typing.List[Genome]):
        with self.references_path.open("wt") as f:
            json.dump(
                source,
                f,
                cls=MetadataLoader._CircularReferenceEncoder,
                default=lambda o: o.__dict__,
            )
