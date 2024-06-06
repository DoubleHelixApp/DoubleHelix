from test.utility import MockFile, MockPath

import pytest

from helix.fasta.fasta_letter_counter import FASTALetterCounter


class MockGenome:
    def __init__(self, fasta, dict) -> None:
        self.fasta = fasta
        self.dict = dict


def gzip_open(path, mode):
    return MockFile(path._buffer)


def test_no_dictionary():
    fa_lines = f">1 irrelevant\n{'N'*5}\n{'N'*5}\n>2 irrelevant\n"

    with pytest.raises(RuntimeError) as e:
        genome = MockGenome(MockPath(buffer=fa_lines), MockPath(exists=False))
        sut = FASTALetterCounter(genome)
        assert "Unable to find dictionary" in str(e.value)


def test_sequence_not_in_dictionary():
    fa_lines = f">1 irrelevant\n{'N'*5}\n{'N'*5}\n>2 irrelevant\n"
    dict_lines = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)

    with pytest.raises(ValueError) as e:
        genome = MockGenome(MockPath(buffer=fa_lines), MockPath(buffer=dict_lines))
        FASTALetterCounter(genome).count_letters()
    assert "not present in dictionary" in str(e.value)


def test_fastq():
    fa_lines = ">1 irrelevant\n{'N'*5}\n{'N'*5}\n+2 irrelevant\n"
    dict_lines = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)

    with pytest.raises(RuntimeError) as e:
        genome = MockGenome(MockPath(buffer=fa_lines), MockPath(buffer=dict_lines))
        FASTALetterCounter(genome).count_letters()
    assert "Expected a FASTA" in str(e.value)


def test_duplicate_sequence():
    fa_lines = f">1 irrelevant\n{'N'*5}\n{'N'*5}\n>1 irrelevant\n"
    dict_lines = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)

    with pytest.raises(RuntimeError) as e:
        genome = MockGenome(MockPath(buffer=fa_lines), MockPath(buffer=dict_lines))
        FASTALetterCounter(genome).count_letters()
    assert "duplicated sequence" in str(e.value)


def test_only_comments():
    fa_lines = f"#Hello\n#Foo\n"
    dict_lines = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)

    with pytest.raises(RuntimeError) as e:
        genome = MockGenome(MockPath(buffer=fa_lines), MockPath(buffer=dict_lines))
        FASTALetterCounter(genome).count_letters()
    assert "no sequences" in str(e.value)
