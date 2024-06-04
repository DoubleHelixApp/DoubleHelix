from pydantic import BaseModel
from helix.data.read_type import ReadType


class AlignmentStats(BaseModel):
    skipped_samples: int = None
    samples_count: int = None
    sequencer: str = None
    duplicate: int = None
    count_length: int = None
    average_length: float = None
    standard_dev_length: float = None
    count_insert_size: int = None
    average_insert_size: float = None
    standard_dev_insert_size: float = None
    count_quality: int = None
    average_quality: float = None
    standard_dev_quality: float = None
    read_type: ReadType = None
