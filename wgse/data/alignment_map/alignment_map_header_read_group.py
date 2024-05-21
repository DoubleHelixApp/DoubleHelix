class AlignmentMapHeaderReadGroup:
    def __init__(self) -> None:
        self.id: str = None
        self.barcode: str = None
        self.sequencing_center: str = None
        self.description: str = None
        self.date: str = None
        self.flow_order: str = None
        self.key_sequence: str = None
        self.library: str = None
        self.programs: str = None
        self.predicted_median_insert_size: int = None
        self.platform: str = None
        self.platform_model: str = None
        self.platform_unit: str = None
        self.sample: str = None
