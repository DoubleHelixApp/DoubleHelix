from helix.data.tabular_data import TabularData


class Search:
    def __init__(self, data: dict[str, TabularData]) -> None:
        self.data = data

    def search(self, text):
        refined_data = {
            x: y for x, y in self.data.items() if x is not None and text in x
        }
        if len(refined_data) != len(self.data) and len(refined_data) != 0:
            return refined_data

        refined_data = {}
        for key, value in self.data.items():
            for row in value.rows:
                for col in row.columns:
                    if col and text in col:
                        refined_data[key] = value
                        break
        return refined_data
