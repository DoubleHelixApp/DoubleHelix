import enum
import logging
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from wgse.configuration import MANAGER_CFG

logger = logging.getLogger(__name__)

if "win" in sys.platform:
    third_party = str(MANAGER_CFG.EXTERNAL.root)
    if third_party not in os.environ["PATH"]:
        os.environ["PATH"] += ";" + third_party
    if ".JAR" not in os.environ["PATHEXT"]:
        os.environ["PATHEXT"] += ";.JAR"


class BgzipAction(enum.Enum):
    Compress = 0
    Decompress = 1
    Reindex = 2


def exe(f, interpreter=[]):
    """This decorator will return a function that will try to launch
    an executable from disk that has the same name of the function
    it's decorating, passing the arguments that were received when
    the function was invoked.

    Args:
        f (Callable): function to decorate.
    """

    def execute_binary(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        args = [*interpreter, shutil.which(f.__name__), *[str(x) for x in args]]

        if wait:
            # Force stdout/stderr to be PIPE as we
            # need to collect the output
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        logger.debug(f"Calling: {shlex.join(args)}")

        output = subprocess.Popen(args, stdout=stdout, stdin=stdin, stderr=stderr)
        if wait == True:
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
        self._samtools = "samtools"
        self._gzip = "gzip"

    def get_file_type(self, path: Path):
        process = subprocess.run([self._htsfile, path], capture_output=True, check=True)
        return process.stdout.decode("utf-8")

    def fasta_index(self, path: Path, output: Path = None):
        if output is None:
            output = Path(str(path) + ".fai")

        arguments = [self._samtools, "faidx", path, "-o", output]
        process = subprocess.run(arguments, check=True, capture_output=True)
        return process.stdout.decode("utf-8")

    def view(self, file: Path, output: Path, *args):
        arguments = [self._samtools, "view", "-H", "--no-PG", *args, file]
        process = subprocess.run(arguments, check=True, capture_output=True)
        return process.stdout.decode("utf-8")

    def make_dictionary(self, path: Path, output: Path = None):
        if output is None:
            output = Path(path.parent, path.name + ".dict")
        arguments = [self._samtools, "dict", str(path), "-o", str(output)]
        process = subprocess.run(arguments, check=True, capture_output=True)
        return process.stdout.decode("utf-8")

    def index(self, path: Path, wait=True):
        return self.samtools(
            ["index", "-@", self._config.threads, "-b", str(path)], wait=wait
        )

    def _gzip_filename(self, input: Path, action: BgzipAction):
        if action == BgzipAction.Compress:
            return Path(str(input) + ".gz")
        elif action == BgzipAction.Decompress:
            if len(input.suffixes) == 0:
                raise RuntimeError(
                    f"Unable to determine decompressed filename, invalid filename {str(input)} (no extensions)."
                )
            ext = "".join(input.suffixes[:-1])
            return input.with_name(input.stem + ext)
        elif action == BgzipAction.Reindex:
            return Path(str(input) + ".gzi")
        else:
            raise RuntimeError(f"Action {action.name} not supported.")

    def gzip(
        self,
        input: Path,
        output: Path,
        action: BgzipAction = BgzipAction.Decompress,
    ) -> Path:
        # TODO: move this logic somewhere else.
        if output.exists():
            raise RuntimeError(
                f"Trying to decompress {str(input)} but the destination file {str(output)} exists."
            )
        inferred_filename = self._gzip_filename(input, action)

        action_flags = {BgzipAction.Compress: "", BgzipAction.Decompress: "-d"}

        arguments = [self._gzip, action_flags[action], str(input)]
        process = subprocess.run(arguments, capture_output=True)

        # RAFZ format is libz compatible but will make gzip sometime exit
        # with a != 0 code, complaining about "trailing garbage data".
        # This is not a real error, as the file is decompressed anyway.
        # The issue is potentially fixable by truncating the file, but
        # there's no practical advantage in doing so. If we fall in this
        # situation, ignore the error.
        if process.returncode != 0:
            if "trailing garbage" not in process.stderr.decode():
                raise RuntimeError(
                    f"gzip exited with return code {process.returncode}: {process.stderr.decode()}"
                )

        if inferred_filename != output:
            inferred_filename.rename(output)

    def bgzip_wrapper(
        self,
        input: Path,
        output: Path,
        action: BgzipAction = BgzipAction.Compress,
    ) -> Path:
        if output.exists():
            output.unlink()

        action_flags = {
            BgzipAction.Compress: "-if",
            BgzipAction.Decompress: "-d",
            BgzipAction.Reindex: "-r",
        }
        inferred_filename = self._gzip_filename(input, action)

        out = self.bgzip(
            [action_flags[action], str(input), "-@", str(self._config.threads)],
            wait=True,
        )
        if inferred_filename != output:
            inferred_filename.rename(output)
            if action == BgzipAction.Compress:
                target = Path(str(output) + ".gzi")
                inferred_gzi_filename = Path(str(inferred_filename) + ".gzi")
                if target.exists():
                    target.unlink()
                if not inferred_gzi_filename.exists():
                    raise FileNotFoundError(f"BGZIP index not found for {inferred_gzi_filename.name}")
                inferred_gzi_filename.rename(target)
        return output

    def idxstats(self, input: Path):
        """Generate BAM index statistics"""
        arguments = [self._samtools, "idxstat", input]
        process = subprocess.run(arguments)
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
    def bgzip(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def samtools(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def bwa(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def bwamem2(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def minimap2(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def fastp(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def bcftools(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @exe
    def tabix(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @jar
    def haplogrep(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @jar
    def FastQC(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @jar
    def picard(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()

    @jar
    def DISCVRSeq(self, args=[], stdout=None, stdin=None, stderr=None, wait=False):
        raise FileNotFoundError()
