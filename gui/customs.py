"""
Created by: Craig Fouts
Created on: 11/21/2020
"""

import gui
from gui.config import Config
import inspect
from json import load
from os import path
import pydre.metrics as metrics
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QAbstractItemView, QComboBox, QHBoxLayout, \
    QLabel, QLineEdit, QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, \
    QWidget
from typing import get_type_hints

config = Config()
module_path = path.dirname(inspect.getfile(gui))
config_path = module_path + r"/config_files/config.ini"
config.read(config_path)


class ProjectTree(QTreeWidget):
    """
    Custom tree widget for building, displaying, and editing project file trees.
    """

    def __init__(self, animated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Config variables
        self.param_types = dict(config.items("parameters"))

        # Widget configurations
        self.setAnimated(animated)
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)

        # FIXME check border
        stylesheet = (
            "QTreeView {"
            "border: none;"
            "}"
            "QTreeView::item:hover {"
            "color: black;"
            "background-color: white;"
            "}"
            "QTreeView::item:!hover {"
            "background-color: white;"
            "}"
            "QTreeView::item:focus {"
            "color: black;"
            "background-color: white;"
            "border: 1px solid white;"
            "}"
        )
        self.setStyleSheet(stylesheet)

        # FIXME
        self.methods = metrics.metricsList
        arguments = inspect.getfullargspec(self.methods["colMean"]).args
        # print(self.methods)
        # print(arguments)
        # print(type(arguments[0]))
        # if isinstance(arguments[0], str):
        #     print("test1")
        # print("{0}: {1}".format(arguments[2], get_type_hints(self.methods["colMean"])))

    def _build_metrics(self, tree, metrics_):
        """
        FIXME
        """

        # FIXME: CUSTOM WIDGETS FOR EACH LEAF

        for i in metrics_:
            text = ["{0}".format(i["name"])]
            branch = QTreeWidgetItem(tree, text)

            le = QLineEdit()
            le.setText(text[0])
            stylesheet = "QLineEdit { border: 1px white; }"
            le.setStyleSheet(stylesheet)
            self.setItemWidget(branch, 0, le)

            leaves = [j for j in i if j != "name"]
            for k in leaves:
                leaf = QTreeWidgetItem(branch)

                widget = QWidget()
                layout = QHBoxLayout()

                label = QLabel("{0}:".format(k))

                types = get_type_hints(self.methods[i["function"]])
                if k == "function":
                    wg = QComboBox()
                    for method in self.methods:
                        wg.addItem(method)
                    idx = wg.findText(i[k])
                    wg.setCurrentIndex(idx)
                elif types[k] == float:
                    wg = QSpinBox()
                    wg.setValue(i[k])
                elif types[k] == str:
                    wg = QLineEdit()
                    wg.setText(i[k])
                    wg.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

                layout.addWidget(label)
                layout.addWidget(wg)
                widget.setLayout(layout)

                self.setItemWidget(leaf, 0, widget)

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

    def build_from_file(self, path_):
        """
        Unloads contents of the given project file and builds a tree for each of
        its parameters.

        args:
            path: Project file path
        """

        # Load project file contents
        contents = load(open(path_))

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
