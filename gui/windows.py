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
from os import path
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

        # # Button callbacks
        # self.ui.pfile_btn.clicked.connect(
        #     partial(self._add_pfile, "JSON (*.json)"))
        # self.ui.dfile_btn.clicked.connect(
        #     partial(self._add_dfiles, "DAT (*.dat)"))
        # self.ui.remove_btn.clicked.connect(self._remove_file)
        # self.ui.edit_pfile_btn.clicked.connect(self._edit_pfile)
        # self.ui.convert_btn.clicked.connect(self._run_pydre)
        #
        # # Input callbacks
        # self.ui.pfile_inp.textChanged.connect(self._toggle_buttons)
        # self.ui.dfile_inp.model().rowsInserted.connect(self._toggle_buttons)
        # self.ui.dfile_inp.model().rowsRemoved.connect(self._toggle_buttons)
        # self.ui.dfile_inp.itemSelectionChanged.connect(self._toggle_remove)

        self.ui.switch_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.tabWidget.tabCloseRequested.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))

    def _toggle_remove(self):
        """
        Enables the Remove button if at least one data file is selected.
        """

        selected_data_files = self.ui.dfile_inp.selectedItems()

        # Toggle remove button
        if len(selected_data_files) > 0:
            self.ui.remove_btn.setEnabled(True)
        else:
            self.ui.remove_btn.setEnabled(False)

    def _toggle_edit_pfile(self):
        """
        Toggles the Edit Project File button based on whether the project file
        input is populated.
        """

        project_file = self.ui.pfile_inp.displayText()

        # Toggle Edit Project File button
        if project_file.strip():
            self.ui.edit_pfile_btn.setEnabled(True)
        else:
            self.ui.edit_pfile_btn.setEnabled(False)

    def _toggle_convert(self):
        """
        Toggles the Convert button based on whether both the project file input
        and the data file input are populated.
        """

        project_file = self.ui.pfile_inp.displayText()
        data_file_count = self.ui.dfile_inp.count()

        # Toggle Convert button
        if project_file.strip() and data_file_count > 0:
            self.ui.convert_btn.setEnabled(True)
        else:
            self.ui.convert_btn.setEnabled(False)

    def _toggle_buttons(self):
        """
        Calls button toggling methods.
        """

        self._toggle_edit_pfile()
        self._toggle_convert()

    def _add_pfile(self, file_type):
        """
        Launches a file selection dialog for the project file.

        args:
            file_type: File type associated with project files
        """

        # Target directory for file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get project file path
        pfile_path, filter_ = QFileDialog.getOpenFileName(self, "Add file",
                                                          dir_, file_type)

        # If a project file is selected, insert it into the QLineEdit
        if pfile_path:
            self.ui.pfile_inp.setText(pfile_path)

    def _add_dfiles(self, file_type):
        """
        Launches a file selection dialog for the data files.

        args:
            file_type: File type associated with data files
        """

        # Target directory for file selection dialog
        dir_ = path.dirname(path.dirname(inspect.getfile(pydre)))

        # Get a list of selected data files
        qfile_paths, filter_ = QFileDialog.getOpenFileNames(self, "Add files",
                                                            dir_, file_type)

        # Add each selected data file to the QListWidget
        for qfile_path in qfile_paths:
            self.ui.dfile_inp.addItem(qfile_path)

    def _remove_file(self):
        """
        Removes the selected data file from the data file input.
        """

        self.ui.dfile_inp.takeItem(self.ui.dfile_inp.currentRow())

    def _edit_pfile(self):
        """
        Launches the project file editor.
        """

        try:
            project_file = open(self.ui.pfile_inp.displayText())
            self.popup = ProjectFilePopup(project_file)
            self.popup.show()
        except FileNotFoundError:
            logger.error("ERROR: Project file not found")

    def _run_pydre(self):
        """
        Runs pydre conversion using the given project file, data files, and
        optional output file.
        """

        project_file = self.ui.pfile_inp.displayText()
        data_files = [self.ui.dfile_inp.item(i) for i in
                      range(self.ui.dfile_inp.count())]
        output_file = self.ui.ofile_inp.displayText()

        # Run pydre conversion
        Pydre.run(project_file, data_files, output_file)
