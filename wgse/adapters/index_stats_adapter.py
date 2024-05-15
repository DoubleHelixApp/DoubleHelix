from wgse.alignment_map.index_stats_calculator import SequenceStatistics
from wgse.data.sequence_type import SequenceType
from wgse.data.tabular_data import TabularData, TabularDataRow


class IndexStatsAdapter:
    def adapt(stats: list[SequenceStatistics]):
        header = [
            "Chromosome",
            "Type",
            "Reference length",
            "Mapped length",
            "Unmapped length",
        ]
        grouped_stats = []
        grouped_others = TabularDataRow(
            "Others",
            [
                "Others",
                sum(
                    x.reference_length for x in stats if x.type == SequenceType.Other
                ),
                sum(x.mapped for x in stats if x.type == SequenceType.Other),
                sum(x.unmapped for x in stats if x.type == SequenceType.Other),
            ],
        )

        percentage_mapped = ""
        percentage_unmapped = ""
        if grouped_others.columns[1] != 0:
            percentage_mapped = (
                f" ({(grouped_others.columns[2]/grouped_others.columns[1])*100:.1f}%)"
            )
            percentage_unmapped = (
                f" ({(grouped_others.columns[3]/grouped_others.columns[1])*100:.1f}%)"
            )

        grouped_others.columns[2] = f"{grouped_others.columns[2]}{percentage_mapped}"
        grouped_others.columns[3] = f"{grouped_others.columns[3]}{percentage_unmapped}"
        grouped_others.columns[1] = str(grouped_others.columns[1])

        for stat in stats:
            if stat.type == SequenceType.Other:
                continue

            percentage_unmapped = ""
            percentage_mapped = ""
            if stat.reference_length != 0:
                percentage_unmapped = (
                    f" ({(stat.unmapped/stat.reference_length)*100:.1f}%)"
                )
                percentage_mapped = f" ({(stat.mapped/stat.reference_length)*100:.1f}%)"

            grouped_stats.append(
                TabularDataRow(
                    stat.name,
                    [
                        stat.type.name,
                        str(stat.reference_length),
                        f"{stat.mapped}{percentage_mapped}",
                        f"{stat.unmapped}{percentage_unmapped}",
                    ],
                )
            )
        grouped_stats.append(grouped_others)

        return TabularData(header, grouped_stats)