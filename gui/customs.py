'''
Created by: Craig Fouts
Created on: 11/21/2020
'''

import copy
import json
from pyclbr import Function
from tkinter import Widget
import typing
from pydre import filters, metrics
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, \
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QWidget
from gui.config import CONFIG_PATH, WIDGET_STYLE_PATH, Config
from gui.popups import FunctionPopup

config = Config()
config.read(CONFIG_PATH)


class WidgetFactory:
    '''Static utility class used to generate configured widgets.
    
    Widgets:
        Combo Box
        Spin Box
        Line Edit
    '''

    @staticmethod
    def combo_box(cb, items, val=None, style=WIDGET_STYLE_PATH):
        '''Generates a configured Combo Box widget populated with the given
        items/optional initial value and linked to the given callback function.
        
        :param cb: Action callback function
        :param items: Combo Box item collection
        :param val: Initial input value (optional)
        :param style: Widget stylesheet path (optional)
        :return: A configured Combo Box widget
        '''

        widget = QComboBox()
        for item in items:
            widget.addItem(item)
        if val is not None:
            widget.setCurrentIndex(items.index(val))
        if style is not None:
            widget.setStyleSheet(open(style).read())
        widget.activated.connect(lambda i: cb(widget.itemText(i)))
        return widget

    @staticmethod
    def spin_box(cb, val=None, style=WIDGET_STYLE_PATH):
        '''Generates a configured Spin Box widget populated with the given
        optional initial value and linked to the given callback function.
        
        :param cb: Action callback function
        :param val: Initial input value (optional)
        :param style: Widget styleshet path (optional)
        :return: A configured Spin Box widget
        '''

        widget = QSpinBox()
        if val is not None:
            widget.setValue(val)
        if style is not None:
            widget.setStyleSheet(open(style).read())
        widget.valueChanged.connect(cb)
        return widget

    @staticmethod
    def line_edit(cb, val=None, style=WIDGET_STYLE_PATH):
        '''Generates a configured Line Edit widget populated with the given
        optional initial value and linked to the given callback funtion.
        
        :param cb: Action callback function
        :param val: Initial input value (optional)
        :param style: Widget stylesheet path (optional)
        :return: A configured Line Edit widget
        '''

        widget = QLineEdit()
        if val is not None:
            widget.setText(val)
        if style is not None:
            widget.setStyleSheet(open(style).read())
        widget.textChanged.connect(cb)
        return widget


class LeafWidget(QWidget):
    '''Configurable leaf widget for displaying and editing various types of 
    project file attributes.

    Widgets:
        Combo Box
        Spin Box
        Line Edit

    :param text: Inline descriptor label text
    '''

    def __init__(self, label, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel(label))

    def combo_box(self, cb, items, val=None, height=30):
        '''Generates a configured project tree leaf widget with a descriptor 
        label and inline Combo Box widget.

        :param cb: Action callback function
        :param items: Combo Box item collection
        :param val: Initial input value (optional)
        :param height: Widget height (optional)
        :return: A configured Combo Box leaf widget
        '''

        widget = WidgetFactory.combo_box(cb, items, val)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self

    def spin_box(self, cb, val=None, height=30):
        '''Generates a configured project tree leaf widget with a descriptor
        label and inline Spin Box widget.

        :param cb: Action callback function
        :param val: Initial input value (optional)
        :param height: Widget height (optional)
        :return: A configured Spin Box leaf widget
        '''

        widget = WidgetFactory.spin_box(cb, val)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self

    def line_edit(self, cb, val=None, height=30):
        '''Generates a configured project tree leaf widget with a descriptor
        label and inline Line Edit widget.

        :param cb: Action callback function
        :param val: Initial input value (optional)
        :param height: Widget height (optional)
        :return: A configured Line Edit leaf widget
        '''

        widget = WidgetFactory.line_edit(cb, val)
        widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        widget.setFixedHeight(height)
        self.layout.addWidget(widget)
        self.setLayout(self.layout)
        return self


