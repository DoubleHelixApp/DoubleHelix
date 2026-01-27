from typing import Optional


class Build:
    def __init__(
        self,
        name: str,
        description=None,
        urls: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.urls = urls
