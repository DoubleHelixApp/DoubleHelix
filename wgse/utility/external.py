import logging
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from wgse.configuration import MANAGER_CFG
from wgse.progress.process_io_monitor import ProcessIOMonitor

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    third_party = str(MANAGER_CFG.EXTERNAL.root)
    if third_party not in os.environ["PATH"]:
        os.environ["PATH"] += ";" + third_party
    if ".JAR" not in os.environ["PATHEXT"]:
        os.environ["PATHEXT"] += ";.JAR"


def exe(f, interpreter=[]):
    """This decorator will return a function that will try to launch
    an executable from disk that has the same name of the function
    it's decorating, passing the arguments that were received when
    the function was invoked.

    Args:
        f (Callable): function to decorate.
    """

    def execute_binary(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        args = [*interpreter, shutil.which(f.__name__), *[str(x) for x in args]]

        if wait:
            # Force stdout/stderr to be PIPE as we
            # need to collect the output
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        logger.debug(f"Calling: {shlex.join(args)}")

        # Force windows to hide the prompt window
        startup_info = None
        if sys.platform == "win32":
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        output = subprocess.Popen(
            args,
            stdout=stdout,
            stdin=stdin,
            stderr=stderr,
            startupinfo=startup_info,
            text=text,
        )
        if io is not None:
            monitor = ProcessIOMonitor(output, io)
            monitor.start()
        if wait is True:
            out, err = output.communicate()
            if output.returncode != 0:
                raise RuntimeError(f"Call to {f.__name__} failed: {err.decode()}")
            return out
        return output

    decorated = execute_binary
    decorated.wrapper = exe
    decorated.__name__ = f.__name__
    return decorated


def jar(f):
    """Same thing as run but this deals with .jar files
    automatically, invoking java from PATH and specifying
    the right arguments, including the full path of the .jar
    file.

    Args:
        f (callable): function to decorate

    Returns:
        callable: Decorated function
    """
    full_path = shutil.which(f.__name__)
    if full_path is None:
        # Should raise NotImplementedError
        f.wrapper = jar
        return f
    full_path = Path(".", full_path)
    full_path = full_path.with_suffix(".jar")
    f.__name__ = str(full_path)
    decorated = exe(f, ["java", "-jar"])
    decorated.wrapper = jar
    return decorated


class External:
    """Wrapper around 3rd party executables

    TODO: make this class contains only wrappers around exe/jar files and
    move the rest of the logic somewhere else (e.g., Samtools class with
    view(), consensus(), ..., a Haplogrep class, a gzip class etc.).
    """

    def __init__(self, config=MANAGER_CFG.EXTERNAL) -> None:
        self._config = config
        if not self._config.root.exists():
            raise FileNotFoundError(
                f"Unable to find root directory for External: {str(self._config.root)}"
            )
        if str(self._config.root) not in os.environ["PATH"]:
            os.environ["PATH"] += ";" + str(self._config.root)

        self._htsfile = "htsfile"

    def get_file_type(self, path: Path):
        process = subprocess.run([self._htsfile, path], capture_output=True, check=True)
        return process.stdout.decode("utf-8")

    def haplogrep_classify(self, vcf_file, output_file):
        output = self.haplogrep(
            ["classify", "--in", vcf_file, "--format", "vcf", "--out", output_file],
            wait=True,
        )
        output.decode("utf-8")
        return output

    # Starting from here all the functions are
    # just calling executables with the same name.
    # See the implementation of @exe and @jar decorator
    # for more details.

    @exe
    def gzip(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def bgzip(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def samtools(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def bwa(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def bwamem2(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def minimap2(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def fastp(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def bcftools(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @exe
    def tabix(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @jar
    def haplogrep(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @jar
    def FastQC(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @jar
    def picard(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()

    @jar
    def DISCVRSeq(
        self,
        args=[],
        stdout=None,
        stdin=None,
        stderr=None,
        wait=False,
        io=None,
        text=False,
    ):
        raise FileNotFoundError()
