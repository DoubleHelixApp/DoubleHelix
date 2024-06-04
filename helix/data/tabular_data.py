class TabularDataRow:
    def __init__(self, header: str, columns: list[str]) -> None:
        self.vertical_header = header
        self.columns = columns


class TabularData:
    def __init__(
        self, horizontal_header: list[str], rows: list[TabularDataRow]
    ) -> None:
        self.horizontal_header = horizontal_header
        self.rows = rows
