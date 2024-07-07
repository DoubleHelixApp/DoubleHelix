from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from helix.microarray.microarray_converter import MicroarrayConverterTarget

# helix.plugin.* are provided by a different package.
# Same concept explained in helix/__init__.py
# from helix.plugins import microarray # type: ignore


# class MicroarraySelection1(QWidget):
#     def __init__(self):
#         super().__init__()

#         microarray_folder = Path(microarray.__file__).parent
#         self.microarray_meta = microarray_folder.joinpath("meta.json")
#         self.setWindowTitle("Table Widget with Checkboxes")
#         self.setGeometry(100, 100, 500, 300)

#         # Create a QTableWidget
#         self.table_widget = QTableWidget(self)
#         self.table_widget.setRowCount(4)  # Set the number of rows
#         self.table_widget.setColumnCount(3)  # Set the number of columns
#         self.setCentralWidget(self.table_widget)

#         # Set headers
#         self.table_widget.setHorizontalHeaderLabels(["", "Provider", "Version", "Tags"])

#     def populate_table(self, path: )
#         # Add items with checkboxes in the first column
#         for row in range(self.table_widget.rowCount()):
#             check_item = QTableWidgetItem()
#             check_item.setFlags(check_item.flags() | Qt.ItemIsUserCheckable)
#             check_item.setCheckState(Qt.Unchecked)
#             self.table_widget.setItem(row, 0, check_item)

#             # Add sample data in the other columns
#             self.table_widget.setItem(row, 1, QTableWidgetItem(f"Item {row+1} - 1"))
#             self.table_widget.setItem(row, 2, QTableWidgetItem(f"Item {row+1} - 2"))


