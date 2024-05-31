import logging
import os
import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
    QAbstractScrollArea,
)

from wgse.adapters.alignment_stats_adapter import AlignmentStatsAdapter
from wgse.adapters.coverage_stats_adapter import CoverageStatsAdapter
from wgse.adapters.header_adapter import (
    HeaderCommentsAdapter,
    HeaderProgramsAdapter,
    HeaderReadGroupAdapter,
    HeaderSequenceAdapter,
)
from wgse.adapters.index_stats_adapter import IndexStatsAdapter
from wgse.adapters.reference_adapter import ReferenceAdapter
from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.alignment_map.depth_analyzer import CoverageStatsCalculator
from wgse.alignment_map.index_stats_calculator import IndexStatsCalculator
from wgse.configuration import MANAGER_CFG
from wgse.data.sorting import Sorting
from wgse.fasta.reference import ReferenceStatus
from wgse.gui.extract.extract_wizard import ExtractWizard
from wgse.gui.table_dialog import ListTableDialog, TableDialog
from wgse.gui.ui_form import Ui_MainWindow
from wgse.progress.base_progress_calculator import BaseProgressCalculator
from wgse.reference.repository_manager import Repository
from wgse.utility.external import External
from wgse.utility.samtools import Samtools
from wgse.utility.shortcut import Shortcut
from wgse.progress.simple_worker import SimpleWorker


