import enum
from wgse.data.alignment_stats import AlignmentStats
from wgse.data.tabular_data import TabularData, TabularDataRow


class AlignmentStatsAdapter:
    def adapt(input_data: AlignmentStats):
        name_map = {
            "skipped_samples": "Skipped samples",
            "samples_count": "Samples count",
            "sequencer": "Sequencer",
            "duplicate": "Duplicates",
            "count_length": "Count length",
            "average_length": "Average length",
            "standard_dev_length": "Standard deviation length",
            "count_insert_size": "Count insert size",
            "average_insert_size": "Average insert size",
            "standard_dev_insert_size": "Standard deviation insert size",
            "count_quality": "Count quality",
            "average_quality": "Average quality",
            "standard_dev_quality": "Standard deviation quality",
            "read_type": "Read type",
        }

        rows = []
        for key, value in name_map.items():
            data = input_data.__dict__[key]
            if isinstance(data, enum.Enum):
                data = str(data.name)
            rows.append(TabularDataRow(value, [str(data)]))
        return TabularData(None, rows)