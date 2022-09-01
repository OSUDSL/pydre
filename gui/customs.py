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
        if tree.setup():
            ...

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

        :return: True if the configuration was successful; False otherwise
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
        if tree.setup():
            ...

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

        :return: True if the configuration was successful; False otherwise
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
        if tree.setup():
            ...

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

        :return: True if the configuration was successful; False otherwise
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
    '''Configurable tree widget for displaying and editing project files.

    Usage:
        tree = ProjectTree(<project file path>)
        if tree.setup():
            ...

    :param project_file: Path to the project file used to construct this tree
    '''

    # def __init__(self, project_file, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     self.project_file = project_file
    #     self.items_ = json.load(open(self.project_file))
    #     self.items_copy = copy.deepcopy(self.items_)
    #     self.trees = {
    #         'rois': lambda r, c: RoisTree(r, c),
    #         'filters': lambda r, c: FiltersTree(r, c),
    #         'metrics': lambda r, c: MetricsTree(r, c)
    #     }
    #     self.add_item = {
    #         'rois': lambda r, i, e: self.add_roi(r, i, expand=e),
    #         'filters': lambda f, i, e: self.add_filter(f, i, expand=e),
    #         'metrics': lambda m, i, e: self.add_metric(m, i, expand=e)
    #     }
    #     self.subtrees = {}
    #     self.roi_counter = 1
    #     self.filter_counter = 1
    #     self.metric_counter = 1

    # def configure_widget(self):
    #     '''TODO

    #     '''

    #     self.setHeaderHidden(True)
    #     self.setAnimated(False)
    #     for collection in sorted(self.items_copy):
    #         tree = self.trees[collection](self, self.items_copy[collection])
    #         if tree.setup() is False:
    #             return False
    #         self.subtrees[collection] = tree
    #     self.expandToDepth(0)
    #     return True

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
        self.counters = {
            'rois': 1,
            'filters': 1,
            'metrics': 1
        }
        self.subtrees = {}

    def setup(self):
        '''Configures the project tree.

        :return: True if the configuration was successful; False otherwise
        '''

        self.setHeaderHidden(True)
        self.setAnimated(False)
        self.clear()
        for collection in sorted(self.items1):
            tree = self.trees[collection](self, self.items1[collection])
            if tree.setup() is False:
                return False
            self.subtrees[collection] = tree
        self.expandToDepth(0)
        return True

    def update(self):
        '''Updates the current collection of project items with any recent
        changes.
        '''

        self.items0.update(self.items1)

    def updated(self):
        '''Reports whether the current collection of project items is up to date
        with recent changes.
        '''

        return self.items0 == self.items1

    def get_items(self, update=True):
        '''Reports the current collection of project items after optionally 
        updating it with recent changes.

        :param update: True if the collection should be updated; False otherwise
        '''

        if update:
            self.update()
        return self.items0

    def get_expanded(self, depth=2):
        '''Reports the currently expanded item branches up to the given depth.
        
        :param depth: Item branch expansion depth (optional)
        :return: Collection of currently expanded item branches
        '''

        expanded = []
        for i in range(depth):
            for idx in range(self.topLevelItem(i).childCount()):
                if self.topLevelItem(i).child(idx).isExpanded():
                    expanded.append([i, idx])
        return expanded

    def set_expanded(self, items):
        '''Sets the given item branches to be expanded.
        
        :param items: Collection of item branches to be expanded
        '''

        for item in items:
            self.topLevelItem(item[0]).child(item[1]).setExpanded(True)

    def add_item(self, collection, item):
        '''Adds the given item to the specified collection, creating that
        collection if it doesn't exist already.

        :param collection: Collection identifier (rois, filters, or metrics)
        :param item: Item to be added as a new branch
        :return: Index of the new item branch
        '''

        self.counters[collection] += 1
        if collection in self.items1:
            idx = len(self.items1[collection])
            self.items1[collection].insert(idx, item)
        else:
            idx = 0
            self.items1[collection] = [item]
        self.setItemSelected(self.topLevelItem(0).child(idx), True)
        self.setup()
        return idx

    def add_roi(self, item=None):
        '''Adds a new roi item to the project tree, creating a generic roi if an
        item dictionary is not provided.
        
        :param item: Roi item to be added as a new branch (optional)
        '''

        expanded = self.get_expanded()
        item = item if item is not None else {
            'type': f'new_roi_{self.counters["rois"]}',
            'filename': f'<roi_file>'}
        self.add_item('rois', item)
        self.set_expanded(expanded)

    def add_filter(self, item=None):
        '''Adds a new filter item to the project tree, creating a generic filter
        if an item dictionary is not provided.
        
        :param item: Filter item to be added as a new branch (optional)
        '''

        expanded = self.get_expanded()
        item = item if item is not None else {
            'name': f'new_filter_{self.counters["filters"]}',
            'function': list(filters.filtersList.keys())[0]
        }
        idx = self.add_item('filters', item)
        new_func = item['function']
        self.subtrees['filters'].update_func(idx, new_func)
        self.set_expanded(expanded)

    def add_metric(self, item=None):
        '''Adds a new filter item to the project tree, creating a generic metric
        if an item dictionary is not provided.
        
        :param item: Metric item to be added as a new branch (optional)
        '''

        expanded = self.get_expanded()
        item = item if item is not None else {
            'name': f'new_metric_{self.counters["metrics"]}',
            'function': list(metrics.metricsList.keys())[0]
        }
        idx = self.add_item('metrics', item)
        new_func = item['function']
        self.subtrees['metrics'].update_func(idx, new_func)
        self.set_expanded(expanded)

    def del_item(self, item):
        '''Removes the given item branch from the project tree.
        
        :param item: Item to be deleted
        '''

        parent = item.parent().text(0)
        key = 'name' if 'name' in self.items1[parent][0].keys() else 'type'
        val = self.itemWidget(item, 0).text()
        self.items1[parent] = [i for i in self.items1[parent] if i[key] != val]
        if len(self.items1[parent]) == 0:
            del self.items1[parent]
        self.setup()

    def del_items(self, items=None):
        '''Removes a collection of item branches from the project tree, using
        the currently selected items if no collection is provided.
        
        :param item: Items to be deleted (optional)
        '''

        expanded = self.get_expanded()
        items = items if items is not None else self.selectedItems()
        for item in items:
            item_widget = self.itemWidget(item, 0)
            if item_widget is None:
                del self.items1[item.text(0)]
            elif type(item_widget) == QLineEdit:
                self.del_item(item)
        self.setup()
        self.set_expanded(expanded)

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
