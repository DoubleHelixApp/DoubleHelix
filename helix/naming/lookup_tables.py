# This file contains some lookup tables to convert forth and back
# between various accession naming systems and the "Number format"
# (i.e., digit only for autosomes, X/Y for sexual, M for mitochondrial).
# NOTE: There's a test that ensure values are unique and the dictionary can be
# reversed.


def __reverse(dictionary: dict):
    """Take a dictionary and swap keys with values"""
    return {v: k for k, v in dictionary.items()}


# Lookup table to convert from NCBI accession to
# Number format. Applies to gapped references.
# Source: https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000001405.29/
REFSEQ_TO_NUMBER = {
    "NC_000001": "1",
    "NC_000002": "2",
    "NC_000003": "3",
    "NC_000004": "4",
    "NC_000005": "5",
    "NC_000006": "6",
    "NC_000007": "7",
    "NC_000008": "8",
    "NC_000009": "9",
    "NC_000010": "10",
    "NC_000011": "11",
    "NC_000012": "12",
    "NC_000013": "13",
    "NC_000014": "14",
    "NC_000015": "15",
    "NC_000016": "16",
    "NC_000017": "17",
    "NC_000018": "18",
    "NC_000019": "19",
    "NC_000020": "20",
    "NC_000021": "21",
    "NC_000022": "22",
    "NC_000023": "X",
    "NC_000024": "Y",
    "NC_012920": "M",
}
NUMBER_TO_REFSEQ = __reverse(REFSEQ_TO_NUMBER)

# Lookup table to convert from GenBank/INSDC
# accession to Number. Applies to gapped references.
# Source: https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000001405.29/
GENBANK_TO_NUMBER = {
    "CM000663": "1",
    "CM000664": "2",
    "CM000665": "3",
    "CM000666": "4",
    "CM000667": "5",
    "CM000668": "6",
    "CM000669": "7",
    "CM000670": "8",
    "CM000671": "9",
    "CM000672": "10",
    "CM000673": "11",
    "CM000674": "12",
    "CM000675": "13",
    "CM000676": "14",
    "CM000677": "15",
    "CM000678": "16",
    "CM000679": "17",
    "CM000680": "18",
    "CM000681": "19",
    "CM000682": "20",
    "CM000683": "21",
    "CM000684": "22",
    "CM000685": "X",
    "CM000686": "Y",
    "J01415": "M",
}
NUMBER_TO_GENBANK = __reverse(GENBANK_TO_NUMBER)

# Lookup table to convert from GenBank accession
# to Number. Applies to T2T references.
# Source: https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_009914755.1/
REFSEQ_T2T_TO_NUMBER = {
    "NC_060925": "1",
    "NC_060926": "2",
    "NC_060927": "3",
    "NC_060928": "4",
    "NC_060929": "5",
    "NC_060930": "6",
    "NC_060931": "7",
    "NC_060932": "8",
    "NC_060933": "9",
    "NC_060934": "10",
    "NC_060935": "11",
    "NC_060936": "12",
    "NC_060937": "13",
    "NC_060938": "14",
    "NC_060939": "15",
    "NC_060940": "16",
    "NC_060941": "17",
    "NC_060942": "18",
    "NC_060943": "19",
    "NC_060944": "20",
    "NC_060945": "21",
    "NC_060946": "22",
    "NC_060947": "X",
    "NC_060948": "Y",
}
NUMBER_TO_REFSEQ_T2T = __reverse(REFSEQ_T2T_TO_NUMBER)

# Lookup table to convert from GenBank accession
# to Number. Applies to T2T references.
# Source: https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_009914755.1/
GENBANK_T2T_TO_NUMBER = {
    "CP068277": "1",
    "CP068276": "2",
    "CP068275": "3",
    "CP068274": "4",
    "CP068273": "5",
    "CP068272": "6",
    "CP068271": "7",
    "CP068270": "8",
    "CP068269": "9",
    "CP068268": "10",
    "CP068267": "11",
    "CP068266": "12",
    "CP068265": "13",
    "CP068264": "14",
    "CP068263": "15",
    "CP068262": "16",
    "CP068261": "17",
    "CP068260": "18",
    "CP068259": "19",
    "CP068258": "20",
    "CP068257": "21",
    "CP068256": "22",
    "CP068255": "X",
    "CP086569": "Y",
    "CP068254": "MT",
}
NUMBER_TO_GENBANK_T2T = __reverse(GENBANK_T2T_TO_NUMBER)


ACCESSION_TO_NUMBER = [
    REFSEQ_TO_NUMBER,
    REFSEQ_T2T_TO_NUMBER,
    GENBANK_TO_NUMBER,
    GENBANK_T2T_TO_NUMBER,
]

NUMBER_TO_ACCESSION = [
    NUMBER_TO_REFSEQ,
    NUMBER_TO_REFSEQ_T2T,
    NUMBER_TO_GENBANK,
    NUMBER_TO_GENBANK_T2T,
]
