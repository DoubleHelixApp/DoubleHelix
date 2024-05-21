from wgse.data.genome import Genome
from wgse.data.sequence import Sequence
from wgse.fasta.reference import Reference


def test():
    genome = Genome("https://reference.com/fasta.fa", source="Fake", build="38")
    sequences = [
        Sequence("chr1", 123, "abcdef1234", genome),
        Sequence("chr2", 124, "abcdef1235", genome),
        Sequence("chr3", 123, "abcdef1236", genome),
    ]
    genome.sequences = sequences

    query_sequences = sequences.copy()

    Reference()
