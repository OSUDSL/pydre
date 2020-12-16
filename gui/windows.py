# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from configparser import ConfigParser
import inspect
from functools import partial
from gui.customs import ProjectTree
from gui.templates import Window
from json import loads
import logging
from os import path
import pydre
from PySide2.QtWidgets import QFileDialog, QTreeWidgetItem

config = ConfigParser()
config.read("./config_files/config.ini")
logger = logging.getLogger("PydreLogger")


class StartWindow(Window):
    """
    Startup window class that handles all tasks related to startup window
    configurations and functionality.
    """

    def __init__(self, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(icon_file, title, ui_file, *args, **kwargs)

        # Config variables
        self.hstretch_factors = loads(config.get("startwindow", "hstretch"))
        self.file_types = dict(config.items("files"))

        # Class variables
        self.main_window = MainWindow(icon_file=icon_file, title=title,
                                      ui_file="ui_files/mainwindow.ui")

        # Window configurations
        self._configure_hsplitters()
        self._configure_callbacks()

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_hsplitters(self):
        """
        Configures horizontal splitters based on config file settings.
        """

        hsplitter_count = self.ui.hsplitter.count()
        for i in range(hsplitter_count):
            stretch_factor = self.hstretch_factors[i]
            self.ui.hsplitter.setStretchFactor(i, stretch_factor)

    def _configure_callbacks(self):
        """
        Configures callback functionality for widget events
        """

        # Button callbacks
        self.ui.open_pfile_btn.clicked.connect(self._handle_open_pfile)

    # ==========================================================================
    # Handler methods ----------------------------------------------------------
    # ==========================================================================

    def _handle_open_pfile(self):
        """
        Handles opening a project file in a new tab.
        """

        # Launch the file explorer for the project file type
        path_ = self._open_file(self.file_types["project"])

        # Launch the project file editor if a project file is selected
        if path_:
            self.ui.close()
            self._launch_pfile_editor()

    # ==========================================================================
    # Reference methods --------------------------------------------------------
    # ==========================================================================

    def _open_file(self, file_type=None):
        """
        Launches a file selection dialog based on the given file type and
        returns the file path if a file is selected.

        args:
            file_type: Optional file type of the desired file

        returns: Path of the selected file or None if no file is selected
        """

        # Target directory for the file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get the file path and filter
        file = QFileDialog.getOpenFileName(self, "Add file", dir_, file_type)

        # Return the file path
        return file[0]

    def _launch_pfile_editor(self):
        """
        TODO
        """

        self.main_window.show()


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(icon_file, title, ui_file, *args, **kwargs)

        # Config variables
        self.sstretch_factors = loads(config.get("startwindow", "sstretch"))
        self.hstretch_factors = loads(config.get("mainwindow", "hstretch"))
        self.vstretch_factors = loads(config.get("mainwindow", "vstretch"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.pfile_paths = {}
        self.focused_pfile = ""

        # Window configurations
        self._configure_ssplitters()
        self._configure_hsplitters()
        self._configure_vsplitters()
        self._configure_shortcuts()
        self._configure_callbacks()

        # TEMP
        self.ui.menu_bar.setVisible(False)

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_ssplitters(self):
        """
        Configures start-page splitters based on config file settings
        """
        ssplitter_count = self.ui.ssplitter.count()
        for i in range(ssplitter_count):
            stretch_factor = self.sstretch_factors[i]
            self.ui.ssplitter.setStretchFactor(i, stretch_factor)

    def _configure_hsplitters(self):
        """
        Configures horizontal splitters based on config file settings.
        """

        hsplitter_count = self.ui.hsplitter.count()
        for i in range(hsplitter_count):
            stretch_factor = self.hstretch_factors[i]
            self.ui.hsplitter.setStretchFactor(i, stretch_factor)

    def _configure_vsplitters(self):
        """
        Configures vertical splitters based on config file settings.
        """

        vsplitter_count = self.ui.vsplitter.count()
        for i in range(vsplitter_count):
            stretch_factor = self.vstretch_factors[i]
            self.ui.vsplitter.setStretchFactor(i, stretch_factor)

    def _configure_shortcuts(self):
        """
        Configures keyboard shortcuts for widgets events.
        """

        # Menu bar action shortcuts
        self.ui.new_action.setShortcut("Ctrl+N")
        self.ui.open_action.setShortcut("Ctrl+O")

    def _configure_callbacks(self):
        """
        Configures callback functionality for widget events.
        """

        # Menu bar action callbacks
        self.ui.new_action.triggered.connect(
            partial(print, "DEBUG: New..."))  # FIXME
        self.ui.open_action.triggered.connect(self._handle_open_pfile)
        self.ui.run_action.triggered.connect(self._handle_run)

        # Button callbacks
        self.ui.open_pfile_btn.clicked.connect(self._handle_open_pfile)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)

        # Tab widget callbacks
        self.ui.pfile_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self._handle_close_pfile)

    # ==========================================================================
    # Handler methods ----------------------------------------------------------
    # ==========================================================================

    def _handle_open_pfile(self):
        """
        Handles opening a project file in a new tab.
        """

        # Launch the file explorer for the project file type
        path_ = self._open_file(self.file_types["project"])

        # Launch the project file editor if a project file is selected
        if path_:
            self._launch_pfile_editor(pfile_path=path_)
            self.resize_and_center(width=1000, height=768)

    def _handle_close_pfile(self, index):
        """
        Handles closing a project file tab.

        args:
            index: Index of tab being closed
        """

        # Delete the tab at the specified index
        self.ui.pfile_tab.removeTab(index)

        # Handle remaining tabs
        self._handle_tab_change(index)

    def _handle_tab_change(self, index):
        """
        Handles general project file tab changes.

        args:
            index: Index of tab being changed
        """

        if self.ui.pfile_tab.count() > 0:
            # Set run action text based on the current tab
            pfile_name = self.ui.pfile_tab.tabText(index)
            self.ui.run_action.setText("Run '{0}'".format(pfile_name))

            # Set focussed project file based on the current tab
            self.focused_pfile = self.pfile_paths[pfile_name]
        else:
            # Switch to startup page
            self.ui.page_stack.setCurrentIndex(0)
            self.resize_and_center(width=600, height=268)

    def _handle_run(self):
        """
        Handles menu bar run action based on the current focussed project file.
        """

        # Set the project file label based on the project file being run
        pfile = self.focused_pfile
        self.ui.pfile_label.setText("Project file: '{0}'".format(pfile))

        # Switch to run page
        self.ui.page_stack.setCurrentIndex(2)

    def _handle_cancel(self):
        """
        Handles cancel button callback on run page.
        """

        # Switch to editor page
        self.ui.page_stack.setCurrentIndex(1)

    # ==========================================================================
    # Reference methods --------------------------------------------------------
    # ==========================================================================

    def _open_file(self, file_type=None):
        """
        Launches a file selection dialog based on the given file type and
        returns the file path if a file is selected.

        args:
            file_type: Optional file type of the desired file

        returns: Path of the selected file or None if no file is selected
        """

        # Target directory for the file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get the file path and filter
        file = QFileDialog.getOpenFileName(self, "Add file", dir_, file_type)

        return file[0]

    def _launch_pfile_editor(self, pfile_path):
        """
        Configures and shows the project file editor in a new tab.

        args:
            pfile_path: Project file path
        """

        # Create new tab for the selected project file
        pfile_name = pfile_path.split("/")[-1]
        self.ui.run_action.setText("Run '{0}'".format(pfile_name))

        if pfile_name not in self.pfile_paths:  # FIXME
            self.pfile_paths[pfile_name] = pfile_path
            pfile_tree = ProjectTree(animated=True)
            tab_count = self.ui.pfile_tab.count()
            self.ui.pfile_tab.insertTab(tab_count, pfile_tree, pfile_name)

            # Build and display the project file editor
            pfile_tree.build_from_file(path=pfile_path)
            self.ui.page_stack.setCurrentIndex(1)
            self.ui.pfile_tab.setCurrentIndex(tab_count)
        else:
            tab = self.ui.pfile_tab.findChild(QTreeWidgetItem, pfile_name)
            index = self.ui.pfile_tab.indexOf(tab)
            print(index)
            self.ui.pfile_tab.setCurrentIndex(index - 1)
