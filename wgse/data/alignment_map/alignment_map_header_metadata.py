from pydantic import BaseModel
from wgse.data.sorting import Sorting


class AlignmentMapHeaderMetadata(BaseModel):
    version: str = None
    sorted: Sorting = None
    grouping: str = None
    subsorting: str = None
