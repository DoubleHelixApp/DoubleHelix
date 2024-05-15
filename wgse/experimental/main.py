import sys

from PyQt6.QtCore import QMetaProperty, QObject, pyqtSignal
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    bab = engine.load("./wgse/experimental/drag_drop_ui.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())