'''
Created by: Craig Fouts
Created on: 11/13/2020
'''

import inspect
import json
import logging
import os
import pydre
from PySide2.QtWidgets import QFileDialog, QInputDialog
from pydre.gui.config import Config, config_filename, PROJECT_PATH
from pydre.gui.customs import ProjectTree
from pydre.gui.handlers import Pydre
from pydre.gui.popups import ErrorPopup, OutputPopup, ProgressPopup, SavePopup
from pydre.gui.templates import Window

config = Config()
config.read(config_filename)
logger = logging.getLogger(__file__)

class MainWindow(Window):
    '''Primary window class responsible for handling all tasks related to GUI
    layout and functionality.

    Usage:
        app = QApplication()
        window = MainWindow(app)
        window.start()
    
    :param app: Parent application object responsible for launching the GUI
    '''

    def __init__(self, app, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__('main', *args, **kwargs)
        self.app = app
        self.files = {}
        self.setup()
        self.to_start()

    
    def setup(self):
        '''Configures initial window settings.
        '''

        self.setup_callbacks()
        self.setup_splitters()
        self.setup_recent()

    def setup_callbacks(self):
        '''Configures callback functionality for actions and widgets.
        '''

        self.setup_actions()
        self.setup_widgets()
        self.setup_buttons()

    def setup_actions(self):
        '''Configures action callback functionality.
        '''

        self.ui.openAct.triggered.connect(self.handle_open)
        self.ui.newAct.triggered.connect(self.handle_new)
        self.ui.saveAct.triggered.connect(self.handle_save)
        self.ui.saveasAct.triggered.connect(self.handle_saveas)
        self.ui.runAct.triggered.connect(self.handle_to_run)

    def setup_widgets(self):
        '''Configures widget callback functionality.
        '''

        self.ui.pfile_tab.currentChanged.connect(self.handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self.handle_tab_close)
        self.ui.recent_lst.itemDoubleClicked.connect(self.handle_select)
        self.ui.data_lst.itemSelectionChanged.connect(self.toggle_remove)
        self.ui.data_lst.model().rowsInserted.connect(self.toggle_run)
        self.ui.data_lst.model().rowsRemoved.connect(self.toggle_run)

    def setup_buttons(self):
        '''Configures button callback functionality.
        '''

        self.ui.open_pfile_btn.clicked.connect(self.handle_open)
        self.ui.new_pfile_btn.clicked.connect(self.handle_new)
        self.ui.new_roi_btn.clicked.connect(self.handle_add_roi)
        self.ui.new_filter_btn.clicked.connect(self.handle_add_filter)
        self.ui.new_metric_btn.clicked.connect(self.handle_add_metric)
        self.ui.remove_item_btn.clicked.connect(self.handle_remove_item)
        self.ui.move_up_btn.clicked.connect(self.handle_up)
        self.ui.move_down_btn.clicked.connect(self.handle_down)
        self.ui.add_dfile_btn.clicked.connect(self.handle_add_dfile)
        self.ui.remove_dfile_btn.clicked.connect(self.handle_remove_dfile)
        self.ui.cancel_btn.clicked.connect(self.handle_cancel)
        self.ui.run_btn.clicked.connect(self.handle_run)

    def setup_splitters(self):
        '''Configures the initial stretch factors for splitter widgets.
        '''

        self.ui.start_hsplitter.setStretchFactor(0, 5)
        self.ui.start_hsplitter.setStretchFactor(1, 7)
        self.ui.main_hsplitter.setStretchFactor(0, 2)
        self.ui.main_hsplitter.setStretchFactor(1, 7)
        self.ui.main_vsplitter.setStretchFactor(0, 7)
        self.ui.main_vsplitter.setStretchFactor(1, 2)
        self.ui.run_vsplitter.setStretchFactor(0, 4)
        self.ui.run_vsplitter.setStretchFactor(1, 1)

    def setup_recent(self):
        '''Configures the recent files list displayed on the start page.
        '''

        self.ui.recent_lst.clear()
        files = config.get('Recent Files', 'paths').split(',')
        for file in filter(lambda i: i != '', files):
            self.ui.recent_lst.addItem(os.path.split(file)[1])

    def handle_open(self):
        '''Handles opening a project file in a new tab.
        '''

        file = self.open_file(config.get('File Types', 'project'))
        if file:
            self.start_editor(file)

    def handle_new(self):
        '''Handles creating and opening a new project file in a new tab.
        '''

        name, ok = QInputDialog.getText(self, 'Pydre', 'File name')
        if ok:
            file = os.path.join(PROJECT_PATH, 'project_files', f'{name}.json')
            with open(file, 'w') as f:
                f.write('{}')
            self.start_editor(file)
        
    def handle_save(self, idx=None):
        '''Handles saving changes made to the project tab at the given index,
        using the current index if no index is given.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        with open(self.files[name][0], 'w') as file:
            self.ui.pfile_tab.currentWidget().update()
            contents = self.ui.pfile_tab.currentWidget().items0
            json.dump(contents, file, indent=4)

    def handle_saveas(self, idx=None):
        '''Handles saving changes made to the project tab as a new filename

        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)

        fileName = QFileDialog.getOpenFileName(self,
                                               "Save project file as...", "", "project files (*.json)")

        with open(fileName, 'w') as file:
            self.ui.pfile_tab.currentWidget().update()
            contents = self.ui.pfile_tab.currentWidget().items0
            json.dump(contents, file, indent=4)

    def handle_to_run(self, idx):
        '''Handles passing the project tab at the given index to the run page,
        using the current index if no index is given.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.curentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.ui.pfile_lbl.setText(self.files[name][0])
        self.to_run()

    def handle_tab_change(self, idx=None):
        '''Handles activity that occurs when the project tab at the given index 
        is opened, closed, or selected.
        
        :param idx: Project tab index (optional)
        '''

        if idx is not None and self.ui.pfile_tab.count() > 0:
            name = self.ui.pfile_tab.tabText(idx)
            self.ui.runAct.setText(f'Run \'{name}\'')
        else:
            self.to_start()

    def handle_tab_close(self, idx):
        '''Handles activity that occurs upon a project tab close request at the
        given index.
        
        :param idx: Project tab index
        '''

        if self.ui.pfile_tab.widget(idx).updated():
            name = self.ui.pfile_tab.tabText(idx)
            text = f'{name} {config.get("Popup Text", "save")}'
            def cb(e): return self.del_tab(idx, e)
            SavePopup(parent=self).show_(text, cb)
        else:
            self.del_tab(idx, False)

    def handle_select(self):
        '''Handles opening a selected project file from the recent files list.
        '''

        recents = config.get('Recent Files', 'paths').split(',')
        idx = self.ui.recent_lst.currentRow()
        file = recents[idx]
        if file:
            self.start_editor(file)

    def handle_add_roi(self, idx=None):
        '''Handles creating and adding a new roi to the project tree at the 
        given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].add_roi()

    def handle_add_filter(self, idx=None):
        '''Handles creating and adding a new filter to the project tree at the
        given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].add_filter()

    def handle_add_metric(self, idx=None):
        '''Handles creating and adding a new metric to the project tree at the
        given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].add_metric()

    def handle_remove_item(self, idx=None):
        '''Handles removing the currently selected items in the project tree at
        the given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].del_items()

    def handle_up(self, idx=None):
        '''Handles moving the currently selected items up from the project tree 
        at the given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].move_up()

    def handle_down(self, idx=None):
        '''Handles moving the currently selected items down in the project tree 
        at the given index, using the current index if no index is provided.
        
        :param idx: Project tab index (optional)
        '''

        idx = idx if idx is not None else self.ui.pfile_tab.currentIndex()
        name = self.ui.pfile_tab.tabText(idx)
        self.files[name][1].move_down()

    def handle_add_dfile(self):
        '''Handles getting and adding one or more data files to the data list 
        using a file selection dialog.
        '''

        type_ = config.get('File Types', 'data')
        files = self.open_files(type_)
        if files is not None:
            for file in files:
                self.ui.data_lst.addItem(file)

    def handle_remove_dfile(self):
        '''Handles removing the currently selected data files from the data
        list.
        '''

        idx = self.ui.data_lst.currentRow()
        self.ui.data_lst.takeItem(idx)

    def handle_cancel(self):
        '''Handles terminating the current run setup and switching back to the 
        editor page.
        '''

        self.ui.data_lst.clear()
        self.toggle_run()
        self.to_editor()

    def handle_run(self):
        '''Handles running pydre with the current project and data file
        configuration as defined in the GUI.
        '''

        if self.ui.ofile_inp.text().strip():
            self.run_pydre()
        else:
            text = config.get('Popup Text', 'output')
            def cb(e): return self.run_pydre() if e else None
            OutputPopup(parent=self).show_(text, cb)

    def start_editor(self, file):
        '''Configures and initiates a project tree editor for the given project 
        file in a new tab.
        
        :param file: Project file from which to build the project tree
        '''

        name = file.split(os.sep)[-1]
        self.add_recent(file)
        if name in self.files:
            idx = self.ui.file_tab.indexOf(name)
            self.ui.file_tab.setCurrentIndex(idx)
        else:
            tree = self.create_tree(file)
            if tree is None:
                self.handle_tab_change()
                ErrorPopup(parent=self).show_('Failed to build project tree.')
                return
            self.files[name] = [file, tree]
        self.to_editor()

    def create_tree(self, file):
        '''Creates and configures a new project tree widget for the given 
        project file.
        
        :param file: Project file from which to build the project tree
        :return: A configured project tree widget
        '''

        tree = ProjectTree(file)
        if tree.setup():
            idx = self.ui.pfile_tab.count()
            self.ui.pfile_tab.insertTab(idx, tree, file.split(os.sep)[-1])
            self.ui.pfile_tab.setCurrentIndex(idx)
            return tree
        return None
            
    def add_recent(self, file):
        '''Adds the name and path of the given project file to the current
        collection of recent files stored in the configuration file.
        
        :param file: Project file to add to the recent files list
        '''

        file = os.path.join(*file.split(os.sep)[-2:])
        recent = config.get('Recent Files', 'paths').split(',')
        if file in recent:
            recent.remove(file)
        recent.insert(0, file)
        config.set('Recent Files', 'paths', ','.join(recent))
        config.update()

    def del_tab(self, idx, save=True):
        '''Removes the project tab at the given index, prompting to save the 
        corresponding project file if changes were made to the project tree.
        
        :param idx: Project tab index
        :param save: True if the project file should be saved; False otherwise
        '''

        if save:
            self.handle_save(idx)
        self.files.pop(self.ui.pfile_tab.tabText(idx))
        self.ui.pfile_tab.removeTab(idx)

    def toggle_remove(self):
        '''Toggles the "Remove" button widget based on the number of currently
        selected data items.
        '''

        count = len(self.ui.data_lst.selectedItems())
        self.ui.remove_btn.setEnabled(True if count > 0 else False)

    def toggle_run(self):
        '''Toggles the "Run" action widget based on the number of data items.
        '''

        count = self.ui.data_lst.count()
        self.ui.run_btn.setEnabled(True if count > 0 else False)

    def to_start(self):
        '''Switches the GUI to the start page (page 1 of 3).
        '''

        width, height = self.screen_width / 3., self.screen_height / 2.5
        self.resize_and_center(width, height)
        self.ui.menu_bar.setVisible(False)
        self.setup_recent()
        self.ui.page_stack.setCurrentIndex(0)

    def to_editor(self):
        '''Switches the GUI to the editor page (page 2 of 3).
        '''
        width, height = self.screen_width / 2.5, self.screen_height / 2.
        self.resize_and_center(width, height)
        self.ui.menu_bar.setVisible(True)
        self.ui.page_stack.setCurrentIndex(1)

    def to_run(self):
        '''Switches the GUI to the run page (page 3 of 3).
        '''

        width, height = self.screen_width / 2.5, self.screen_height / 2.
        self.resize_and_center(width, height)
        self.ui.menu_bar.setVisible(True)
        self.ui.page_stack.setCurrentIndex(2)

    def open_file(self, filter=None):
        '''Launches a file selection dialog based on the given file type filter
        and returns a file path if one is selected.
        
        :param filter: File type filter (optional)
        :return: File path if one is selected; None otherwise
        '''

        dir = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))
        file = QFileDialog.getOpenFileName(self, 'Open File', dir, filter)[0]
        return os.path.abspath(file) if file else None

    def open_files(self, filter=None):
        '''Launches a file selection dialog based on the given file type filter
        and returns a collection of file paths if one or more are selected.
        
        :param filter: File type filter (optional)
        :return: Collection of file paths if any are selected; None otherwise
        '''

        dir = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))
        files = QFileDialog.getOpenFileNames(self, 'Open File', dir, filter)[0]
        return [os.path.abspath(file) for file in files] if files else None

    def add_to_log(self, entry):
        '''Adds the given entry to the GUI log list.
        
        :param entry: Item to be logged
        '''

        self.ui.log_lst.addItem(entry)
        self.ui.log_lst.scrollToBottom()

    def run_pydre(self):
        '''Runs pydre with the current project and data file configuration 
        as defined in the GUI.
        '''

        text = config.get('Popup Text', 'progress')
        file = self.ui.pfile_lbl.text()
        count = self.ui.data_lst.count()
        data = [self.ui.data_lst.item(i).text() for i in range(count)]
        name = self.ui.ofile_inp.displayText()
        progress = ProgressPopup(self.app, parent=self).show_(text)
        Pydre.run(self.app, file, data, name, progress)
