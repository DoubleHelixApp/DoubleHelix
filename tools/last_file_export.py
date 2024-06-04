import webbrowser

from helix.adapters.alignment_map_file_info_adapter import AlignmentMapFileInfoAdapter
from helix.adapters.alignment_stats_adapter import AlignmentStatsAdapter
from helix.adapters.header_adapter import HeaderAdapter
from helix.adapters.index_stats_adapter import IndexStatsAdapter
from helix.alignment_map.alignment_map_file import AlignmentMapFile
from helix.configuration import MANAGER_CFG
from helix.renderers.html_aligned_file_report import HTMLAlignedFileReport

if __name__ == "__main__":
    """This script will generate a report for
    the last file that was opened by Helix."""
    input = MANAGER_CFG.GENERAL.last_path
    if input is None:
        exit()
    if not input.exists():
        exit()
    if not input.is_file():
        exit()

    file = AlignmentMapFile(input)

    file_info_adapted = AlignmentMapFileInfoAdapter.adapt(file.file_info)
    index_stat_adapted = IndexStatsAdapter.adapt(file.file_info.index_stats)
    alignment_stats_adapted = AlignmentStatsAdapter.adapt(
        file.file_info.alignment_stats
    )
    header_adapted = HeaderAdapter.adapt(file.header)

    html_report = HTMLAlignedFileReport()
    html_page = html_report.make(
        file_info_adapted,
        index_stat_adapted,
        alignment_stats_adapted,
        header_adapted.sequences,
        header_adapted.read_groups,
        header_adapted.programs,
        header_adapted.comments,
    )

    extensions = "".join(MANAGER_CFG.GENERAL.last_path.suffixes[:-1])
    name = MANAGER_CFG.GENERAL.last_path.stem + extensions + ".html"
    target = input.with_name(name)

    with target.open("wt") as f:
        f.write(html_page)

    webbrowser.open(target)
