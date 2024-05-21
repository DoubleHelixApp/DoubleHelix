class AlignmentMapHeaderSequence:
    def __init__(self) -> None:
        self.name: str = None
        self.length: int = None
        self.md5: str = None
        self.uri: str = None
        self.alternate_locus: str = None
        self.molecule_topology: str = None
        self.species: str = None
        self.alternative_names: str = None
        self.genome_assembly_identifier: str = None
        self.description: str = None

    def __str__(self) -> str:
        return f"{self.name}: Length {self.length}bp, MD5: {self.md5}"

    def __repr__(self) -> str:
        return self.__str__()
