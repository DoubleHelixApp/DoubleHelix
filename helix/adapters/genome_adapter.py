from helix.data.genome import Genome
from helix.data.tabular_data import TabularData, TabularDataRow
from helix.utility.unit_prefix import UnitPrefix


class GenomeAdapter:
    def adapt(genome: Genome):
        column = {
            "FASTA URL": genome.fasta_url,
            "FAI URL": genome.fai_url,
            "GZI URL": genome.gzi_url,
            "Suffix": genome.suffix,
            "Build": genome.build,
            "Source": genome.source,
            "Sequences": (
                "Available" if genome.sequences is not None else "Not available"
            ),
            "Description": genome.description,
            "Size": UnitPrefix.convert_bytes(genome.download_size),
            "Decompressed Size": UnitPrefix.convert_bytes(genome.decompressed_size),
            "BGZip Size": UnitPrefix.convert_bytes(genome.bgzip_size),
            "MD5": genome.downloaded_md5,
            "Decompressed MD5": genome.decompressed_md5,
            "BGZip MD5": genome.bgzip_md5,
            "MtDNA Model": genome.mitochondrial_model,
            "Parent Folder": genome.parent_folder,
        }
        return TabularData(
            None, [TabularDataRow(x, [str(y)]) for x, y in column.items()]
        )
