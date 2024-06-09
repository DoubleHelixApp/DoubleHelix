import logging
from pathlib import Path
import time
from threading import Thread

try:
    import debugpy
except ImportError:
    pass


class FileIOMonitor(Thread):
    def __init__(self, path: Path, report, target, polling=1) -> None:
        super().__init__()
        self.path: Path = path
        self.target = target
        self.report = report
        self.polling = polling
        self._quitting = False
        self.start()

    def run(self):
        if debugpy:
            if debugpy.is_client_connected():
                debugpy.debug_this_thread()
        try:
            while not self._quitting:
                write_bytes = self.path.stat().st_size
                self.report(None, write_bytes)
                if write_bytes == self.target:
                    break
                time.sleep(self.polling)
        except Exception as e:
            # The process can end anytime and psutil will fail.
            # That's not an error.
            logging.error(f"Exception in FileIOMonitor: {e!s}")
            pass
        finally:
            # Signal the process ended.
            self.report(None, None)

    def quit(self):
        self._quitting = True
