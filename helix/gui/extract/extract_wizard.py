import enum
import webbrowser

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)

from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.alignment_map.variant_caller import VariantCaller
from helix.data.file_type import FileType
from helix.gui.extract.format_selection import ExtractTargetFormat, FormatSelection
from helix.gui.extract.microarray_selection import MicroarraySelection
from helix.gui.extract.sequence_selection import (
    ExtractTargetSequences,
    SequenceSelection,
)
from helix.progress.simple_worker import SimpleWorker
from helix.renderers.html_aligned_file_report import HTMLAlignedFileReport


class ExtractTargetSteps(enum.Enum):
    FormatSelection = enum.auto()
    SequenceSelection = enum.auto()
    MicroarraySelection = enum.auto()


class ExtractWizard(QDialog):
    def __init__(self, current_file, parent=None, progress=None) -> None:
        self.current_file: AlignmentMapFile = current_file
        super().__init__(parent, Qt.WindowType.Dialog)
        self._progress = progress
        self._worker = None

        self.resize(648, 600)
        self.setObjectName("extract")
        self.setWindowTitle("Extract data")

        # Specify what options were selected
        self.status = None
        self.options = None

        # [Back] <--> [Next]
        self.back_button = QPushButton("Back", self)
        self.back_button.setObjectName("backButton")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.next_button = QPushButton("Next", self)
        self.next_button.setObjectName("nextButton")

        self._format_selection = FormatSelection(
            self, self.current_file.file_info.file_type
        )
        self._sequence_selection = SequenceSelection(self)
        self._microarray_selection = MicroarraySelection(self)

        self.mainLayout = QGridLayout(self)
        self.mainLayout.setObjectName("mainLayout")

        # 1st row
        self.main = self._format_selection
        self.mainLayout.addWidget(self.main, 0, 0, 1, 3)
        self.main.show()

        # 2nd row [BACK] (space) [NEXT]
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
            ExtractTargetFormat.VCF: self._to_vcf,
            ExtractTargetFormat.Unknown: self._to_unknown,
        }

        # TODO: move to test
        assert all(x in self._format_handlers for x in ExtractTargetFormat)

    def _to_bam(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.BAM, progress=self._progress
        )
        self.close()

    def _to_sam(self):
        if self.current_file is None:
            return
        self._worker = SimpleWorker(
            self.current_file.convert, FileType.SAM, progress=self._progress
        )
        self.close()

    def _to_cram(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.CRAM, progress=self._progress
        )
        self.close()

    def _to_fasta(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.FASTA, progress=self._progress
        )
        self.close()

    def _to_fastq(self):
        if self.current_file is None:
            return
        self._worker = SimpleWorker(
            self.current_file.convert, FileType.FASTQ, progress=self._progress
        )
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
        self._progress(None, None)
        webbrowser.open(target)
        self.close()

    def _to_microarray(self):
        pass

    def _to_vcf(self):
        if self.current_file is None:
            return

        self._worker = VariantCaller(self.current_file, progress=self._progress)
        self._worker.start()
        self.close()

    def _to_unknown(self):
        raise RuntimeError("BUG: Invalid target format")

    def move_to(self, target):
        if self.main is not None:
            self.main.hide()
        self.mainLayout.replaceWidget(self.main, target)
        self.main = target
        self.main.show()

    def _format_selected(self):
        selected = [x.isChecked() for x in self._format_selection._format_options]
        if not any(selected):
            return
        assert len([x for x in selected if x]) == 1
        index = selected.index(True)
        button = self._format_selection._format_options[index]
        self._target_format = ExtractTargetFormat[button.objectName()]

        if self._target_format == ExtractTargetFormat.HTML:
            self._to_html()
        elif self._target_format == ExtractTargetFormat.Microarray:
            self.move_to(self._microarray_selection)
        else:
            self.move_to(self._sequence_selection)

    def _microarray_selected(self):
        selected = [x for x in self._microarray_selection.checkboxes if x.isChecked()]
        if len(selected) == 0:
            return
        self.status = ExtractTargetFormat.Microarray
        self.options = [x.text() for x in selected]
        self.close()

    def _sequence_selected(self):
        selected = [x.isChecked() for x in self._sequence_selection.sequencesOptions]
        if not any(selected):
            return
        assert len([x for x in selected if x]) == 1
        index = selected.index(True)
        button = self._sequence_selection.sequencesOptions[index]
        self.status = ExtractTargetSequences[button.objectName()]
        self.options = button.text()
        self.close()
        # self._format_handlers[self._target_format]()

    def back(self):
        if self.main.objectName() == FormatSelection.__name__:
            pass
        elif self.main.objectName() == SequenceSelection.__name__:
            self.move_to(self._format_selection)
        elif self.main.objectName() == MicroarraySelection.__name__:
            self.move_to(self._format_selection)

    def next(self):
        if self.main.objectName() == FormatSelection.__name__:
            self._format_selected()
        elif self.main.objectName() == SequenceSelection.__name__:
            self._sequence_selected()
        elif self.main.objectName() == MicroarraySelection.__name__:
            self._microarray_selected()
