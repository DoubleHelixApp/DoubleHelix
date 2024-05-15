from wgse.alignment_map.alignment_map_header import AlignmentMapHeader
from wgse.data.sorting import Sorting


def test_header_parsed_correctly():
    lines = [
        "@HD\tVN:1.0\tSO:coordinate",
    ]
    sut = AlignmentMapHeader(lines)
    assert len(sut.sequences) == 0
    assert sut.metadata.sorted == Sorting.Coordinate
    assert sut.metadata.version == "1.0"

def test_unsorted_parsed_correctly():
    lines = [
        "@HD\tVN:1.0\tSO:unsorted",
    ]
    sut = AlignmentMapHeader(lines)
    assert len(sut.sequences) == 0
    assert sut.metadata.sorted == Sorting.Unsorted
    assert sut.metadata.version == "1.0"
    
def test_unsorted_parsed_correctly():
    lines = [
        "@HD\tVN:1.0\tSO:unknown",
    ]
    sut = AlignmentMapHeader(lines)
    assert len(sut.sequences) == 0
    assert sut.metadata.sorted == Sorting.Unknown
    assert sut.metadata.version == "1.0"

def test_sequences_parsed_correctly():
    lines = [
        "@SQ\tSN:Seq1\tLN:123\tM5:abcdefabcdef123123\tUR:/directory/genome.fasta"
    ]
    sut = AlignmentMapHeader(lines)
    assert sut.metadata is None
    assert len(sut.sequences) == 1
    assert "Seq1" in sut.sequences
    assert sut.sequences["Seq1"].length == 123
    assert sut.sequences["Seq1"].md5 == "abcdefabcdef123123"
    assert sut.sequences["Seq1"].uri == "/directory/genome.fasta"
