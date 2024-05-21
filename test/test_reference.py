from collections import OrderedDict

from wgse.data.genome import Genome
from wgse.data.sequence import Sequence
from wgse.fasta.reference import Reference, ReferenceStatus


def test_query_is_a_perfect_match():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 123, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), [sequences_1[0]]),
        ]
    )

    assert Reference(query_sequences).status == ReferenceStatus.Downloadable


def test_query_is_superset():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 123, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), [sequences_1[0]]),
            (Sequence("chr2", 124, None), []),
        ]
    )

    assert Reference(query_sequences).status == ReferenceStatus.Unknown


def test_genome_is_superset():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 123, "a", genome_1),
        Sequence("chr2", 124, "b", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), [sequences_1[0]]),
        ]
    )

    assert Reference(query_sequences).status == ReferenceStatus.Buildable


def test_no_matches():
    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), []),
        ]
    )

    assert Reference(query_sequences).status == ReferenceStatus.Unknown
