from pathlib import Path

from helix.reference.reference import Reference
from helix.utility.external import External


class MicroarrayGenerator:
    def __init__(
        self, vcf_file: Path, reference: Reference, external: External
    ) -> None:
        self.input = vcf_file
        self._external = external
        self._reference = reference

    def do(self):
        # output = ""
        # destination = ""
        # tabix_opt = f"-p vcf {self.input}"
        # bcftools_opt = f"annotate -Oz -a
        # {self._reference.ready_reference} -c CHROM,POS,ID {self.input}"
        # bcftools_opt = (
        # f"query -f '%ID\tCHROM\t%POS[\t%TGT\n' {output} -o {destination} "
        # )
        pass

    # VCF -> Indexing -> Annotate -> Indexing -> Query
