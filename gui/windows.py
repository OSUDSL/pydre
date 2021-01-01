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
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QFileDialog, QTreeWidgetItem

config = ConfigParser()
config.read("./config_files/config.ini")
logger = logging.getLogger("PydreLogger")


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(icon_file, title, ui_file, *args, **kwargs)

        # Config variables
        self.app_icon = config.get("icons", "app")
        self.app_title = config.get("titles", "app")
        self.explorer_title = config.get("titles", "explorer")
        self.shstretch_factors = loads(config.get("splitters", "shstretch"))
        self.mhstretch_factors = loads(config.get("splitters", "mhstretch"))
        self.mvstretch_factors = loads(config.get("splitters", "mvstretch"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # FIXME
        self.pfile_widgets = {}

        # Class variables
        self.pfile_paths = {}
        self.focused_pfile = ""

        # Application configurations
        self._configure_shortcuts()
        self._configure_callbacks()

        # Startup configurations
        self._configure_window()
        self._configure_splitters()

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_shortcuts(self):
        """
        Configures keyboard shortcuts for widgets events.
        """

        # Menu bar action shortcuts
        self.ui.new_action.setShortcut("Ctrl+N")
        self.ui.open_action.setShortcut("Ctrl+O")

    def _set_mb_callbacks(self):
        """
        Sets all menu bar action callbacks.
        """

        self.ui.open_action.triggered.connect(self._handle_open_pfile)
        self.ui.run_action.triggered.connect(self._handle_run)

    def _set_button_callbacks(self):
        """
        Sets all button callbacks.
        """

        self.ui.open_pfile_btn.clicked.connect(self._handle_open_pfile)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)

    def _set_widget_callbacks(self):
        """
        Sets all miscellaneous widget callbacks.
        """

        self.ui.pfile_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self._handle_close_pfile)

    def _configure_callbacks(self):
        """
        Configures callback functionality for widget events.
        """

        self._set_mb_callbacks()
        self._set_button_callbacks()
        self._set_widget_callbacks()

    def _configure_window(self):
        """
        Configures general window settings.
        """

        self.ui.setWindowIcon(QIcon(self.app_icon))
        self.ui.setWindowTitle(self.app_title)
        self.ui.menu_bar.setVisible(False)

    def _set_start_splitters(self):
        """
        Sets the initial splitter width for splitters on the startup window page
        based on config file settings.
        """

        # Configure horizontal splitters
        shsplitter_count = self.ui.shsplitter.count()
        for i in range(shsplitter_count):
            stretch_factor = self.shstretch_factors[i]
            self.ui.shsplitter.setStretchFactor(i, stretch_factor)

    def _set_main_splitters(self):
        """
        Set the initial splitter width for splitters on the main window page
        based on config file settings.
        """

        # Configure horizontal splitters
        mhsplitter_count = self.ui.mhsplitter.count()
        for i in range(mhsplitter_count):
            stretch_factor = self.mhstretch_factors[i]
            self.ui.mhsplitter.setStretchFactor(i, stretch_factor)

        # Configure vertical splitters
        mvsplitter_count = self.ui.mvsplitter.count()
        for i in range(mvsplitter_count):
            stretch_factor = self.mvstretch_factors[i]
            self.ui.mvsplitter.setStretchFactor(i, stretch_factor)

    def _configure_splitters(self):
        """
        Configures all splitter widgets.
        """

        self._set_start_splitters()
        self._set_main_splitters()

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
            self.ui.menu_bar.setVisible(True)
            self.resize_and_center(width=1100, height=800)

    def _handle_close_pfile(self, index):
        """
        Handles closing a project file tab.

        args:
            index: Index of tab being closed
        """

        # TODO
        self.pfile_paths.pop(self.ui.pfile_tab.tabText(index))

        # Remove the tab at the specified index
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
            # Hide menu bar
            self.ui.menu_bar.setVisible(False)

            # Switch to startup page
            self.ui.page_stack.setCurrentIndex(0)
            self.resize_and_center(width=700, height=400)

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

    def _open_file(self, type_=None):
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
        text = "Add file"  # FIXME
        path_, filter_ = QFileDialog.getOpenFileName(self, text, dir_, type_)

        return path_

    def _launch_pfile_editor(self, pfile_path):
        """
        Configures and shows the project file editor in a new tab.

        args:
            pfile_path: Project file path
        """

        # Create new tab for the selected project file
        pfile_name = pfile_path.split("/")[-1]
        self.ui.run_action.setText("Run '{0}'".format(pfile_name))

        if pfile_name not in self.pfile_paths:
            self.pfile_paths[pfile_name] = pfile_path
            pfile_tree = ProjectTree(c_width=300, animated=True)
            self.pfile_widgets[pfile_name] = pfile_tree
            tab_count = self.ui.pfile_tab.count()
            self.ui.pfile_tab.insertTab(tab_count, pfile_tree, pfile_name)

            # Build and display the project file editor
            pfile_tree.build_from_file(path=pfile_path)
            self.ui.page_stack.setCurrentIndex(1)
            self.ui.pfile_tab.setCurrentIndex(tab_count)
        else:
            tab = self.ui.pfile_tab.indexOf(self.pfile_widgets[pfile_name])
            self.ui.pfile_tab.setCurrentIndex(tab)
