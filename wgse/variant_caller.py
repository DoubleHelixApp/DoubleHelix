import enum
import shlex
import subprocess
from wgse.alignment_map.alignment_map_file import AlignmentMapFile
from wgse.utility.external import External
from wgse.configuration import MANAGER_CFG


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
    ) -> None:
        self._external = external
        self._ext_config = ext_config
        self._ploidy = str(repo_config.metadata.joinpath("ploidy.txt"))

    def call(self, aligned_file: AlignmentMapFile, type=VariantCallingType.Both):
        reference = str(aligned_file.file_info.reference_genome.ready_reference.fasta)
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

        mpileup: subprocess.Popen = self._external.bcftools(
            pileup_opt, stdout=subprocess.PIPE
        )

        call = self._external.bcftools(call_opt, stdin=mpileup.stdout)
        call.communicate()
        tabix = self._external.tabix(tabix_opt, wait=True)


if __name__ == "__main__":
    file = AlignmentMapFile(MANAGER_CFG.GENERAL.last_path)
    caller = VariantCaller()
    caller.call(file)
