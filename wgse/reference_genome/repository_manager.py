import logging
from collections import OrderedDict

from wgse.alignment_map.alignment_map_header import AlignmentMapHeader
from wgse.configuration import RepositoryConfig
from wgse.data.genome import Genome
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
        mtdna: MtDNA = MtDNA(),
        config: RepositoryConfig = RepositoryConfig(),
    ) -> None:
        self._loader = loader
        self._downloader = downloader
        self._mtdna = mtdna
        self.genomes = self._loader.load()
        # Index individual sequences by their MD5 and length
        self._sequences_by_md5: dict[str, list[Sequence]] = self._group_sequences(
            lambda s: s.md5, self.genomes
        )
        self._sequences_by_length: dict[int, list[Sequence]] = self._group_sequences(
            lambda s: s.length, self.genomes
        )
        self._config = config

    def analyze_references(self):
        # Analyzing sequence by sequence
        different_md5_same_length = []
        for ln, seqs in self._sequences_by_length.items():
            unique_seq = set()
            name = None
            for seq in seqs:
                unique_seq.add(seq.md5)
                name = seq.name
            # Filtering by an arbitrary value so that what's left are mostly
            # normal chromosomes sequences.
            if (len(unique_seq) > 1) and ln > 57227414:
                different_md5_same_length.append(ln)
                logging.debug(
                    f"There are {len(unique_seq)} different MD5 for length {ln} ({name})."
                )

        # Analyzing the whole genome, looking for identical length sequences
        # with different MD5 sequences
        different_md5s_same_lengths = {}
        for genome in self.genomes:
            if genome.sequences is None:
                continue
            seq_lengths = ",".join([str(x.length) for x in genome.sequences])
            seq_md5 = ",".join([x.md5 for x in genome.sequences])
            if seq_lengths not in different_md5s_same_lengths:
                different_md5s_same_lengths[seq_lengths] = []
            if seq_md5 not in different_md5s_same_lengths[seq_lengths]:
                different_md5s_same_lengths[seq_lengths].append(seq_md5)

        ambiguous = len(
            [x for x, y in different_md5s_same_lengths.items() if len(y) > 1]
        )
        logging.debug(f"Found {ambiguous} ambiguous genomes.")
        for different_md5_same_length, md5s in different_md5s_same_lengths.items():
            if len(md5s) > 1:
                logging.debug("")

    def find(self, sequences: list[Sequence]):
        md5_available = all([x.md5 is not None for x in sequences])
        matching = OrderedDict([(x, []) for x in sequences])
        if md5_available:
            for sequence in sequences:
                if sequence.md5 in self._sequences_by_md5:
                    matching[sequence] = self._sequences_by_md5[sequence.md5]
        else:
            for sequence in sequences:
                if sequence.length in self._sequences_by_length:
                    matching[sequence] = self._sequences_by_length[sequence.length]
        return Reference(matching)

    def _group_sequences(self, criteria, genomes: list[Genome]):
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

    def _create_companion_files(self, genome: Genome, force=False):
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

    def self_test(self):
        for index, reference in enumerate(self.genomes):
            if reference.sequences is None:
                try:
                    logging.info(f"Processing {reference} as it has no sequences.")
                    genome = self.ingest(
                        reference.fasta_url, reference.source, reference.build
                    )
                    self.genomes[index] = genome
                    self._loader.save(self.genomes)
                except Exception as e:
                    logging.critical(e)

    def ingest(
        self, url: str = None, source: str = None, build: str = None, force=False
    ):
        genome = Genome(
            url, source=source, build=build, parent_folder=self._config.genomes
        )
        downloader = Downloader()
        decompressor = Decompressor()
        compressor = BGZIPCompressor()

        if genome.fasta.exists() and not force:
            logging.info(f"File {genome.fasta.name} already exist. Re-using it.")
            self._create_companion_files(genome, force)
            genome.sequences = self._get_sequences(genome)
            return genome
        elif genome.fasta.exists() and force:
            genome.fasta.unlink()
            genome.bgzip_md5 = None
            genome.downloaded_md5 = None
            genome.decompressed_md5 = None
            genome.bgzip_size = None
            genome.download_size = None
            genome.decompressed_size = None

        logging.info(f"Ingesting {genome}.")
        logging.info(f"1/4: Downloading fasta from: {genome.fasta_url}.")
        download_output = downloader.perform(genome)
        logging.info(f"2/4: Decompressing: {download_output.name}.")
        decompressor_output = decompressor.perform(genome, download_output)
        logging.info(f"3/4: Compressing to gzip: {decompressor_output.name}.")
        compressor_output = compressor.perform(genome, decompressor_output)
        logging.info(f"4/4: Extracting sequence data: {compressor_output.name}.")
        self._create_companion_files(genome)
        genome.sequences = self._get_sequences(genome)
        return genome