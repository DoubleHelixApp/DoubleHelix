from test.utility import MockFile, MockPath

import pytest

from helix.fasta.fasta_letter_counter import FASTALetterCounter


class MockGenome:
    def __init__(self, fasta_lines, dictionary_lines) -> None:
        self.fasta = MockPath(buffer=fasta_lines)
        self.dict = MockPath(buffer=dictionary_lines)


def gzip_open(path: MockPath, mode):
    return MockFile(path._buffer)


def test_run_continuing_across_lines_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'N'*5}\n{'N'*5}\n"
    dict_line = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz\n"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 0
    assert result[0].runs[0].length == 10


def test_run_starting_at_0_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'N'*3}{'A'*5}\n"
    dict_line = (
        "@HD\tVN:1.0\tSO:unsorted\n" "@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 0
    assert result[0].runs[0].length == 3


def test_run_starting_in_the_middle_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'A'*3}{'N'*5}{'A'*3}\n"
    dict_line = (
        "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:11\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 3
    assert result[0].runs[0].length == 5


def test_run_ending_with_line_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'A'*3}{'N'*5}\n"
    dict_line = (
        "@HD\tVN:1.0\tSO:unsorted\n" "@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 3
    assert result[0].runs[0].length == 5


def test_run_not_continuing_in_next_line_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'A'*3}{'N'*5}\n{'A'*3}\n"
    dict_line = (
        "@HD\tVN:1.0\tSO:unsorted\n"
        "@SQ\tSN:1\tLN:11\tM5:dummy\tUR:file://c:/foo.fa.gz"
    )
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 3
    assert result[0].runs[0].length == 5


def test_run_not_continuing_in_next_line_is_processed_correctly():
    # Arrange
    fa_lines = f">1 irrelevant\n{'A'*3}{'N'*5}\n>2 irrelevant\n{'A'*3}{'N'*5}\n"
    dict_line = "@HD\tVN:1.0\tSO:unsorted\n@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz\n@SQ\tSN:2\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz"
    pytest.MonkeyPatch().setattr("gzip.open", gzip_open)
    sut = FASTALetterCounter(MockGenome(fa_lines, dict_line))

    # Act
    result = sut.count_letters()

    # Assert
    assert len([x for x in result if x.name == "1"]) == 1
    assert len([x for x in result if x.name == "2"]) == 1
    assert len(result[0].runs) == 1
    assert result[0].runs[0].start == 3
    assert result[0].runs[0].length == 5
    assert len(result[1].runs) == 1
    assert result[1].runs[0].start == 3
    assert result[1].runs[0].length == 5
