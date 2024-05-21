class AlignmentMapHeaderProgram:
    def __init__(self) -> None:
        self.id: str = None
        self.name: str = None
        self.command_line: str = None
        self.previous: AlignmentMapHeaderProgram = None
        self.description: str = None
        self.program_version: str = None
