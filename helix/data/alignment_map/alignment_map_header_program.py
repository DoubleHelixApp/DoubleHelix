from pydantic import BaseModel


class AlignmentMapHeaderProgram(BaseModel):
    id: str = None
    name: str = None
    command_line: str = None
    previous: "AlignmentMapHeaderProgram" = None
    description: str = None
    program_version: str = None
