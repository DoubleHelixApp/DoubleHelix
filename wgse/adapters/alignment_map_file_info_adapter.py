from wgse.data.alignment_map.alignment_map_file_info import AlignmentMapFileInfo
from wgse.data.tabular_data import TabularData, TabularDataRow


class AlignmentMapFileInfoAdapter:
    def adapt(stats: AlignmentMapFileInfo):
        label_map = {
            "path": "Path",
            "sorted": "Sorted",
            "indexed": "Indexed",
            "file_type": "File type",
            "reference_genome": "Reference genome",
            "content": "Content",
            "mitochondrial_dna_type": "Mitochondrial DNA type",
            "name_type_chromosomes": "Name type chromosomes",
            "name_type_mtdna": "Name type mtDNA",
            "sequence_count": "Sequence count",
            "gender": "Gender",
        }
        size = stats.path.stat().st_size
        size /= 1024**3
        size = f"{size:.1f} GB"

        data = {x: None for x in label_map.values()}
        data["Sorted"] = [stats.sorted.name]
        data["Mitochondrial DNA type"] = [stats.mitochondrial_dna_model.name]
        data["Name type mtDNA"] = [stats.name_type_mtdna.name]
        data["Name type chromosomes"] = [stats.name_type_chromosomes.name]
        data["Gender"] = [stats.gender.name]
        data["File type"] = [stats.file_type.name]
        data["Path"] = [str(stats.path)]
        data["Size"] = [size]
        for key, value in label_map.items():
            if value not in data or data[value] is None:
                data[value] = [str(stats.__dict__[key])]
        data = TabularData(None, [TabularDataRow(x[0], x[1]) for x in data.items()])
        return data
