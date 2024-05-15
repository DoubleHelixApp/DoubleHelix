from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDialog,
                               QTableWidget, QTableWidgetItem, QVBoxLayout)


class TableDialog(QDialog):
    def __init__(
        self, title="Dialog", parent=None, f=Qt.WindowType.Dialog, horizontal = False
    ) -> None:
        super().__init__(parent, f)
        self.horizontal = horizontal
        self.setObjectName(title)
        self.setWindowTitle(title)
        self.resize(648, 480)
        
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.tableWidget)
        
        self.setWindowModality(Qt.WindowModality.ApplicationModal)        
        QMetaObject.connectSlotsByName(self)

    def set_data(self, headers, rows):
        for index, header in enumerate(headers):
            if self.horizontal:
                self.tableWidget.setRowCount(len(rows))
                self.tableWidget.setColumnCount(max(len(x) for x in rows))
                self.tableWidget.setHorizontalHeaderItem(index, QTableWidgetItem(header))
                self.tableWidget.horizontalHeader().setStretchLastSection(True)
                self.tableWidget.verticalHeader().hide()
            else:
                self.tableWidget.setRowCount(len(rows))
                self.tableWidget.setColumnCount(max(len(x) for x in rows))
                self.tableWidget.setVerticalHeaderItem(index, QTableWidgetItem(header))
                self.tableWidget.horizontalHeader().setStretchLastSection(True)
                self.tableWidget.horizontalHeader().hide()

        for row_index, row in enumerate(rows):
            for col_index, text in enumerate(row):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(text))
                
class ListTableDialog(TableDialog):
    def __init__(self, title="Dialog", parent=None, f=Qt.WindowType.Dialog, horizontal=False) -> None:
        super().__init__(title, parent, f, horizontal)
        self.itemList = QComboBox(self)
        self.itemList.setObjectName(u"itemList")
        self.verticalLayout.insertWidget(0, self.itemList)
        self.data = None
        self.itemList.currentIndexChanged.connect(self.index_changed)
        
    def set_data(self, data: dict[str, (list[str], list[list[str]])]):
        self.itemList.addItems(list(data.keys()))
        self.data = data
        self.index_changed(0)
    
    def index_changed(self, index):
        if self.data is None:
            return
        text = self.itemList.itemText(index)
        super().set_data(self.data[text][0], self.data[text][1])