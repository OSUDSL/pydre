# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from configparser import ConfigParser
import inspect
from gui.customs import ProjectTree
from gui.templates import Window
from json import loads
import logging
from os import path
import pydre
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QFileDialog

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
        self.c_width = int(config.get("trees", "c_width"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # Class variables
        self.pfile_widgets = {}
        self.pfile_paths = {}
        self.focused_pfile = ""

        # Application configurations
        self._configure_shortcuts()
        self._configure_callbacks()

        # Window configurations
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

        if path_:
            """Launch the project file editor if a project file is selected"""

            self._launch_pfile_editor(path_=path_)
            self.ui.menu_bar.setVisible(True)
            self.resize_and_center(width=1100, height=800)  # FIXME

    def _handle_close_pfile(self, idx):
        """
        Handles closing a project file tab.

        args:
            idx: Index of tab being closed
        """

        # Remove the project file from the paths dict
        pfile = self.ui.pfile_tab.tabText(idx)
        self.pfile_paths.pop(pfile)

        # Remove the tab at the specified index
        self.ui.pfile_tab.removeTab(idx)

        # Handle any remaining tabs
        tab_count = self.ui.pfile_tab.count()
        self._handle_tab_change(tab_count - 1)

    def _handle_tab_change(self, idx):
        """
        Handles general project file tab changes.

        args:
            idx: Index of tab being changed/selected
        """

        if self.ui.pfile_tab.count() > 0:
            """Handle a new tab focus if remaining tabs exist"""

            # Set the run action text based on the current tab
            pfile = self.ui.pfile_tab.tabText(idx)
            self.ui.run_action.setText("Run '{0}'".format(pfile))

            # Set the focussed project file based on the current tab
            self.focused_pfile = self.pfile_paths[pfile]
        else:
            """Handle no remaining tabs"""

            # Switch to startup page
            self.ui.page_stack.setCurrentIndex(0)
            self.ui.menu_bar.setVisible(False)
            self.resize_and_center(width=700, height=400)  # FIXME

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
            type_: Optional file type of the desired file

        returns: Path of the selected file or None if no file is selected
        """

        # Target directory for the file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get the file path and filter
        title = self.explorer_title
        path_, filter_ = QFileDialog.getOpenFileName(self, title, dir_, type_)

        return path_

    def _create_project_tree(self, name, path_):
        """
        Creates and displays a ProjectTree widget for the given project file.

        args:
            name: Project file name
            path_: Project file path
        """

        # Create project file tree
        tree = ProjectTree(c_width=self.c_width, animated=True)
        tree.build_from_file(path=path_)
        self.pfile_paths[name] = tree

        # Open the project file tree in a new tab
        tab_count = self.ui.pfile_tab.count()
        self.ui.pfile_tab.insertTab(tab_count, tree, name)
        self.ui.pfile_tab.setCurrentIndex(tab_count)

    def _launch_pfile_editor(self, path_):
        """
        Configures and shows the project file editor in a new tab.

        args:
            path_: Project file path
        """

        name = path_.split("/")[-1]

        # Set the run action text based on the selected project file
        self.ui.run_action.setText("Run '{0}'".format(name))

        if name not in self.pfile_paths:
            """Open the project file in a new tab if it is not yet open"""

            # Add project file to currently-open project files dict
            self.pfile_paths[name] = path_

            # Create a ProjectTree widget for the selected project file
            self._create_project_tree(name=name, path_=path_)

            # Display the project file editor for the selected project file
            self.ui.page_stack.setCurrentIndex(1)
        else:
            """Switch to the selected project file tab if it is already open"""

            tab = self.ui.pfile_tab.indexOf(self.pfile_widgets[name])
            self.ui.pfile_tab.setCurrentIndex(tab)
