"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

import pydre
from gui.config import Config
import inspect
from json import load
from os import path
import pydre.metrics as metrics
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, \
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QWidget
from typing import get_type_hints

config = Config()
PROJECT_PATH = path.dirname(path.abspath(__file__))
CONFIG_PATH = path.join(PROJECT_PATH, "config_files/config.ini")
config.read(CONFIG_PATH)


class LeafWidget(QWidget):
    """
    Custom leaf widget for displaying and editing project file parameters.
    """

    def __init__(self, layout=QHBoxLayout, items=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = layout()
        self.items = items

    def combo_box(self, text, value=None):
        """
        TODO
        """

        label = QLabel("{0}:".format(text))
        cb = QComboBox()

        for item in self.items:
            cb.addItem(item)

        if value is not None:
            idx = list(self.items.keys()).index(value)
            cb.setCurrentIndex(idx)

        self.layout.addWidget(label)
        self.layout.addWidget(cb)
        self.setLayout(self.layout)

        return self

    def spin_box(self, text, value=None):
        """
        TODO
        """

        label = QLabel("{0}:".format(text))
        sb = QSpinBox()

        if value is not None:
            sb.setValue(value)

        self.layout.addWidget(label)
        self.layout.addWidget(sb)
        self.setLayout(self.layout)

        return self

    def line_edit(self, text, value=None):
        """
        TODO
        """

        label = QLabel("{0}:".format(text))
        le = QLineEdit()

        if value is not None:
            le.setText(value)

        le.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        self.layout.addWidget(label)
        self.layout.addWidget(le)
        self.setLayout(self.layout)

        return self


class ProjectTree(QTreeWidget):
    """
    Custom tree widget for building, displaying, and editing project file trees.
    """

    def __init__(self, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.metrics = metrics.metricsList
        self.widgets_by_type = {
            None: lambda t, v: LeafWidget(items=self.metrics).combo_box(t, v),
            float: lambda t, v: LeafWidget().spin_box(t, v),
            str: lambda t, v: LeafWidget().line_edit(t, v)
        }

        # Widget configurations
        self.setAnimated(animated)
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)
        self._configure_style()

    def _configure_style(self):
        """
        TODO
        """

        stylesheet_path = path.join(PROJECT_PATH, "stylesheets/project_tree.css")
        stylesheet = open(stylesheet_path).read()
        self.setStyleSheet(stylesheet)

    def _build_branch(self, tree, name):
        """
        TODO
        """

        branch = QTreeWidgetItem(tree, [name])
        widget = QLineEdit()
        widget.setText(name)
        self.setItemWidget(branch, 0, widget)

        return branch

    def _build_leaf(self, branch, metric, attribute, type_=None):
        """
        TODO
        """

        leaf = QTreeWidgetItem(branch)
        widget = self.widgets_by_type[type_](attribute, metric[attribute])
        self.setItemWidget(leaf, 0, widget)

        return leaf

    def _build_metrics(self, tree, metrics_):
        """
        TODO
        """

        for metric in metrics_:
            # Generate a branch for each metric
            branch = self._build_branch(tree, metric["name"])

            # Get argument types for the current metric function
            types = get_type_hints(self.metrics[metric["function"]])

            # Generate a leaf for each metric argument
            arguments = [arg for arg in metric if arg != "name"]
            for argument in arguments:
                type_ = types[argument] if argument != "function" else None
                self._build_leaf(branch, metric, argument, type_)

    def _build_rois(self, tree, rois):
        """
        TODO
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

    def build_from_dict(self, contents):
        """
        Builds a tree for each of the parameters in the given project file
        dictionary.

        args:
            contents: Dictionary of the contents of a project file
        """

        # Generate a tree for each parameter type
        for i in contents:
            tree = QTreeWidgetItem(self, [i])
            if i == "metrics":
                self._build_metrics(tree, contents[i])
            elif i == "rois":
                self._build_rois(tree, contents[i])

    def build_from_file(self, path_):
        """
        Loads contents of the given project file and builds a tree for each of
        its parameters.

        args:
            path: Project file path
        """

        # Load project file contents
        contents = load(open(path_))

        # Generate tree for each parameter type
        self.build_from_dict(contents)
