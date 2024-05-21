from wgse.data.sorting import Sorting


class AlignmentMapHeaderMetadata:
    def __init__(self) -> None:
        self.version: str = None
        self.sorted: Sorting = None
        self.grouping: str = None
        self.subsorting: str = None
