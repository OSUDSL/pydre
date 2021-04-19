"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

import copy

import inspect
import pydre.metrics as pydre_metrics
from PySide2 import QtCore
from gui.popups import FunctionPopup
from gui.config import Config
from json import dump, load
from os import path
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, \
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

        if self.items is not None:
            for item in self.items:
                cb.addItem(item)
        else:
            # TODO: Add log message here
            print("Items list required at initialization for combo box")

        if value is not None:
            try:
                idx = list(self.items.keys()).index(value)
                cb.setCurrentIndex(idx)
            except ValueError:
                print("ERROR: value:", value)

        cb.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

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

        le.setStyleSheet(
            "border-style: outset; border-width: 1px; border-color: black;")

        self.layout.addWidget(label)
        self.layout.addWidget(le)
        self.setLayout(self.layout)

        return self


class ProjectTree(QTreeWidget):
    """
    Custom tree widget for building, displaying, and editing project file trees.
    """

    def __init__(self, file, metrics, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.pfile = file
        self.metrics = metrics
        self.default_contents = load(open(self.pfile))  # TODO: Better name
        self.contents = copy.deepcopy(self.default_contents)
        self.widgets_by_type = {
            None: lambda t, v: LeafWidget(items=self.metrics).combo_box(t, v),
            float: lambda t, v: LeafWidget().spin_box(t, v),
            str: lambda t, v: LeafWidget().line_edit(t, v)
        }
        self.trees = {}
        self.branches = {}

        # Widget configurations
        self.setAnimated(animated)
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)
        self._configure_style()

        # Build project tree
        self._build_tree()

        print("Contents: ", self.contents)

    def _configure_style(self):
        """
        TODO
        """

        style_path = path.join(PROJECT_PATH, "stylesheets/project_tree.css")
        stylesheet = open(style_path).read()
        self.setStyleSheet(stylesheet)

    def _build_metrics_branch(self, tree, name, idx):
        """
        TODO
        """

        branch = QTreeWidgetItem(tree, [name])
        widget = QLineEdit()
        widget.setText(name)
        self.setItemWidget(branch, 0, widget)

        # TODO
        widget.textChanged.connect(
            lambda e: self._update_metric(e, idx, "name"))

        return branch

    def _build_metrics_leaf(self, branch, metric, idx, attribute, type_=None):
        """
        TODO
        """

        leaf = QTreeWidgetItem(branch)
        print("type:", type)
        print("attribute:", attribute)
        print("metric:", metric)
        widget = self.widgets_by_type[type_](attribute, metric[attribute])

        if type_ is None:
            widget.children()[2].currentIndexChanged.connect(
                lambda e: self._update_metric_function(widget.children()[2].itemText(e), widget.children()[2], idx, attribute))
        elif type_ == float:
            widget.children()[2].valueChanged.connect(
                lambda e: self._update_metric(e, idx, attribute))
        elif type_ == str:
            widget.children()[2].textChanged.connect(
                lambda e: self._update_metric(e, idx, attribute))

        self.setItemWidget(leaf, 0, widget)

        return leaf

    def _build_metrics(self, tree, metrics_):
        """
        TODO
        """

        for metric in metrics_:
            # Generate a branch for each metric
            idx = metrics_.index(metric)
            branch = self._build_metrics_branch(tree, metric["name"], idx)
            self.branches[metric["name"]] = branch

            # Get argument types for the current metric function
            types = get_type_hints(self.metrics[metric["function"]])
            print("metrics:", self.metrics)

            # Generate a leaf for each metric argument
            arguments = [arg for arg in metric if arg != "name"]
            for argument in arguments:
                type_ = types[argument] if argument != "function" else None
                self._build_metrics_leaf(branch, metric, idx, argument, type_)

    def _rebuild_branch(self, tree, metric, idx):
        """
        TODO
        """

        branch = self._build_metrics_branch(tree, metric["name"], idx)
        types = get_type_hints(self.metrics[metric["function"]])
        print("types:", types)
        arguments = [arg for arg in types.keys()]
        for value in types.values():
            if (value == str or value == float):
                self._build_metrics_leaf(
                    branch, metric, idx, arguments[list(types.values()).index(value)], value)
            else:
                self._build_metrics_leaf(
                    branch, metric, idx, arguments[list(types.values()).index(value)])

    def _build_rois_branch(self, tree, name, idx):
        """
        TODO
        """

        branch = QTreeWidgetItem(tree, [name])
        widget = QLineEdit()
        widget.setText(name)
        self.setItemWidget(branch, 0, widget)

        widget.textChanged.connect(lambda e: self._update_roi(e, idx, "type"))

        return branch

    def _build_rois_leaf(self, branch, roi, idx, attribute):
        """
        TODO
        """

        leaf = QTreeWidgetItem(branch)
        widget = self.widgets_by_type[str](attribute, roi[attribute])

        widget.children()[2].textChanged.connect(
            lambda e: self._update_roi(e, idx, attribute))

        self.setItemWidget(leaf, 0, widget)

        return leaf

    def _build_rois(self, tree, rois):
        """
        TODO
        """

        for roi in rois:
            # Generate a branch for each roi
            idx = rois.index(roi)
            branch = self._build_rois_branch(tree, roi["type"], idx)

            # Generate leaves for the current roi
            attributes = [attr for attr in roi if attr != "type"]
            for attribute in attributes:
                self._build_rois_leaf(branch, roi, idx, attribute)

    def _build_tree(self):
        """
        Builds a tree for each of the class project file's parameter types.

        args:
            path: Project file path
        """

        for i in self.contents:
            tree = QTreeWidgetItem(self, [i])
            if i == "metrics":
                self._build_metrics(tree, self.contents[i])
                self.trees["metrics"] = tree
            elif i == "rois":
                self._build_rois(tree, self.contents[i])
                self.trees["rois"] = tree

    def _update_metric(self, e, idx, attribute):
        """
        TODO
        """

        self.contents["metrics"][idx][attribute] = e

    def _popup_clicked(self, i, w, e, idx):
        """
        TODO
        """

        if i.text() == "&Yes":
            self._update_metric(e, idx, "function")
        else:
            index = w.findText(
                self.contents["metrics"][idx]["function"], QtCore.Qt.MatchFixedString)
            w.setCurrentIndex(index)

    def _update_metric_function(self, e, w, idx, attribute):
        """
        TODO
        """

        # popup = FunctionPopup()

        # def temp(i):
        #     print(i.text())
        #     self._popup_clicked(i, w, e, idx)

        # popup.buttonClicked.connect(lambda i: temp(i))
        # popup.exec_()

        # FIXME: Need to rebuild metrics before rebuilding the branch
        name = self.contents["metrics"][idx]["name"]
        self.contents["metrics"][idx] = {}
        self.contents["metrics"][idx]["name"] = name
        self.contents["metrics"][idx]["function"] = e
        types = get_type_hints(
            pydre_metrics.metricsList[self.contents["metrics"][idx]["function"]])
        print("names: ", self.contents["metrics"][idx])
        print("types:", types)

        branch = self.branches[self.contents["metrics"][idx]["name"]]
        while branch.childCount() > 1:
            branch.takeChild(1)

        print("type keys:", types.keys())
        for arg in types.keys():
            if arg != "drivedata":
                if types[arg] == str:
                    self.contents["metrics"][idx][arg] = ""
                else:
                    self.contents["metrics"][idx][arg] = 0
                self._build_metrics_leaf(
                    branch, self.contents["metrics"][idx], idx, arg, types[arg])

    def _update_roi(self, e, idx, attribute):
        """
        TODO
        """

        self.contents["rois"][idx][attribute] = e

    def build_from_file(self, file):
        """
        TODO
        """

    def compare_contents(self):
        """
        TODO
        """

        return self.default_contents == self.contents

    def get_contents(self):
        """
        TODO
        """

        return self.contents

    def update_contents(self):
        """
        TODO
        """

        self.default_contents = copy.deepcopy(self.contents)
