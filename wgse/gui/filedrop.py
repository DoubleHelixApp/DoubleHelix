# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filedrop.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QSizePolicy, QWidget)

class Ui_Drop(object):
    def setupUi(self, Drop):
        if not Drop.objectName():
            Drop.setObjectName(u"Drop")
        Drop.resize(400, 300)
        self.horizontalLayout = QHBoxLayout(Drop)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(Drop)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label)


        self.horizontalLayout.addWidget(self.groupBox)


        self.retranslateUi(Drop)

        QMetaObject.connectSlotsByName(Drop)
    # setupUi

    def retranslateUi(self, Drop):
        Drop.setWindowTitle(QCoreApplication.translate("Drop", u"Form", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("Drop", u"Drop a file here to begin", None))
    # retranslateUi

