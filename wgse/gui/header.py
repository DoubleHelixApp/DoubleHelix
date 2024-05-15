# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'header.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHeaderView,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_HeaderDialog(object):
    def setupUi(self, HeaderDialog):
        if not HeaderDialog.objectName():
            HeaderDialog.setObjectName(u"HeaderDialog")
        HeaderDialog.resize(640, 480)
        self.verticalLayout = QVBoxLayout(HeaderDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.itemList = QComboBox(HeaderDialog)
        self.itemList.setObjectName(u"itemList")

        self.verticalLayout.addWidget(self.itemList)

        self.table = QTableWidget(HeaderDialog)
        self.table.setObjectName(u"table")

        self.verticalLayout.addWidget(self.table)


        self.retranslateUi(HeaderDialog)

        QMetaObject.connectSlotsByName(HeaderDialog)
    # setupUi

    def retranslateUi(self, HeaderDialog):
        HeaderDialog.setWindowTitle(QCoreApplication.translate("HeaderDialog", u"Dialog", None))
    # retranslateUi

