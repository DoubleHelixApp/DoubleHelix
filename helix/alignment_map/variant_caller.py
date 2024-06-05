import enum
import logging
import shlex
import subprocess
from time import sleep

from helix.progress.base_progress_calculator import BaseProgressCalculator
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.configuration import MANAGER_CFG
from helix.progress.simple_worker import SimpleWorker
from helix.utility.external import External


class VariantCallingType(enum.Enum):
    InDel = enum.auto()
    SNP = enum.auto()
    Both = enum.auto()


class VariantCaller(SimpleWorker):
    def __init__(
        self,
        input: AlignmentMapFile,
        calling_type=VariantCallingType.Both,
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
        self._quitting_ack = False
        self._current_operation = None
        self._progress = progress
        self._logger = logger
        self._input_file = input
        self._calling_type = calling_type

        if self._input_file.file_info.index_stats is None:
            raise RuntimeError("Index stats cannot be None for variant calling")
        if self._input_file.file_info.reference_genome.ready_reference is None:
            raise RuntimeError("Reference cannot be None for variant calling")

    def call(self):
        return self.run()

    def run(self):
        self.current_file = self._input_file
        reference = str(
            self._input_file.file_info.reference_genome.ready_reference.fasta
        )
        self._logger.info(
            f"Calling variants with {self._input_file.file_info.reference_genome.ready_reference}"
        )
        input_file = self._input_file.path

        skip_variant_opt = ""
        if self._calling_type == VariantCallingType.InDel:
            skip_variant_opt = "-V snps"
        elif self._calling_type == VariantCallingType.SNP:
            skip_variant_opt = "-V indels"

        output_file = self._input_file.path.with_name(
            f"{self._input_file.path.stem}_{self._calling_type.name}.vcf.gz"
        )

        pileup_opt = f'mpileup -B -I -C 50 --threads {self._ext_config.threads} -f "{reference}" -Ou "{input_file}"'
        call_opt = f'call --ploidy-file "{self._ploidy}" {skip_variant_opt} -mv -P 0 --threads {self._ext_config.threads} -Oz -o "{output_file}"'
        tabix_opt = f'-p vcf "{output_file}"'

        pileup_opt = shlex.split(pileup_opt)
        call_opt = shlex.split(call_opt)
        tabix_opt = shlex.split(tabix_opt)

        progress = None
        if self._progress is not None:
            mapped_sequences = [
                x.mapped for x in self.current_file.file_info.index_stats
            ]
            mapped_sequences = sum(mapped_sequences)

            # 112 bytes seems to be the average bytes written for a single base
            total_bytes = (
                mapped_sequences
                * self.current_file.file_info.alignment_stats.average_length
                * 112
            )

            progress = BaseProgressCalculator(
                self._progress, total_bytes, "[1/2] Calling"
            )
            progress = progress.compute_on_write_bytes

        self._current_operation = self._external.bcftools(
            pileup_opt,
            stdout=subprocess.PIPE,
            io=progress,
        )

        call = self._external.bcftools(call_opt, stdin=self._current_operation.stdout)
        call.communicate()
        if self._is_quitting:
            self._quitting_ack = True
            return

        progress = BaseProgressCalculator(
            self._progress, output_file.stat().st_size, "[2/2] Indexing"
        )
        self._current_operation = self._external.tabix(
            tabix_opt, io=progress.compute_on_read_bytes
        )
        self._current_operation.wait()
        self._quitting_ack = True

    def kill(self):
        self._is_quitting = True
        try:
            # The while is just to prevent a (unlikely IMO but who knows) situation
            # where _is_quitting is seen as False by the other thread after Popen.kill()
            # has been called.
            for _ in range(10):
                operation = self._current_operation
                if self._quitting_ack:
                    break
                if operation is not None:
                    operation.kill()
                self._current_operation = None
                if self._quitting_ack:
                    break
                sleep(0.5)
            if not self._quitting_ack:
                raise RuntimeError(
                    f"Failed 10 attempts to kill {self._current_operation}."
                )
        except Exception as e:
            self._logger.error(f"Error while killing variant calling: {e!s}")
