'''
Created by: Craig Fouts
Created on: 11/21/2020
'''

import copy
import json
import os
import typing

from PySide2.QtCore import QModelIndex
from pydre import filters, metrics
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, \
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QWidget
from gui.config import Config, CONFIG_PATH
from gui.popups import FunctionPopup

config = Config()
config.read(CONFIG_PATH)


class WidgetFactory:
    '''TODO

    '''

    @staticmethod
    def combo_box(value, cb, items, border=True):
        '''TODO

        '''

        combo_box = QComboBox()
        for item in items:
            combo_box.addItem(item)
        index = items.index(value)
        combo_box.setCurrentIndex(index)
        combo_box.activated.connect(lambda i: cb(combo_box.itemText(i)))
        if border:
            combo_box.setStyleSheet('border: 1px solid black;')
        return combo_box

    @staticmethod
    def spin_box(value, cb, border=True):
        '''TODO

        '''

        spin_box = QSpinBox()
        spin_box.setValue(value)
        spin_box.valueChanged.connect(cb)
        if border:
            spin_box.setStyleSheet('border: 1px solid black;')
        return spin_box

    @staticmethod
    def line_edit(value, cb, border=True):
        '''TODO

        '''

        line_edit = QLineEdit()
        line_edit.setText(value)
        line_edit.textChanged.connect(cb)
        if border:
            line_edit.setStyleSheet('border: 1px solid black;')
        return line_edit


