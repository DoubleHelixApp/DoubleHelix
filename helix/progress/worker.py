import logging
import os
import signal
from subprocess import Popen
from threading import Thread

try:
    import debugpy
except Exception:
    debugpy = None


class Worker(Thread):
    """Execute a function in another thread.

    It can work in two ways:
        1. Supplying a function that returns a Popen object
        2. Supplying any function and an object that contains a
           kill function
    Example:
        >>> worker = Worker(None, lambda: Popen(["sleep", "10"]))
        >>> worker.kill()
    In this case Worker will call the lambda, store the Popen object
    and call .communicate() on it.
        >>> worker = Worker(MyObjectClass, my_object.long_operation)
        >>> worker.kill()
    In this case Worker will call long_operation in another thread
    and call my_object.kill() when attempting to kill the operation. How the
    operation will be killed is delegated to MyObjectClass.
    """

    def __init__(self, object, function, *args, **kwargs) -> None:
        super().__init__()
        self.object = object
        self.function = function
        self._kwargs = kwargs
        self._args = args
        if self.function is not None:
            self.start()

    def run(self):
        try:
            if debugpy is not None:
                if debugpy.is_client_connected():
                    debugpy.debug_this_thread()
            self.object = self.function(*self._args, **self._kwargs)
            if self.object is not None and isinstance(self.object, Popen):
                self.object.communicate()
        except Exception:
            pass

    def kill(self):
        object = self.object
        if object is None:
            logging.error("Trying to kill a Worker but there's nothing to kill.")
            return
        try:
            if hasattr(os.sys, "winver") or not isinstance(object, Popen):
                object.kill()
            else:
                object.send_signal(signal.SIGTERM)
        except Exception as e:
            logging.error(f"Error when killing process {e!s}")
