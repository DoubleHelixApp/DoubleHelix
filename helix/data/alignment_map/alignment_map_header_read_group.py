from pydantic import BaseModel


class AlignmentMapHeaderReadGroup(BaseModel):
    id: str = None
    barcode: str = None
    sequencing_center: str = None
    description: str = None
    date: str = None
    flow_order: str = None
    key_sequence: str = None
    library: str = None
    programs: str = None
    predicted_median_insert_size: int = None
    platform: str = None
    platform_model: str = None
    platform_unit: str = None
    sample: str = None
