from PySide6.QtCore import Qt

from wgse.alignment_map.index_stats_calculator import SequenceStatistics
from wgse.data.alignment_stats import AlignmentStats
from wgse.data.sequence_type import SequenceType
from wgse.gui.table_dialog import TableDialog


class IndexStatisticsDialog(TableDialog):
    def __init__(self, parent=None) -> None:
         super().__init__("Index Statistics", parent, horizontal=True)

    def exec(self, stats : list[SequenceStatistics]):            
        header = [
            "Chromosome",
            "Type",
            "Reference length",
            "Mapped length",
            "Unmapped length",
        ]
        grouped_stats = []
        others = [
            "Others",
            "Others",
            sum(x.reference_length for x in stats if x.type == SequenceType.Other),
            sum(x.mapped for x in stats if x.type == SequenceType.Other),
            sum(x.unmapped for x in stats if x.type == SequenceType.Other),
        ]
        
        percentage_mapped = ""
        percentage_unmapped = ""
        if others[2] != 0:
            percentage_mapped = f" ({(others[3]/others[2])*100:.1f}%)"
            percentage_unmapped = f" ({(others[4]/others[2])*100:.1f}%)"
        
        others[3] = f"{others[3]}{percentage_mapped}"
        others[4] = f"{others[4]}{percentage_unmapped}"
        others[2] = str(others[2])

        for stat in stats:
            if stat.type == SequenceType.Other:
                continue
            
            percentage_unmapped = ""
            percentage_mapped = ""
            if stat.reference_length != 0:
                percentage_unmapped = f" ({(stat.unmapped/stat.reference_length)*100:.1f}%)"
                percentage_mapped = f" ({(stat.mapped/stat.reference_length)*100:.1f}%)"
                
            grouped_stats.append(
                [
                    stat.name,
                    stat.type.name,
                    str(stat.reference_length),
                    f"{stat.mapped}{percentage_mapped}",
                    f"{stat.unmapped}{percentage_unmapped}"
                ]
            )
        grouped_stats.append(others)
        
        self.set_data(header, grouped_stats)
        super().exec()

    def exec_(self, stats : list[SequenceStatistics]):            
        header = [
            "Chromosome Type",
            "Reference length",
            "Mapped length",
            "Unmapped length",
        ]
        types = set(x.type for x in stats)
        grouped_stats = []
        for type in types:
            grouped_stats.append(
                [
                    type.name,
                    str(sum(x.reference_length for x in stats if x.type == type)),
                    str(sum(x.mapped for x in stats if x.type == type)),
                    str(sum(x.unmapped for x in stats if x.type == type))
                ]
            )
            pass
        
        self.set_data(header, grouped_stats)
        super().exec()