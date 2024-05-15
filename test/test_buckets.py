import pytest

from wgse.fasta.letter_run_buckets import LetterRunBuckets
from wgse.fasta.letter_run_collection import LetterRunCollection


def test_single_bucket():
    # Arrange
    sequence = LetterRunCollection("Foo", 1000)
    sequence.open_run(0)
    sequence.close_run(100)
    # Act
    # 1000/10 = 100 -> 10 buckets with length of 100
    sut = LetterRunBuckets(sequence, 10, 0).buckets
    # Assert
    assert 0 in sut
    assert len(sut) == 1
    assert sut[0] == 99
    
def test_more_run_in_single_bucket():
    # Arrange
    sequence = LetterRunCollection("Foo", 1000)
    sequence.open_run(0)
    sequence.close_run(50)
    
    sequence.open_run(51)
    sequence.close_run(60)
    # Act
    # 1000/10 = 100 -> 10 buckets with length of 100
    sut = LetterRunBuckets(sequence, 10, 0).buckets
    # Assert
    assert 0 in sut
    assert len(sut) == 1
    assert sut[0] == 59
    
def test_run_in_multiple_buckets():
    # Arrange
    sequence = LetterRunCollection("Foo", 1000)
    sequence.open_run(0)
    sequence.close_run(150)
    # Act
    # 1000/10 = 100 -> 10 buckets with length of 100
    sut = LetterRunBuckets(sequence, 10, 0).buckets
    # Assert
    assert 0 in sut
    assert 1 in sut
    assert len(sut) == 2
    assert sut[0] == 99 # 0 -> 99
    assert sut[1] == 50 # 99 -> 151
    
def test_too_many_buckets():
    sequence = LetterRunCollection("Foo", 1000)

    sequence.open_run(0)
    sequence.close_run(99)

    sequence.open_run(100)
    sequence.close_run(201)

    sut = LetterRunBuckets(sequence, 1001, 0).buckets
    assert len(sut) == 0
    
def test_run_end_to_end_divisible():
    sequence = LetterRunCollection("Foo", 1000)

    sequence.open_run(0)
    sequence.close_run(1000)
    sut = LetterRunBuckets(sequence, 10, 0).buckets
    for index in range(10):
        assert index in sut
        assert sut[index] == 99


def test_run_end_to_end_non_divisible():
    sequence = LetterRunCollection("Foo", 1000)

    sequence.open_run(0)
    sequence.close_run(1000)
    sut = LetterRunBuckets(sequence, 3, 0).buckets
    assert 0 in sut
    assert 1 in sut
    assert 2 in sut    
    assert 3 in sut
    
    assert len(sut) == 4
    assert sut[0] == 332
    assert sut[1] == 332
    assert sut[2] == 332
    assert sut[3] == 1