import webbrowser
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.alignment_map.variant_caller import VariantCaller
from helix.data.extract_target_format import ExtractTargetFormat
from helix.data.file_type import FileType
from helix.progress.simple_worker import SimpleWorker
from helix.renderers.html_aligned_file_report import HTMLAlignedFileReport


class Converter:
    def __init__(
        self,
        current_file: AlignmentMapFile,
        target_format: ExtractTargetFormat,
        options,
        progress=None,
    ) -> None:
        self._format_handlers = {
            ExtractTargetFormat.Microarray: self._to_microarray,
            ExtractTargetFormat.BAM: self._to_bam,
            ExtractTargetFormat.SAM: self._to_sam,
            ExtractTargetFormat.CRAM: self._to_cram,
            ExtractTargetFormat.FASTQ: self._to_fastq,
            ExtractTargetFormat.FASTA: self._to_fasta,
            ExtractTargetFormat.HTML: self._to_html,
            ExtractTargetFormat.VCF: self._to_vcf,
            ExtractTargetFormat.Unknown: self._to_unknown,
        }

        self.current_file = current_file
        self.target_format = target_format
        self.options = options
        self._progress = progress

        # TODO: move to test
        assert all(x in self._format_handlers for x in ExtractTargetFormat)

    def _to_bam(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.BAM, progress=self._progress
        )

    def _to_sam(self):
        if self.current_file is None:
            return
        self._worker = SimpleWorker(
            self.current_file.convert, FileType.SAM, progress=self._progress
        )

    def _to_cram(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.CRAM, progress=self._progress
        )

    def _to_fasta(self):
        if self.current_file is None:
            return

        self._worker = SimpleWorker(
            self.current_file.convert, FileType.FASTA, progress=self._progress
        )

    def _to_fastq(self):
        if self.current_file is None:
            return
        self._worker = SimpleWorker(
            self.current_file.convert, FileType.FASTQ, progress=self._progress
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
