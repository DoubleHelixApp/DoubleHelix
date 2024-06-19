import logging
from collections import OrderedDict
from typing import Callable

from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.configuration import RepositoryConfig
from helix.data.genome import Genome
from helix.data.sequence import Sequence
from helix.reference.reference import Reference
from helix.files.bgzip import BGzip, BgzipAction
from helix.files.decompressor import Decompressor
from helix.files.downloader import Downloader
from helix.reference.genome_metadata_loader import MetadataLoader
from helix.mtDNA.mt_dna import MtDNA
from helix.utility.samtools import Samtools


class Repository:
    """
    Manages the reference genomes and their metadata.

    Examples:
        >>> repository = Repository()
        >>> reference = repository.find(file.file_info.sequences)
    """

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

    def analyze_references(self) -> None:
        # Analyzing sequence by sequence
        different_md5_same_length = []
        for length, seqs in self._sequences_by_length.items():
            unique_seq_set = set()
            name = None
            for seq in seqs:
                unique_seq_set.add(seq.md5)
                name = seq.name
            if len(unique_seq_set) > 1 and length > 57227414:
                different_md5_same_length.append(length)
                logging.debug(
                    f"There are {len(unique_seq_set)} different MD5 for length {length} ({name})."
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
        for length, md5s in different_md5s_same_lengths.items():
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

    def _create_companion_files(
        self, genome: Genome, force=False, progress=None, action: str = None
    ):
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

    def acquire(
        self, genome: Genome, progress: Callable[[str, int], None] = None, force=False
    ) -> Genome:
        """
        Download and convert to BGZip format (if necessary) a reference genome. Create
        additionals files that are needed by DoubleHelix.

        Args:
            genome (Genome): Genome to acquire
            progress (Callable[[str, int], None]): Callback function that takes two
                arguments: a string indicating the progress message and an integer
                indicating the progress percentage.
            force (bool): Determines whether to overwrite existing files.

        Returns:
            Genome: The reference genome.
        """
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

        logging.info(f"Start Downloading from: {genome.fasta_url}.")
        download_output = downloader.perform(
            genome, progress, f"[1/4] Downloading from: {genome.fasta_url}"
        )
        logging.info(f"Start Decompressing: {download_output.name}.")
        decompressor_output = decompressor.perform(
            genome,
            progress,
            download_output,
            f"[2/4] Decompressing: {download_output.name}",
        )
        logging.info(f"Start compressing to BGZip: {decompressor_output.name}.")
        compressor_output = compressor.perform(
            genome,
            progress,
            decompressor_output,
            f"[3/4] Compressing to BGZip: {decompressor_output.name}",
        )
        logging.info(f"Creating companion files: {compressor_output.name}.")
        self._create_companion_files(
            genome,
            force,
            progress,
            f"[4/4] Creating companion files: {compressor_output.name}",
        )
        return genome

    def ingest(self, url, source, build, force=False):
        """Add a genome to the repository.

        Build a new Genome object with the input parameters and call acquire() on it

        Args:
            url (str): Url for the FASTA file.
            source (str): Source of the Genome (i.e., "Ensembl")
            build (str): Build of the Genome (i.e., "38").
            force (bool, optional): True to force the ingestion even if the files exist.
                Defaults to False.

        Returns:
            Genome: Genome after ingestion

        Examples:
            >>> manager = RepositoryManager()
            >>> manager.genomes.append(
            >>>     manager.ingest(
            >>>         "https://source/reference.fa",
            >>>         "NIH", # Should match an entry in sources.json
            >>>         "38",  # Only 38 or 37
            >>>     )
            >>> )
            >>> GenomeMetadataLoader().save(manager.genomes)
        """
        genome = Genome(url, source=source, build=build)
        genome.parent_folder = self._config.genomes
        logging.info(f"Ingesting {genome}.")
        genome = self.acquire(genome, force)
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
