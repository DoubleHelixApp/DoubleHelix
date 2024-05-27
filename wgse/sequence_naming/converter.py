from wgse.data.chromosome_name_type import ChromosomeNameType
from wgse.data.sequence_type import SequenceType
from wgse.sequence_naming.lookup_tables import (
    GENBANK_T2T_TO_NUMBER,
    GENBANK_TO_NUMBER,
    NUMBER_TO_GENBANK,
    NUMBER_TO_GENBANK_T2T,
    NUMBER_TO_REFSEQ,
    NUMBER_TO_REFSEQ_T2T,
    REFSEQ_T2T_TO_NUMBER,
    REFSEQ_TO_NUMBER,
)


class Converter:
    def canonicalize(sequence_name: str) -> str:
        return Converter.convert(sequence_name, ChromosomeNameType.Number)

    def get_type(sequence_name: str) -> str:
        canonical_name = Converter.canonicalize(sequence_name)
        if canonical_name.isnumeric():
            return SequenceType.Autosome
        elif canonical_name == "X":
            return SequenceType.X
        elif canonical_name == "Y":
            return SequenceType.Y
        elif canonical_name == "M":
            return SequenceType.Mitochondrial
        elif canonical_name == "*":
            return SequenceType.Unmapped
        return SequenceType.Other

    def _find_in_table(input, table):
        normalized = input
        for key in table:
            if input.startswith(key):
                normalized = table[key]
                break
        return normalized

    def convert(input: str, target: ChromosomeNameType) -> str:
        # Convert the input to Number format:
        # chr1 -> 1; chrMT/MT->M; NC_000001 -> 1
        normalized = input.upper()
        if normalized.startswith("CHR"):
            normalized = normalized.replace("CHR", "", 1)
        if normalized.startswith("MT"):
            normalized = normalized.replace("MT", "M", 1)

        if input.startswith("NC_"):
            normalized = Converter._find_in_table(normalized, REFSEQ_TO_NUMBER)
            normalized = Converter._find_in_table(normalized, REFSEQ_T2T_TO_NUMBER)
        elif input.startswith("CM") or input.startswith("J"):
            normalized = Converter._find_in_table(normalized, GENBANK_TO_NUMBER)
        elif input.startswith("CP"):
            normalized = Converter._find_in_table(normalized, GENBANK_T2T_TO_NUMBER)

        # Convert from Number format to target
        normalized = normalized.upper()
        if target == ChromosomeNameType.Chr:
            if normalized.isnumeric() or normalized in ["M", "X", "Y"]:
                return "chr" + normalized.upper()
            return normalized
        elif target == ChromosomeNameType.Number:
            return normalized
        elif target == ChromosomeNameType.GenBank:
            return NUMBER_TO_GENBANK.get(normalized, None)
        elif target == ChromosomeNameType.RefSeq:
            return NUMBER_TO_REFSEQ.get(normalized, None)
        elif target == ChromosomeNameType.RefSeqT2T:
            return NUMBER_TO_REFSEQ_T2T.get(normalized, None)
        elif target == ChromosomeNameType.GenBankT2T:
            return NUMBER_TO_GENBANK_T2T.get(normalized, None)
        raise ValueError(f"Converting to unrecognized target format: {target.name}")
