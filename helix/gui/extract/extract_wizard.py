import enum

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)

from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.gui.extract.format_selection import ExtractTargetFormat, FormatSelection
from helix.gui.extract.microarray_selection import MicroarraySelection
from helix.gui.extract.sequence_selection import (
    ExtractTargetSequences,
    SequenceSelection,
)


class ExtractTargetSteps(enum.Enum):
    FormatSelection = enum.auto()
    SequenceSelection = enum.auto()
    MicroarraySelection = enum.auto()


class ExtractWizard(QDialog):
    def __init__(self, current_file, parent=None) -> None:
        self.current_file: AlignmentMapFile = current_file
        super().__init__(parent, Qt.WindowType.Dialog)

        self.resize(648, 600)
        self.setObjectName("extract")
        self.setWindowTitle("Extract data")

        # Specify what options were selected
        self.target_format = None
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

    def exec(self):
        super().exec()
        return (self.target_format, self.options)

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
        self.target_format = ExtractTargetFormat[button.objectName()]

        if self.target_format == ExtractTargetFormat.HTML:
            self.close()
        elif self.target_format == ExtractTargetFormat.Microarray:
            self.move_to(self._microarray_selection)
        else:
            self.move_to(self._sequence_selection)

    def _microarray_selected(self):
        selected = [x for x in self._microarray_selection.checkboxes if x.isChecked()]
        if len(selected) == 0:
            return
        self.options = [x.text() for x in selected]
        self.close()

    def _sequence_selected(self):
        selected = [x.isChecked() for x in self._sequence_selection.sequencesOptions]
        if not any(selected):
            return
        assert len([x for x in selected if x]) == 1
        index = selected.index(True)
        button = self._sequence_selection.sequencesOptions[index]
        self.target = ExtractTargetSequences[button.objectName()]
        self.options = button.text()
        self.close()

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
