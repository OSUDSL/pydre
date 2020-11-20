# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from configparser import ConfigParser
import inspect
from functools import partial
from gui.templates import Window
from gui.ui_files.ui_mainwindow import Ui_MainWindow
from json import load, loads
import logging
from os import path
import pydre
from PySide2.QtWidgets import QFileDialog, QTreeWidget, QTreeWidgetItem

config = ConfigParser()
config.read("./config_files/config.ini")
logger = logging.getLogger("PydreLogger")


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self):
        super().__init__(Ui_MainWindow, "images/icon.png", "Pydre")

        # Class variables
        self.param_types = dict(config.items("parameters"))

        # Initial window configurations
        self.ui.splitter.setStretchFactor(0, int(
            config.get("geometry", "stretch_factor_0")))
        self.ui.splitter.setStretchFactor(1, int(
            config.get("geometry", "stretch_factor_1")))

        # Menu bar action shortcuts
        self.ui.new_action.setShortcut("Ctrl+N")
        self.ui.open_action.setShortcut("Ctrl+O")

        # Menu bar action callbacks
        self.ui.new_action.triggered.connect(partial(print, "DEBUG: New..."))
        self.ui.open_action.triggered.connect(
            partial(self._open_pfile, "JSON (*.json)"))

        # Button callbacks
        self.ui.open_file_btn.clicked.connect(
            partial(self._open_pfile, "JSON (*.json)"))

        # Tab widget callbacks
        self.ui.pfile_tab.tabCloseRequested.connect(
            lambda index: self._close_tab(index))

    def _build_pfile_tree(self, pfile_tree, pfile_path):
        """
        TODO
        """

        # Load project file contents
        pfile_contents = load(open(pfile_path))

        # Set tree column title
        pfile_tree.setHeaderLabel("Project parameters")

        # Generate tree for each parameter type
        for i in pfile_contents:
            tree = QTreeWidgetItem(pfile_tree, [i])

            # Generate branch for the contents of each parameter type
            for index, j in enumerate(pfile_contents[i]):
                branch = QTreeWidgetItem(tree, [
                    '{0} {1}'.format(self.param_types[i], index + 1)])

                # Generate leaf for each parameter
                for k in j:
                    QTreeWidgetItem(branch, ['{0}: {1}'.format(k, j[k])])

    def _launch_editor(self, pfile_path):
        """
        TODO
        """

        # Get project file name from path
        pfile_name = pfile_path.split("/")[-1]

        # Create new tab for the selected project file
        pfile_tree = QTreeWidget()  # TODO: Create custom tree widget class
        pfile_tree.setAnimated(True)
        self.ui.pfile_tab.insertTab(self.ui.pfile_tab.count(), pfile_tree,
                                    pfile_name)

        # Build and display the project file editor
        self._build_pfile_tree(pfile_tree, pfile_path)
        self.ui.page_stack.setCurrentIndex(1)
        self.ui.pfile_tab.setCurrentIndex(self.ui.pfile_tab.count() - 1)

    def _open_pfile(self, file_type):
        """
        TODO
        """

        # Target directory for file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get project file path
        pfile_path, filter_ = QFileDialog.getOpenFileName(self, "Add file",
                                                          dir_, file_type)

        # Launch the project file editor if a project file is selected
        self._launch_editor(pfile_path) if pfile_path else None

    def _close_tab(self, index):
        """
        TODO
        """

        self.ui.pfile_tab.removeTab(index)

        if self.ui.pfile_tab.count() == 0:
            self.ui.page_stack.setCurrentIndex(0)
