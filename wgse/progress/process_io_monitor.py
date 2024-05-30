import logging
import time
from subprocess import Popen
from threading import Thread

import debugpy
import psutil


class ProcessIOMonitor(Thread):
    def __init__(self, process: Popen, report, polling=1) -> None:
        super().__init__()
        self.process: Popen = process
        self.report = report
        self.polling = polling

    def run(self):
        if debugpy.is_client_connected():
            debugpy.debug_this_thread()
        try:
            process = psutil.Process(self.process.pid)
            while True:
                counters = process.io_counters()
                self.report(counters.read_bytes, counters.write_bytes)
                if process.status() != psutil.STATUS_RUNNING:
                    break
                time.sleep(self.polling)
        except Exception as e:
            # The process can end anytime and psutil will fail.
            # That's not an error.
            if not isinstance(e, psutil.NoSuchProcess):
                logging.error(f"Exception in ProcessIOMonitor: {e!s}")
            pass
        finally:
            # Signal the process ended.
            self.report(None, None)
