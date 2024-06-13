from collections import OrderedDict
from helix.data.alignment_map.alignment_map_file_info import AlignmentMapFileInfo
from helix.data.tabular_data import TabularData, TabularDataRow
from helix.reference.reference import ReferenceStatus
from helix.utility.unit_prefix import UnitPrefix


class AlignmentMapFileInfoAdapter:
    def adapt(stats: AlignmentMapFileInfo) -> TabularData:
        label_map = OrderedDict(
            [
                ("sorted", "Sorted"),
                ("indexed", "Indexed"),
                ("file_type", "File type"),
                ("content", "Content"),
                ("gender", "Gender"),
            ]
        )

        data = OrderedDict()
        data["Directory"] = [str(stats.path.parent)]
        data["Filename"] = [stats.path.name]
        data["Size"] = [UnitPrefix.convert_bytes(stats.path.stat().st_size)]
        data["File type"] = [stats.file_type.name]
        if stats.reference_genome.status == ReferenceStatus.Available:
            data["Reference"] = [
                f"Based on GRCh{stats.reference_genome.build}, available"
            ]
        elif stats.reference_genome.status == ReferenceStatus.Buildable:
            data["Reference"] = [
                f"Likely based on GRCh{stats.reference_genome.build}, buildable"
            ]
        elif stats.reference_genome.status == ReferenceStatus.Downloadable:
            data["Reference"] = [
                f"Based on GRCh{stats.reference_genome.build}, downloadable"
            ]
        elif stats.reference_genome.status == ReferenceStatus.Unknown:
            data["Reference"] = [
                f"Likely based on GRCh{stats.reference_genome.build}. unknown"
            ]
        data["Gender"] = [stats.gender.name]
        data["Sorted"] = [stats.sorted.name]
        data["Mitochondrial DNA Model"] = [stats.mitochondrial_dna_model.name]

        for key, value in label_map.items():
            if value == "Path":
                continue
            if value not in data or data[value] is None:
                data[value] = [str(stats.__dict__[key])]
        data = TabularData(None, [TabularDataRow(x[0], x[1]) for x in data.items()])
        return data
