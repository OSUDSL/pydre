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

    def __init__(self, headers, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setHeaderLabels(headers)
        self.setAnimated(animated)

        self.param_types = dict(config.items("parameters"))

    @staticmethod
    def _fill_leaves(branch, parameters):
        """TODO"""

        for param in parameters:
            text = ["{0}: {1}".format(param, parameters[param])]
            QTreeWidgetItem(branch, text)

    def _fill_branches(self, tree, parameters):
        """TODO"""

        for index, type_ in parameters:
            text = ["{0} {1}".format()]

    def build(self, path):
        """
        TODO
        """




