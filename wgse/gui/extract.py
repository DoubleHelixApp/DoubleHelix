import enum
import webbrowser
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QDialog,
    QWidget,
)

from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.data.file_type import FileType
from wgse.gui.microarray_format import MicroarrayFormatWidget
from wgse.renderers.html_aligned_file_report import HTMLAlignedFileReport
from wgse.microarray.microarray_converter import MicroarrayConverter


class ExtractTargetFormat(enum.Enum):
    Microarray = enum.auto()
    SAM = enum.auto()
    BAM = enum.auto()
    CRAM = enum.auto()
    FASTA = enum.auto()
    FASTQ = enum.auto()
    HTML = enum.auto()
    Unknown = enum.auto()


class ExtractTargetSequences(enum.Enum):
    All = enum.auto()
    YOnly = enum.auto()
    MtOnly = enum.auto()
    YAndMT = enum.auto()
    Unmapped = enum.auto()
    Manual = enum.auto()
    Unknown = enum.auto()
    
class ExtractTargetSteps(enum.Enum):
    FormatSelection = enum.auto()
    SequenceSelection = enum.auto()
    MicroarraySelection = enum.auto()


class ExtractDialog(QDialog):
    def __init__(self, current_file, parent=None) -> None:
        self.current_file: AlignmentMapFile = current_file
        super().__init__(parent, Qt.WindowType.Dialog)

        self.resize(648, 600)
        self.setObjectName("extract")
        self.setWindowTitle("Extract data")

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.next_button = QPushButton("Next", self)
        self.next_button.setObjectName("nextButton")
        self.back_button = QPushButton("Back", self)
        self.back_button.setObjectName("backButton")

        self._target_format = ExtractTargetFormat.Unknown
        self._target_sequences = ExtractTargetSequences.Unknown

        # Create a page as follow:
        # - Main content, 1st row, spanning 3 columns
        # - Spacer, 2nd row, 1nd column
        # - "Next" button, 2nd row, 2nd column
        self._format_selection = self.create_format_selection()
        self._sequence_selection = self.create_sequences_selection()
        self._microarray_selection = MicroarrayFormatWidget(self)

        self.main = self._format_selection
        self.main.show()
        self.mainLayout = QGridLayout(self)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.addWidget(self.main, 0, 0, 1, 3)
        
        self.mainLayout.addWidget(self.back_button, 1, 0, 1, 1)
        self.mainLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)
        self.mainLayout.addWidget(self.next_button, 1, 2, 1, 1)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        QMetaObject.connectSlotsByName(self)
        self.next_button.clicked.connect(self.next)
        self.back_button.clicked.connect(self.back)

        self._format_handlers = {
            ExtractTargetFormat.Microarray: self._to_microarray,
            ExtractTargetFormat.BAM: self._to_bam,
            ExtractTargetFormat.SAM: self._to_sam,
            ExtractTargetFormat.CRAM: self._to_cram,
            ExtractTargetFormat.FASTQ: self._to_fastq,
            ExtractTargetFormat.FASTA: self._to_fasta,
            ExtractTargetFormat.HTML: self._to_html,
            ExtractTargetFormat.Unknown: self._to_unknown
        }

        # TODO: move to test
        assert all(x in self._format_handlers for x in ExtractTargetFormat)

    def _create_page(self, main_content):
        self.main.hide()
        self.mainLayout.replaceWidget(self.main, main_content)
        self.main = main_content

    def create_microarray_selection(self):
        microarraySelection = QGroupBox(self)
        microarraySelection.setObjectName("microarraySelection")
        microarraySelection.setTitle("Select the sequences to extract")

        all = "All sequences"
        
        self.sequencesOptions = [
            QRadioButton(all, microarraySelection),
        ]

        self.sequencesOptions[0].setObjectName(ExtractTargetSequences.All.name)
        self.sequencesOptions[1].setObjectName(ExtractTargetSequences.YOnly.name)
        self.sequencesOptions[2].setObjectName(ExtractTargetSequences.MtOnly.name)
        self.sequencesOptions[3].setObjectName(ExtractTargetSequences.YAndMT.name)
        self.sequencesOptions[4].setObjectName(ExtractTargetSequences.Unmapped.name)
        self.sequencesOptions[5].setObjectName(ExtractTargetSequences.Manual.name)

        groupBoxLayout = QVBoxLayout(microarraySelection)
        groupBoxLayout.setObjectName("groupBoxLayout")
        for item in self.sequencesOptions:
            groupBoxLayout.addWidget(item)

        microarraySelection.hide()
        return microarraySelection

    def create_sequences_selection(self):
        sequencesSelection = QGroupBox(self)
        sequencesSelection.setObjectName("sequencesSelection")
        sequencesSelection.setTitle("Select the sequences to extract")

        all = "All sequences"
        y_only = "Y only, useful e.g. on yDNA Warehouse, yTree, Cladefinder"
        mt_only = "MT-Only, useful e.g. on yFull (for biological females), Mitoverse, Haplogrep"
        ymt = "Y and MT, useful e.g. on yFull (for biological males)"
        unmapped = "Unmapped data (microbiome), useful e.g. on Kaiju, CosmosID"
        custom = "Custom, specify the sequences manually"

        self.sequencesOptions = [
            QRadioButton(all, sequencesSelection),
            QRadioButton(y_only, sequencesSelection),
            QRadioButton(mt_only, sequencesSelection),
            QRadioButton(ymt, sequencesSelection),
            QRadioButton(unmapped, sequencesSelection),
            QRadioButton(custom, sequencesSelection),
        ]

        self.sequencesOptions[0].setObjectName(ExtractTargetSequences.All.name)
        self.sequencesOptions[1].setObjectName(ExtractTargetSequences.YOnly.name)
        self.sequencesOptions[2].setObjectName(ExtractTargetSequences.MtOnly.name)
        self.sequencesOptions[3].setObjectName(ExtractTargetSequences.YAndMT.name)
        self.sequencesOptions[4].setObjectName(ExtractTargetSequences.Unmapped.name)
        self.sequencesOptions[5].setObjectName(ExtractTargetSequences.Manual.name)

        groupBoxLayout = QVBoxLayout(sequencesSelection)
        groupBoxLayout.setObjectName("groupBoxLayout")
        for item in self.sequencesOptions:
            groupBoxLayout.addWidget(item)

        sequencesSelection.hide()
        return sequencesSelection

    def create_format_selection(self):
        format = QGroupBox(self)
        format.setObjectName("formatSelection")
        format.setTitle("Select the destination format")

        microarray = "Microarray, textual format containing genotyping info"
        sam = "SAM, textual format for aligned file"
        bam = "BAM, binary equivalent of SAM"
        cram = "CRAM, highly compressed equivalent of BAM"
        fastq = "FASTQ, textual format for unaligned files"
        fasta = "FASTA, textual format obtained with a consensus algorithm"
        html = "HTML, report containing an overview of the file"
        
        self._format_options = [
            QRadioButton(microarray, format),
            QRadioButton(sam, format),
            QRadioButton(bam, format),
            QRadioButton(cram, format),
            QRadioButton(fastq, format),
            QRadioButton(fasta, format),
            QRadioButton(html, format),
        ]

        self._format_options[0].setObjectName(ExtractTargetFormat.Microarray.name)
        self._format_options[1].setObjectName(ExtractTargetFormat.BAM.name)
        self._format_options[2].setObjectName(ExtractTargetFormat.SAM.name)
        self._format_options[3].setObjectName(ExtractTargetFormat.CRAM.name)
        self._format_options[4].setObjectName(ExtractTargetFormat.FASTQ.name)
        self._format_options[5].setObjectName(ExtractTargetFormat.FASTA.name)
        self._format_options[6].setObjectName(ExtractTargetFormat.HTML.name)

        groupBoxLayout = QVBoxLayout(format)
        groupBoxLayout.setObjectName("groupBoxLayout")
        for item in self._format_options:
            groupBoxLayout.addWidget(item)

        format.hide()
        return format

    def _to_bam(self):
        if self.current_file is None:
            return
        self.current_file.convert(FileType.BAM)
        self.close()

    def _to_sam(self):
        if self.current_file is None:
            return

        self.current_file.convert(FileType.SAM)
        self.close()

    def _to_cram(self):
        if self.current_file is None:
            return

        self.current_file.convert(FileType.CRAM)
        self.close()

    def _to_fasta(self):
        if self.current_file is None:
            return

        self.current_file.convert(FileType.FASTA)
        self.close()

    def _to_fastq(self):
        if self.current_file is None:
            return
        self.close()

    def _to_html(self):
        if self.current_file is None:
            return

        html_page = HTMLAlignedFileReport.from_aligned_file(self.current_file)
        current_path = self.current_file.path
        extensions = "".join(current_path.suffixes[:-1])
        name = current_path.stem + extensions + ".html"
        target = current_path.with_name(name)

        with target.open("wt") as f:
            f.write(html_page)
        webbrowser.open(target)

    def _to_microarray(self):
        pass


    def _to_unknown(self):
        raise RuntimeError("BUG: Invalid target format")

    def move_to(self, target):
        self.mainLayout.replaceWidget(self.main, target)
        if self.main is not None:
            self.main.hide()
        target.show()
        self.main=target

    def _format_selected(self):
        selected = [x.isChecked() for x in self._format_options]
        if not any(selected):
            return
        assert len([x for x in selected if x]) == 1
        index = selected.index(True)
        button = self._format_options[index]
        self._target_format = ExtractTargetFormat[button.objectName()]
        if self._target_format == ExtractTargetFormat.HTML:
            self._to_html()
            self.close()
        elif self._target_format == ExtractTargetFormat.Microarray:
            self.move_to(self._microarray_selection)
        else:
            self.move_to(self._sequence_selection)

    def _perform_extraction(self):
        sequences = self._target_sequences
        format = self._target_format
        input = self.current_file.path

    def _sequence_selected(self):
        selected = [x.isChecked() for x in self.sequencesOptions]
        if not any(selected):
            return
        assert len([x for x in selected if x]) == 1
        index = selected.index(True)
        button = self.sequencesOptions[index]
        self._target_sequences = ExtractTargetSequences[button.objectName()]

    def back(self):
        if self.main.objectName() == "formatSelection":
            pass
        elif self.main.objectName() == "sequencesSelection":
            self.move_to(self._format_selection)
        elif self.main.objectName() == "microarrayFormatSelection":
            self.move_to(self._format_selection)
    
    def next(self):
        if self.main.objectName() == "formatSelection":
            self._format_selected()
        elif self.main.objectName() == "sequencesSelection":
            self._sequence_selected()
