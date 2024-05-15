import pytest

from wgse.fasta.letter_run_collection import LetterRunCollection


def test_sequence_with_invalid_length():
    with pytest.raises(IndexError) as e:
        LetterRunCollection("Foo", 0)
    assert "greater than" in str(e.value)

def test_end_incomplete_sequence():
    with pytest.raises(ValueError) as e:
        sut = LetterRunCollection("Foo", 100)
        sut.end(99)
    assert "but processed" in str(e.value)
    
def test_open_run_on_ended_sequence():
    with pytest.raises(RuntimeError) as e:
        sut = LetterRunCollection("Foo", 100)
        sut.end(100)
        sut.open_run(101)
    assert "ended" in str(e.value)

def test_double_open_run():
    with pytest.raises(RuntimeError) as e:
        sut = LetterRunCollection("Foo", 10)
        sut.open_run(0)
        sut.open_run(0)
    assert "already opened" in str(e.value)

def test_negative_open():
    with pytest.raises(IndexError) as e:
        sut = LetterRunCollection("Foo", 10)
        sut.open_run(-10)
    assert "negative" in str(e.value)

def test_close_run_less_equal_than_open():
    with pytest.raises(RuntimeError) as e:
        sut = LetterRunCollection("Foo", 10)
        sut.open_run(0)
        sut.close_run(0)
    assert "greater" in str(e.value)

def test_only_close_run():
    with pytest.raises(RuntimeError) as e:
        sut = LetterRunCollection("Foo", 10)
        sut.close_run(0)
    assert "already closed" in str(e.value)

def test_double_close_run():
    with pytest.raises(RuntimeError) as e:
        sut = LetterRunCollection("Foo", 1)
        sut.open_run(0)
        sut.close_run(1)
        sut.close_run(1)
    assert "already closed" in str(e.value)

def test_close_run_greater_than_open():
    # Arrange
    sut = LetterRunCollection("Foo", 10)
    # Act    
    sut.open_run(0)
    sut.close_run(1)
    # Assert
    assert len(sut.runs) == 1
    assert sut.runs[0].start == 0
    assert sut.runs[0].length == 1

def test_overlapping_runs():
    with pytest.raises(ValueError) as e:
        sut = LetterRunCollection("Foo", 19)
        sut.open_run(0)
        sut.close_run(15)

        sut.open_run(15)
        sut.close_run(19)
    assert "overlapping" in str(e.value)

def test_filter():
    # Arrange
    sequence = LetterRunCollection("Foo", 449)
    # Act
    sequence.open_run(0)
    sequence.close_run(150)
    sequence.open_run(300)
    sequence.close_run(449)
    sut = sequence.filter(lambda x: x.length > 149)
    # Assert
    assert len(sut) == 1
    assert sut[0].start == 0
    assert sut[0].length == 150
    
def test_is_run_open():
    sut = LetterRunCollection("Foo", 150)
    sut.open_run(0)
    assert sut.is_run_open() == True
    sut.close_run(150)
    assert sut.is_run_open() == False