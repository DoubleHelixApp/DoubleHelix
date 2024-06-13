import logging
import os
import signal
from subprocess import Popen
from threading import Thread

import debugpy


class SimpleWorker(Thread):
    """Execute a function in another thread.

    It can work in two ways:
        1. Supplying a function that returns a Popen object
        2. Supplying any function and an object that contains a
           kill function
    Example:
        >>> worker = SimpleWorker(None, lambda: Popen(["sleep", "10"]))
        >>> worker.kill()
    In this case SimpleWorker will call the lambda, store the Popen object
    and call .communicate() on it.
        >>> worker = SimpleWorker(MyObjectClass, my_object.long_operation)
        >>> worker.kill()
    In this case SimpleWorker will call long_operation in another thread
    and call my_object.kill() when attempting to kill the operation. How the
    operation will be killed is delegated to MyObjectClass.
    """

    def __init__(self, object, function, *args, **kwargs) -> None:
        super().__init__()
        self.function = function
        self.object = object
        self._kwargs = kwargs
        self._args = args
        if self.function is not None:
            self.start()

    def run(self):
        if debugpy.is_client_connected():
            debugpy.debug_this_thread()
        self.object = self.function(*self._args, **self._kwargs)
        if self.object is not None and isinstance(self.object, Popen):
            self.object.communicate()

    def kill(self):
        object = self.object
        if object is None:
            logging.error("Trying to kill a SimpleWorker but there's nothing to kill.")
            return
        try:
            if hasattr(os.sys, "winver") or not isinstance(object, Popen):
                object.kill()
            else:
                object.send_signal(signal.SIGTERM)
        except Exception as e:
            logging.error(f"Error when killing process {e!s}")
