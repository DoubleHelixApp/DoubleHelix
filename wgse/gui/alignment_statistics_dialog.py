from PySide6.QtCore import Qt

from wgse.data.alignment_stats import AlignmentStats
from wgse.gui.table_dialog import TableDialog


class AlignmentStatisticsDialog(TableDialog):
    def __init__(self, parent=None) -> None:
         super().__init__("Alignment Statistics", parent)

    def exec(self, stats : AlignmentStats):
            header = [
                "Sequencer",
                "Duplicate",
                "Average length",
                "Standard deviation length",
                "Average insert size",
                "Standard deviation insert size",
                "Average alignment quality",
                "Standard deviation quality",
                "Read type",
            ]
            data = [
                [stats.sequencer],
                [str(stats.duplicate)],
                [f"{stats.average_length:.1f}"],
                [f"{stats.standard_dev_length:.1f}"],
                [f"{stats.average_insert_size:.1f}"],
                [f"{stats.standard_dev_insert_size:.1f}"],
                [f"{stats.average_quality:.1f}"],
                [f"{stats.standard_dev_quality:.1f}"],
                [stats.read_type.name],
            ]

            self.set_data(header, data)
            super().exec()