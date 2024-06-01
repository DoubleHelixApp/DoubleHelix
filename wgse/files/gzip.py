import enum
from pathlib import Path

from wgse.utility.external import External


class GZipAction(enum.Enum):
    Compress = 0
    Decompress = 1


class GZip:
    def __init__(self, external=External()) -> None:
        self._external = external

    def _gzip_filename(self, input: Path, action: GZipAction):
        if action == GZipAction.Compress:
            return Path(str(input) + ".gz")
        elif action == GZipAction.Decompress:
            if len(input.suffixes) == 0:
                raise RuntimeError(
                    f"Unable to determine decompressed filename, invalid filename {str(input)} (no extensions)."
                )
            ext = "".join(input.suffixes[:-1])
            return input.with_name(input.stem + ext)
        else:
            raise RuntimeError(f"Action {action.name} not supported.")

    def gzip(
        self,
        input: Path,
        output: Path,
        action: GZipAction = GZipAction.Decompress,
    ) -> Path:
        # TODO: move this logic somewhere else.
        if output.exists():
            raise RuntimeError(
                f"Trying to decompress {str(input)} but the destination file {str(output)} exists."
            )
        inferred_filename = self._gzip_filename(input, action)

        action_flags = {GZipAction.Compress: "", GZipAction.Decompress: "-d"}

        process = self._external.gzip([action_flags[action], str(input)])
        process.wait()

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
