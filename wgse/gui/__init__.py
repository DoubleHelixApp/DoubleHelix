import sys

from PySide6.QtWidgets import QApplication

from wgse.gui.main import WGSEWindow


def main():
    app = QApplication(sys.argv)
    widget = WGSEWindow()
    widget.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()