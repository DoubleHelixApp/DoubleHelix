import enum

from PySide6.QtWidgets import QGroupBox, QRadioButton, QVBoxLayout, QWidget


class ExtractTargetSequences(enum.Enum):
    All = enum.auto()
    YOnly = enum.auto()
    MtOnly = enum.auto()
    YAndMT = enum.auto()
    Unmapped = enum.auto()
    Manual = enum.auto()
    Unknown = enum.auto()


class SequenceSelection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.sequences = QGroupBox(self)
        self.inner_layout = QVBoxLayout(self.sequences)

        self.sequences.setTitle("Select the sequences to extract")

        self.setObjectName(SequenceSelection.__name__)
        self.inner_layout.setObjectName("groupBoxLayout")

        self.sequencesOptions = [
            QRadioButton(label, self.sequences)
            for label in [
                "All sequences",
                "Y only, useful e.g. on yDNA Warehouse, yTree, Cladefinder",
                "MT-Only, useful e.g. on yFull (for biological females), Mitoverse, Haplogrep",
                "Y and MT, useful e.g. on yFull (for biological males)",
                "Unmapped data (microbiome), useful e.g. on Kaiju, CosmosID",
                "Custom, specify the sequences manually",
            ]
        ]

        self.sequencesOptions[0].setObjectName(ExtractTargetSequences.All.name)
        self.sequencesOptions[1].setObjectName(ExtractTargetSequences.YOnly.name)
        self.sequencesOptions[2].setObjectName(ExtractTargetSequences.MtOnly.name)
        self.sequencesOptions[3].setObjectName(ExtractTargetSequences.YAndMT.name)
        self.sequencesOptions[4].setObjectName(ExtractTargetSequences.Unmapped.name)
        self.sequencesOptions[5].setObjectName(ExtractTargetSequences.Manual.name)

        for item in self.sequencesOptions:
            self.inner_layout.addWidget(item)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.sequences)
        self.setLayout(self.main_layout)
        self.hide()
