import subprocess
from math import sqrt

from wgse.alignment_map.alignment_map_row import (AlignmentMapFlag,
                                                  AlignmentMapRow)
from wgse.configuration import MANAGER_CFG
from wgse.data.file_type import FileType
from wgse.data.alignment_map_file_info import AlignmentMapFileInfo
from wgse.data.alignment_stats import AlignmentStats
from wgse.data.read_type import ReadType
from wgse.utility.external import External
from wgse.utility.sequencers import Sequencers


class AlignmentStatsCalculator:
    def __init__(
        self,
        path: AlignmentMapFileInfo,
        config = MANAGER_CFG.ALIGNMENT_STATS,
        external: External = External(),
        sequencers: Sequencers = Sequencers(),
    ) -> None:
        self.aligned_file = path
        self._config = config
        self._external = external
        self._sequencers = sequencers

    def get_stats(self):
        samples = self._read_samples(self._config.skip, self._config.samples)
        stats = self._process_samples(samples)
        # TODO: handle long reads
        return stats

    def _read_samples(self, skip, samples_count):
        options = []
        if self.aligned_file.file_type == FileType.CRAM:
            ready_reference = self.aligned_file.reference_genome.ready_reference
            if  ready_reference is None:
                raise RuntimeError("Unable to compute stats because there is no reference available for a CRAM file")
            options.extend(["-T", ready_reference.fasta])
        options.append(self.aligned_file.path)

        process: subprocess.Popen = self._external.samtools(
            ["view", *options], stdout=subprocess.PIPE
        )
        samples = []
        for line in iter(process.stdout.readline, b""):
            if len(samples) == (skip + samples_count):
                break
            samples.append(AlignmentMapRow(line.decode()))
        process.kill()
        # Take the last self.samples if they're enough.
        # Otherwise just take them all.
        start_index = -min(len(samples), samples_count)
        end_index = min(len(samples), skip + samples_count)
        samples = samples[start_index:end_index]
        return samples

    def _process_samples(self, samples: list[AlignmentMapRow]) -> AlignmentStats:
        duplicate_count = 0
        ignored_rows = [
            AlignmentMapFlag.SECONDARY_ALIGNMENT,
            AlignmentMapFlag.NOT_PASSING,
            AlignmentMapFlag.DUPLICATE,
            AlignmentMapFlag.SUPPLEMENTARY_ALIGNMENT,
        ]
        read_type_count = 0
        considered_samples = 0

        if len(samples) == 0:
            raise RuntimeError("Cannot compute stats as the file is empty")

        # Process the template name for 1st sample to determine the sequencer
        # as it should not give a different result on the other samples.
        sequencer = self._sequencers.determine_sequencer(samples[0].query_template_name)

        # Used to compute stats for read length
        count_length = 0
        average_length = 0
        squared_deviation_length = 0

        # Used to compute stats for insert size
        count_insert_size = 0
        average_insert_size = 0
        squared_deviation_insert_size = 0

        # Used to compute stats for alignment quality
        count_quality = 0
        average_quality = 0
        squared_deviation_quality = 0

        for sample in samples:
            if sample.flag & AlignmentMapFlag.DUPLICATE:
                duplicate_count += 1
            if any(sample.flag & x for x in ignored_rows):
                continue

            if sample.flag & AlignmentMapFlag.MULTIPLE_SEGMENTS:
                read_type_count += 1
            else:
                read_type_count += -1

            considered_samples += 1

            # Compute stats for read length
            read_length = len(sample.sequence)
            # The sequence can be '*' sometimes. Ignore in that case.
            # Ref.: Page 9 of the standard.
            if read_length > 1:
                count_length += 1
                delta_length = read_length - average_length
                average_length += delta_length / count_length
                new_delta_length = read_length - average_length
                squared_deviation_length += delta_length * new_delta_length

            # Compute stats for insertion size
            if sample.mate_sequence_name == "=":
                abs_template_length = abs(sample.template_length)
                if abs_template_length < 50000:
                    count_insert_size += 1
                    delta_insert_size = abs_template_length - average_insert_size
                    average_insert_size += delta_insert_size / count_insert_size
                    new_delta_insert_size = abs_template_length - average_insert_size
                    squared_deviation_insert_size += (
                        delta_insert_size * new_delta_insert_size
                    )

            # Compute stats for alignment quality
            count_quality += 1
            delta_quality = sample.mapping_quality - average_quality
            average_quality += delta_quality / count_quality
            new_delta_quality = sample.mapping_quality - average_quality
            squared_deviation_quality += delta_quality * new_delta_quality

        # Establish the read type based on the majority of samples
        majority = considered_samples * 0.5
        read_type = ReadType.Unknown
        if read_type_count > majority:
            read_type = ReadType.Paired
        elif read_type_count < -majority:
            read_type = ReadType.Single

        if count_length <= 2:
            raise RuntimeError(
                "Unable to compute read length stats as the number of valid samples is less than 2."
            )
        if count_insert_size <= 2 and read_type == ReadType.Paired:
            raise RuntimeError(
                "Unable to compute insert size stats as the number of valid samples is less than 2."
            )
        if count_quality <= 2:
            raise RuntimeError(
                "Unable to compute alignment quality stats as the number of valid samples is less than 2."
            )
        if read_type == ReadType.Unknown:
            raise RuntimeError(
                "Unable to determine read type as there's a similar number of single vs paired reads."
            )

        stats = AlignmentStats()
        stats.samples_count = self._config.samples
        stats.skipped_samples = self._config.skip
        stats.read_type = read_type
        stats.duplicate = duplicate_count
        stats.sequencer = sequencer

        stats.count_length = count_length
        stats.count_insert_size = count_insert_size
        stats.count_quality = count_quality

        stats.average_length = average_length
        stats.average_quality = average_quality
        stats.average_insert_size = average_insert_size

        stats.standard_dev_length = sqrt(squared_deviation_length / (count_length - 1))
        stats.standard_dev_insert_size = sqrt(
            squared_deviation_insert_size / (count_insert_size - 1)
        )
        stats.standard_dev_quality = sqrt(
            squared_deviation_quality / (count_quality - 1)
        )
        return stats