class LeafWidget(QWidget):
    '''Custom leaf widget for displaying and editing project file parameters.

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QHBoxLayout()
        self.text_ = None

    def _configure_layout(self, text, widget):
        '''TODO

        '''

        label = QLabel(text)
        self.layout.addWidget(label)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)

    def combo_box(self, items, text, value, cb):
        '''TODO

        '''

        self.text_ = text
        combo_box = WidgetFactory.combo_box(value, cb, items)
        combo_box.setFixedHeight(30)
        self._configure_layout(text, combo_box)
        return self

    def spin_box(self, text, value, cb):
        '''TODO

        '''

        self.text_ = text
        spin_box = WidgetFactory.spin_box(value, cb)
        self._configure_layout(text, spin_box)
        spin_box.setFixedHeight(30)
        return self

    def line_edit(self, text, value, cb):
        '''TODO

        '''

        self.text_ = text
        line_edit = WidgetFactory.line_edit(value, cb)
        line_edit.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._configure_layout(text, line_edit)
        line_edit.setFixedHeight(30)
        return self

    def text(self):
        '''TODO

        '''

        return self.text_


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
        line_edit = WidgetFactory.line_edit(roi['type'], cb, border=False)
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

    def add_item(self, item):
        '''TODO

        '''

        print(item)


class FiltersTree(QTreeWidget):
    '''TODO

    '''

    def __init__(self, root, filters_, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root
        self.filters = filters_
        self.tree = QTreeWidgetItem(self.root, ['filters'])
        items = list(filters.filtersList.keys())
        self.widgets = {
            None: lambda t, v, c: LeafWidget().combo_box(items, t, v, c),
            float: lambda t, v, c: LeafWidget().spin_box(t, v, c),
            str: lambda t, v, c: LeafWidget().line_edit(t, v, c)
        }
        self.branches = {}
        self.values = {}
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
        def cb(e): return self._update_filters(index, 'name', e)
        line_edit = WidgetFactory.line_edit(filter_['name'], cb, border=False)
        for attribute in filter(lambda a: a != 'name', filter_):
            self._configure_leaf(branch, index, attribute)
        self.root.setItemWidget(branch, 0, line_edit)

    def _configure_leaf(self, branch, index, attribute):
        '''TODO

        '''

        leaf = QTreeWidgetItem(branch)
        filter_ = self.filters[index]
        function = filters.filtersList[filter_['function']]
        types = typing.get_type_hints(function)
        type_ = types[attribute] if attribute != 'function' else None
        def cb(e): return self._update_filter(index, attribute, e)
        widget = self.widgets[type_](attribute, filter_[attribute], cb)
        self.root.setItemWidget(leaf, 0, widget)

    def _update_filter(self, index, attribute, value):
        '''TODO

        '''

        if attribute == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self._handle_update(index, value, e)
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.filters[index][attribute] = value

    def _handle_update(self, index, value, update):
        '''TODO

        '''

        if not update:
            value = self.filters[index]['function']
        self.update_filter_function(index, value)

    def _update_argument(self, index, values, argument, type_):
        '''TODO

        '''

        if argument in values:
            self.filters[index][argument] = values[argument]
        else:
            self.filters[index][argument] = '' if type_ == str else 0

    def update_filter_function(self, index, value):
        '''TODO

        '''

        self.values = self.filters[index]
        self.filters[index] = {'name': self.values['name'], 'function': value}
        branch = self.branches[self.filters[index]['name']]
        branch.takeChildren()
        function = filters.filtersList[self.filters[index]['function']]
        types = typing.get_type_hints(function)
        self._configure_leaf(branch, index, 'function')
        for argument in filter(lambda a: a != 'drivedata', types.keys()):
            type_ = types[argument]
            self._update_argument(index, self.values, argument, type_)
            self._configure_leaf(branch, index, argument)

    def get_collection(self):
        '''TODO

        '''

        return self.filters


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
        self.values = {}
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
        line_edit = WidgetFactory.line_edit(metric['name'], cb, border=False)
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
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.metrics[index][attribute] = value

    def _handle_update(self, index, value, update):
        '''TODO

        '''

        if not update:
            value = self.metrics[index]['function']
        self.update_metric_function(index, value)

    def _update_argument(self, index, values, argument, type_):
        '''TODO

        '''

        if argument in values:
            self.metrics[index][argument] = values[argument]
        else:
            self.metrics[index][argument] = '' if type_ == str else 0

    def update_metric_function(self, index, value):
        '''TODO

        '''

        self.values.update(self.metrics[index])
        self.metrics[index] = {'name': self.values['name'], 'function': value}
        branch = self.branches[self.metrics[index]['name']]
        branch.takeChildren()
        function = metrics.metricsList[self.metrics[index]['function']]
        types = typing.get_type_hints(function)
        self._configure_leaf(branch, index, 'function')
        for argument in filter(lambda a: a != 'drivedata', types.keys()):
            type_ = types[argument]
            self._update_argument(index, self.values, argument, type_)
            self._configure_leaf(branch, index, argument)

    def get_collection(self):
        '''TODO

        '''

        return self.metrics

    def expand(self):
        '''TODO

        '''

        print('test')
        self.expandToDepth(1)


class ProjectTree(QTreeWidget):
    '''Custom tree widget for displaying and editing project files.

    '''

    def __init__(self, project_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.project_file = project_file
        self.items_ = json.load(open(self.project_file))
        self.items_copy = copy.deepcopy(self.items_)
        self.trees = {
            'rois': lambda r, c: RoisTree(r, c),
            'filters': lambda r, c: FiltersTree(r, c),
            'metrics': lambda r, c: MetricsTree(r, c)
        }
        self.subtrees = {}
        self.roi_counter = 1
        self.filter_counter = 1
        self.metric_counter = 1
        self._configure_settings()
        self._configure_widget()

    def _configure_widget(self):
        '''TODO

        '''

        for collection in sorted(self.items_copy):
            tree = self.trees[collection](self, self.items_copy[collection])
            self.subtrees[collection] = tree
        self.expandToDepth(0)

    def _configure_settings(self):
        '''TODO

        '''

        # style_path = config.get('Stylesheets', 'projectTree')
        # style_path = os.path.join(GUI_PATH, style_path)
        # stylesheet = open(style_path).read()
        # self.setStyleSheet(stylesheet)
        self.setAnimated(True)
        self.setHeaderHidden(True)

    def get_contents(self):
        '''TODO

        '''

        self.update_contents()
        return self.items_

    def update_contents(self):
        '''TODO

        '''

        self.items_ = self.items_copy

    def changed(self):
        '''TODO

        '''

        if self.items_copy != self.items_:
            return True
        return False

    def add_roi(self):
        '''TODO

        '''

        self.clear()
        new_roi = {
            'type': f'new_roi_{self.roi_counter}',
            'filename': 'roi_file'
        }
        self.roi_counter += 1
        if 'rois' not in self.items_copy:
            self.items_copy['rois'] = [new_roi]
        else:
            self.items_copy['rois'].append(new_roi)
        self._configure_widget()
        # rois_tree = self.subtrees['rois']

    def add_filter(self, filter=None, new_index=-1):
        '''TODO

        '''

        self.clear()
        new_filter = filter if filter else {
            'name': f'new_filter_{self.filter_counter}',
            'function': list(filters.filtersList.keys())[0]
        }
        self.filter_counter += 1
        if 'filters' not in self.items_copy:
            self.items_copy['filters'] = [new_filter]
        else:
            self.items_copy['filters'].insert(new_index, new_filter)
        self._configure_widget()
        index = len(self.items_copy['filters']) - 1
        value = new_filter['function']
        filters_tree = self.subtrees['filters']
        filters_tree.update_filter_function(index, value)
        self.setItemSelected(self.itemAt(0, 0).child(new_index), True)

    def add_metric(self):
        '''TODO

        '''

        new_metric = {
            'name': f'new_metric_{self.metric_counter}',
            'function': list(metrics.metricsList.keys())[0]
        }
        self.metric_counter += 1
        if 'metrics' not in self.items_copy:
            self.items_copy['metrics'] = [new_metric]
        else:
            self.items_copy['metrics'].append(new_metric)
        self.clear()
        self._configure_widget()
        index = len(self.items_copy['metrics']) - 1
        value = new_metric['function']
        metrics_tree = self.subtrees['metrics']
        metrics_tree.update_metric_function(index, value)

    def remove_selected(self):
        '''TODO

        '''

        for item in self.selectedItems():
            item_widget = self.itemWidget(item, 0)
            if not item_widget:
                del self.items_copy[item.text(0)]
            elif type(item_widget) == QLineEdit:
                parent = item.parent().text(0)
                name = item_widget.text()
                if 'name' in self.items_copy[parent][0].keys():
                    self.items_copy[parent] = [
                        i for i in self.items_copy[parent] if i['name'] != name
                    ]
                else:
                    self.items_copy[parent] = [
                        i for i in self.items_copy[parent] if i['type'] != name
                    ]
                if len(self.items_copy[parent]) == 0:
                    del self.items_copy[parent]
        self.clear()
        self._configure_widget()

    def move_selected_up(self):
        '''TODO

        '''

        index = self.indexFromItem(self.selectedItems()[0]).row()
        filter = self.items_copy['filters'][index]
        self.remove_selected()
        self.add_filter(filter, index - 1)

    def move_selected_down(self):
        '''TODO
        
        '''

        index = self.indexFromItem(self.selectedItems()[0]).row()
        filter = self.items_copy['filters'][index]
        self.remove_selected()
        self.add_filter(filter, index + 1)
