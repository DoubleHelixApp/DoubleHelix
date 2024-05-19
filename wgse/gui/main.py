import os
import sys
import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

from wgse.adapters.alignment_stats_adapter import AlignmentStatsAdapter
from wgse.adapters.header_adapter import (
    HeaderCommentsAdapter,
    HeaderProgramsAdapter,
    HeaderReadGroupAdapter,
    HeaderSequenceAdapter,
)
from wgse.adapters.index_stats_adapter import IndexStatsAdapter
from wgse.adapters.reference_adapter import ReferenceAdapter
from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.alignment_map.index_stats_calculator import IndexStatsCalculator
from wgse.configuration import MANAGER_CFG
from wgse.data.gender import Gender
from wgse.data.sorting import Sorting
from wgse.gui.extract import ExtractDialog
from wgse.gui.table_dialog import ListTableDialog, TableDialog
from wgse.gui.ui_form import Ui_MainWindow
from wgse.utility.external import External
from wgse.utility.shortcut import Shortcut
from wgse.utility.simple_worker import SimpleWorker
from wgse.variant_caller import VariantCaller


class WGSEWindow(QMainWindow):
    def launch():
        app = QApplication(sys.argv)
        widget = WGSEWindow()
        widget.show()
        sys.exit(app.exec())

    def __init__(
        self,
        parent=None,
        config=MANAGER_CFG.GENERAL,
        external: External = External(),
    ):
        super().__init__(parent)
        self._external = external
        self.config = config
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

        self.ui.fileInformationTable.setAlternatingRowColors(True)

        self.ui.fileInformationTable.doubleClicked.connect(self.file_item_clicked)
        self.ui.extract.clicked.connect(self.export)
        self.ui.variant.clicked.connect(self.variant_calling)
        self.ui.progress.hide()
        self.ui.stop.hide()
        self.ui.stop.clicked.connect(self.stop)

        self._long_operation: SimpleWorker = None
        if self.config.last_path != None:
            self.on_open(self.config.last_path)

    def variant_calling(self):
        if self.current_file is None:
            return
        self._prepare_long_operation(f"Variant calling.")
        self._long_operation = VariantCaller(progress=self._set_calling_progress)
        self._worker = SimpleWorker(
            self._long_operation.call,
            self.current_file,
        )

    def _set_calling_progress(self, sub_operation, total, current):
        if current is None:
            self._prepare_ready()
            return
        if total is None or total == 0:
            return
        self.ui.statusbar.showMessage(f"Variant calling, {sub_operation}")
        self.ui.progress.setValue((current / total) * 100)

    def stop(self):
        if self._long_operation is not None:
            self._long_operation.kill()
        self._prepare_ready()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            print("Dropped file:", file_path)
            # Do something with the dropped file

    def export(self):
        if self.current_file is None:
            return
        dialog = ExtractDialog(self.current_file, self)
        dialog.exec()

    def on_close(self):
        MANAGER_CFG.save()
        self.close()

    def closeEvent(self, event=False):
        MANAGER_CFG.save()
        event.accept()

    def on_doc(self):
        webbrowser.open("https://wgse-ng.readthedocs.io", 2)

    def on_open(self, file: Path = False):
        if not file:
            title = "Open file"
            type = "Aligned File (*.bam *.sam *.cram);;"
            type += "Unaligned file (*.fastq);;"
            type += "References (*.fa *.gz *.fna *.fasta)"
            last_path = str(Path.home())
            if self.config.last_path != None:
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
        else:
            self._gender_determined(info.gender)
        click_to_open = "(Click here to open)"

        size = self.current_file.path.stat().st_size
        size /= 1024**3
        size = f"{size:.1f} GB"

        rows = [
            ("Directory", str(self.current_file.path.parent)),
            ("Filename", str(self.current_file.path.name)),
            ("Size", size),
            ("File Type", info.file_type.name),
            (
                "Reference",
                f"{info.reference_genome.build} ({info.reference_genome.status.name})",
            ),
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
        os.startfile(self.current_file.file_info.path.parent)

    def _do_sorting(self):
        if self.current_file is None:
            return
        if self.current_file.file_info.sorted not in [
            Sorting.Unknown,
            Sorting.Unsorted,
        ]:
            return

        prompt = QMessageBox()
        prompt.setWindowTitle("File is not sorted")
        prompt.setText("Do you want to sort the file?")
        prompt.setInformativeText("This may take a while.")
        prompt.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        prompt.setDefaultButton(QMessageBox.StandardButton.No)
        choice = QMessageBox.StandardButton(prompt.exec())
        if choice == QMessageBox.StandardButton.No:
            return

    def _do_indexing(self, user_informed=False):
        if self.current_file is None:
            return
        if self.current_file.file_info.indexed:
            return
        if not user_informed:
            prompt = QMessageBox()
            prompt.setWindowTitle("File is not indexed")
            prompt.setText("Do you want to index the file?")
            prompt.setInformativeText("This may take a while.")
            prompt.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            prompt.setDefaultButton(QMessageBox.StandardButton.No)
            choice = QMessageBox.StandardButton(prompt.exec())
            if choice == QMessageBox.StandardButton.No:
                return
        self._prepare_long_operation("Indexing")
        self._long_operation = SimpleWorker(
            self._external.index, self.current_file.path, io=self._set_index_progress
        )

    def _prepare_long_operation(self, message):
        self.ui.progress.setMaximum(100)
        self.ui.progress.setMinimum(0)
        self.ui.progress.setValue(0)
        self.ui.progress.show()
        self.ui.stop.setEnabled(True)
        self.ui.stop.show()
        self.ui.statusbar.showMessage(message)

    def _prepare_ready(self):
        self._long_operation = None
        self.ui.progress.hide()
        self.ui.stop.setEnabled(False)
        self.ui.stop.hide()
        self.reload()
        self.ui.statusbar.showMessage("Ready.")

    def _set_index_progress(self, read_bytes, _):
        if read_bytes is None:
            self._prepare_ready()
            return
        percentage = read_bytes / self.current_file.path.stat().st_size
        print(int(percentage * 100))
        self.ui.progress.setValue(int(percentage * 100))

    def reload(self):
        self.ui.progress.hide()
        self.ui.stop.hide()
        self.ui.statusbar.showMessage("Ready")
        self.on_open(self.current_file.path)

    def _show_index_stats(self):
        if self.current_file is None:
            return
        if not self.current_file.file_info.indexed:
            prompt = QMessageBox()
            prompt.setWindowTitle("File is not indexed")
            prompt.setText("Index stats are not available if the file is not indexed.")
            prompt.setInformativeText(
                "Do you want to index the file? This may take a while."
            )
            prompt.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            prompt.setDefaultButton(QMessageBox.StandardButton.No)
            choice = QMessageBox.StandardButton(prompt.exec())
            if choice == QMessageBox.StandardButton.No:
                return
            self._do_indexing(user_informed=True)
        if self.current_file.file_info.index_stats is None:
            prompt = QMessageBox()
            prompt.setWindowTitle("Index stats not available")
            prompt.setText("Index stats needs to be calculated for this file.")
            prompt.setInformativeText(
                "Do you want to calculate the stats? This may take a while."
            )
            prompt.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            prompt.setDefaultButton(QMessageBox.StandardButton.No)
            choice = QMessageBox.StandardButton(prompt.exec())
            if choice == QMessageBox.StandardButton.No:
                return

            indexed_stats = IndexStatsCalculator(self.current_file.path)
            self.current_file.file_info.index_stats = indexed_stats.get_stats()
            self.current_file.file_info.gender = self.current_file.get_gender(
                self.current_file.file_info.index_stats
            )

        dialog = TableDialog("Index Statistics", self)
        dialog.set_data(
            IndexStatsAdapter.adapt(self.current_file.file_info.index_stats)
        )
        dialog.exec()

    def _show_coverage_stats(self):
        return

    def _show_reference(self):
        adapted = ReferenceAdapter.adapt(self.current_file.file_info.reference_genome)
        dialog = TableDialog("Reference genome", self)
        dialog.set_data(adapted)
        dialog.exec()

    def _show_alignment_stats(self):
        if self.current_file is None:
            return
        dialog = TableDialog("Alignment statistics", self)
        dialog.set_data(
            AlignmentStatsAdapter.adapt(self.current_file.file_info.alignment_stats)
        )
        dialog.exec()

    def _show_header(self):
        if self.current_file is None:
            return

        dialog = ListTableDialog("Header", self)
        data = {
            "Sequences": HeaderSequenceAdapter.adapt(
                self.current_file.header.sequences.values()
            ),
            "Programs": HeaderProgramsAdapter.adapt(self.current_file.header.programs),
            "Read groups": HeaderReadGroupAdapter.adapt(
                self.current_file.header.read_groups
            ),
            "Comments": HeaderCommentsAdapter.adapt(self.current_file.header.comments),
        }
        dialog.set_data(data)
        dialog.exec()

    def _gender_determined(self, gender: Gender):
        pass
