from pathlib import Path

import pytest

from helix.data.genome import Genome
import base64

# Each contains the same reference in different formats with a single sequence named chr10 having 60bp long.
format_map = {
    "bgzip": "fake_genome_bgzip.fasta.gz",
    "gzip": "fake_genome.fasta.gz",
    "fasta": "fake_genome.fasta",
    "zip": "fake_genome.zip",
    "razf": "fake_genome_razf.fasta.gz",
}
reverse_format_map = {x: y for y, x in format_map.items()}

file_map = {
    format_map[
        "bgzip"
    ]: "H4sIBAAAAAAA/wYAQkMCAE8As0vOKDI04OVyD3F2d3R0d3R2dwfSIY4hIc5A6Oju7AgUBTKcQSKOzs4gDJIHiTsDhdydHUMAtSygWkQAAAAfiwgEAAAAAAD/BgBCQwIAGwADAAAAAAAAAAAA",
    format_map[
        "gzip"
    ]: "H4sICKGhYmYEAGZha2VfZ2Vub21lLmZhc3RhABWKsQkAMQAC+4ffJVkgIBYu4AZpUmf/IoqIcrr2uXP8n0wBAqWkYTOCiNAUloCsu5czKAc/tSygWkQAAAA=",
    format_map[
        "fasta"
    ]: "PmNocjEwDQpHVENHQUFHQUNHR0dBQVRBVFRDVENUQUdDQUFBR0NUQUNBVFRDQUNDQ0FDQ0FBVEFDQUFBQ1RUQ0dDQVQ=",
    format_map[
        "zip"
    ]: "UEsDBBQAAAAIAF0/x1i1LKBaNQAAAEQAAAARAAAAZmFrZV9nZW5vbWUuZmFzdGEVibEJADEAAvuH3yVZICAWLuAGaVJn/yKKiHK39rlz/J9MAQKlrGEzgYjQHJaAbOvLGaSIB1BLAQI/ABQAAAAIAF0/x1i1LKBaNQAAAEQAAAARACQAAAAAAAAAIAAAAAAAAABmYWtlX2dlbm9tZS5mYXN0YQoAIAAAAAAAAQAYAOIsJMmfuNoB0n99zZ+42gFLn4mpn7jaAVBLBQYAAAAAAQABAGMAAABkAAAAAAA=",
    format_map[
        "razf"
    ]: "H4sIBAAAAAAAAwcAUkFaRgGAALNLzigyNODlcg9xdnd0dHd0dncH0iGOISHOQOjo7uwIFAUynEEijs7OIAySB4k7A4WACkIAtSygWkQAAAAAAAAAAAAAAAAAAAAAAAAAAAAARAAAAAAAAABQ",
}

md5_map = {
    format_map["bgzip"]: "ca76b4375bd41f81cfe2003d314dd4b2",
    format_map["gzip"]: "a070ccf700131775e1d8a3cc9128107a",
    format_map["fasta"]: "069c8ead795424e20e4a21fc5e368599",
    format_map["zip"]: "c463c4be4bf8d9a03bcd99ab74eaf1b8",
    format_map["razf"]: "4e299205f6a94ed9b18795f81fa80b33",
}


@pytest.fixture()
def remote_repo_fixture(tmp_path: Path):
    genomes = {}
    tmp_path = tmp_path.joinpath("repo")
    tmp_path.mkdir(exist_ok=True)
    for name, content in file_map.items():
        path = tmp_path.joinpath(name).absolute()
        with path.open("wb") as f:
            f.write(base64.b64decode(content))
        uri_path = path.as_uri()  # e.g., file://c:/.. or file://home/..

        genome = Genome(uri_path, build="38", source="Fake")
        genomes[reverse_format_map[name]] = {
            "genome": genome,
            "file_on_disk": path,
            "md5": md5_map[name],
            "size": path.stat().st_size,
        }
    return genomes
