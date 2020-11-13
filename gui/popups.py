# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from gui.templates import Popup
import json
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout


class ProjectFilePopup(Popup):

    def __init__(self, project_file, *args, **kwargs):
        super().__init__(None, "Project File", "icon.png", *args, **kwargs)
        self.project_file = project_file

        self.resize(400, 300)  # FIXME

        self.layout = QVBoxLayout()

        self.json_tree = QTreeWidget()
        self.json_tree.setHeaderLabels(['Project parameters'])
        self._build_tree()

        self.layout.addWidget(self.json_tree)
        self.setLayout(self.layout)

    def _build_tree(self):
        """
        FIXME
        """

        try:
            pfile = open(self.project_file)
            pfile_contents = json.load(pfile)
            for i in pfile_contents:
                parent = QTreeWidgetItem(self.json_tree, [i])
                metric = 1
                for j in pfile_contents[i]:
                    branch = QTreeWidgetItem(parent, ['{0} {1}'.format(i, metric)])
                    # child = QTreeWidgetItem(parent, ['{0}: {1}'.format(k, j[k]) for k in j])
                    for k in j:
                        child = QTreeWidgetItem(branch, ['{0}: {1}'.format(k, j[k])])
                    metric += 1
        except FileNotFoundError:
            print("File not found")

    def run(self):
        """
        Displays the JSON window
        """

        self.show()