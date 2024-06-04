# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(724, 562)
        MainWindow.setMinimumSize(QSize(0, 20))
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName("actionDocumentation")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionLog_viewer = QAction(MainWindow)
        self.actionLog_viewer.setObjectName("actionLog_viewer")
        self.actionGenomes = QAction(MainWindow)
        self.actionGenomes.setObjectName("actionGenomes")
        self.actionCreate_launcher_on_desktop = QAction(MainWindow)
        self.actionCreate_launcher_on_desktop.setObjectName(
            "actionCreate_launcher_on_desktop"
        )
        self.actionHaplotype = QAction(MainWindow)
        self.actionHaplotype.setObjectName("actionHaplotype")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.extract = QPushButton(self.centralwidget)
        self.extract.setObjectName("extract")

        self.horizontalLayout.addWidget(self.extract)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 3)

        self.progress = QProgressBar(self.centralwidget)
        self.progress.setObjectName("progress")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress.sizePolicy().hasHeightForWidth())
        self.progress.setSizePolicy(sizePolicy)
        self.progress.setMinimumSize(QSize(0, 0))
        self.progress.setValue(24)

        self.gridLayout.addWidget(self.progress, 2, 0, 1, 1)

        self.stop = QPushButton(self.centralwidget)
        self.stop.setObjectName("stop")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.stop.sizePolicy().hasHeightForWidth())
        self.stop.setSizePolicy(sizePolicy1)
        self.stop.setMinimumSize(QSize(0, 0))

        self.gridLayout.addWidget(self.stop, 2, 2, 1, 1)

        self.fileInformationTable = QTableWidget(self.centralwidget)
        self.fileInformationTable.setObjectName("fileInformationTable")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.fileInformationTable.sizePolicy().hasHeightForWidth()
        )
        self.fileInformationTable.setSizePolicy(sizePolicy2)
        self.fileInformationTable.setStyleSheet("")
        self.fileInformationTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fileInformationTable.setAlternatingRowColors(False)
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

        self.gridLayout.addWidget(self.fileInformationTable, 0, 0, 1, 3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 724, 21))
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy3)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
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
        self.menuTools.addAction(self.actionHaplotype)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionCreate_launcher_on_desktop)

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate(
                "MainWindow", "Helix - Genome sequencing data manipulation tool", None
            )
        )
        self.actionSettings.setText(
            QCoreApplication.translate("MainWindow", "Settings", None)
        )
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", "Open", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionDocumentation.setText(
            QCoreApplication.translate("MainWindow", "Documentation", None)
        )
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", "About", None)
        )
        self.actionLog_viewer.setText(
            QCoreApplication.translate("MainWindow", "Log viewer", None)
        )
        self.actionGenomes.setText(
            QCoreApplication.translate("MainWindow", "Reference genomes", None)
        )
        self.actionCreate_launcher_on_desktop.setText(
            QCoreApplication.translate("MainWindow", "Create launcher on desktop", None)
        )
        self.actionHaplotype.setText(
            QCoreApplication.translate("MainWindow", "Haplotype", None)
        )
        self.extract.setText(QCoreApplication.translate("MainWindow", "Extract", None))
        self.stop.setText(QCoreApplication.translate("MainWindow", "Stop", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", "Tools", None))

    # retranslateUi
