class TabularDataRow:
    def __init__(self, header: str, value: list[str]) -> None:
        self.header = header
        self.value = value


class TabularData:
    def __init__(
        self, horizontal_header: list[str], rows: list[TabularDataRow]
    ) -> None:
        self.horizontal_header = horizontal_header
        self.rows = rows