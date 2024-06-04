import logging
from collections import OrderedDict

from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.configuration import RepositoryConfig
from helix.data.genome import Genome
from helix.data.sequence import Sequence
from helix.fasta.reference import Reference
from helix.files.bgzip import BGzip, BgzipAction
from helix.files.decompressor import Decompressor
from helix.files.downloader import Downloader
from helix.reference.genome_metadata_loader import MetadataLoader
from helix.mtDNA.mt_dna import MtDNA
from helix.utility.samtools import Samtools


class Repository:
    def __init__(
        self,
        loader: MetadataLoader = MetadataLoader(),
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
            if seq_md5 not in [x[0] for x in different_md5s_same_lengths[seq_lengths]]:
                different_md5s_same_lengths[seq_lengths].append((seq_md5, genome))

        ambiguous = len(
            [x for x, y in different_md5s_same_lengths.items() if len(y) > 1]
        )
        logging.debug(f"Found {ambiguous} possible ambiguous sequences of lengths:")
        index = 0
        for different_md5_same_length, md5s in different_md5s_same_lengths.items():
            if len(md5s) > 1:
                for md5, genome in md5s:
                    logging.debug(f"{index+1}) {genome.fasta_url!s}")
                index += 1

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
            if fai_size is not None:
                genome.fai_url = fai_url

        if genome.gzi_url is None:
            gzi_url = genome.fasta_url + ".gzi"
            gzi_size = self._downloader.get_file_size(gzi_url)
            if gzi_size is not None:
                genome.gzi_url = gzi_url

        if genome.download_size is None:
            size = self._downloader.get_file_size(genome.fasta_url)
            if size is not None:
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
        samtools = Samtools()
        bgzip = BGzip()
        logging.info(f"{genome}: Starting post-download tasks.")
        if not genome.gzi.exists():
            logging.info(f"{genome}: Generating bgzip index.")
            bgzip.bgzip_wrapper(genome.fasta, genome.gzi, BgzipAction.Reindex)
        else:
            logging.info(f"{genome}: bgzip index exists.")

        if not genome.dict.exists():
            logging.info(f"{genome}: Generating dictionary file.")
            samtools.make_dictionary(genome.fasta, genome.dict)
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

    def download(self, genome: Genome, progress=None, force=False):
        downloader = Downloader()
        decompressor = Decompressor()
        compressor = BGzip()

        if genome.fasta.exists() and not force:
            logging.info(f"File {genome.fasta.name} already exist. Re-using it.")
            self._create_companion_files(genome, force)
            return genome
        elif genome.fasta.exists() and force:
            genome.fasta.unlink()
            genome.bgzip_md5 = None
            genome.downloaded_md5 = None
            genome.decompressed_md5 = None
            genome.bgzip_size = None
            genome.download_size = None
            genome.decompressed_size = None

        logging.info(f"1/4: Downloading fasta from: {genome.fasta_url}.")
        download_output = downloader.perform(genome, progress)
        logging.info(f"2/4: Decompressing: {download_output.name}.")
        decompressor_output = decompressor.perform(genome, download_output)
        logging.info(f"3/4: Compressing to gzip: {decompressor_output.name}.")
        compressor_output = compressor.perform(genome, decompressor_output)
        logging.info(f"4/4: Extracting sequence data: {compressor_output.name}.")
        self._create_companion_files(genome)
        return genome

    def ingest(
        self, url: str = None, source: str = None, build: str = None, force=False
    ):
        genome = Genome(
            url, source=source, build=build, parent_folder=self._config.genomes
        )
        logging.info(f"Ingesting {genome}.")
        genome = self.download(genome, force)
        genome.sequences = self._get_sequences(genome)
        return genome


if __name__ == "__main__":
    import tempfile
    import hashlib
    from os import close
    import pathlib

    genomes = MetadataLoader().load()
    decompressor = BGzip()
    for genome in genomes:
        if genome.decompressed_md5 is None:
            continue
        if genome.fasta.exists():
            temp = tempfile.mkstemp(suffix=None, prefix=None, dir=None, text=False)
            close(temp[0])
            temp_file = pathlib.Path(temp[1])
            temp_file.unlink()
            decompressor.bgzip_wrapper(genome.fasta, temp_file, BgzipAction.Decompress)
            md5_hash = hashlib.md5()
            with temp_file.open("rb") as f:
                while True:
                    chunk = f.read(4096 * 1000)
                    if not chunk:
                        break
                    md5_hash.update(chunk)
            genome.decompressed_md5 = md5_hash.hexdigest()
            temp_file.unlink()
    MetadataLoader().save(genomes)
    exit()

    genomes = MetadataLoader().load()
    genomes = [x for x in genomes if x.decompressed_md5 is not None]
    for genome in genomes:
        target = genome.fasta.with_name(genome.decompressed_md5)
        target = target.with_suffix("".join(genome.fasta.suffixes))
        target_dict = genome.dict.with_name(genome.decompressed_md5)
        target_dict = target_dict.with_suffix("".join(genome.dict.suffixes))
        target_gzi = genome.gzi.with_name(genome.decompressed_md5)
        target_gzi = target_gzi.with_suffix("".join(genome.gzi.suffixes))
        if not target.exists() and genome.fasta.exists():
            genome.fasta.rename(target)
        if not target_dict.exists() and genome.dict.exists():
            genome.dict.rename(target_dict)
        if not target_gzi.exists() and genome.gzi.exists():
            genome.gzi.rename(target_gzi)
