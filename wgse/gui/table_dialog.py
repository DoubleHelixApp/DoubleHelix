from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    # QHeaderView,
)

from wgse.data.tabular_data import TabularData


class TableDialog(QDialog):
    def __init__(self, title="Dialog", parent=None, f=Qt.WindowType.Dialog) -> None:
        super().__init__(parent, f)
        self.setObjectName(title)
        self.setWindowTitle(title)
        self.resize(640, 480)

        self.tableWidget = QTableWidget(self)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.ResizeMode.ResizeToContents
        # )
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.tableWidget)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        QMetaObject.connectSlotsByName(self)

    def set_data(self, data: TabularData):
        self.tableWidget.setRowCount(len(data.rows))
        self.tableWidget.setColumnCount(max(len(x.columns) for x in data.rows))
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        if data.horizontal_header:
            for index, header in enumerate(data.horizontal_header):
                self.tableWidget.setHorizontalHeaderItem(
                    index, QTableWidgetItem(header)
                )
        else:
            self.tableWidget.horizontalHeader().hide()

        vertical_header = False
        for row_index, row in enumerate(data.rows):
            if row.vertical_header is not None:
                self.tableWidget.setVerticalHeaderItem(
                    row_index, QTableWidgetItem(row.vertical_header)
                )
                vertical_header = True
            for col_index, text in enumerate(row.columns):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(text))
        if not vertical_header:
            self.tableWidget.verticalHeader().hide()


class ListTableDialog(TableDialog):
    """A simple dialog that is showing a list and a table"""

    def __init__(self, title="Dialog", parent=None, f=Qt.WindowType.Dialog) -> None:
        super().__init__(title, parent, f)
        self.itemList = QComboBox(self)
        self.verticalLayout.insertWidget(0, self.itemList)
        self.data = None
        self.itemList.currentIndexChanged.connect(self.index_changed)

    def set_data(self, data: dict[str, TabularData]):
        self.itemList.addItems(list(data.keys()))
        self.data = data
        self.index_changed(0)

    def index_changed(self, index):
        if self.data is None:
            return
        text = self.itemList.itemText(index)
        super().set_data(self.data[text])
