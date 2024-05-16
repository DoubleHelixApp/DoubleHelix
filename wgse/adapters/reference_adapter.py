from wgse.alignment_map.index_stats_calculator import SequenceStatistics
from wgse.data.sequence_type import SequenceType
from wgse.data.tabular_data import TabularData, TabularDataRow
from wgse.fasta.reference import Reference


class ReferenceAdapter:
    def adapt(stats: Reference):
        # We've at least a match, build a table with it
        ref_map = {}
        if len(stats.matching) > 0:
            for match in stats.matching:
                for key, value in stats.reference_map.items():
                    for sequence in value:
                        if sequence.parent == match:
                            if key not in ref_map:
                                ref_map[key] = []
                            ref_map[key].append(sequence)
        else:
            ref_map = stats.reference_map
        max_columns = max([len(x) for x in ref_map.values()])
        genome_index_map = {}
        headers = ["Loaded file"]
        max_index = 0
        rows = []
        for key, value in ref_map.items():
            row = [None for x in range(max_columns+1)]
            row[0] = key
            for sequence in value:
                if sequence.parent not in genome_index_map:
                    genome_index_map[sequence.parent] = max_index
                    headers.append(str(sequence.parent))
                    max_index += 1
                row[genome_index_map[sequence.parent]+1] = sequence
            rows.append([str(x) for x in row])
        return TabularData(headers, [TabularDataRow(None, x) for x in rows])