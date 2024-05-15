
class Sequence:
    def __init__(
        self, name: str, length: int, md5: str = None
    ) -> None:
        self.name = name
        self.length = length
        self.md5 = md5
        self.__parent = None

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.name}: Length: {self.length}bp, MD5: {self.md5}"