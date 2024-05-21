import enum
import logging
import shlex
import subprocess

from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.configuration import MANAGER_CFG
from wgse.utility.external import External


class VariantCallingType(enum.Enum):
    InDel = enum.auto()
    SNP = enum.auto()
    Both = enum.auto()


class VariantCaller:
    def __init__(
        self,
        repo_config=MANAGER_CFG.REPOSITORY,
        ext_config=MANAGER_CFG.EXTERNAL,
        external: External = External(),
        progress=None,
        logger=logging.getLogger(__name__),
    ) -> None:
        self._external = external
        self._ext_config = ext_config
        self._ploidy = str(repo_config.metadata.joinpath("ploidy.txt"))
        self._is_quitting = False
        self._current_operation = None
        self._progress = progress
        self._logger = logger

    def call(self, aligned_file: AlignmentMapFile, type=VariantCallingType.Both):
        if aligned_file.file_info.index_stats is None:
            raise RuntimeError("Index stats cannot be None for variant calling")
        if aligned_file.file_info.reference_genome.ready_reference is None:
            raise RuntimeError("Reference cannot be None for variant calling")
        self.current_file = aligned_file
        reference = str(aligned_file.file_info.reference_genome.ready_reference.fasta)
        self._logger.info(
            f"Calling variants with {aligned_file.file_info.reference_genome.ready_reference}"
        )
        input_file = aligned_file.path

        skip_variant_opt = ""
        if type == VariantCallingType.InDel:
            skip_variant_opt = "-V snps"
        elif type == VariantCallingType.SNP:
            skip_variant_opt = "-V indels"

        output_file = aligned_file.path.with_name(
            f"{aligned_file.path.stem}_{type.name}.vcf.gz"
        )

        pileup_opt = f'mpileup -B -I -C 50 --threads {self._ext_config.threads} -f "{reference}" -Ou "{input_file}"'
        call_opt = f'call --ploidy-file "{self._ploidy}" {skip_variant_opt} -mv -P 0 --threads {self._ext_config.threads} -Oz -o "{output_file}"'
        tabix_opt = f'-p vcf "{output_file}"'

        pileup_opt = shlex.split(pileup_opt)
        call_opt = shlex.split(call_opt)
        tabix_opt = shlex.split(tabix_opt)

        mapped_sequences = [x.mapped for x in self.current_file.file_info.index_stats]
        mapped_sequences = sum(mapped_sequences)

        # 112 bytes seems to be the average bytes written for a single base
        self.pileup_bytes_write = (
            mapped_sequences
            * self.current_file.file_info.alignment_stats.average_length
            * 112
        )

        self._current_operation: subprocess.Popen = self._external.bcftools(
            pileup_opt,
            stdout=subprocess.PIPE,
            io=lambda r, w: self._progress("[1/2] Calling", self.pileup_bytes_write, w),
        )

        call = self._external.bcftools(call_opt, stdin=self._current_operation.stdout)
        call.communicate()
        if self._is_quitting:
            return
        self._current_operation = self._external.tabix(
            tabix_opt,
            wait=True,
            io=lambda r, w: self._progress(
                "[2/2] Indexing", output_file.stat().st_size, r
            ),
        )

    def kill(self):
        self._is_quitting = True
        self._current_operation.kill()

    def _stats(self, operation, read, write):
        if write is not None:
            print(f"{operation}: {(write/self.pileup_bytes_write)*100}")


if __name__ == "__main__":
    file = AlignmentMapFile(MANAGER_CFG.GENERAL.last_path)
    caller = VariantCaller()
    caller.call(file)
