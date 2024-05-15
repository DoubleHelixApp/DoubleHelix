from test.utility import MockFile, MockPath

import pytest

from wgse.fasta.fasta_letter_counter import FASTALetterCounter


class MockGenome:
    def __init__(self, fasta_lines, dictionary_lines) -> None:
        self.fasta = MockPath(fasta_lines)
        self.dict = MockPath(dictionary_lines)


def gzip_open(path, mode):
    return MockFile(path.lines)


def test_run_continuing_across_lines_is_processed_correctly():
    # Arrange
    fa_lines = [
        ">1 irrelevant\n",
        f"{'N'*5}\n",
        f"{'N'*5}\n",
    ]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:10\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
    fa_lines = [">1 irrelevant\n", f"{'N'*3}{'A'*5}\n"]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
    fa_lines = [
        ">1 irrelevant\n",
        f"{'A'*3}{'N'*5}{'A'*3}\n",
    ]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:11\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
    fa_lines = [">1 irrelevant", f"{'A'*3}{'N'*5}\n"]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
    fa_lines = [
        ">1 irrelevant",
        f"{'A'*3}{'N'*5}\n",
        f"{'A'*3}\n",
    ]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:11\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
    fa_lines = [
        ">1 irrelevant",
        f"{'A'*3}{'N'*5}\n",
        ">2 irrelevant",
        f"{'A'*3}{'N'*5}\n",
    ]
    dict_line = [
        "@HD\tVN:1.0\tSO:unsorted",
        "@SQ\tSN:1\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz",
        "@SQ\tSN:2\tLN:8\tM5:dummy\tUR:file://c:/foo.fa.gz",
    ]
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
