from helix.data.chromosome_name_type import ChromosomeNameType
from helix.naming.converter import Converter
from helix.naming.lookup_tables import ACCESSION_TO_NUMBER


def test_convert_to_number():
    converted_chr1 = Converter.convert("chr1", ChromosomeNameType.Number)
    converted_1 = Converter.convert("1", ChromosomeNameType.Number)
    converted_chrmt = Converter.convert("chrMT", ChromosomeNameType.Number)
    converted_mt = Converter.convert("MT", ChromosomeNameType.Number)
    converted_m = Converter.convert("M", ChromosomeNameType.Number)
    converted_chrx = Converter.convert("chrX", ChromosomeNameType.Number)
    converted_x = Converter.convert("X", ChromosomeNameType.Number)
    converted_chry = Converter.convert("chrY", ChromosomeNameType.Number)
    converted_y = Converter.convert("Y", ChromosomeNameType.Number)
    converted_acc = Converter.convert("CM000663", ChromosomeNameType.Number)

    assert converted_chr1 == "1"
    assert converted_1 == "1"
    assert converted_acc == "1"
    assert converted_chrmt == "M"
    assert converted_mt == "M"
    assert converted_m == "M"
    assert converted_chrx == "X"
    assert converted_x == "X"
    assert converted_chry == "Y"
    assert converted_y == "Y"


def test_convert_to_chr():
    converted_chr1 = Converter.convert("chr1", ChromosomeNameType.Chr)
    converted_1 = Converter.convert("1", ChromosomeNameType.Chr)
    converted_chrmt = Converter.convert("chrMT", ChromosomeNameType.Chr)
    converted_mt = Converter.convert("MT", ChromosomeNameType.Chr)
    converted_m = Converter.convert("M", ChromosomeNameType.Chr)
    converted_chrx = Converter.convert("chrX", ChromosomeNameType.Chr)
    converted_x = Converter.convert("X", ChromosomeNameType.Chr)
    converted_chry = Converter.convert("chrY", ChromosomeNameType.Chr)
    converted_y = Converter.convert("Y", ChromosomeNameType.Chr)
    converted_acc = Converter.convert("CM000663", ChromosomeNameType.Chr)

    assert converted_chr1 == "chr1"
    assert converted_1 == "chr1"
    assert converted_acc == "chr1"
    assert converted_chrmt == "chrM"
    assert converted_mt == "chrM"
    assert converted_m == "chrM"
    assert converted_chrx == "chrX"
    assert converted_x == "chrX"
    assert converted_chry == "chrY"
    assert converted_y == "chrY"


def test_convert_to_accession():
    converted_chr1 = Converter.convert("chr1", ChromosomeNameType.GenBank)
    converted_1 = Converter.convert("1", ChromosomeNameType.GenBank)
    converted_chrmt = Converter.convert("chrMT", ChromosomeNameType.GenBank)
    converted_mt = Converter.convert("MT", ChromosomeNameType.GenBank)
    converted_m = Converter.convert("M", ChromosomeNameType.GenBank)
    converted_chrx = Converter.convert("chrX", ChromosomeNameType.GenBank)
    converted_x = Converter.convert("X", ChromosomeNameType.GenBank)
    converted_chry = Converter.convert("chrY", ChromosomeNameType.GenBank)
    converted_y = Converter.convert("Y", ChromosomeNameType.GenBank)

    assert converted_chr1 == "CM000663"
    assert converted_1 == "CM000663"
    assert converted_chrmt == "J01415"
    assert converted_mt == "J01415"
    assert converted_m == "J01415"
    assert converted_chrx == "CM000685"
    assert converted_x == "CM000685"
    assert converted_chry == "CM000686"
    assert converted_y == "CM000686"


def test_lookup_values_uniqueness():
    for table in ACCESSION_TO_NUMBER:
        assert len(set(x for x in table.values())) == len(table)