class MicroarraySelection(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName(MicroarraySelection.__name__)
        self.main_group_box = QGroupBox("Select microarray format", parent)
        self.inner_layout = QVBoxLayout(self.main_group_box)
        self.main_layout = QVBoxLayout()

        self.main_group_box.setObjectName("mainGroupBox")
        self.inner_layout.setObjectName("innerLayout")

        self.combined_checkboxes = None
        self.genealogy_checkboxes = None
        self.health_checkboxes = None
        self.ancient_dna_checkboxes = None

        self.combined_group = self._create_combined_group_box(self.main_group_box)
        self.genealogy_group = self._create_genealogy_group_box(self.main_group_box)
        self.health_group = self._create_health_group_box(self.main_group_box)
        self.ancient_group = self._create_ancient_dna_group_box(self.main_group_box)

        self.checkboxes = [
            *self.combined_checkboxes,
            *self.genealogy_checkboxes,
            *self.health_checkboxes,
            *self.ancient_dna_checkboxes,
        ]

        self.inner_layout.addWidget(self.combined_group)
        self.inner_layout.addWidget(self.genealogy_group)
        self.inner_layout.addWidget(self.health_group)
        self.inner_layout.addWidget(self.ancient_group)

        self.main_layout.addWidget(self.main_group_box)
        self.setLayout(self.main_layout)
        self.hide()

    def _create_combined_group_box(self, parent):
        boldFont = QFont()
        boldFont.setBold(True)

        combined_group = QGroupBox("Combined Kits", parent)
        layout = QGridLayout(combined_group)

        combinedWGSELabel = QLabel("WGSE", combined_group)
        combined23AndMeLabel = QLabel("23AndMe", combined_group)
        combinedReichLabLabel = QLabel("ReichLab", combined_group)

        self.combined_checkboxes = [
            QCheckBox("All", combined_group),
            QCheckBox("v3 *", combined_group),
            QCheckBox("v5", combined_group),
            QCheckBox("v3 + v5 *", combined_group),
            QCheckBox("API SNPs", combined_group),
            QCheckBox("1240K+HumanOrigins", combined_group),
        ]

        combinedWGSELabel.setFont(boldFont)
        combined23AndMeLabel.setFont(boldFont)
        combinedReichLabLabel.setFont(boldFont)

        combined_group.setObjectName("combinedKitsGroupBox")
        layout.setObjectName("combinedLayout")

        combinedWGSELabel.setObjectName("combinedWGSELabel")
        combined23AndMeLabel.setObjectName("combined23AndMeLabel")
        combinedReichLabLabel.setObjectName("combinedReichLabLabel")

        self.combined_checkboxes[0].setObjectName(MicroarrayConverterTarget.All.name)
        self.combined_checkboxes[1].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v3.name
        )
        self.combined_checkboxes[2].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v5.name
        )
        self.combined_checkboxes[3].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v35.name
        )
        self.combined_checkboxes[4].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_SNPs_API.name
        )
        self.combined_checkboxes[5].setObjectName(
            MicroarrayConverterTarget.ReichLab_HumanOrigins_v1.name
        )

        layout.addWidget(combinedWGSELabel, 0, 0, 1, 1)
        layout.addWidget(combined23AndMeLabel, 1, 0, 1, 1)
        layout.addWidget(combinedReichLabLabel, 2, 0, 1, 1)

        layout.addWidget(self.combined_checkboxes[0], 0, 1, 1, 1)
        layout.addWidget(self.combined_checkboxes[1], 0, 2, 1, 1)
        layout.addWidget(self.combined_checkboxes[2], 0, 3, 1, 1)
        layout.addWidget(self.combined_checkboxes[3], 1, 1, 1, 1)
        layout.addWidget(self.combined_checkboxes[4], 1, 2, 1, 1)
        layout.addWidget(self.combined_checkboxes[5], 2, 1, 1, 1)
        return combined_group

    def _create_genealogy_group_box(self, parent):
        boldFont = QFont()
        boldFont.setBold(True)

        genealogy_group = QGroupBox("Genealogy", parent)
        layout = QGridLayout(genealogy_group)

        genealogyAncestryDNALabel = QLabel("Ancestry", genealogy_group)
        genealogy23AndMeLabel = QLabel("23AndMe", genealogy_group)
        genealogyFamilyTreeDNALabel = QLabel("FamilyTreeDNA", genealogy_group)
        genealogyLivingDNALabel = QLabel("Living DNA", genealogy_group)
        genealogyMyHeritageLabel = QLabel("MyHeritage", genealogy_group)

        self.genealogy_checkboxes = [
            QCheckBox("v3", genealogy_group),
            QCheckBox("v4", genealogy_group),
            QCheckBox("v5", genealogy_group),
            QCheckBox("v1", genealogy_group),
            QCheckBox("v2", genealogy_group),
            QCheckBox("v1", genealogy_group),
            QCheckBox("v2", genealogy_group),
            QCheckBox("v3", genealogy_group),
            QCheckBox("v1", genealogy_group),
            QCheckBox("v2", genealogy_group),
            QCheckBox("v1", genealogy_group),
            QCheckBox("v2", genealogy_group),
        ]

        genealogy_group.setObjectName("genealogyGroupBox")
        layout.setObjectName("genealogyLayout")
        genealogy23AndMeLabel.setObjectName("genealogy23AndMeLabel")
        genealogyAncestryDNALabel.setObjectName("genealogyAncestryDNA")
        genealogyFamilyTreeDNALabel.setObjectName("genealogyFamilyTreeDNA")
        genealogyLivingDNALabel.setObjectName("genealogyLivingDNALabel")
        genealogyMyHeritageLabel.setObjectName("genealogyMyHeritageLabel")

        genealogy23AndMeLabel.setFont(boldFont)
        genealogyAncestryDNALabel.setFont(boldFont)
        genealogyFamilyTreeDNALabel.setFont(boldFont)
        genealogyLivingDNALabel.setFont(boldFont)
        genealogyMyHeritageLabel.setFont(boldFont)

        self.genealogy_checkboxes[0].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v3.name
        )
        self.genealogy_checkboxes[1].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v4.name
        )
        self.genealogy_checkboxes[2].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v5.name
        )
        self.genealogy_checkboxes[3].setObjectName(
            MicroarrayConverterTarget.Ancestry_v1.name
        )
        self.genealogy_checkboxes[4].setObjectName(
            MicroarrayConverterTarget.Ancestry_v2.name
        )
        self.genealogy_checkboxes[5].setObjectName(
            MicroarrayConverterTarget.FTDNA_v1.name
        )
        self.genealogy_checkboxes[6].setObjectName(
            MicroarrayConverterTarget.FTDNA_v2.name
        )
        self.genealogy_checkboxes[7].setObjectName(
            MicroarrayConverterTarget.FTDNA_v3.name
        )
        self.genealogy_checkboxes[8].setObjectName(
            MicroarrayConverterTarget.LivingDNA_v1.name
        )
        self.genealogy_checkboxes[9].setObjectName(
            MicroarrayConverterTarget.LivingDNA_v2.name
        )
        self.genealogy_checkboxes[10].setObjectName(
            MicroarrayConverterTarget.MyHeritage_v1.name
        )
        self.genealogy_checkboxes[11].setObjectName(
            MicroarrayConverterTarget.MyHeritage_v2.name
        )

        layout.addWidget(genealogy23AndMeLabel, 0, 0, 1, 1)
        layout.addWidget(genealogyAncestryDNALabel, 2, 0, 1, 1)
        layout.addWidget(genealogyFamilyTreeDNALabel, 3, 0, 1, 1)
        layout.addWidget(genealogyLivingDNALabel, 4, 0, 1, 1)
        layout.addWidget(genealogyMyHeritageLabel, 5, 0, 1, 1)

        layout.addWidget(self.genealogy_checkboxes[0], 0, 1, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[1], 0, 2, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[2], 0, 3, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[3], 2, 1, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[4], 2, 2, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[5], 3, 1, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[6], 3, 2, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[7], 3, 3, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[8], 4, 1, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[9], 4, 2, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[10], 5, 1, 1, 1)
        layout.addWidget(self.genealogy_checkboxes[11], 5, 2, 1, 1)
        return genealogy_group

    def _create_ancient_dna_group_box(self, parent):
        boldFont = QFont()
        boldFont.setBold(True)

        ancient_group = QGroupBox("Ancient DNA", parent)
        layout = QGridLayout(ancient_group)
        reich_lab_label = QLabel("Reich Lab", ancient_group)

        reich_lab_label.setFont(boldFont)

        ancient_group.setObjectName("ancientDNAGroupBox")
        layout.setObjectName("ancientDNALayout")
        reich_lab_label.setObjectName("ancientDNAReichLabLabel")

        self.ancient_dna_checkboxes = [
            QCheckBox("AADR 1240K", ancient_group),
            QCheckBox("Human Origins v1", ancient_group),
        ]

        self.ancient_dna_checkboxes[0].setObjectName(
            MicroarrayConverterTarget.ReichLab_AADR.name
        )
        self.ancient_dna_checkboxes[1].setObjectName(
            MicroarrayConverterTarget.ReichLab_HumanOrigins_v1.name
        )

        spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )

        layout.addWidget(reich_lab_label, 0, 0, 1, 1)
        layout.addWidget(self.ancient_dna_checkboxes[0], 0, 1, 1, 1)
        layout.addWidget(self.ancient_dna_checkboxes[1], 0, 2, 1, 1)
        layout.addItem(spacer, 0, 3, 1, 1)

        return ancient_group

    def _create_health_group_box(self, parent):
        health_group = QGroupBox("Health", parent)
        health_layout = QGridLayout(health_group)

        self.health_checkboxes = [
            QCheckBox("23AndMe", health_group),
            QCheckBox("TellMeGen", health_group),
            QCheckBox("MTHFR Genetics", health_group),
            QCheckBox("AncestryDNA", health_group),
            QCheckBox("SelfDecode", health_group),
        ]

        health_group.setObjectName("healthGroupBox")
        self.health_checkboxes[0].setObjectName(
            MicroarrayConverterTarget.TwentyThreeAndMe_v5.name
        )
        self.health_checkboxes[1].setObjectName(
            MicroarrayConverterTarget.TellMeGen.name
        )
        self.health_checkboxes[2].setObjectName(MicroarrayConverterTarget.MTHFR.name)
        self.health_checkboxes[3].setObjectName(
            MicroarrayConverterTarget.Ancestry_v2.name
        )
        self.health_checkboxes[4].setObjectName(
            MicroarrayConverterTarget.SelfDecode.name
        )

        spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        health_layout.setObjectName("healthLayout")
        health_layout.addItem(spacer, 0, 0, 2, 1)
        health_layout.addWidget(self.health_checkboxes[0], 0, 1, 1, 1)
        health_layout.addWidget(self.health_checkboxes[1], 0, 2, 1, 1)
        health_layout.addWidget(self.health_checkboxes[2], 0, 3, 1, 1)

        health_layout.addWidget(self.health_checkboxes[3], 1, 1, 1, 1)
        health_layout.addWidget(self.health_checkboxes[4], 1, 2, 1, 1)
        return health_group
