import logging
import os
import signal
from subprocess import Popen
from threading import Thread

import debugpy


class SimpleWorker(Thread):
    def __init__(self, function, *args, **kwargs) -> None:
        super().__init__()
        self.function = function
        self.process = None
        self._kwargs = kwargs
        self._args = args
        self.start()

    def run(self):
        if debugpy.is_client_connected():
            debugpy.debug_this_thread()
        self.process = self.function(*self._args, **self._kwargs)
        if self.process is not None and isinstance(self.process, Popen):
            self.process.communicate()

    def kill(self):
        process = self.process
        if process is None:
            logging.debug("Trying to kill a SimpleWorker but there's nothing to kill.")
            return
        if not isinstance(process, Popen):
            raise RuntimeError("Trying to kill a process that is not a Popen object.")
        try:
            if hasattr(os.sys, "winver"):
                process.kill()
            else:
                process.send_signal(signal.SIGTERM)
        except Exception as e:
            logging.error(f"Error when killing process {e!s}")
