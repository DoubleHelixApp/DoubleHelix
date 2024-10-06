import logging
import time
from subprocess import Popen
from threading import Thread

import debugpy
import psutil


class ProcessIOMonitor(Thread):
    """Monitor read/write on disk of a process
    until its death.

    Args:
        process (Popen): Process to monitor
        report Callable[[str, float], None]: function to report read/write on disk
        polling (float): Seconds between polling
    """

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
        except psutil.NoSuchProcess:
            # The process can end anytime and psutil will fail.
            # That's not an error.
            pass
        except Exception as e:
            logging.error(f"Exception in ProcessIOMonitor: {e!s}")
        finally:
            # Signal the process ended.
            self.report(None, None)
