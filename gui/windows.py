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

        # Config variables
        self.stretch_factors = loads(config.get("geometry", "stretch_factors"))
        self.file_types = dict(config.items("files"))
        self.param_types = dict(config.items("parameters"))

        # Application configurations
        self._configure_widgets()
        self._configure_shortcuts()
        self._configure_callbacks()

    # ==========================================================================
    # Window configuration methods ---------------------------------------------
    # ==========================================================================

    def _configure_widgets(self):
        """
        Configures widgets based on config file settings
        """

        # Set horizontal splitter location based on config file
        for i in range(self.ui.splitter.count()):
            self.ui.splitter.setStretchFactor(i, self.stretch_factors[i])

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

        # Button callbacks
        self.ui.open_pfile_btn.clicked.connect(self._handle_open)

        # Tab widget callbacks
        self.ui.pfile_tab.tabCloseRequested.connect(
            lambda index: self._handle_close(index))

    # ==========================================================================
    # Handler methods ----------------------------------------------------------
    # ==========================================================================

    def _handle_open(self):
        """

        """

        pfile_path = self._open_file(self.file_types["project"])
        self._launch_pfile_editor(pfile_path)

    def _handle_close(self, index):
        """
        TODO
        """

        self.ui.pfile_tab.removeTab(index)

        if self.ui.pfile_tab.count() == 0:
            self.ui.page_stack.setCurrentIndex(0)

    # ==========================================================================
    # Reference methods --------------------------------------------------------
    # ==========================================================================

    # TODO: Create custom tree class to handle this
    def _create_branch(self, tree):
        """
        TODO
        """

    def _build_pfile_tree(self, pfile_tree, pfile_path):
        """
        Creates and fills the project file editor tree

        args:
            pfile_tree: Project file tree widget
            pfile_path: Project file path
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
                branch_text = ['{0} {1}'.format(self.param_types[i], index + 1)]
                branch = QTreeWidgetItem(tree, branch_text)

                # Generate leaf for each parameter
                for k in j:
                    leaf_text = ['{0}: {1}'.format(k, j[k])]
                    QTreeWidgetItem(branch, leaf_text)

    def _launch_pfile_editor(self, pfile_path):
        """
        Configures and shows the project file editor in a new tab

        args:
            pfile_path: Project file path
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

        # Get project file path
        file_path, filter_ = QFileDialog.getOpenFileName(self, "Add file",
                                                         dir_, file_type)

        return file_path if file_path else None
