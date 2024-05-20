class LetterRun:
    """Represent a single run of a specific letter"""

    def __init__(self) -> None:
        self.start = None
        self.length = None

    def open(self, position: int):
        self.start = position

    def close(self, length: int):
        self.length = length
