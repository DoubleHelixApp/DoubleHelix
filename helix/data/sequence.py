from helix.naming.converter import Converter


class Sequence:
    def __init__(self, name: str, length: int, md5: str = None, parent=None) -> None:
        self.name = name
        self.length = length
        self.md5 = md5
        self.__parent = parent
        self.__type = None
        self.__canonic_name = None

    @property
    def type(self):
        if self.__type is None:
            self.__type = Converter.get_type(self.name)
        return self.__type

    @property
    def canonic_name(self):
        if self.__canonic_name is None:
            self.__canonic_name = Converter.canonicalize(self.name)
        return self.__canonic_name

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.md5 is None:
            return f"{self.name}, {self.length}bp"
        else:
            max_length = min(len(self.md5), 6)
            return f"{self.name}, {self.length}bp, ..{self.md5[-max_length:]}"
