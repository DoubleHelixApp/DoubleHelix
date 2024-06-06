class MockFileContent:
    def __init__(self, buffer) -> None:
        self.buffer = buffer
        self.seek = 0

    def __iter__(self):
        for line in self.buffer.split("\n"):
            yield line

    def write(self, buffer):
        self.buffer += buffer

    def read(self, b):
        max_read = min(len(self.buffer), self.seek + b)
        if (self.seek - max_read) == 0:
            return None
        self.seek = max_read
        return bytes(self.buffer[self.seek : max_read], "utf8")


class MockFile:
    def __init__(self, buffer) -> None:
        self.buffer = buffer

    def __enter__(self):
        return MockFileContent(self.buffer)

    def __exit__(self, _, _1, _2):
        return


class MockPath:
    class _StatObj:
        def __init__(self, size) -> None:
            self.st_size = size

    def __init__(self, path="foo", content={}, buffer="", exists=True):
        self.path = path
        self._content = content
        self._exists = exists
        self._buffer = buffer

    def joinpath(self, *str):
        target = "\\".join(str)
        if target in self._content:
            return self._content[target]
        raise ValueError()

    def exists(self):
        return self._exists

    def __str__(self) -> str:
        return self.path

    def rename(self, target):
        self.path = str(target)

    def open(self, *kargs, **kwargs):
        return MockFile(self._buffer)

    def stat(self):
        return MockPath._StatObj(len(self._buffer))

    def unlink(self):
        self._exists = False

    @property
    def name(self):
        return self.path

    @property
    def suffix(self):
        split = self.path.rsplit(".")
        if len(split) > 1:
            return split[1]
        return ""

    def with_suffix(self, suffix):
        no_suffix = self.path.rsplit(".")[0]
        target = no_suffix + "." + suffix
        if target in self._content:
            return self._content[target]
        return MockPath(target)
