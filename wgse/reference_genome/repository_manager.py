import logging
from collections import OrderedDict

from wgse.alignment_map.alignment_map_header import AlignmentMapHeader
from wgse.data.reference import Genome
from wgse.data.sequence import Sequence
from wgse.utility.external import BgzipAction, External
from wgse.fasta.reference import Reference
from wgse.reference_genome.bgzip_compressor import BGZIPCompressor
from wgse.reference_genome.decompressor import Decompressor
from wgse.reference_genome.downloader import Downloader
from wgse.reference_genome.genome_metadata_loader import GenomeMetadataLoader
from wgse.utility.mt_dna import MtDNA
from wgse.utility.sequence_orderer import SequenceOrderer


class RepositoryManager:
    def __init__(
        self,
        loader: GenomeMetadataLoader = GenomeMetadataLoader(),
        downloader: Downloader = Downloader(),
        mtdna : MtDNA = MtDNA()
    ) -> None:
        self._loader = loader
        self._downloader = downloader
        self._mtdna = mtdna
        self._genomes = self._loader.load()
        # Index individual sequences by their MD5 and length
        self._sequences_by_md5: dict[str, list[Sequence]] = self._group_sequences(
            lambda s: s.md5, self._genomes
        )
        self._sequences_by_length: dict[int, list[Sequence]] = self._group_sequences(
            lambda s: s.length, self._genomes
        )

    def find(self, sequences: list[Sequence]):
        md5_available = all([x.md5 is not None for x in sequences])
        matching = OrderedDict([(x,[]) for x in sequences])
        if md5_available:
            for sequence in sequences:
                if sequence.md5 in self._sequences_by_md5:
                    matching[sequence] = self._sequences_by_md5[sequence.md5]
        else:
            for sequence in sequences:
                if sequence.length in self._sequences_by_length:
                    matching[sequence] = self._sequences_by_length[sequence.length]
        return Reference(matching)

    def _group_sequences(self, criteria, genomes : list[Genome]):
        grouped = {}
        for genome in genomes:
            if genome.sequences is None:
                continue
            for sequence in genome.sequences:
                evaluated_criteria = criteria(sequence)
                if evaluated_criteria not in grouped:
                    grouped[evaluated_criteria] = []
                grouped[evaluated_criteria].append(sequence)
        return grouped

    def _sequences_md5(self, sequences: list[Sequence]):
        if sequences is None:
            return None
        names = [x.name for x in sequences]
        return ",".join(
            [
                sequences[x[0]].md5
                for x in SequenceOrderer(names)
                if sequences[x[0]].md5 is not None
            ]
        )

    def _sequences_length(self, sequences: list[Sequence]):
        if sequences is None:
            return None
        names = [x.name for x in sequences]
        return ",".join(
            [
                str(sequences[x[0]].length)
                for x in SequenceOrderer(names)
                if sequences[x[0]].length is not None
            ]
        )

    def _get_sizes(self, genome: Genome):
        if genome.fai_url is None:
            fai_url = genome.fasta_url + ".fai"
            fai_size = self._downloader.get_file_size(fai_url)
            if fai_size != None:
                genome.fai_url = fai_url

        if genome.gzi_url is None:
            gzi_url = genome.fasta_url + ".gzi"
            gzi_size = self._downloader.get_file_size(gzi_url)
            if gzi_size != None:
                genome.gzi_url = gzi_url

        if genome.download_size is None:
            size = self._downloader.get_file_size(genome.fasta_url)
            if size != None:
                genome.download_size = size
            else:
                raise RuntimeError(
                    f"Unable to get the size of the fasta file for {genome.fasta_url}"
                )

    def _get_sequences(self, genome: Genome):
        dictionary: AlignmentMapHeader = AlignmentMapHeader.load_from_file(genome.dict)
        sequences = []
        for name, entry in dictionary.sequences.items():
            sequence = Sequence(name, entry.length, entry.md5)
            sequences.append(sequence)
        return sequences

    def _create_companion_files(self, genome: Genome):
        _external = External()
        logging.info(f"{genome}: Starting post-download tasks.")
        if not genome.gzi.exists():
            logging.info(f"{genome}: Generating bgzip index.")
            _external.bgzip_wrapper(genome.fasta, genome.gzi, BgzipAction.Reindex)
        else:
            logging.info(f"{genome}: bgzip index exists.")

        if not genome.dict.exists():
            logging.info(f"{genome}: Generating dictionary file.")
            _external.make_dictionary(genome.fasta, genome.dict)
        else:
            logging.info(f"{genome}: Dictionary file exists.")

    def ingest(self, url: str = None, source: str = None, build: str = None):
        genome = Genome(url, source=source, build=build)
        downloader = Downloader()
        decompressor = Decompressor()
        compressor = BGZIPCompressor()

        logging.info(f"Ingesting {genome}.")
        logging.info(f"1/4: Downloading fasta from: {genome.fasta_url}.")
        output = downloader.perform(genome)
        logging.info(f"2/4: Decompressing: {output.name}.")
        output = decompressor.perform(genome, output)
        logging.info(f"3/4: Compressing to gzip: {output.name}.")
        output = compressor.perform(genome, output)
        logging.info(f"4/4: Extracting sequence data: {output.name}.")
        genome.sequences = self._get_sequences(genome)
        return genome
