# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(724, 562)
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionLog_viewer = QAction(MainWindow)
        self.actionLog_viewer.setObjectName(u"actionLog_viewer")
        self.actionGenomes = QAction(MainWindow)
        self.actionGenomes.setObjectName(u"actionGenomes")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_6 = QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.informationTab = QWidget()
        self.informationTab.setObjectName(u"informationTab")
        self.gridLayout = QGridLayout(self.informationTab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_6 = QPushButton(self.informationTab)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.gridLayout.addWidget(self.pushButton_6, 2, 1, 1, 1)

        self.exportButton = QPushButton(self.informationTab)
        self.exportButton.setObjectName(u"exportButton")

        self.gridLayout.addWidget(self.exportButton, 2, 0, 1, 1)

        self.pushButton_7 = QPushButton(self.informationTab)
        self.pushButton_7.setObjectName(u"pushButton_7")

        self.gridLayout.addWidget(self.pushButton_7, 2, 2, 1, 1)

        self.pushButton = QPushButton(self.informationTab)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 2, 3, 1, 1)

        self.fileInformationTable = QTableWidget(self.informationTab)
        self.fileInformationTable.setObjectName(u"fileInformationTable")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileInformationTable.sizePolicy().hasHeightForWidth())
        self.fileInformationTable.setSizePolicy(sizePolicy)
        self.fileInformationTable.setStyleSheet(u"")
        self.fileInformationTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fileInformationTable.setAlternatingRowColors(True)
        self.fileInformationTable.setShowGrid(True)
        self.fileInformationTable.setGridStyle(Qt.DotLine)
        self.fileInformationTable.setSortingEnabled(False)
        self.fileInformationTable.setColumnCount(0)
        self.fileInformationTable.horizontalHeader().setVisible(False)
        self.fileInformationTable.horizontalHeader().setCascadingSectionResizes(False)
        self.fileInformationTable.horizontalHeader().setStretchLastSection(True)
        self.fileInformationTable.verticalHeader().setVisible(True)
        self.fileInformationTable.verticalHeader().setCascadingSectionResizes(False)
        self.fileInformationTable.verticalHeader().setMinimumSectionSize(30)
        self.fileInformationTable.verticalHeader().setDefaultSectionSize(30)
        self.fileInformationTable.verticalHeader().setHighlightSections(False)
        self.fileInformationTable.verticalHeader().setStretchLastSection(False)

        self.gridLayout.addWidget(self.fileInformationTable, 0, 0, 1, 4)

        self.progressBar = QProgressBar(self.informationTab)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 4)

        self.tabWidget.addTab(self.informationTab, "")

        self.gridLayout_6.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 724, 21))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy1)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuHelp.addAction(self.actionAbout)
        self.menuTools.addAction(self.actionLog_viewer)
        self.menuTools.addAction(self.actionGenomes)

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WGSE - Genome sequencing data manipulation tool", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionLog_viewer.setText(QCoreApplication.translate("MainWindow", u"Log viewer", None))
        self.actionGenomes.setText(QCoreApplication.translate("MainWindow", u"Reference genomes", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"Haplotype", None))
        self.exportButton.setText(QCoreApplication.translate("MainWindow", u"Extract", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"Variant calling", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Analysis", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.informationTab), QCoreApplication.translate("MainWindow", u"Information", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
    # retranslateUi

