"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

from configparser import ConfigParser
import inspect
from json import load
import pydre.metrics as metrics
from PySide2.QtWidgets import QComboBox, QTreeWidget, QTreeWidgetItem

import pydre

config = ConfigParser()
config.read("./config_files/config.ini")


class ProjectTree(QTreeWidget):
    """
    Custom tree widget for building, displaying, and editing project file trees.
    """

    def __init__(self, c_width, headers=None, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Class variables
        if headers is None:
            self.headers = ["Project parameters", ""]
        else:
            self.headers = headers

        # Widget configurations
        self.setColumnWidth(0, c_width)
        self.setHeaderLabels(self.headers)
        self.setAnimated(animated)

        # FIXME
        self.methods = metrics.metricsList
        arguments = inspect.getfullargspec(self.methods["colMean"]).args
        # print(self.methods)
        # print(arguments)
        # print(type(arguments[0]))
        # if isinstance(arguments[0], str):
        #     print("test1")
        # print("{0}: {1}".format(arguments[2], type(arguments[2])))

    def _build_metrics(self, tree, metrics_):
        """
        FIXME
        """

        for i in metrics_:
            text = ["{0}".format(i["name"])]
            branch = QTreeWidgetItem(tree, text)

            leaves = [j for j in i if j != "name"]
            for k in leaves:
                text = ["{0}:".format(k)]
                leaf = QTreeWidgetItem(branch, text)

                cb = QComboBox()
                for method in self.methods:
                    cb.addItem(method)

                idx = cb.findText(i["function"])
                cb.setCurrentIndex(idx)
                self.setItemWidget(leaf, 1, cb)

    def _build_rois(self, tree, rois):
        """
        FIXME
        """

        for i in rois:
            text = ["{0}".format(i["type"])]
            branch = QTreeWidgetItem(tree, text)

            leaves = [j for j in i if j != "type"]
            for k in leaves:
                text = ["{0}:".format(k)]
                leaf = QTreeWidgetItem(branch, text)

                cb = QComboBox()

                self.setItemWidget(leaf, 1, cb)

    def _build_tree(self, tree, contents, parameter):
        """
        Builds a tree for the specified parameter of the given project file.

        args:
            tree: Parent tree widget item
            contents: Dictionary of the contents of the project file
            parameter: Specified parameter for which the tree is being built
        """

        # Generate branches for the specified parameter
        print(contents)
        for c in contents:
            print(c)
            if c == "metrics":
                self._build_metrics(tree, contents[c])

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
            if i == "metrics":
                self._build_metrics(tree, contents[i])
            elif i == "rois":
                self._build_rois(tree, contents[i])

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
