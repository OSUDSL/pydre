"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

from configparser import ConfigParser
from json import load
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem

config = ConfigParser()
config.read("./config_files/config.ini")


class ProjectTree(QTreeWidget):
    """
    TODO
    """

    def __init__(self, headers=None, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Class variables
        if headers is None:
            self.headers = ["Project parameters"]
        else:
            self.headers = headers

        # Widget configurations
        self.setHeaderLabels(self.headers)
        self.setAnimated(animated)

    @staticmethod
    def _fill_leaves(branch, attributes):
        """TODO"""

        # Generate leaves with the give attributes list
        for i in attributes:
            text = ["{0}: {1}".format(i, attributes[i])]
            QTreeWidgetItem(branch, text)

    def _fill_branches(self, tree, contents, parameter):
        """TODO"""

        # Generate branches for the specified parameter
        for index, i in enumerate(contents[parameter]):
            text = ["{0} {1}".format(self.param_types[parameter], index + 1)]
            branch = QTreeWidgetItem(tree, text)
            self._fill_leaves(branch, i)

    def build_from_file(self, path):
        """
        TODO
        """

        # Load project file contents
        contents = load(open(path))

        # Generate tree for each parameter type
        for i in contents:
            tree = QTreeWidgetItem(self, [i])
            self._fill_branches(tree, contents, i)
