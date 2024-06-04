import sys

from PySide6.QtWidgets import QApplication

from helix.gui.main import HelixWindow


def main():
    app = QApplication(sys.argv)
    # Use a less broken UI style
    app.setStyle("fusion")
    widget = HelixWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
