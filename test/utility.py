class MockFile:
    def __init__(self, lines) -> None:
        self.lines = lines

    def __enter__(self):
        return self.lines

    def __exit__(self, _, _1, _2):
        return


class MockPath:
    def __init__(
        self,
        lines=[],
        exists=True,
        name="foo.fa.gz",
        stem="foo.fa",
        parent="bar",
        suffix=".gz",
        files = [],
        **kwargs
    ) -> None:
        self.lines = lines
        self.name = name
        self.stem = stem
        self.parent = parent
        self.suffix = suffix
        self.files : list[MockPath] = files
        self._exists = exists
        self.__dict__.update(kwargs)

    def open(self, *_1):
        return MockFile(self.lines)

    def joinpath(self, path):
        name = self.name + "/" + path
        joined = [x for x in self.files if x.name == name]
        assert len(joined) == 1
        return joined[1]
    
    def exists(self):
        return self._exists
