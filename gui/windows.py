# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from configparser import ConfigParser
import inspect
from functools import partial
from gui.customs import ProjectTree
from gui.templates import Window
from gui.ui_files.ui_mainwindow import Ui_MainWindow
from json import loads
import logging
from os import path
import pydre
from PySide2.QtWidgets import QFileDialog

config = ConfigParser()
config.read("./config_files/config.ini")
logger = logging.getLogger("PydreLogger")


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self, icon_file, title, *args, **kwargs):
        super().__init__(icon_file, title, Ui_MainWindow, *args, **kwargs)

        # Config variables
        self.hstretch_factors = loads(config.get("geometry", "hstretch"))
        self.vstretch_factors = loads(config.get("geometry", "vstretch"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.pfile_paths = {}
        self.focused_pfile = ""

        # Application configurations
        self._configure_hsplitters()
        self._configure_vsplitters()
        self._configure_shortcuts()
        self._configure_callbacks()

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_hsplitters(self):
        """
        Configures horizontal splitters based on config file settings
        """

        hsplitter_count = self.ui.hsplitter.count()
        for i in range(hsplitter_count):
            stretch_factor = self.hstretch_factors[i]
            self.ui.hsplitter.setStretchFactor(i, stretch_factor)

    def _configure_vsplitters(self):
        """
        Configures vertical splitters based on config file settings
        """

        vsplitter_count = self.ui.vsplitter.count()
        for i in range(vsplitter_count):
            stretch_factor = self.vstretch_factors[i]
            self.ui.vsplitter.setStretchFactor(i, stretch_factor)

    def _configure_shortcuts(self):
        """
        Configures keyboard shortcuts for widgets events
        """

        # Menu bar action shortcuts
        self.ui.new_action.setShortcut("Ctrl+N")
        self.ui.open_action.setShortcut("Ctrl+O")

    def _configure_callbacks(self):
        """
        Configures callback functionality for widget events
        """

        # Menu bar action callbacks
        self.ui.new_action.triggered.connect(
            partial(print, "DEBUG: New..."))  # FIXME
        self.ui.open_action.triggered.connect(self._handle_open)
        self.ui.run_action.triggered.connect(self._handle_run)

        # Button callbacks
        self.ui.open_pfile_btn.clicked.connect(self._handle_open)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)

        # Tab widget callbacks
        self.ui.pfile_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self._handle_close)

    # ==========================================================================
    # Handler methods ----------------------------------------------------------
    # ==========================================================================

    def _handle_open(self):
        """
        TODO
        """

        # Launch the file explorer for the project file type
        path_ = self._open_file(self.file_types["project"])

        # Launch the project file editor if a project file is selected
        if path_:
            self._launch_pfile_editor(pfile_path=path_)
            self._resize_and_center(width=1100, height=768)

    def _handle_close(self, index):
        """
        TODO
        """

        # Delete the tab at the specified index
        self.ui.pfile_tab.removeTab(index)

        # Handle remaining tabs
        self._handle_tab_change(index)

    def _handle_tab_change(self, index):
        """
        TODO
        """

        if self.ui.pfile_tab.count() > 0:
            # Set run action text based on the current tab
            pfile_name = self.ui.pfile_tab.tabText(index)
            self.ui.run_action.setText("Run '{0}'".format(pfile_name))

            # Set focussed project file based on the current tab
            self.focused_pfile = self.pfile_paths[pfile_name]
        else:
            self.ui.page_stack.setCurrentIndex(0)
            self._resize_and_center(width=500, height=268)

    def _handle_run(self):
        """
        TODO
        """

        # Set the project file label based on the project file being run
        pfile = self.focused_pfile
        self.ui.pfile_label.setText("Project file: '{0}'".format(pfile))

        # Switch to run page
        self.ui.page_stack.setCurrentIndex(2)

    def _handle_cancel(self):
        """
        TODO
        """

        # Switch to editor page
        self.ui.page_stack.setCurrentIndex(1)

    # ==========================================================================
    # Reference methods --------------------------------------------------------
    # ==========================================================================

    def _open_file(self, file_type=None):
        """
        Launches a file selection dialog based on the given file type and
        returns the file path if one is selected

        args:
            file_type: Optional file type of the desired file

        returns: Path of the selected file or None if no file is selected
        """

        # Target directory for file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get tuple of file path and filter
        file = QFileDialog.getOpenFileName(self, "Add file", dir_, file_type)

        return file[0]

    def _launch_pfile_editor(self, pfile_path):
        """
        Configures and shows the project file editor in a new tab

        args:
            pfile_path: Project file path
        """

        # Create new tab for the selected project file
        tab = self.ui.pfile_tab.count()
        pfile_tree = ProjectTree(animated=True)
        pfile_name = pfile_path.split("/")[-1]
        self.pfile_paths[pfile_name] = pfile_path
        self.ui.pfile_tab.insertTab(tab, pfile_tree, pfile_name)

        # Build and display the project file editor
        self.ui.run_action.setText("Run '{0}'".format(pfile_name))
        pfile_tree.build_from_file(path=pfile_path)
        self.ui.page_stack.setCurrentIndex(1)
        self.ui.pfile_tab.setCurrentIndex(tab)
