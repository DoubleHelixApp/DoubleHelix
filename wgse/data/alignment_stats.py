
from wgse.data.read_type import ReadType


class AlignmentStats:
    def __init__(self) -> None:
        self.skipped_samples: int = None
        self.samples_count: int = None
        self.sequencer: str = None
        self.duplicate: int = None
        self.count_length: int = None
        self.average_length: float = None
        self.standard_dev_length: float = None
        self.count_insert_size: int = None
        self.average_insert_size: float = None
        self.standard_dev_insert_size: float = None
        self.count_quality: int = None
        self.average_quality: float = None
        self.standard_dev_quality: float = None
        self.read_type: ReadType = None