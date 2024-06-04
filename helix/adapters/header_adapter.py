from helix.alignment_map.alignment_map_header import AlignmentMapHeader
from helix.data.alignment_map.alignment_map_header_program import (
    AlignmentMapHeaderProgram,
)
from helix.data.alignment_map.alignment_map_header_read_group import (
    AlignmentMapHeaderReadGroup,
)
from helix.data.alignment_map.alignment_map_header_sequence import (
    AlignmentMapHeaderSequence,
)
from helix.data.tabular_data import TabularData, TabularDataRow


class HeaderSequenceAdapter:
    def adapt(input_data: list[AlignmentMapHeaderSequence]):
        return TabularData(
            [
                "Name",
                "Length",
                "MD5",
                "Alternate locus",
                "Alternative names",
                "Description",
                "Genome",
                "Molecule topology",
                "Species",
                "URI",
            ],
            [
                TabularDataRow(
                    None,
                    [
                        x.name,
                        str(x.length),
                        x.md5,
                        x.alternate_locus,
                        x.alternative_names,
                        x.description,
                        x.genome_assembly_identifier,
                        x.molecule_topology,
                        x.species,
                        x.uri,
                    ],
                )
                for x in input_data
            ],
        )


class HeaderProgramsAdapter:
    def adapt(input_data: list[AlignmentMapHeaderProgram]):
        return TabularData(
            ["ID", "Description", "Command line", "Previous", "Program version"],
            [
                TabularDataRow(
                    None,
                    [
                        x.id,
                        x.name,
                        x.description,
                        x.command_line,
                        x.previous,
                        x.program_version,
                    ],
                )
                for x in input_data
            ],
        )


class HeaderReadGroupAdapter:
    def adapt(input_data: list[AlignmentMapHeaderReadGroup]):
        return TabularData(
            [
                "ID",
                "Description",
                "Barcode",
                "Date",
                "Flow order",
                "Key sequence",
                "Library",
                "Platform",
                "Platform model",
                "Platform unit",
                "Predicted median insert size",
                "Sample",
                "Sequencing Center",
                "Programs",
            ],
            [
                TabularDataRow(
                    None,
                    [
                        x.id,
                        x.description,
                        x.barcode,
                        x.date,
                        x.flow_order,
                        x.key_sequence,
                        x.library,
                        x.platform,
                        x.platform_model,
                        x.platform_unit,
                        x.predicted_median_insert_size,
                        x.sample,
                        x.sequencing_center,
                        x.programs,
                    ],
                )
                for x in input_data
            ],
        )


class HeaderCommentsAdapter:
    def adapt(input_data: list[str]):
        return TabularData(["Text"], [TabularDataRow(None, [x for x in input_data])])


class AdaptedHeader:
    def __init__(self, sequences, read_groups, programs, comments) -> None:
        self.sequences: TabularData = sequences
        self.read_groups: TabularData = read_groups
        self.programs: TabularData = programs
        self.comments: TabularData = comments


class HeaderAdapter:
    def adapt(input_data: AlignmentMapHeader) -> AdaptedHeader:
        return AdaptedHeader(
            HeaderSequenceAdapter.adapt(input_data.sequences.values()),
            HeaderReadGroupAdapter.adapt(input_data.read_groups),
            HeaderProgramsAdapter.adapt(input_data.programs),
            HeaderCommentsAdapter.adapt(input_data.comments),
        )