class RoisTree(QTreeWidget):
    '''Configurable subtree widget for displaying and editing project rois.

    Usage:
        tree = RoisTree(<root tree>, <roi items>)

    :param root: Parent in which to embed this subtree
    :param items: Collection of roi items
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['rois'])
        self.branches = {}

    def setup(self):
        '''Configures the rois subtree.
        '''

        for idx in range(len(self.items)):
            if self.setup_branch(idx) is False:
                return False
        return True

    def setup_branch(self, idx):
        '''Configures the item branch at the given index.

        :param idx: Index of the item branch
        :return: True if the configuration was successful; False otherwise
        '''

        branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(e): return self.update(idx, 'type', e)
        line_edit = WidgetFactory.line_edit(cb, item['type'], style=None)
        for key in filter(lambda i: i != 'type', item):
            if self.setup_leaf(branch, idx, key) is False:
                return False
        self.root.setItemWidget(branch, 0, line_edit)
        self.branches[item['type']] = branch
        return True

    def setup_leaf(self, branch, idx, key):
        '''Configures the specified attribute leaf embedded in the item branch
        at the given index.

        :param branch: Parent branch in which to embed this leaf
        :param idx: Index of the parent branch
        :param key: Key of the roi attribute
        :return: True if the configuration was successful; False otherwise
        '''

        try:
            leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            def cb(e): return self.update(idx, key, e)
            line_edit = LeafWidget(key).line_edit(cb, item[key])
            self.root.setItemWidget(leaf, 0, line_edit)
        except KeyError:
            return False
        return True

    def update(self, idx, key, val):
        '''Updates the specified attribute leaf embedded in the item branch at 
        the given index.

        :param idx: Index of the item branch
        :param key: Key of the roi attribute
        :param val: New attribute value
        '''

        self.items[idx][key] = val

    def add_item(self, item):
        '''TODO
        '''

        print(item)


class FiltersTree(QTreeWidget):
    '''Configurable subtree widget for displaying and editing project filters.

    Usage:
        tree = FiltersTree(<root tree>, <filter items>)

    :param root: Parent in which to embed this subtree
    :param items: Collection of filter items
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['filters'])
        combo_items = list(filters.filtersList.keys())
        self.widgets = {
            None: lambda t, c, v: LeafWidget(t).combo_box(c, combo_items, v),
            float: lambda t, c, v: LeafWidget(t).spin_box(c, v),
            str: lambda t, c, v: LeafWidget(t).line_edit(c, v)
        }
        self.branches, self.values = {}, {}

    def setup(self):
        '''Configures the filters subtree.
        '''

        for idx in range(len(self.items)):
            if self.setup_branch(idx) is False:
                return False
        return True

    def setup_branch(self, idx):
        '''Configures the item branch at the given index.

        :param idx: Index of the item branch
        :return: True if the configuration was successful; False otherwise
        '''

        branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(e): return self.update(idx, 'name', e)
        line_edit = WidgetFactory.line_edit(cb, item['name'], style=None)
        for key in filter(lambda i: i != 'name', item):
            if self.setup_leaf(branch, idx, key) is False:
                return False
        self.root.setItemWidget(branch, 0, line_edit)
        self.branches[item['name']] = branch
        return True

    def setup_leaf(self, branch, idx, key):
        '''Configures the specified attribute leaf embedded in the item branch 
        at the given index.

        :param branch: Parent branch in which to embed this leaf
        :param idx: Index of the parent branch
        :param key: Key of the filter attribute
        :return: True if the configuration was successful; False otherwise
        '''

        try:
            leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            func = filters.filtersList[item['function']]
            types = typing.get_type_hints(func)
            type_ = types[key] if key != 'function' else None
            def cb(e): return self.update(idx, key, e)
            widget = self.widgets[type_](key, cb, item[key])
            self.root.setItemWidget(leaf, 0, widget)
        except KeyError:
            return False
        return True

    def update(self, idx, key, val):
        '''Updates the specified attribute leaf embedded in the item branch at
        the given index.
        
        :param idx: Index of the item branch
        :param key: Key of the filter attribute
        :param val: New attribute value
        '''

        if key == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self.handle_func_update(idx, val, e)
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.items[idx][key] = val

    def handle_func_update(self, idx, val, update=True):
        '''Handles updates to the filter function attribute embedded in the item
        branch at the given index emitted by popups acting on the filters 
        subtree.
        
        :param idx: Index of the item branch
        :param val: New function attribute value
        :param update: True if the update should be performed; False otherwise
        '''

        if update is False:
            val = self.items[idx]['function']
        self.update_func(idx, val)

    def update_func(self, idx, val):
        '''Updates the filter function attribute embedded in the item branch at 
        the given index.
        
        :param idx: Index of the item branch
        :param val: New function attribute value
        '''

        self.values.update(self.items[idx])
        self.items[idx] = {'name': self.values['name'], 'function': val}
        branch = self.branches[self.values['name']]
        branch.takeChildren()
        new_func = filters.filtersList[self.items[idx]['function']]
        types = typing.get_type_hints(new_func)
        self.setup_leaf(branch, idx, 'function')
        for key in filter(lambda i: i != 'drivedata', types.keys()):
            self.update_arg(idx, key, self.values, types[key])

    def update_arg(self, idx, key, vals, type_):
        '''Updates the filter argument attribute for the function embedded in 
        the item branch at the given index.

        :param idx: Index of the item branch
        :param key: Key of the filter argument attribute
        :param val: New attribute value
        :param type_: Type of the filter argument
        '''

        if key in vals:
            self.items[idx][key] = vals[key]
        else:
            self.items[idx][key] = '' if type_ == str else 0
        branch = self.branches[self.items[idx]['name']]
        self.setup_leaf(branch, idx, key)


