'''
Created by: Craig Fouts
Created on: 11/21/2020
'''

import copy
import json
import os
import typing
from gui.config import Config
from gui.popups import FunctionPopup
from pydre import metrics
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, \
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QWidget

config = Config()
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_PATH, 'config_files/config.ini')
config.read(CONFIG_PATH)


class WidgetFactory:
    '''TODO

    '''

    @staticmethod
    def combo_box(value, cb, items):
        '''TODO

        '''

        combo_box = QComboBox()
        for item in items:
            combo_box.addItem(item)
        index = items.index(value)
        combo_box.setCurrentIndex(index)
        combo_box.activated.connect(lambda i: cb(combo_box.itemText(i)))
        return combo_box

    @staticmethod
    def spin_box(value, cb):
        '''TODO

        '''

        spin_box = QSpinBox()
        spin_box.setValue(value)
        spin_box.valueChanged.connect(cb)
        return spin_box

    @staticmethod
    def line_edit(value, cb, border=True):
        '''TODO

        '''

        line_edit = QLineEdit()
        line_edit.setText(value)
        if not border:
            line_edit.setStyleSheet('border: none;')
        line_edit.textChanged.connect(cb)
        return line_edit


class LeafWidget(QWidget):
    '''Custom leaf widget for displaying and editing project file parameters.

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QHBoxLayout()

    def _configure_layout(self, label, widget):
        '''TODO

        '''

        self.layout.addWidget(label)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)

    def combo_box(self, items, text, value, cb):
        '''TODO

        '''

        label = QLabel(text)
        combo_box = WidgetFactory.combo_box(value, cb, items)
        self._configure_layout(label, combo_box)
        return self

    def spin_box(self, text, value, cb):
        '''TODO

        '''

        label = QLabel(text)
        spin_box = WidgetFactory.spin_box(value, cb)
        self._configure_layout(label, spin_box)
        return self

    def line_edit(self, text, value, cb):
        '''TODO

        '''

        label = QLabel(text)
        line_edit = WidgetFactory.line_edit(value, cb)
        line_edit.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._configure_layout(label, line_edit)
        return self


class MetricsTree(QTreeWidget):
    '''TODO

    '''

    def __init__(self, root, metrics_, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root
        self.metrics = metrics_
        self.tree = QTreeWidgetItem(self.root, ['metrics'])
        items = list(metrics.metricsList.keys())
        self.widgets = {
            None: lambda t, v, c: LeafWidget().combo_box(items, t, v, c),
            float: lambda t, v, c: LeafWidget().spin_box(t, v, c),
            str: lambda t, v, c: LeafWidget().line_edit(t, v, c)
        }
        self.branches = {}
        self.function_popup = FunctionPopup()
        self._configure_widget()

    def _configure_widget(self):
        '''TODO

        '''

        for index in range(len(self.metrics)):
            self._configure_branch(index)

    def _configure_branch(self, index):
        '''TODO

        '''

        branch = QTreeWidgetItem(self.tree)
        metric = self.metrics[index]
        self.branches[metric['name']] = branch
        def cb(e): return self._update_metric(index, 'name', e)
        line_edit = WidgetFactory.line_edit(metric['name'], cb, False)
        for attribute in filter(lambda a: a != 'name', metric):
            self._configure_leaf(branch, index, attribute)
        self.root.setItemWidget(branch, 0, line_edit)

    def _configure_leaf(self, branch, index, attribute):
        '''TODO

        '''

        leaf = QTreeWidgetItem(branch)
        metric = self.metrics[index]
        function = metrics.metricsList[metric['function']]
        types = typing.get_type_hints(function)
        type_ = types[attribute] if attribute != 'function' else None
        def cb(e): return self._update_metric(index, attribute, e)
        widget = self.widgets[type_](attribute, metric[attribute], cb)
        self.root.setItemWidget(leaf, 0, widget)

    def _update_metric(self, index, attribute, value):
        '''TODO

        '''

        if attribute == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self._handle_update(index, value, e)
            self.function_popup.show_(text, cb)
        else:
            self.metrics[index][attribute] = value

    def _handle_update(self, index, value, update):
        '''TODO

        '''

        if not update:
            value = self.metrics[index]['function']
        self._update_metric_function(index, value)

    def _update_metric_function(self, index, value):
        '''TODO

        '''

        metric = self.metrics[index]
        self.metrics[index] = {'name': metric['name'], 'function': value}
        branch = self.branches[self.metrics[index]['name']]
        branch.takeChildren()
        function = metrics.metricsList[self.metrics[index]['function']]
        types = typing.get_type_hints(function)
        self._configure_leaf(branch, index, 'function')
        for argument in filter(lambda a: a != 'drivedata', types.keys()):
            type_ = types[argument]
            self.metrics[index][argument] = "" if type_ is str else 0
            self._configure_leaf(branch, index, argument)

    def get_collection(self):
        '''TODO

        '''

        return self.metrics


class RoisTree(QTreeWidget):
    '''TODO

    '''

    def __init__(self, root, rois, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root
        self.rois = rois
        self.tree = QTreeWidgetItem(self.root, ['rois'])
        self.branches = {}
        self._configure_widget()

    def _configure_widget(self):
        '''TODO

        '''

        for index in range(len(self.rois)):
            self._configure_branch(index)

    def _configure_branch(self, index):
        '''TODO

        '''

        branch = QTreeWidgetItem(self.tree)
        roi = self.rois[index]
        self.branches[roi['type']] = branch
        def cb(e): return self._update_roi(index, attribute, e)
        line_edit = WidgetFactory.line_edit(roi['type'], cb, False)
        for attribute in filter(lambda a: a != 'type', roi):
            self._configure_leaf(branch, index, attribute)
        self.root.setItemWidget(branch, 0, line_edit)

    def _configure_leaf(self, branch, index, attribute):
        '''TODO

        '''

        leaf = QTreeWidgetItem(branch)
        roi = self.rois[index]
        def cb(e): return self._update_roi(index, attribute, e)
        line_edit = LeafWidget().line_edit(attribute, roi[attribute], cb)
        self.root.setItemWidget(leaf, 0, line_edit)

    def _update_roi(self, index, attribute, value):
        '''TODO

        '''

        self.rois[index][attribute] = value

    def get_collection(self):
        '''TODO

        '''

        return self.rois


class FiltersTree(QTreeWidget):
    '''TODO

    '''

    def __init__(self, root, filters, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root
        self.filters = filters
        self.tree = QTreeWidgetItem(self.root, ['filters'])
        self.branches = {}
        self._configure_widget()

    def _configure_widget(self):
        '''TODO

        '''

        for index in range(len(self.filters)):
            self._configure_branch(index)

    def _configure_branch(self, index):
        '''TODO

        '''

        branch = QTreeWidgetItem(self.tree)
        filter_ = self.filters[index]
        self.branches[filter_['name']] = branch
        def cb(e): return self._update_filters(index, attribute, e)
        line_edit = WidgetFactory.line_edit(filter_['name'], cb, False)
        for attribute in filter(lambda a: a != 'name', filter_):
            self._configure_leaf(branch, index, attribute)
        self.root.setItemWidget(branch, 0, line_edit)

    def _configure_leaf(self, branch, index, attribute):
        '''TODO

        '''

        leaf = QTreeWidgetItem(branch)
        filter_ = self.filters[index]
        def cb(e): return self._update_filters(index, attribute, e)
        line_edit = LeafWidget().line_edit(attribute, filter_[attribute], cb)
        self.root.setItemWidget(leaf, 0, line_edit)

    def _update_filters(self, index, attribute, value):
        '''TODO

        '''

        self.filters[index][attribute] = value

    def get_collection(self):
        '''TODO

        '''

        return self.filters


class ProjectTree(QTreeWidget):
    '''Custom tree widget for displaying and editing project files.

    '''

    def __init__(self, project_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.project_file = project_file
        self.contents = json.load(open(self.project_file))
        self.mutable_copy = copy.deepcopy(self.contents)
        self.trees = {
            'metrics': lambda r, c: MetricsTree(r, c),
            'rois': lambda r, c: RoisTree(r, c),
            'filters': lambda r, c: FiltersTree(r, c)
        }
        self.subtrees = {}
        self._configure_widget()

    def _configure_widget(self):
        '''TODO

        '''

        self._configure_settings()
        for collection in self.mutable_copy:
            tree = self.trees[collection](self, self.mutable_copy[collection])
            self.subtrees[collection] = tree

    def _configure_settings(self):
        '''TODO

        '''

        style_path = config.get('Stylesheets', 'projectTree')
        style_path = os.path.join(PROJECT_PATH, style_path)
        stylesheet = open(style_path).read()
        self.setStyleSheet(stylesheet)
        self.setAnimated(True)
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)

    def get_contents(self):
        '''TODO

        '''

        self.update_contents()
        return self.contents

    def update_contents(self):
        '''TODO

        '''

        self.contents = self.mutable_copy

    def changed(self):
        '''TODO

        '''

        if self.mutable_copy != self.contents:
            return True
        return False
