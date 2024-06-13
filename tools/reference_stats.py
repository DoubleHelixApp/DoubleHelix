import argparse
import logging
import time
from pathlib import Path

from helix.data.genome import Genome
from helix.fasta.fasta_letter_counter import FASTALetterCounter
from helix.fasta.fasta_stats_files import FASTAStatsFiles
from helix.utility.samtools import Samtools

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument(
        "--reference",
        help="Indicate the path of the bgzip compressed reference genome",
        type=Path,
        default=Path("reference\\genomes\\_hs37d5.fa\\seq1.fa.gz"),
    )
    parser.add_argument(
        "--reference-dict",
        help="Indicate the path of dictionary for the reference genome",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--long-run-threshold",
        help="Indicate the threshold for long runs to be considered when making .buc files.",
        type=int,
        default=300,
    )
    parser.add_argument(
        "--buckets-number",
        help="Indicate the total number of buckets to be considered when making .buc files.",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--external",
        help=(
            "Indicate the root directory for 3rd parties executables "
            "(only needed to generate the .dict file if not already available)."
        ),
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--verbose",
        help="Set logging level",
        choices=["INFO", "DEBUG", "WARNING", "ERROR"],
        type=str,
        default="INFO",
    )
    args = parser.parse_args()

    logging.getLogger().setLevel(logging.__dict__[args.verbose])

    start = time.time()
    genome = Genome(args.reference)

    if not genome.dict.exists():
        samtools = Samtools()
        samtools.make_dictionary(args.reference, genome.dict)

    fasta_file = FASTALetterCounter(genome)
    unknown_bases_stats = FASTAStatsFiles(
        fasta_file,
        args.long_run_threshold,
        args.buckets_number,
    )
    unknown_bases_stats.generate_stats()
    end = time.time()
    logging.info(f"Time {end-start}s")
