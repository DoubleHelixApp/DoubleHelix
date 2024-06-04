import datetime

from jinja2 import Environment, FileSystemLoader

from helix.adapters.alignment_map_file_info_adapter import AlignmentMapFileInfoAdapter
from helix.adapters.alignment_stats_adapter import AlignmentStatsAdapter
from helix.adapters.header_adapter import HeaderAdapter
from helix.adapters.index_stats_adapter import IndexStatsAdapter
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.configuration import MANAGER_CFG
from helix.data.tabular_data import TabularData
from helix.VERSION import version


class HTMLAlignedFileReport:
    def __init__(self, config=MANAGER_CFG.REPOSITORY) -> None:
        self._templates_folder = config.metadata.joinpath("report_templates")

    def from_aligned_file(file=AlignmentMapFile):
        file_info_adapted = AlignmentMapFileInfoAdapter.adapt(file.file_info)
        index_stat_adapted = IndexStatsAdapter.adapt(file.file_info.index_stats)
        alignment_stats_adapted = AlignmentStatsAdapter.adapt(
            file.file_info.alignment_stats
        )
        header_adapted = HeaderAdapter.adapt(file.header)

        html_report = HTMLAlignedFileReport()
        return html_report.make(
            file_info_adapted,
            index_stat_adapted,
            alignment_stats_adapted,
            header_adapted.sequences,
            header_adapted.read_groups,
            header_adapted.programs,
            header_adapted.comments,
        )

    def make(
        self,
        file_info_data: TabularData,
        index_stat_data: TabularData,
        alignment_stats_data: TabularData,
        sequences_data: TabularData,
        read_groups_data: TabularData,
        programs_data: TabularData,
        comments_data: TabularData,
    ):
        file_loader = FileSystemLoader(self._templates_folder)
        env = Environment(loader=file_loader)
        template = env.get_template("table_tab.html")
        return template.render(
            file_info_data=file_info_data,
            index_stat_data=index_stat_data,
            alignment_stats_data=alignment_stats_data,
            sequences_data=sequences_data,
            read_groups_data=read_groups_data,
            programs_data=programs_data,
            comments_data=comments_data,
            general={"now": datetime.datetime.now(), "version": version},
        )