class WGSEWindow(QMainWindow):

    _percentage_updated = Signal(int)
    _message_updated = Signal(str)
    _operation_ended = Signal()
    _coverage_ready = Signal()

    def launch():
        app = QApplication(sys.argv)
        widget = WGSEWindow()
        widget.show()
        sys.exit(app.exec())

    def __init__(
        self,
        parent=None,
        config=MANAGER_CFG.GENERAL,
        external=External(),
        samtools=Samtools(),
        repository=Repository(),
    ):
        super().__init__(parent)
        self._external = external
        self._samtools = samtools
        self._repository = repository
        self.config = config
        self.current_file = None
        self._logger = logging.getLogger("main")

        self.switch_to_main()
        self.ui.actionDocumentation.triggered.connect(self.on_doc)
        self.ui.actionOpen.triggered.connect(self.on_open)
        self.ui.actionExit.triggered.connect(self.on_close)
        self.ui.actionSettings.triggered.connect(self.on_settings)
        self.ui.actionCreate_launcher_on_desktop.triggered.connect(self.create_launcher)

    def create_launcher(self):
        path = Shortcut().create()
        message_box = QMessageBox()
        message_box.setWindowTitle("Created")
        message_box.setText(f"A link to WGSE-NG was created at {path}")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()

    def switch_to_main(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.fileInformationTable.doubleClicked.connect(self.file_item_clicked)
        self.ui.extract.clicked.connect(self.export)
        self.ui.stop.clicked.connect(self.stop)

        self._message_updated.connect(self.ui.statusbar.showMessage)
        self._percentage_updated.connect(self.ui.progress.setValue)
        self._coverage_ready.connect(self._show_coverage_stats)
        self._operation_ended.connect(self._prepare_ready)

        self._long_operation: SimpleWorker = None
        self._prepare_ready(self.config.last_path)

    def stop(self):
        if self._long_operation is not None:
            self._long_operation.kill()
            self._long_operation = None
            self._worker = None
        self._prepare_ready()

    def export(self):
        if self.current_file is None:
            return
        self._prepare_long_operation("Prepare exporting")
        dialog = ExtractWizard(self.current_file, self, progress=self._set_progress)
        dialog.exec()
        if dialog._worker is not None:
            self._long_operation = dialog
            self._worker = dialog._worker
        else:
            self._prepare_ready()

    def closeEvent(self, event=False):
        MANAGER_CFG.save()
        event.accept()

    def on_close(self):
        MANAGER_CFG.save()
        self.close()

    def on_doc(self):
        webbrowser.open("https://wgse-ng.readthedocs.io", 2)

    def on_open(self, file: Path = False):
        if not file:
            title = "Open file"
            type = "Aligned File (*.bam *.sam *.cram);;"
            type += "Unaligned file (*.fastq);;"
            type += "References (*.fa *.gz *.fna *.fasta)"
            last_path = str(Path.home())
            if self.config.last_path is not None:
                if self.config.last_path.is_dir():
                    last_path = str(self.config.last_path)
                else:
                    last_path = str(Path(self.config.last_path).parent)
            file = QFileDialog.getOpenFileName(self, title, last_path, type)
            if file[0] == "":
                return
            file = Path(file[0])

        if not file.exists():
            return
        if not file.is_file():
            return

        self.config.last_path = file
        self.load_aligned(file)

    def on_settings(self):
        pass

    def load_aligned(self, file):
        self.current_file = AlignmentMapFile(Path(file))
        info = self.current_file.file_info

        sorted_string = info.sorted.name
        if info.sorted in [Sorting.Unknown, Sorting.Unsorted]:
            sorted_string += " (Click to sort)"

        indexed_string = str(info.indexed)
        gender_string = info.gender.name
        if not info.indexed:
            indexed_string += " (Click to index)"
            gender_string += " (File is not indexed)"
        click_to_open = "(Click here to open)"

        reference_str = (
            f"{info.reference_genome.build}, {info.reference_genome.status.name} "
        )
        reference_str += "(Click for details)"

        size = self.current_file.path.stat().st_size
        size /= 1024**3
        size = f"{size:.1f} GB"

        rows = [
            ("Directory", str(self.current_file.path.parent)),
            ("Filename", str(self.current_file.path.name)),
            ("Size", size),
            ("File Type", info.file_type.name),
            ("Reference", reference_str),
            ("Gender", gender_string),
            ("Sorted", sorted_string),
            ("Indexed", indexed_string),
            ("Mitochondrial DNA Model", info.mitochondrial_dna_model.name),
            ("Header", click_to_open),
            ("Alignment stats", click_to_open),
            ("Index stats", click_to_open),
            ("Coverage stats", click_to_open),
        ]

        self.ui.fileInformationTable.setRowCount(len(rows))
        self.ui.fileInformationTable.setColumnCount(1)
        for index, row in enumerate(rows):
            header, value = row
            self.ui.fileInformationTable.setVerticalHeaderItem(
                index, QTableWidgetItem(header)
            )
            self.ui.fileInformationTable.setItem(index, 0, QTableWidgetItem(value))

    def file_item_clicked(self, index: QModelIndex):
        if self.current_file is None:
            return
        handlers = {
            "Directory": self._open_dir,
            "Sorted": self._do_sorting,
            "Indexed": self._do_indexing,
            "Reference": self._show_reference,
            "Header": self._show_header,
            "Alignment stats": self._show_alignment_stats,
            "Index stats": self._show_index_stats,
            "Coverage stats": self._show_coverage_stats,
        }
        item = self.ui.fileInformationTable.verticalHeaderItem(index.row())
        if item.text() not in handlers:
            return
        handlers[item.text()]()

    def _open_dir(self):
        if getattr(os, "startfile", None):
            os.startfile(self.current_file.file_info.path.parent)

    def _do_sorting(self):
        if self.current_file is None:
            return
        if self.current_file.file_info.sorted not in [
            Sorting.Unknown,
            Sorting.Unsorted,
        ]:
            return

        choice = self._yn_message_box(
            "File is not sorted",
            "Do you want to sort the file?",
            "This may take a while.",
        )
        if choice == QMessageBox.StandardButton.No:
            return

    def _do_indexing(self, user_informed=False):
        if self.current_file is None:
            return
        if self.current_file.file_info.indexed:
            return
        if not user_informed:
            choice = self._yn_message_box(
                "File is not indexed",
                "Do you want to index the file?",
                "This may take a while.",
            )
            if choice == QMessageBox.StandardButton.No:
                return
        self._prepare_long_operation("Start indexing.")
        progress = BaseProgressCalculator(
            self._set_progress, self.current_file.path.stat().st_size, "Indexing"
        )

        try:
            self._long_operation = SimpleWorker(
                self._samtools.index,
                self.current_file.path,
                io=progress.compute_on_read_bytes,
            )
        except Exception as e:
            self._logger.error(f"Error while initializing indexing: {e!s}")
            self._prepare_ready()

    def _set_progress(self, label, percentage):
        # Memento: this is always called from another thread.
        #   Don't put anything here that is updating the UI if
        #   you don't want the app to crash spectacularly and
        #   you don't want to spend the next 2 hours troubleshooting
        #   the issue. Manage every interaction with the UI with
        #   signal/slots.
        if label is None:
            self._operation_ended.emit()
            return
        self._percentage_updated.emit(percentage)
        self._message_updated.emit(label)

    def _prepare_long_operation(self, message):
        self.ui.progress.setMaximum(100)
        self.ui.progress.setMinimum(0)
        self.ui.progress.setValue(0)
        self.ui.progress.show()
        self.ui.stop.setEnabled(True)
        self.ui.stop.show()
        self.ui.extract.hide()
        self.ui.statusbar.showMessage(message)

    def _prepare_ready(self, path=None):
        self._long_operation = None
        self.ui.progress.hide()
        self.ui.stop.setEnabled(False)
        self.ui.stop.hide()
        if self.current_file is not None:
            self.on_open(self.current_file.path)
        elif path is not None:
            self.on_open(path)
        self.ui.statusbar.showMessage("Ready")
        self.ui.extract.show()

    def _yn_message_box(self, title, text, info=None):
        prompt = QMessageBox()
        prompt.setWindowTitle(title)
        prompt.setText(text)
        if info is not None:
            prompt.setInformativeText(info)

        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        prompt.setStandardButtons(buttons)
        prompt.setDefaultButton(QMessageBox.StandardButton.Yes)
        return QMessageBox.StandardButton(prompt.exec())

    def _show_index_stats(self):
        if self.current_file is None:
            return

        if not self.current_file.file_info.indexed:
            choice = self._yn_message_box(
                "File is not indexed",
                "Index stats are not available if the file is not indexed.",
                "Do you want to index the file? This may take a while.",
            )
            if choice == QMessageBox.StandardButton.No:
                return
            self._do_indexing(user_informed=True)

        if self.current_file.file_info.index_stats is None:
            choice = self._yn_message_box(
                "Index stats not available",
                "Index stats needs to be calculated for this file.",
                "Do you want to calculate the stats? This may take a while.",
            )
            if choice == QMessageBox.StandardButton.No:
                return

            indexed_stats = IndexStatsCalculator(self.current_file.path)
            self.current_file.file_info.index_stats = indexed_stats.get_stats()
            self.current_file.file_info.gender = self.current_file.get_gender(
                self.current_file.file_info.index_stats
            )
            self.current_file.save_meta()

        index_stats = self.current_file.file_info.index_stats
        dialog = TableDialog("Index Statistics", self)
        dialog.set_data(IndexStatsAdapter.adapt(index_stats))
        dialog.exec()

    def _show_coverage_stats(self):
        if self.current_file is None:
            return

        if self.current_file.file_info.coverage_stats is None:
            choice = self._yn_message_box(
                "Coverage stats are not computed",
                "Do you want to calculate coverage stats? This may take a while.",
            )
            if choice == QMessageBox.StandardButton.No:
                return
            self._prepare_long_operation("Preparing to compute coverage stats")
            self._worker = SimpleWorker(self._compute_coverage_stats)
        else:
            coverage_statistics = self.current_file.file_info.coverage_stats
            dialog = TableDialog("Coverage Statistics", self)
            dialog.tableWidget.setSizeAdjustPolicy(
                QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
            )
            dialog.set_data(CoverageStatsAdapter.adapt(coverage_statistics))
            dialog.tableWidget.resizeColumnsToContents()
            dialog.exec()

    def _compute_coverage_stats(self):
        self._long_operation = CoverageStatsCalculator(progress=self._set_progress)
        self.current_file.file_info.coverage_stats = self._long_operation.get_stats(
            self.current_file
        )
        self.current_file.save_meta()
        self._coverage_ready.emit()

    def _show_reference(self):
        if self.current_file is None:
            return
        reference = self.current_file.file_info.reference_genome
        if (
            reference.ready_reference is None
            and reference.status == ReferenceStatus.Downloadable
        ):
            choice = self._yn_message_box(
                "Reference is not on disk",
                "A matching reference genome for this aligned file is available to be downloaded",
                "Would you like to download it?",
            )
            if choice == QMessageBox.StandardButton.Yes:
                self._perform_reference_download()
        reference = self.current_file.file_info.reference_genome
        dialog = TableDialog("Reference genome", self)
        dialog.tableWidget.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        dialog.set_data(ReferenceAdapter.adapt(reference))
        dialog.tableWidget.resizeColumnsToContents()
        dialog.exec()

    def _perform_reference_download(self):
        if self.current_file is None:
            return
        status = self.current_file.file_info.reference_genome.status
        if status != ReferenceStatus.Downloadable:
            return
        reference = self.current_file.file_info.reference_genome
        for match in reference.matching:
            try:
                SimpleWorker(self._repository.download, match, self._set_progress)
                break
            except Exception as e:
                self._logger.error(f"Error while downloading the reference: {e!s}")

    def _show_alignment_stats(self):
        if self.current_file is None:
            return

        if self.current_file.file_info.alignment_stats is None:
            self._yn_message_box(
                "Alignment stats not available",
                "Cannot compute alignment stats if there are no references available.",
                "",
            )
            return
        alignment_stats = self.current_file.file_info.alignment_stats
        dialog = TableDialog("Alignment statistics", self)
        dialog.set_data(AlignmentStatsAdapter.adapt(alignment_stats))
        dialog.exec()

    def _show_header(self):
        if self.current_file is None:
            return

        sequences = self.current_file.header.sequences.values()
        programs = self.current_file.header.programs
        read_groups = self.current_file.header.read_groups
        comments = self.current_file.header.comments

        dialog = ListTableDialog("Header", self)
        dialog.set_data(
            {
                "Sequences": HeaderSequenceAdapter.adapt(sequences),
                "Programs": HeaderProgramsAdapter.adapt(programs),
                "Read groups": HeaderReadGroupAdapter.adapt(read_groups),
                "Comments": HeaderCommentsAdapter.adapt(comments),
            }
        )
        dialog.exec()
