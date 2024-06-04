from jinja2 import Environment, FileSystemLoader

from helix.configuration import MANAGER_CFG
from helix.data.tabular_data import TabularData


class HTMLSimpleTableReport:
    def __init__(self, name, config=MANAGER_CFG.REPOSITORY) -> None:
        self._name = name
        self._templates_folder = config.metadata.joinpath("report_templates")

    def make(self, table: TabularData):
        file_loader = FileSystemLoader(self._templates_folder)
        env = Environment(loader=file_loader)
        template = env.get_template("table_simple.html")
        return template.render(data={"title": self._name, "table": table})
