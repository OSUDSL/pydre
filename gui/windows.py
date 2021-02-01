# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

import inspect
from gui.config import Config
from gui.customs import ProjectTree
from gui.templates import Window
from json import dump, loads
import logging
from os import path, sep
import pydre
from pydre import metrics
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QFileDialog

config = Config()
PROJECT_PATH = path.dirname(path.abspath(__file__))
CONFIG_PATH = path.join(PROJECT_PATH, "config_files/config.ini")
config.read(CONFIG_PATH)

logger = logging.getLogger("PydreLogger")


class MainWindow(Window):
    """
    Primary window class that handles all tasks related to main window
    configurations and functionality.
    """

    def __init__(self, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(icon_file, title, ui_file, *args, **kwargs)

        # Config variables
        self.explorer_title = config.get("titles", "explorer")
        self.shstretch_factors = loads(config.get("splitters", "shstretch"))
        self.mhstretch_factors = loads(config.get("splitters", "mhstretch"))
        self.mvstretch_factors = loads(config.get("splitters", "mvstretch"))
        self.file_types = dict(config.items("types"))
        self.param_types = dict(config.items("parameters"))
        self.recent_names = config.get("recent", "names").split(",")
        self.recent_paths = config.get("recent", "paths").split(",")

        # Class variables
        self.app_icon = icon_file
        self.app_title = title
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

        self.ui.open_action.triggered.connect(self._handle_open)
        self.ui.save_action.triggered.connect(self._handle_save)
        self.ui.run_action.triggered.connect(self._handle_run)

        self.ui.recent_files.itemDoubleClicked.connect(self._handle_select)

    def _set_button_callbacks(self):
        """
        Sets all button callbacks.
        """

        self.ui.open_pfile_btn.clicked.connect(self._handle_open)
        self.ui.cancel_btn.clicked.connect(self._handle_cancel)

    def _set_widget_callbacks(self):
        """
        Sets all miscellaneous widget callbacks.
        """

        self.ui.pfile_tab.currentChanged.connect(self._handle_tab_change)
        self.ui.pfile_tab.tabCloseRequested.connect(self._handle_close)

    def _configure_callbacks(self):
        """
        Configures callback functionality for widget events.
        """

        self._set_mb_callbacks()
        self._set_button_callbacks()
        self._set_widget_callbacks()

    def _set_recent_files(self):
        """
        Sets the files to be displayed in the recent files QListWidget.
        """

        self.ui.recent_files.clear()
        names = [name for name in self.recent_names if name != ""]
        for name in names:
            self.ui.recent_files.addItem(name)

    def _configure_window(self):
        """
        Configures general window settings.
        """

        self.ui.setWindowIcon(QIcon(self.app_icon))
        self.ui.setWindowTitle(self.app_title)
        self.ui.menu_bar.setVisible(False)
        self._set_recent_files()

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

    def _handle_open(self):
        """
        Handles opening a project file in a new tab.
        """

        # Launch the file explorer for the project file type
        path_ = self._open_file(self.file_types["project"])

        if path_:
            """Launch the project file editor if a project file is selected"""

            self._launch_editor(path_)
            self.ui.menu_bar.setVisible(True)
            self.resize_and_center(1100, 800)

    def _handle_select(self):
        """
        Handles selecting a project file from the recent files menu.
        """

        # Get the selected project file path
        idx = self.ui.recent_files.currentRow()
        relative_path = self.recent_paths[idx]
        path_ = path.join(path.dirname(PROJECT_PATH), relative_path)

        # Launch the project file editor
        self._launch_editor(path_)
        self.ui.menu_bar.setVisible(True)
        self.resize_and_center(1100, 800)

    def _handle_close(self, idx):
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
            self._set_recent_files()
            self.ui.page_stack.setCurrentIndex(0)
            self.ui.menu_bar.setVisible(False)
            self.resize_and_center(700, 400)

    def _handle_save(self):
        """
        TODO
        """

        # TODO: Should this be in customs.py?
        # TODO: Add log message on save

        print(self.ui.pfile_tab.currentWidget().get_contents())
        name = self.pfile_widgets[self.ui.pfile_tab.currentWidget()]
        with open(self.pfile_paths[name], "w") as file:
            dump(self.ui.pfile_tab.currentWidget().get_contents(), file, indent=4)

    def _handle_run(self):
        """
        Handles menu bar run action based on the current focussed project file.
        """

        # Set the project file label based on the project file being run
        text = "Project file: {0}".format(self.focused_pfile)
        self.ui.pfile_label.setText(text)

        # Switch to run page
        self.ui.page_stack.setCurrentIndex(2)

    def _handle_cancel(self):
        """
        Handles cancel button callback on run page.
        """

        # Reset project file label text
        self.ui.pfile_label.setText("")

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

        return path.abspath(path_)

    def _create_project_tree(self, name, path_):
        """
        Creates and displays a ProjectTree widget for the given project file.

        args:
            name: Project file name
            path_: Project file path
        """

        # Create project file tree
        tree = ProjectTree(path_, metrics.metricsList, True)
        self.pfile_widgets[tree] = name  # FIXME?
        self.pfile_paths[name] = path_

        # Open the project file tree in a new tab
        tab_count = self.ui.pfile_tab.count()
        self.ui.pfile_tab.insertTab(tab_count, tree, name)
        self.ui.pfile_tab.setCurrentIndex(tab_count)

    def _add_to_recent(self, name, path_):
        """
        Adds the given project file name and path to the recent files lists in
        the config file.

        args:
            name: Project file name
            path_: Project file path
        """

        relative_path = path.join(*path_.split(sep)[-2:])

        # Remove the given name and path if they are already saved
        if name in self.recent_names:
            self.recent_names.remove(name)
            self.recent_paths.remove(relative_path)

        # Insert the given name and path at the beginning of the respective list
        self.recent_names.insert(0, name)
        self.recent_paths.insert(0, relative_path)

        # Set and add write lists in the config file
        config.set("recent", "names", ",".join(self.recent_names))
        config.set("recent", "paths", ",".join(self.recent_paths))
        config.update()

    def _launch_editor(self, path_):
        """
        Configures and shows the project file editor in a new tab.

        args:
            path_: Project file path
        """

        name = path_.split(sep)[-1]

        # Update recent files with the given file
        self._add_to_recent(name, path_)

        # Set the run action text based on the selected project file
        self.ui.run_action.setText("Run '{0}'".format(name))

        if name not in self.pfile_paths:
            """Open the project file in a new tab if it is not yet open"""

            # Add project file to currently-open project files dict
            self.pfile_paths[name] = path_

            # Create a ProjectTree widget for the selected project file
            self._create_project_tree(name, path_)

            # Display the project file editor for the selected project file
            self.ui.page_stack.setCurrentIndex(1)
        else:
            """Switch to the selected project file tab if it is already open"""

            tab = self.ui.pfile_tab.indexOf(self.pfile_widgets[name])
            self.ui.pfile_tab.setCurrentIndex(tab)
