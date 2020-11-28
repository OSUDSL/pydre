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
from PySide2.QtWidgets import QDesktopWidget, QFileDialog

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

        # Config variables
        self.stretch_factors = loads(config.get("geometry", "stretch_factors"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.pfile_paths = []
        self.focused_pfile = ""

        # Application configurations
        self._configure_widgets()
        self._configure_shortcuts()
        self._configure_callbacks()

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_geometry(self, width, height):
        """
        TODO
        """

        # Set window dimensions
        self.resize(width, height)

        # Center window on the screen
        frame = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(screen_center)
        self.move(frame.topLeft())

    def _configure_widgets(self):
        """
        Configures widgets based on config file settings
        """

        # Set horizontal splitter location based on config file
        splitter_count = self.ui.splitter.count()
        for i in range(splitter_count):
            stretch_factor = self.stretch_factors[i]
            self.ui.splitter.setStretchFactor(i, stretch_factor)

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
        self.ui.new_action.triggered.connect(partial(print, "DEBUG: New..."))
        self.ui.open_action.triggered.connect(self._handle_open)
        self.ui.run_action.triggered.connect(partial(self.ui.page_stack.setCurrentIndex, 2))  # FIXME

        # Button callbacks
        self.ui.open_pfile_btn.clicked.connect(self._handle_open)
        self.ui.cancel_btn.clicked.connect(partial(self.ui.page_stack.setCurrentIndex, 1))  # FIXME

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
        pfile_path = self._open_file(self.file_types["project"])

        # Launch the project file editor if a project file is selected
        if pfile_path:
            self._launch_pfile_editor(pfile_path)
            self._configure_geometry(1100, 768)

    def _handle_close(self, index):
        """
        TODO
        """

        # Delete the tab at the specified index
        self.ui.pfile_tab.removeTab(index)

        # Switch to initial open page if no tabs remain
        if self.ui.pfile_tab.count() == 0:
            self.ui.page_stack.setCurrentIndex(0)
            self._configure_geometry(500, 268)

    def _handle_run(self):
        """
        TODO
        """

    

    def _handle_tab_change(self, index):
        """
        TODO
        """

        # Set run action text based on the current project file tab
        pfile_name = self.ui.pfile_tab.tabText(index)
        self.ui.run_action.setText("Run '{0}'".format(pfile_name))

        self.ui.run_box.setTitle("Project file: '{0}'".format(pfile_name))  # FIXME: Move to appropriate method

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

        # Add project file path to currently open project files
        self.pfile_paths.append(file[0])

        return file[0]

    def _launch_pfile_editor(self, pfile_path):
        """
        Configures and shows the project file editor in a new tab

        args:
            pfile_path: Project file path
        """

        # Create new tab for the selected project file
        tab = self.ui.pfile_tab.count()
        pfile_tree = ProjectTree()
        pfile_name = pfile_path.split("/")[-1]
        self.ui.pfile_tab.insertTab(tab, pfile_tree, pfile_name)

        # Build and display the project file editor
        self.ui.run_action.setText("Run '{0}'".format(pfile_name))
        pfile_tree.build_from_file(pfile_path)
        self.ui.page_stack.setCurrentIndex(1)
        self.ui.pfile_tab.setCurrentIndex(tab)
