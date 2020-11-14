# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from gui.templates import Popup
from gui.ui_files.ui_projectfilepopup import Ui_Form
import json
from PySide2.QtWidgets import QTreeWidgetItem


class ProjectFilePopup(Popup):
    """
    Project file editor that handles all tasks related to viewing and
    configuring the given project JSON file.
    """

    def __init__(self, project_file, *args, **kwargs):
        super().__init__(Ui_Form, "images/icon.png", "Project Editor")

        # self.project_file = project_file
        #
        # self.layout = QVBoxLayout()
        #
        # self.json_tree = QTreeWidget()
        # self.json_tree.setHeaderLabels(['Project parameters'])
        # self._build_tree()
        #
        # self.layout.addWidget(self.json_tree)
        # self.setLayout(self.layout)

    def _build_tree(self):
        """
        FIXME
        """

        pfile_contents = json.load(self.project_file)
        for i in pfile_contents:
            parent = QTreeWidgetItem(self.json_tree, [i])
            metric = 1
            for j in pfile_contents[i]:
                branch = QTreeWidgetItem(parent, ['{0} {1}'.format(i, metric)])
                # child = QTreeWidgetItem(parent, ['{0}: {1}'.format(k, j[k]) for k in j])
                for k in j:
                    child = QTreeWidgetItem(branch,
                                            ['{0}: {1}'.format(k, j[k])])
                metric += 1
