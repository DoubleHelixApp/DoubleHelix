import base64
from pathlib import Path


files = [
    Path("test", "data", "fake_genome_bgzip.fasta.gz"),
    Path("test", "data", "fake_genome.fasta.gz"),
    Path("test", "data", "fake_genome.fasta"),
    Path("test", "data", "fake_genome.zip"),
]

for file in files:
    with file.open("rb") as f:
        b = f.read()
        print(f'{file.name}="{base64.standard_b64encode(b).decode("utf-8")}"')
