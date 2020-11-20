# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

import inspect
from functools import partial
from gui.handlers import Pydre
from gui.popups import ProjectFilePopup
from gui.templates import Window
from gui.ui_files.ui_mainwindow import Ui_MainWindow
import logging
from os import path, sep
import pydre
from PySide2.QtWidgets import QFileDialog

logger = logging.getLogger("PydreLogger")


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self):
        super().__init__(Ui_MainWindow, "images/icon.png", "Pydre")

        # Initial window configurations
        self.ui.splitter.setStretchFactor(0, 2)
        self.ui.splitter.setStretchFactor(1, 3)

        # Button callbacks
        self.ui.open_file_btn.clicked.connect(
            partial(self._open_pfile, "JSON (*.json)"))

        # Tab widget callbacks
        self.ui.pfile_tab.tabCloseRequested.connect(
            lambda index: self._close_tab(index))

    def _build_tree(self):
        """
        TODO
        """

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
        if pfile_path:
            pfile_name = pfile_path.split("/")[-1]
            self._launch_editor(pfile_name)

    def _launch_editor(self, pfile_name):
        """
        TODO
        """

        self.ui.pfile_tab.setTabText(0, pfile_name)
        self.ui.page_stack.setCurrentIndex(1)

    def _close_tab(self, index):
        """
        TODO
        """

        self.ui.pfile_tab.removeTab(index)

        if self.ui.pfile_tab.count() == 0:
            self.ui.page_stack.setCurrentIndex(0)
