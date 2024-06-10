from helix.data.tabular_data import TabularData, TabularDataRow
from helix.reference.reference import Reference


class ReferenceAdapter:
    def adapt(stats: Reference):
        ref_map = {}
        if len(stats.matching) > 0:
            # If We've at least a perfect match,
            # build a table with it
            for match in stats.matching:
                for key, value in stats.reference_map.items():
                    for sequence in value:
                        if sequence.parent == match:
                            if key not in ref_map:
                                ref_map[key] = []
                            ref_map[key].append(sequence)
        else:
            # Otherwise, consider every reference that
            # matches at least by one sequence
            ref_map = stats.reference_map
        parents = set(x.parent for y in ref_map.values() for x in y)
        max_columns = len(parents)
        genome_index_map = {}
        headers = ["Loaded file"]
        max_index = 0
        rows = []
        for key, value in ref_map.items():
            row = [None] * (max_columns + 1)
            row[0] = key
            for sequence in value:
                if sequence.parent not in genome_index_map:
                    genome_index_map[sequence.parent] = max_index
                    headers.append(str(sequence.parent))
                    max_index += 1
                row[genome_index_map[sequence.parent] + 1] = sequence
            rows.append([str(x) for x in row])
        return TabularData(headers, [TabularDataRow(None, x) for x in rows])
