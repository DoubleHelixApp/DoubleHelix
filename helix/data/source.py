import typing

from helix.data.build import Build


class Source:
    def __init__(
        self,
        name: str,
        urls: typing.List[str] = None,
        builds: typing.List[Build] = None,
        description: str = None,
    ) -> None:
        self.name = name
        self.builds = builds
        self.description = description
        self.urls = urls

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.name}"
