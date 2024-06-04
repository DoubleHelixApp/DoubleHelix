import typing


class Build:
    def __init__(
        self,
        name: str,
        description=None,
        urls: typing.List[str] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.urls = urls
