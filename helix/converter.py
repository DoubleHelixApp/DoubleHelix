import webbrowser
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.alignment_map.variant_caller import VariantCaller
from helix.data.extract_target_format import ExtractTargetFormat
from helix.data.file_type import FileType
from helix.progress.worker import Worker
from helix.renderers.html_aligned_file_report import HTMLAlignedFileReport


class Converter:
    def __init__(
        self,
        current_file: AlignmentMapFile,
        target_format: ExtractTargetFormat,
        options,
        progress=None,
    ) -> None:
        if current_file is None:
            raise ValueError("current_file cannot be null")

        if target_format is None:
            raise ValueError("target_format cannot be null")

        self._format_handlers = {
            ExtractTargetFormat.Microarray: self._to_microarray,
            ExtractTargetFormat.BAM: lambda: self._simple_conversion(FileType.BAM),
            ExtractTargetFormat.SAM: lambda: self._simple_conversion(FileType.SAM),
            ExtractTargetFormat.CRAM: lambda: self._simple_conversion(FileType.CRAM),
            ExtractTargetFormat.FASTQ: lambda: self._simple_conversion(FileType.FASTQ),
            ExtractTargetFormat.FASTA: lambda: self._simple_conversion(FileType.FASTA),
            ExtractTargetFormat.HTML: self._to_html,
            ExtractTargetFormat.VCF: self._to_vcf,
            ExtractTargetFormat.Unknown: self._to_unknown,
        }

        if target_format not in self._format_handlers:
            raise ValueError("Invalid target_format")

        self.current_file = current_file
        self.target_format = target_format
        self.options = options
        self._progress = progress

        # TODO: move to test
        assert all(x in self._format_handlers for x in ExtractTargetFormat)

    def start(self):
        self._format_handlers[self.target_format]()

    def _simple_conversion(self, file_type):
        if self.current_file is None:
            return

        self._worker = Worker(
            None,
            self.current_file.convert,
            file_type,
            progress=self._progress,
        )

    def _to_html(self):
        if self.current_file is None:
            return

        html_page = HTMLAlignedFileReport.from_aligned_file(self.current_file)
        current_path = self.current_file.path
        extensions = "".join(current_path.suffixes[:-1])
        name = current_path.stem + extensions + ".html"
        target = current_path.with_name(name)

        with target.open("wt") as f:
            f.write(html_page)
        self._progress(None, None)
        webbrowser.open(target)

    def _to_microarray(self):
        pass

    def _to_vcf(self):
        if self.current_file is None:
            return

        self._worker = VariantCaller(self.current_file, progress=self._progress)
        self._worker.start()

    def _to_unknown(self):
        raise RuntimeError("BUG: Invalid target format")

    def kill(self):
        if self._worker is None:
            return
        self._worker.kill()
