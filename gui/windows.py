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
from gui.handlers import Pydre
from gui.popups import OutputPopup, SavePopup
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

        self.save_popup = SavePopup()
        self.output_popup = OutputPopup()
        self.project_files = {}
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

        self._configure_action_callbacks()
        self._configure_widget_callbacks()
        self._configure_button_callbacks()

    def _configure_action_callbacks(self):
        '''TODO

        '''

        self.ui.open_act.triggered.connect(self._handle_open_pfile)
        self.ui.save_act.triggered.connect(self._handle_save)
        self.ui.run_act.triggered.connect(self._handle_run_act)

    def _configure_widget_callbacks(self):
        '''TODO

        '''

        self.ui.recent_lst.itemDoubleClicked.connect(self._handle_select_pfile)
        self.ui.pfile_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self._handle_tab_close)
        self.ui.data_lst.itemSelectionChanged.connect(self._toggle_remove_btn)
        self.ui.data_lst.model().rowsInserted.connect(self._toggle_run_btn)
        self.ui.data_lst.model().rowsRemoved.connect(self._toggle_run_btn)

    def _configure_button_callbacks(self):
        '''TODO

        '''

        self.ui.open_pfile_btn.clicked.connect(self._handle_open_pfile)
        self.ui.add_btn.clicked.connect(self._handle_add_dfile)
        self.ui.remove_btn.clicked.connect(self._handle_remove_dfile)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)
        self.ui.run_btn.clicked.connect(self._handle_run_click)

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
        recent_pfiles = config.get('Recent Files', 'paths').split(',')
        for path_ in filter(lambda f: f != '', recent_pfiles):
            _, name = os.path.split(path_)
            self.ui.recent_lst.addItem(name)

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

        pfile_type = config.get('File Types', 'project')
        pfile_path = self._open_file(pfile_type)
        self._launch_editor(pfile_path) if pfile_path else None

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

    def _launch_editor(self, pfile_path):
        '''Configures and shows a file editor in a new tab.

        '''

        pfile_name = pfile_path.split(os.sep)[-1]
        self._add_to_recent(pfile_path)
        if pfile_name not in self.project_files:
            project_tree = self._create_project_tree(pfile_name, pfile_path)
            self.project_files[pfile_name] = [pfile_path, project_tree]
        else:
            index = self.ui.file_tab.indexOf(pfile_name)
            self.ui.file_tab.setCurrentIndex(index)
        self.switch_to_editor()

    def _add_to_recent(self, pfile_path):
        '''Adds the given project file name and path to the recent files lists
        in the configuration file.

        '''

        relative_path = os.path.join(*pfile_path.split(os.sep)[-2:])
        recent = config.get('Recent Files', 'paths').split(',')
        recent.remove(relative_path) if relative_path in recent else None
        recent.insert(0, relative_path)
        config.set('Recent Files', 'paths', ','.join(recent))
        config.update()

    def _create_project_tree(self, pfile_name, pfile_path):
        '''Creates and displays a FileTree widget for the given file.

        '''

        project_tree = ProjectTree(pfile_path)
        index = self.ui.pfile_tab.count()
        self.ui.pfile_tab.insertTab(index, project_tree, pfile_name)
        self.ui.pfile_tab.setCurrentIndex(index)
        return project_tree

    def _handle_add_dfile(self):
        '''TODO

        '''

        dfile_type = config.get('File Types', 'data')
        dfile_paths = self._open_files(dfile_type)
        for path_ in dfile_paths:
            self.ui.data_lst.addItem(path_)

    def _handle_remove_dfile(self):
        '''TODO

        '''

        row = self.ui.data_lst.currentRow()
        self.ui.data_lst.takeItem(row)

    def _handle_save(self, index):
        '''TODO

        '''

        pfile_name = self.ui.pfile_tab.tabText(index)
        with open(self.project_files[pfile_name][0], 'w') as pfile:
            contents = self.ui.pfile_tab.currentWidget().get_contents()
            json.dump(contents, pfile, indent=4)

    def _handle_run_act(self):
        '''TODO

        '''

        index = self.ui.pfile_tab.currentIndex()
        pfile_name = self.ui.pfile_tab.tabText(index)
        pfile_path = self.project_files[pfile_name][0]
        self.ui.pfile_lbl.setText(pfile_path)
        self.switch_to_run()

    def _handle_tab_change(self, index):
        '''Handles functionality that occurs when a tab is opened, closed, or
        selected.

        '''

        if self.ui.pfile_tab.count() > 0:
            pfile_name = self.ui.pfile_tab.tabText(index)
            self.ui.run_act.setText(f"Run '{pfile_name}'")
        else:
            self.switch_to_start()

    def _handle_tab_close(self, index):
        '''TODO

        '''

        if self.ui.pfile_tab.currentWidget().changed():
            pfile_name = self.ui.pfile_tab.tabText(index)
            text = f"{pfile_name} " + config.get('Popup Text', 'save')
            def callback(e): return self._handle_close(index, e)
            self.save_popup.show_(text, callback)
        else:
            self._handle_close(index, False)

    def _handle_close(self, index, save):
        '''TODO

        '''

        self._handle_save(index) if save else None
        self.project_files.pop(self.ui.pfile_tab.tabText(index))
        self.ui.pfile_tab.removeTab(index)

    def _handle_cancel(self):
        '''TODO

        '''

        self.ui.data_lst.clear()
        self._toggle_run_btn()
        self.switch_to_editor()

    def _handle_run_click(self):
        '''TODO

        '''

        if self.ui.ofile_inp.text().strip():
            self._handle_run()
        else:
            text = config.get('Popup Text', 'output')
            def callback(e): return self._handle_run() if e else None
            self.output_popup.show_(text, callback)

    def _handle_run(self):
        '''TODO

        '''

        project_file = self.ui.pfile_lbl.text()
        count = self.ui.data_lst.count()
        data_files = [self.ui.data_lst.item(i).text() for i in range(count)]
        output_file = self.ui.ofile_inp.displayText()
        Pydre.run(project_file, data_files, output_file)

    def _toggle_remove_btn(self):
        '''TODO

        '''

        count = len(self.ui.data_lst.selectedItems())
        self.ui.remove_btn.setEnabled(True if count > 0 else False)

    def _toggle_run_btn(self):
        '''TODO

        '''

        count = self.ui.data_lst.count()
        self.ui.run_btn.setEnabled(True if count > 0 else False)

    def switch_to_start(self):
        '''Swithes to the start page (page 1 / 3).

        '''

        self.resize_and_center(700, 400)
        self.ui.menu_bar.setVisible(False)
        self._configure_recent()
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