class MetricsTree(QTreeWidget):
    '''Configurable subtree widget for displaying and editing project metrics.

    Usage:
        tree = MetricsTree(<root tree>, <metric items>)

    :param root: Parent in which to embed this subtree
    :param items: Collection of filter items
    '''

    def __init__(self, root, items, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.root = root
        self.items = items
        self.tree = QTreeWidgetItem(self.root, ['metrics'])
        combo_items = list(metrics.metricsList.keys())
        self.widgets= {
            None: lambda t, c, v: LeafWidget(t).combo_box(c, combo_items, v),
            float: lambda t, c, v: LeafWidget(t).spin_box(c, v),
            str: lambda t, c, v: LeafWidget(t).line_edit(c, v)
        }
        self.branches, self.values = {}, {}

    def setup(self):
        '''Configures the metrics subtree.
        '''

        for index in range(len(self.items)):
            if self.setup_branch(index) is False:
                return False
        return True

    def setup_branch(self, idx):
        '''Configures the item branch at the given index.
        
        :param idx: Index of the item branch
        :return: True if the configuration was successful; False otherwise
        '''

        branch = QTreeWidgetItem(self.tree)
        item = self.items[idx]
        def cb(e): return self.update(idx, 'name', e)
        line_edit = WidgetFactory.line_edit(cb, item['name'], style=None)
        for key in filter(lambda i: i != 'name', item):
            if self.setup_leaf(branch, idx, key) is False:
                return False
        self.root.setItemWidget(branch, 0, line_edit)
        self.branches[item['name']] = branch
        return True

    def setup_leaf(self, branch, idx, key):
        '''Configures the specified attribute leaf embedded in the item branch
        at the given index.
        
        :param branch: Parent branch in which to embed this leaf
        :param idx: Index of the parent branch
        :param key: Key of the filter attribute
        :return: True if the configuration was successful; False otherwise
        '''

        try:
            leaf = QTreeWidgetItem(branch)
            item = self.items[idx]
            func = metrics.metricsList[item['function']]
            types = typing.get_type_hints(func)
            type_ = types[key] if key != 'function' else None
            def cb(e): return self.update(idx, key, e)
            widget = self.widgets[type_](key, cb, item[key])
            self.root.setItemWidget(leaf, 0, widget)
        except KeyError:
            return False
        return True

    def update(self, idx, key, val):
        '''Updates the specified attribute leaf embedded in the item branch at
        the given index.
        
        :param idx: Index of the item branch
        :param key: Key of the filter attribute
        :param val: New attrbute value
        '''

        if key == 'function':
            text = config.get('Popup Text', 'function')
            def cb(e): return self.handle_func_update(idx, val, e)
            FunctionPopup(parent=self).show_(text, cb)
        else:
            self.items[idx][key] = val

    def handle_func_update(self, idx, val, update=True):
        '''Handles updates to the metric function attribute embedded in the item
        branch at the given index emitted by popups acting on the filters
        subtree.
        
        :param idx: Index of the item branch
        :param val: New function attribute value
        :param update: True if the update should be performed; False otherwise
        '''

        if update is False:
            val = self.items[idx]['function']
        self.update_func(idx, val)

    def update_func(self, idx, val):
        '''Updates the metric function attribute embedded in the item branch at
        the given index.
        
        :param idx: Index of the item branch
        :param val: New function attribute value
        '''

        self.values.update(self.items[idx])
        self.items[idx] = {'name': self.values['name'], 'function': val}
        branch = self.branches[self.values['name']]
        branch.takeChildren()
        new_func = metrics.metricsList[self.items[idx]['function']]
        types = typing.get_type_hints(new_func)
        self.setup_leaf(branch, idx, 'function')
        for key in filter(lambda i: i != 'drivedata', types.keys()):
            self.update_arg(idx, key, self.values, types[key])

    def update_arg(self, idx, key, vals, type_):
        '''Updates the metric argument attribute for the function embedded in
        the item branch at the given index.
        
        :param idx: Index of the item branch
        :param key: Key of the metric argument attribute
        :param val: New attribute value
        :param type_: Type of the metric argument
        '''

        if key in vals:
            self.items[idx][key] = vals[key]
        else:
            self.items[idx][key] = '' if type_ == str else 0
        branch = self.branches[self.items[idx]['name']]
        self.setup_leaf(branch, idx, key)


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
        self.add_item = {
            'rois': lambda r, i, e: self.add_roi(r, i, expand=e),
            'filters': lambda f, i, e: self.add_filter(f, i, expand=e),
            'metrics': lambda m, i, e: self.add_metric(m, i, expand=e)
        }
        self.subtrees = {}
        self.roi_counter = 1
        self.filter_counter = 1
        self.metric_counter = 1

    def configure_widget(self):
        '''TODO

        '''

        self.setHeaderHidden(True)
        self.setAnimated(False)
        for collection in sorted(self.items_copy):
            tree = self.trees[collection](self, self.items_copy[collection])
            if tree.setup() is False:
                return False
            self.subtrees[collection] = tree
        self.expandToDepth(0)
        return True

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

    def add_filter(self, filter=None, index=-1, expand=[]):
        '''TODO

        '''

        for i in range(3):
            for idx in range(self.topLevelItem(i).childCount()):
                if self.topLevelItem(i).child(idx).isExpanded():
                    expand.append([i, idx])

        index = len(self.items_copy['filters']) if index == -1 else index
        self.clear()
        new_filter = filter if filter else {
            'name': f'new_filter_{self.filter_counter}',
            'function': list(filters.filtersList.keys())[0]
        }
        self.filter_counter += 1
        if 'filters' not in self.items_copy:
            self.items_copy['filters'] = [new_filter]
        else:
            self.items_copy['filters'].insert(index, new_filter)
        self._configure_widget()
        value = new_filter['function']
        filters_tree = self.subtrees['filters']
        filters_tree.update_func(index, value)
        count = self.topLevelItem(0).childCount()
        self.setItemSelected(self.topLevelItem(0).child(index % count), True)

        for item in expand:
            self.topLevelItem(item[0]).child(item[1]).setExpanded(True)

    def add_metric(self, metric=None, index=-1, expand=[]):
        '''TODO

        '''

        for i in range(3):
            for idx in range(self.topLevelItem(i).childCount()):
                if self.topLevelItem(i).child(idx).isExpanded():
                    expand.append([i, idx])

        index = len(self.items_copy['metrics']) if index == -1 else index
        new_metric = metric if metric else {
            'name': f'new_metric_{self.metric_counter}',
            'function': list(metrics.metricsList.keys())[0]
        }
        self.metric_counter += 1
        if 'metrics' not in self.items_copy:
            self.items_copy['metrics'] = [new_metric]
        else:
            self.items_copy['metrics'].insert(index, new_metric)
        self.clear()
        self._configure_widget()
        value = new_metric['function']
        metrics_tree = self.subtrees['metrics']
        metrics_tree.update_metric_function(index, value)
        self.setItemSelected(self.topLevelItem(1).child(index), True)

        for item in expand:
            self.topLevelItem(item[0]).child(item[1]).setExpanded(True)

    def add_roi(self, roi=None, index=-1, expand=[]):
        '''TODO

        '''

        for i in range(3):
            for idx in range(self.topLevelItem(i).childCount()):
                if self.topLevelItem(i).child(idx).isExpanded():
                    expand.append([i, idx])

        index = len(self.items_copy['rois']) if index == -1 else index
        self.clear()
        new_roi = roi if roi else {
            'type': f'new_roi_{self.roi_counter}',
            'filename': 'roi_file'
        }
        self.roi_counter += 1
        if 'rois' not in self.items_copy:
            self.items_copy['rois'] = [new_roi]
        else:
            self.items_copy['rois'].insert(index, new_roi)
        self._configure_widget()
        self.setItemSelected(self.topLevelItem(2).child(index), True)

        for item in expand:
            self.topLevelItem(item[0]).child(item[1]).setExpanded(True)

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
        sub_tree = self.selectedItems()[-1].parent()
        sub_tree_text = sub_tree.text(0)

        if sub_tree_text == 'filters':
            i = 0
        elif sub_tree_text == 'metrics':
            i = 1
        else:
            i = 2
        expanded = []
        for idx in range(sub_tree.childCount()):
            if sub_tree.child(idx).isExpanded():
                expanded.append([i, idx])

        item = self.items_copy[sub_tree_text][index]
        if index > 0:
            if sub_tree.child(index).isExpanded():
                if not sub_tree.child(index - 1).isExpanded():
                    expanded.remove([i, index])
                expanded.append([i, index - 1])
            self.remove_selected()
            self.add_item[sub_tree_text](item, index - 1, expanded)

    def move_selected_down(self):
        '''TODO

        '''

        index = self.indexFromItem(self.selectedItems()[0]).row()
        sub_tree = self.selectedItems()[-1].parent()
        sub_tree_text = sub_tree.text(0)

        if sub_tree_text == 'filters':
            i = 0
        elif sub_tree_text == 'metrics':
            i = 1
        else:
            i = 2
        expanded = []
        for idx in range(sub_tree.childCount()):
            if sub_tree.child(idx).isExpanded():
                expanded.append([i, idx])

        item = self.items_copy[sub_tree_text][index]
        if index < sub_tree.childCount() - 1:
            if sub_tree.child(index).isExpanded():
                if not sub_tree.child(index + 1).isExpanded():
                    expanded.remove([i, index])
                expanded.append([i, index + 1])
            self.remove_selected()
            self.add_item[sub_tree_text](item, index + 1, expanded)
