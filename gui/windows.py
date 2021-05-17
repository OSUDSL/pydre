'''
Created by: Craig Fouts
Created on: 11/13/2020
'''

import inspect
import json
import logging
import os
import pydre
from gui.config import Config
from gui.customs import ProjectTree
from gui.popups import SavePopup
from gui.templates import Window
from PySide2.QtWidgets import QFileDialog

config = Config()
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_PATH, 'config_files/config.ini')
config.read(CONFIG_PATH)

logger = logging.getLogger('PydreLogger')


class MainWindow(Window):
    '''Primary window class that handles all tasks related to the main window
    configurations and functionality.

    '''

    def __init__(self, *args, **kwargs):
        ui_path = config.get('UI Files', 'main')
        ui_path = os.path.join(PROJECT_PATH, ui_path)
        super().__init__(ui_path, *args, **kwargs)

        self.project_files = {}
        self.save_popup = SavePopup()
        self._configure_window()

    def _configure_window(self):
        '''Configures initial window settings.

        '''

        self._configure_callbacks()
        self._configure_splitters()
        self._configure_recent()
        self.ui.menu_bar.setVisible(False)

    def _configure_callbacks(self):
        '''Configures callback functionality for actions and widgets.

        '''

        self.ui.open_act.triggered.connect(self._handle_open_pfile)
        self.ui.save_act.triggered.connect(self._handle_save)
        self.ui.run_act.triggered.connect(self._handle_run_act)
        self.ui.recent_lst.itemDoubleClicked.connect(self._handle_select_pfile)
        self.ui.data_lst.itemSelectionChanged.connect(self._toggle_remove_btn)
        self.ui.data_lst.model().rowsInserted.connect(self._toggle_run_btn)
        self.ui.data_lst.model().rowsRemoved.connect(self._toggle_run_btn)
        self.ui.open_pfile_btn.clicked.connect(self._handle_open_pfile)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)
        self.ui.add_btn.clicked.connect(self._handle_add_dfile)
        self.ui.remove_btn.clicked.connect(self._handle_remove_dfile)
        self.ui.file_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.file_tab.tabCloseRequested.connect(self._handle_tab_close)

    def _configure_splitters(self):
        '''Configures the initial stretch factors for splitter widgets.

        '''

        self.ui.start_hsplitter.setStretchFactor(0, 4)
        self.ui.start_hsplitter.setStretchFactor(1, 7)
        self.ui.main_hsplitter.setStretchFactor(0, 2)
        self.ui.main_hsplitter.setStretchFactor(1, 7)
        self.ui.main_vsplitter.setStretchFactor(0, 7)
        self.ui.main_vsplitter.setStretchFactor(1, 2)

    def _configure_recent(self):
        '''Configures the recent files list displayed on the start page.

        '''

        self.ui.recent_lst.clear()
        recent_names = config.get('Recent Files', 'names').split(',')
        for file in filter(lambda f: f != '', recent_names):
            self.ui.recent_lst.addItem(file)

    def _handle_select_pfile(self):
        '''Handles selecting a file from the recent files list.

        '''

        directory = os.path.dirname(PROJECT_PATH)
        recent_paths = config.get('Recent Files', 'paths').split(',')
        index = self.ui.recent_lst.currentRow()
        file_path = os.path.join(directory, recent_paths[index])
        self._launch_editor(file_path) if file_path else None

    def _handle_open_pfile(self):
        '''Handles opening a project file in a new tab.

        '''

        file_type = config.get('File Types', 'project')
        file_path = self._open_file(file_type)
        self._launch_editor(file_path) if file_path else None

    def _open_file(self, filter=None):  # TODO: MOVE TO UTILITY CLASS
        '''Launches a file selection dialog based on the given file type and
        returns a file path if one is selected.

        '''

        title = "Open File"
        directory = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))
        path_, _ = QFileDialog.getOpenFileName(self, title, directory, filter)
        return os.path.abspath(path_) if path_ else None

    def _open_files(self, filter=None):  # TODO: MOVE TO UTILITY CLASS
        '''Launches a file selection dialog based on the given file type and
        returns a list of file paths if one or more is selected.

        '''

        title = "Open File"
        directory = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))
        paths, _ = QFileDialog.getOpenFileNames(self, title, directory, filter)
        return [os.path.abspath(path_) for path_ in paths]

    def _launch_editor(self, file_path):
        '''Configures and shows a file editor in a new tab.

        '''

        file_name = file_path.split(os.sep)[-1]
        self._add_to_recent(file_name, file_path)
        if file_name not in self.project_files:
            project_tree = self._create_project_tree(file_name, file_path)
            self.project_files[file_name] = [file_path, project_tree]
        else:
            index = self.ui.file_tab.indexOf(file_name)
            self.ui.file_tab.setCurrentIndex(index)
        self.switch_to_editor()

    def _add_to_recent(self, file_name, file_path):
        '''Adds the given project file name and path to the recent files lists
        in the configuration file.

        '''

        relative_path = os.path.join(*file_path.split(os.sep)[-2:])
        recent_names = config.get('Recent Files', 'names').split(',')
        recent_paths = config.get('Recent Files', 'paths').split(',')
        if file_name in recent_names:
            recent_names.remove(file_name)
            recent_paths.remove(relative_path)
        recent_names.insert(0, file_name)
        recent_paths.insert(0, relative_path)
        config.set('Recent Files', 'names', ','.join(recent_names))
        config.set('Recent Files', 'paths', ','.join(recent_paths))

    def _create_project_tree(self, file_name, file_path):
        '''Creates and displays a FileTree widget for the given file.

        '''

        project_tree = ProjectTree(file_path)
        index = self.ui.file_tab.count()
        self.ui.file_tab.insertTab(index, project_tree, file_name)
        self.ui.file_tab.setCurrentIndex(index)
        return project_tree

    def _handle_cancel(self):
        '''TODO

        '''

        self.ui.data_lst.clear()
        self.switch_to_editor()

    def _handle_add_dfile(self):
        '''TODO

        '''

        file_type = config.get('File Types', 'data')
        file_paths = self._open_files(file_type)
        for path_ in file_paths:
            self.ui.data_lst.addItem(path_)

    def _handle_remove_dfile(self):
        '''TODO

        '''

        row = self.ui.data_lst.currentRow()
        self.ui.data_lst.takeItem(row)

    def _handle_save(self, index):
        '''TODO

        '''

        file_name = self.ui.file_tab.tabText(index)
        with open(self.project_files[file_name][0], 'w') as file:
            contents = self.ui.file_tab.currentWidget().get_contents()
            json.dump(contents, file, indent=4)

    def _handle_run_act(self):
        '''TODO

        '''

        index = self.ui.file_tab.currentIndex()
        pfile_name = self.ui.file_tab.tabText(index)
        pfile_path = self.project_files[pfile_name][0]
        self.ui.pfile_lbl.setText(pfile_path)
        self.switch_to_run()

    def _handle_tab_change(self, index):
        '''Handles functionality that occurs when a tab is opened, closed, or
        selected.

        '''

        if self.ui.file_tab.count() > 0:
            file_name = self.ui.file_tab.tabText(index)
            self.ui.run_act.setText(f"Run '{file_name}'")
        else:
            self.switch_to_start()

    def _handle_tab_close(self, index):
        '''TODO

        '''

        if self.ui.file_tab.currentWidget().changed():
            file_name = self.ui.file_tab.tabText(index)
            text = f"{file_name} " + config.get('Popup Text', 'save')
            def callback(e): return self._handle_close(index, e)
            self.save_popup.show_(text, callback)
        else:
            self._handle_close(index, False)

    def _handle_close(self, index, save):
        '''TODO

        '''

        self._handle_save(index) if save else None
        self.project_files.pop(self.ui.file_tab.tabText(index))
        self.ui.file_tab.removeTab(index)

    def _toggle_remove_btn(self):
        '''TODO

        '''

        dfile_count = len(self.ui.data_lst.selectedItems())
        self.ui.remove_btn.setEnabled(True if dfile_count > 0 else False)

    def _toggle_run_btn(self):
        '''TODO

        '''

        dfile_count = self.ui.data_lst.count()
        self.ui.run_btn.setEnabled(True if dfile_count > 0 else False)

    def switch_to_start(self):
        '''Swithes to the start page (page 1 / 3).

        '''

        self.resize_and_center(700, 400)
        self.ui.menu_bar.setVisible(False)
        self._configure_recent_files()
        self.ui.page_stack.setCurrentIndex(0)

    def switch_to_editor(self):
        '''Switches to the editor page (page 2 / 3).

        '''

        self.resize_and_center(1100, 800)
        self.ui.menu_bar.setVisible(True)
        self.ui.page_stack.setCurrentIndex(1)

    def switch_to_run(self):
        '''Switches to the run page (page 3 / 3).

        '''

        self.resize_and_center(1100, 800)
        self.ui.menu_bar.setVisible(True)
        self.ui.page_stack.setCurrentIndex(2)
