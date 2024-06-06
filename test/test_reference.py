from collections import OrderedDict

from helix.data.genome import Genome
from helix.data.sequence import Sequence
from helix.reference.reference import Reference, ReferenceStatus


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

    ref = Reference(query_sequences)
    assert ref.status == ReferenceStatus.Buildable
    assert len(ref.matching) == 0


def test_name_is_not_matching():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("1", 123, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), [sequences_1[0]]),
        ]
    )

    ref = Reference(query_sequences)
    assert ref.status == ReferenceStatus.Buildable
    assert len(ref.matching) == 0


def test_genome_has_different_md5():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 123, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, "b"), [sequences_1[0]]),
        ]
    )

    assert len(Reference(query_sequences).matching) == 0


def test_genome_has_different_length():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 122, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), [sequences_1[0]]),
        ]
    )

    assert len(Reference(query_sequences).matching) == 0


def test_only_one_genome_matches():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 122, "a", genome_1),
        Sequence("chr2", 123, "b", genome_1),
    ]
    genome_1.sequences = sequences_1

    genome_2 = Genome("https://reference_2.com/fasta.fa", source="Fake", build="38")
    sequences_2 = [
        Sequence("chr1", 122, "a", genome_2),
    ]
    genome_2.sequences = sequences_2

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 122, "a"), [sequences_1[0], sequences_2[0]]),
            (Sequence("chr2", 123, "b"), [sequences_1[1]]),
        ]
    )

    assert len(Reference(query_sequences).matching) == 1


def test_genome_has_different_length_and_md5():
    genome_1 = Genome("https://reference_1.com/fasta.fa", source="Fake", build="38")
    sequences_1 = [
        Sequence("chr1", 123, "a", genome_1),
    ]

    genome_1.sequences = sequences_1

    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 122, "b"), [sequences_1[0]]),
        ]
    )

    assert len(Reference(query_sequences).matching) == 0


def test_no_matches():
    query_sequences = OrderedDict(
        [
            (Sequence("chr1", 123, None), []),
        ]
    )

    assert Reference(query_sequences).status == ReferenceStatus.Unknown
