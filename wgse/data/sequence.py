class Sequence:
    def __init__(self, name: str, length: int, md5: str = None, parent=None) -> None:
        self.name = name
        self.length = length
        self.md5 = md5
        self.__parent = parent

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @property
    def type(self):
        pass

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.md5 is None:
            return f"{self.name}, {self.length}bp"
        else:
            max_length = min(len(self.md5), 6)
            return f"{self.name}, {self.length}bp, ..{self.md5[-max_length:]}"
