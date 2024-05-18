from PyQt6.QtCore import QObject, QThread
from PySide6.QtCore import Signal


import os
import signal
from subprocess import Popen

import debugpy
import psutil


class IOMonitor(QThread):
    def __init__(
        self, process: Popen, io_report, polling_seconds=1, parent=None
    ) -> None:
        super().__init__(parent)
        self.process: Popen = process
        self.io_report = io_report
        self.polling_seconds = polling_seconds

    def run(self):
        debugpy.debug_this_thread()
        try:
            while True:
                self.sleep(self.polling_seconds)
                process = psutil.Process(self.process.pid)
                counters = process.io_counters()
                self.io_report(counters.read_bytes, counters.write_bytes)
                if process.status() != psutil.STATUS_RUNNING:
                    break
        except Exception as e:
            self.io_report(None, None)


class SimpleWorker(QThread):
    def __init__(self, function, parent=None, io_report=None) -> None:
        super().__init__(parent)
        self.progress = Signal(int)
        self.function = function
        self.process: Popen = None
        self.io_report = io_report
        self._io_monitor = None

    def run(self):
        debugpy.debug_this_thread()
        self.process = self.function()
        if isinstance(self.process, Popen) and self.io_report is not None:
            self._io_monitor = IOMonitor(self.process, self.io_report)
            self._io_monitor.start()
        if self.process is not None:
            self.process.wait()

    def kill(self):
        if hasattr(os.sys, "winver"):
            self.process.kill()
        else:
            self.process.send_signal(signal.SIGTERM)
