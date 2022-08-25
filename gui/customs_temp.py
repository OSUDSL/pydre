'''
Created by Craig Fouts
Created on: 11/21/2020
'''

import copy
import json
import re
from tkinter import Widget
import typing
from gui.popups import FunctionPopup
from pydre import filters, metrics
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, \
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QWidget
from gui.config import Config, CONFIG_PATH

config = Config()
config.read(CONFIG_PATH)


class WidgetFactory:
    '''Static utility class used to generate common inline widgets.
    
    Widgets:
        Combo Box
        Spin Box
        Line Edit
    '''

    @staticmethod
    def combo_box(val, cb, items):
        '''TODO
        
        :param val:
        :param cb:
        :param items:
        :return:
        '''

        widget = QComboBox()
        for item in items:
            widget.addItem(item)
        widget.setCurrentIndex(items.index(val))
        widget.activated.connect(lambda i: cb(widget.itemText(i)))
        return widget

    @staticmethod
    def spin_box(val, cb):
        '''TODO
        
        :param val:
        :param cb:
        :return:
        '''

        widget = QSpinBox()
        widget.setValue(val)
        widget.valueChanged.connect(cb)
        return widget

    @staticmethod
    def line_edit(val, cb):
        '''TODO
        
        :param val:
        :param cb:
        :return:
        '''

        widget = QLineEdit()
        widget.setText(val)
        widget.textChanged.connect(cb)
        return widget


class LeafWidget(QWidget):
    '''TODO
    
    Widgets:
        Combo Box
        Spin Box
        Line Edit
    '''

    def __init__(self, text, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(text))

    def combo_box(self, val, cb, items, height=30):
        '''TODO
        
        :param val:
        :param cb:
        :param items:
        :param height:
        :return:
        '''

        widget = WidgetFactory.combo_box(val, cb, items)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self

    def spin_box(self, val, cb, height=30):
        '''TODO
        
        :param val:
        :param cb:
        :param height:
        :return:
        '''

        widget = WidgetFactory.spin_box(val, cb)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self

    def line_edit(self, val, cb, height=30):
        '''TODO
        
        :param val:
        :param cb:
        :param height:
        :return:
        '''

        widget = WidgetFactory.line_edit(val, cb)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self


class RoisTree(QTreeWidget):
    '''TODO

    :param root:
    :param items:
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['rois'])
        self.branches = {}

    def update(self, idx, key, val):
        '''TODO
        
        :param idx:
        :param key:
        :param val:
        '''

        self.items[idx][key] = val

    def setup(self):
        '''TODO
        '''

        for idx in range(len(self.items)):
            if not self.setup_branch(idx):
                return False
        return True

    def setup_leaf(self, branch, idx, key):
        '''TODO
        
        :param branch:
        :param idx:
        :param key:
        :return:
        '''

        try:
            new_leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            def cb(val): return self.update(idx, key, val)
            line_edit = LeafWidget(key).line_edit(item[key], cb)
            self.root.setItemWidget(new_leaf, 0, line_edit)
        except KeyError:
            return False
        return True

    def setup_branch(self, idx):
        '''TODO
        
        :param idx:
        '''

        new_branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(val): return self.update(idx, 'type', val)
        line_edit = WidgetFactory.line_edit(item['type'], cb)
        for key in filter(lambda k: k != 'type', item):
            if self.setup_leaf(new_branch, idx, key) is False:
                return False
        self.root.setItemWidget(new_branch, 0, line_edit)
        self.branches[item['type']] = new_branch
        return True


class FiltersTree(QTreeWidget):
    '''TODO

    :param root:
    :param items:
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['filters'])
        self.branches = {}
        combo_items = list(filters.filtersList.keys())
        self.widgets = {
            None: lambda t, v, c: LeafWidget(t).combo_box(v, c, combo_items),
            float: lambda t, v, c: LeafWidget(t).spin_box(v, c),
            str: lambda t, v, c: LeafWidget(t).line_edit(v, c)
        }

    def update_func(self, idx, val):
        '''TODO
        
        :param idx:
        :param val:
        '''

        name = self.items[idx]['name']
        self.items[idx] = {'name': name, 'function': val}
        branch = self.branches[name]
        branch.takeChildren()
        new_func = filters.filtersList[self.items[idx]['function']]
        types = typing.get_type_hints(new_func)
        self.setup_leaf(branch, idx, 'function')
        for key in filter(lambda k: k != 'drivedata', types.keys()):
            self.update_item(idx, key)

    def update_item(self, idx, key, val, type_):
        '''TODO
        
        :param idx:
        :param key:
        :param val:
        :param type_:
        '''

        if key in self.items[idx]:
            self.items[idx][key] = val
        else:
            self.items[idx][key] = '' if type_ == str else 0
        name = self.items[idx]['name']
        branch = self.branches[name]
        self.setup_leaf(branch, idx, key)

    def handle_update(self, idx, val, update=True):
        '''TODO
        
        :param idx:
        :param val:
        :param update:
        '''

        if update is False:
            val = self.items[idx]['function']
        self.update_func(idx, val)

    def update(self, idx, key, val):
        '''TODO
        
        :param idx:
        :param key:
        :param val:
        '''

        if key == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self.handle_update(idx, val, e)
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.items[idx][key] = val

    def setup_leaf(self, branch, idx, key):
        '''TODO
        
        :param branch:
        :param idx:
        :param key:
        :return:
        '''

        try:
            new_leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            func = filters.filtersList[item['function']]
            types = typing.get_type_hints(func)
            type_ = types[key] if key != 'function' else None
            def cb(e): return self.update(idx, key, e)
            widget = self.widgets[type_](key, item[key], cb)
            self.root.setItemWidget(new_leaf, 0, widget)
        except KeyError:
            return False
        return True

    def setup_branch(self, idx):
        '''TODO
        
        :param idx:
        :return:
        '''

        new_branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(e): return self.update(idx, 'name', e)
        line_edit = WidgetFactory.line_edit(item['name'], cb)
        for key in filter(lambda k: k != 'name', item):
            if self.setup_leaf(new_branch, idx, key) is False:
                return False
        self.root.setItemWidget(new_branch, 0, line_edit)
        self.branches[item['name']] = new_branch
        return True

    def setup(self):
        '''TODO
        '''

        for idx in range(len(self.items)):
            if self.setup_branch(idx) is False:
                return False
        return True

