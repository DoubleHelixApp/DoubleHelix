import enum

from PySide6.QtWidgets import QGroupBox, QRadioButton, QVBoxLayout, QWidget


class ExtractTargetFormat(enum.Enum):
    Microarray = enum.auto()
    SAM = enum.auto()
    BAM = enum.auto()
    CRAM = enum.auto()
    FASTA = enum.auto()
    FASTQ = enum.auto()
    HTML = enum.auto()
    Unknown = enum.auto()


class FormatSelection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.format = QGroupBox("Select the destination format", self)
        self.inner_layout = QVBoxLayout(self.format)

        self.setObjectName(FormatSelection.__name__)
        self.inner_layout.setObjectName("groupBoxLayout")

        self._format_options = [
            QRadioButton(label, self.format)
            for label in [
                "Microarray, textual format containing genotyping info",
                "SAM, textual format for aligned file",
                "BAM, binary equivalent of SAM",
                "CRAM, highly compressed equivalent of BAM",
                "FASTA, textual format obtained with a consensus algorithm",
                "FASTQ, textual format for unaligned files",
                "HTML, report containing an overview of the file",
            ]
        ]

        self._format_options[0].setObjectName(ExtractTargetFormat.Microarray.name)
        self._format_options[1].setObjectName(ExtractTargetFormat.SAM.name)
        self._format_options[2].setObjectName(ExtractTargetFormat.BAM.name)
        self._format_options[3].setObjectName(ExtractTargetFormat.CRAM.name)
        self._format_options[4].setObjectName(ExtractTargetFormat.FASTA.name)
        self._format_options[5].setObjectName(ExtractTargetFormat.FASTQ.name)
        self._format_options[6].setObjectName(ExtractTargetFormat.HTML.name)

        for item in self._format_options:
            self.inner_layout.addWidget(item)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.format)
        self.setLayout(self.main_layout)
        self.hide()
