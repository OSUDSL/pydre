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

    def __init__(self, project_file):
        super().__init__(Ui_Form, "images/icon.png", "Project Editor")

        # Class parameters
        self.project_file = project_file

        # Class variables
        self.param_types = {'rois': 'roi', 'metrics': 'metric'}

        # Button callbacks
        self.ui.cancel_btn.clicked.connect(self.close)
        self.ui.save_btn.clicked.connect(self._save)
        self.ui.finish_btn.clicked.connect(self._finish)

        self._build_tree()

    def _build_tree(self):
        """
        FIXME
        """

        # Load project file contents
        pfile_contents = json.load(self.project_file)

        # Generate tree for each parameter type
        for i in pfile_contents:
            tree = QTreeWidgetItem(self.ui.pfile_tree, [i])

            # Generate branch for the contents of each parameter type
            for idx, j in enumerate(pfile_contents[i]):
                branch = QTreeWidgetItem(tree, [
                    '{0} {1}'.format(self.param_types[i], idx + 1)])

                # Generate leaf for each parameter
                for k in j:
                    QTreeWidgetItem(branch, ['{0}: {1}'.format(k, j[k])])

    def _save(self):
        """
        FIXME
        """

        print("DEBUG: Project file saved :)")

    def _finish(self):
        """
        FIXME
        """

        self._save()
        self.close()
