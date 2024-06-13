import enum
from pathlib import Path

from helix.utility.external import External


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
                raise RuntimeError(f"Error decompressing {input!s}: no extension")
            no_ext = input.name.removesuffix("".join(input.suffixes))
            ext = "".join(input.suffixes[:-1])
            return input.with_name(no_ext + ext)
        else:
            raise RuntimeError(f"Action {action.name} not supported.")

    def gzip(
        self,
        input: Path,
        output: Path,
        action: GZipAction = GZipAction.Decompress,
    ) -> Path:
        if output.exists():
            raise RuntimeError(
                f"Trying to decompress {str(input)} but the destination file {str(output)} exists."
            )
        inferred_filename = self._gzip_filename(input, action)

        action_flags = {GZipAction.Compress: "", GZipAction.Decompress: "-d"}

        try:
            self._external.gzip([action_flags[action], str(input)], wait=True)
        except RuntimeError as ex:
            # RAFZ format is libz compatible but will make gzip sometime exit
            # with a != 0 code, complaining about "trailing garbage data".
            # This is not a real error, as the file is decompressed anyway.
            # The issue is potentially fixable by truncating the file, but
            # there's no practical advantage in doing so. If we fall in this
            # situation, ignore the error.
            if "trailing garbage" not in str(ex):
                raise ex

        if not inferred_filename.exists():
            raise FileNotFoundError(
                "Unable to find inferred filename after gzip action."
            )

        if inferred_filename != output:
            if output.exists():
                output.unlink()
            inferred_filename.rename(output)
