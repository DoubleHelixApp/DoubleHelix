from PyQt6.QtCore import QThread
from PySide6.QtCore import Signal


import os
import signal
from subprocess import Popen


class SimpleWorker(QThread):
    def __init__(self, function, parent=None) -> None:
        super().__init__(parent)
        self.progress = Signal(int)
        self.function = function
        self.process: Popen = None

    def run(self):
        self.process = self.function()
        self.process.wait()

    def kill(self):
        if hasattr(os.sys, "winver"):
            self.process.kill()
        else:
            self.process.send_signal(signal.SIGTERM)