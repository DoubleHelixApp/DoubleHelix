import random
import textwrap
from pathlib import Path

from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.reference.genome_metadata_loader import MetadataLoader


class FakeReferenceGenomeGenerator:

    ACGT_PERCENTAGE = {"A": 0.309, "T": 0.294, "G": 0.199, "C": 0.198}

    def __init__(self, fasta_dictionary: Path, read_length: int):
        self.read_length = read_length
        self.dictionary = AlignmentMapHeader.load_from_file(fasta_dictionary)

    def generate_fasta(self, length, filename: Path = Path("fake_genome.fasta")):
        bases = list(FakeReferenceGenomeGenerator.ACGT_PERCENTAGE.keys())
        bases_weights = list(FakeReferenceGenomeGenerator.ACGT_PERCENTAGE.values())

        total_bases = sum([x.length for x in self.dictionary.sequences.values()])

        with open(filename, "w") as f:
            for name, entry in self.dictionary.sequences.items():
                length_adapted = int((entry.length / total_bases) * length)
                reminder = length_adapted % self.read_length
                length_adapted += self.read_length - reminder
                sequence = "".join(
                    random.choices(bases, weights=bases_weights, k=length_adapted)
                )
                lines = "\n".join(textwrap.wrap(sequence, 60))
                if len(sequence) == 0:
                    print(f"Got 0bp to generate for sequence {name}. Skipping")
                    continue
                print(f"Got {length_adapted}bp for sequence {name}")
                f.write(f">{name}\n")
                f.write(lines + "\n")


# Example usage:
if __name__ == "__main__":
    metadata = MetadataLoader()
    g = metadata.load()

    generator = FakeReferenceGenomeGenerator(g[0].dict, 150)
    generator.generate_fasta(100000)
