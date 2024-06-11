from helix.data.coverage_stats import CoverageStats, DepthBin
from helix.data.tabular_data import TabularData, TabularDataRow
from helix.utility.unit_prefix import UnitPrefix


class CoverageStatsAdapter:
    def adapt(input_data: list[CoverageStats]):
        rows = []
        for sequence_stats in input_data:
            row = [
                sequence_stats.sequence_name,
                str(UnitPrefix.convert(sequence_stats.bin_entries[DepthBin.Zero])),
                str(
                    UnitPrefix.convert(
                        sequence_stats.bin_entries[DepthBin.Between0And3]
                    )
                ),
                str(
                    UnitPrefix.convert(
                        sequence_stats.bin_entries[DepthBin.Between3And7]
                    )
                ),
                str(UnitPrefix.convert(sequence_stats.bin_entries[DepthBin.MoreThan7])),
                str(UnitPrefix.convert(sequence_stats.all_average)),
                str(UnitPrefix.convert(sequence_stats.non_zero_average)),
            ]
            rows.append(TabularDataRow(None, row))
        horizontal_header = [
            "Sequence Name",
            "# Reads: 0",
            "# Reads: 0-3",
            "# Reads: 3-7",
            "# Reads: >7",
            "Average",
            "Non-zero average",
        ]
        return TabularData(horizontal_header, rows)
