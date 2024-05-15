from wgse.alignment_map.alignment_map_header import AlignmentMapHeader
from wgse.gui.table_dialog import ListTableDialog


class HeaderDialog(ListTableDialog):
    def __init__(self, parent) -> None:
        super().__init__("Header", parent, horizontal=True)

    def exec(self, header : AlignmentMapHeader):
        data = {
            "Sequences": (
                ["Name", "Length", "MD5"],
                [
                    (x.name, str(x.length), x.md5)
                    for x in header.sequences.values()
                ],
            ),
            "Programs": (
                ["ID", "Description", "Command line", "Previous", "Program version"],
                [
                    [
                        x.id,
                        x.name,
                        x.description,
                        x.command_line,
                        x.previous,
                        x.program_version,
                    ]
                    for x in header.programs
                ],
            ),
            "Read groups": (
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
                    ]
                    for x in header.read_groups
                ],
            ),
            "Comments" : (["Text"], [[x for x in header.comments]])
        }
        self.set_data(data)
        super().exec()