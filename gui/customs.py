"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

from configparser import ConfigParser
from json import load
from PySide2.QtWidgets import QComboBox, QTreeWidget, QTreeWidgetItem

config = ConfigParser()
config.read("./config_files/config.ini")


class ProjectTree(QTreeWidget):
    """
    Custom tree widget for building, displaying, and editing project file trees.
    """

    def __init__(self, headers=None, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Class variables
        if headers is None:
            self.headers = ["Project parameters", ""]
        else:
            self.headers = headers

        # Widget configurations
        self.setHeaderLabels(self.headers)
        self.setAnimated(animated)

    def _build_tree(self, tree, contents, parameter):
        """
        Builds a tree for the specified parameter of the given project file.

        args:
            tree: Parent tree widget item
            contents: Dictionary of the contents of the project file
            parameter: Specified parameter for which the tree is being built
        """

        # Generate branches for the specified parameter
        for index, i, in enumerate(contents[parameter]):
            text = ["{0} {1}".format(self.param_types[parameter], index + 1)]
            branch = QTreeWidgetItem(tree, text)

            # Generate leaves for the attributes in each branch
            for j in i:
                text = ["{0}: {1}".format(j, i[j])]
                leaf = QTreeWidgetItem(branch, text)
                self.setItemWidget(leaf, 1, QComboBox())

    def build_from_file(self, path):
        """
        Unloads contents of the given project file and builds a tree for each of
        its parameters.

        args:
            path: Project file path
        """

        # Load project file contents
        contents = load(open(path))

        # Generate tree for each parameter type
        for i in contents:
            tree = QTreeWidgetItem(self, [i])
            self._build_tree(tree, contents, i)

    def build_from_dict(self, contents):
        """
        Builds a tree for each of the parameters in the given project file
        dictionary.

        args:
            contents: Dictionary of the contents of a project file
        """

        # Generate tree for each parameter type
        for i in contents:
            tree = QTreeWidgetItem(self, [i])
            self._build_tree(tree, contents, i)