class MetricsTree(QTreeWidget):
    '''TODO
    
    :param root:
    :param items:
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['metrics'])
        self.branches = {}
        combo_items = list(metrics.metricsList.keys())
        self.widgets = {
            None: lambda t, v, c: LeafWidget(t).combo_box(v, c, combo_items),
            float: lambda t, v, c: LeafWidget(t).spin_box(v, c),
            str: lambda t, v, c: LeafWidget(t).line_edit(v, c)
        }

    def update_func(self, idx, val):
        '''TODO
        
        :param idx:
        :param val:
        '''

        name = self.items[idx]['name']
        self.items[idx] = {'name': name, 'function': val}
        branch = self.branches[name]
        branch.takeChildren()
        new_func = metrics.metricsList[self.items[idx]['function']]
        types = typing.get_type_hints(new_func)
        self.setup_leaf(branch, idx, 'function')
        for key in filter(lambda k: k != 'drivedata', types.keys()):
            self.update_item(idx, key)

    def update_item(self, idx, key, val, type_):
        '''TODO
        
        :param idx:
        :param key:
        :param val:
        :param type_:
        '''

        if key in self.items[idx]:
            self.items[idx][key] = val
        else:
            self.items[idx][key] = '' if type_ == str else 0
        name = self.items[idx]['name']
        branch = self.branches[name]
        self.setup_leaf(branch, idx, key)

    def handle_update(self, idx, val, update=True):
        '''TODO
        
        :param idx:
        :param val:
        :param update:
        '''

        if update is False:
            val = self.items[idx]['function']
        self.update_func(idx, val)

    def update(self, idx, key, val):
        '''TODO
        
        :param idx:
        :param key:
        :param val:
        '''

        if key == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self.handle_update(idx, val, e)
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.items[idx][key] = val

    def setup_leaf(self, branch, idx, key):
        '''TODO
        
        :param branch:
        :param idx:
        :param key:
        :return:
        '''

        try:
            new_leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            func = metrics.metricsList[item['function']]
            types = typing.get_type_hints(func)
            type_ = types[key] if key != 'function' else None
            def cb(e): return self.update(idx, key, e)
            widget = self.widgets[type_](key, item[key], cb)
            self.root.setItemWidget(new_leaf, 0, widget)
        except KeyError as e:
            return False
        return True

    def setup_branch(self, idx):
        '''TODO
        
        :param idx:
        :return:
        '''

        new_branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(e): return self.update(idx, 'name', e)
        line_edit = WidgetFactory.line_edit(item['name'], cb)
        for key in filter(lambda k: k != 'name', item):
            if self.setup_leaf(new_branch, 0, key) is False:
                return False
        self.root.setItemWidget(new_branch, 0, line_edit)
        self.branches[item['name']] = new_branch
        return True

    def setup(self):
        '''TODO
        '''

        for idx in range(len(self.items)):
            if self.setup_branch(idx) is False:
                return False
        return True


class ProjectTree(QTreeWidget):
    '''TODO
    '''

    def __init__(self, project_file, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.project_file = project_file
        self.items0 = json.load(open(self.project_file))
        self.items1 = copy.deepcopy(self.items0)
        self.trees = {
            'rois': lambda r, c: RoisTree(r, c),
            'filters': lambda r, c: FiltersTree(r, c),
            'metrics': lambda r, c: MetricsTree(r, c)
        }
        self.subtrees = {}
        # self.add_item = {
        #     'rois': lambda r, i, e: self.add_roi
        # }
        self.counters = {
            'rois': 0,
            'filters': 0,
            'metrics': 0
        }

    def update(self):
        '''TODO
        '''

        self.items0 = self.items1

    def updated(self):
        '''TODO

        :return:
        '''

        return self.items0 == self.items1

    def setup(self):
        '''Convenience method for configuring default widget settings.
        '''

        self.setHeaderHidden(True)
        self.setAnimated(False)
        self.clear()
        for collection in sorted(self.items1):
            tree = self.trees[collection](self, self.items1[collection])
            if not tree.setup():
                return False
            self.subtrees[collection] = tree
            self.counters[collection] += 1
        self.expandToDepth(0)
        return True

    def get_items(self):
        '''TODO

        :return:
        '''

        self.update(self)
        return self.items0

    def get_expanded(self, depth=1):
        '''TODO
        
        :param depth:
        :return:
        '''

        expanded = []
        for i in range(depth):
            for idx in range(self.topLevelItem(i).childCount()):
                if self.topLevelItem(i).child(idx).isExpanded():
                    expanded.append([i, idx])
        return expanded

    def set_expanded(self, items):
        '''TODO
        
        :param items:
        '''

        for item in items:
            self.topLevelItem(item[0]).child(item[1]).setExpanded(True)

    def _add_item(self, item, collection):
        '''TODO
        
        :param item:
        :param collection:
        :return:
        '''

        if collection not in self.items1:
            idx = 0
            self.items1[collection] = [item]
        else:
            idx = len(self.items1[collection])
            self.items1[collection].insert(idx, item)
        self.setItemSelected(self.topLevelItem(0).child(idx), True)
        self.counters[collection] += 1
        return idx

    def _del_item(self, item):
        '''TODO
        
        :param item:
        '''

        parent = item.parent().text(0)
        key = 'name' if 'name' in self.items1[parent][0].keys() else 'type'
        val = self.itemWidget(item, 0).text()
        self.items1[parent] = [i for i in self.items1[parent] if i[key] != val]
        if len(self.items1[parent]) == 0:
            del self.items1[parent]

    def add_roi(self, roi=None):
        '''TODO

        :param roi:
        '''

        expanded = self.get_expanded()
        self.clear()
        new_roi = roi if roi is not None else {
            'type': f'new_roi_{self.counters["rois"]}',
            'filename': 'roi_file'
        }
        self._add_item(new_roi, 'rois')
        self.set_expanded(expanded)

    def add_filter(self, filter=None):
        '''TODO
        
        :param filter:
        '''

        expanded = self.get_expanded()
        new_filter = filter if filter is not None else {
            'name': f'new_filter_{self.counters["filters"]}',
            'function': list(filters.filtersList.keys())[0]
        }
        idx = self._add_item(new_filter, 'filters')
        new_function = new_filter['function']
        self.items1['filters'].update_func(idx, new_function)
        self.setup()
        self.set_expanded(expanded)

    def add_metric(self, metric=None):
        '''TODO
        
        :param metric:
        '''

        expanded =self.get_expanded()
        self.clear()
        new_metric = metric if metric is not None else {
            'name': f'new_metric_{self.counters["metrics"]}',
            'function': list(metrics.metricsList.keys())[0]
        }
        idx = self._add_item(new_metric, 'metrics')
        new_function = new_metric['function']
        self.items1['metrics'].update_func(idx, new_function)
        self.setup()
        self.set_expanded(expanded)

    def del_items(self, items=None):
        '''TODO

        :param items:
        '''

        if items is None:
            items = self.selectedItems()
        for item in items:
            item_widget = self.itemWidget(item, 0)
            if item_widget is None:
                del self.items1[item.text(0)]
            elif type(item_widget) == QLineEdit:
                self._del_item(item)
        self.setup()
