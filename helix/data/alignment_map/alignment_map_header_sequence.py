from helix.data.sequence import Sequence


class AlignmentMapHeaderSequence(Sequence):
    def __init__(
        self, name: str = None, length: int = None, md5: str = None, parent=None
    ) -> None:
        super().__init__(name, length, md5, parent)
        self.uri: str = None
        self.alternate_locus: str = None
        self.molecule_topology: str = None
        self.species: str = None
        self.alternative_names: str = None
        self.genome_assembly_identifier: str = None
        self.description: str = None
