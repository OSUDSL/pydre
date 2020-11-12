# """
# Created by: Craig Fouts
# Created on: 9/17/2020
# """

import sys
import os
import inspect
from functools import partial
from PySide2.QtWidgets import *
from gui.ui_mainwindow import Ui_MainWindow
from PySide2.QtGui import QIcon
import logging
import pydre.project
import pydre.core
import json

logger = logging.getLogger("PydreLogger")


# TODO: CREATE PARENT WINDOW CLASS


class Window(QMainWindow):

    def __init__(self, window_ui, icon_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurations
        self.ui = window_ui()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(icon_file))


class Popup(QWidget):

    def __init__(self, title, icon_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurations
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_file))


class MainWindow(Window):
    app = QApplication()

    def __init__(self, *args, **kwargs):
        super().__init__(Ui_MainWindow, "icon.png", *args, **kwargs)

        # Button callbacks
        self.ui.pfile_btn.clicked.connect(
            partial(self._add_pfile, "JSON (*.json)"))
        self.ui.dfile_btn.clicked.connect(
            partial(self._add_dfile, "DAT (*.dat)"))
        self.ui.remove_btn.clicked.connect(self._remove_file)
        self.ui.edit_pfile_btn.clicked.connect(self._test)
        self.ui.convert_btn.clicked.connect(self.run_pydre)

        # Input callbacks
        self.ui.pfile_inp.textChanged.connect(self._toggle_enable)
        self.ui.dfile_inp.itemSelectionChanged.connect(self._select_file)

    def _test(self):
        try:
            pfile = open(self.ui.pfile_inp.displayText())
            self.popup = JSONPopup(self.ui.pfile_inp.displayText())
            self.popup.run()
        except FileNotFoundError:
            print("File not found")

    def _enable_edit_pfile(self):
        """
        Enables menu actions if enough parameters are satisfied.
        """

        if not self.ui.pfile_inp.displayText() == "" and not \
                self.ui.pfile_inp.displayText().isspace():
            self.ui.edit_pfile_btn.setEnabled(True)
        else:
            self.ui.edit_pfile_btn.setEnabled(False)

    def _enable_convert(self):
        """
        Enables the convert button if enough parameters are satisfied.
        """

        if not self.ui.pfile_inp.displayText() == "" and not \
                self.ui.pfile_inp.displayText().isspace() and \
                self.ui.dfile_inp.count() > 0:
            self.ui.convert_btn.setEnabled(True)
        else:
            self.ui.convert_btn.setEnabled(False)

    def _toggle_enable(self):
        """
        Calls enabling methods
        """

        self._enable_convert()
        self._enable_edit_pfile()

    def _add_pfile(self, file_type):
        """
        Launches a file selection dialog for the project file.

        args:
            file_type: File type associated with project files
        """

        pydre_path = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))

        # Get project file path
        path, filter_ = QFileDialog.getOpenFileName(self, "Add file",
                                                    pydre_path, file_type)

        # If a project file is selected, insert it into the QLineEdit
        if path:
            self.ui.pfile_inp.setText(path)

        self._enable_convert()

    def _add_dfile(self, file_type):
        """
        Launches a file selection dialog for the data files.

        args:
            file_type: File type associated with data files
        """

        pydre_path = os.path.dirname(os.path.dirname(inspect.getfile(pydre)))

        # Get a list of selected data files
        paths, filter_ = QFileDialog.getOpenFileNames(self, "Add files",
                                                      pydre_path, file_type)

        # Add each selected data file to the QListWidget
        for path in paths:
            self.ui.dfile_inp.addItem(path)

        self._enable_convert()

    def _remove_file(self):
        """
        Removes the selected data file from the QListWidget
        """

        self.ui.dfile_inp.takeItem(self.ui.dfile_inp.currentRow())

        if self.ui.dfile_inp.count() == 0:
            self.ui.remove_btn.setEnabled(False)

        self._enable_convert()

    def _select_file(self):
        """
        Enables the remove button if any data files are selected
        """

        self.ui.remove_btn.setEnabled(True)

    def _edit_pfile(self):
        """
        Launches project file editor
        """

        print("heyo")

    def run_pydre(self):
        """
        Runs PyDre and saves the resulting output file.
        """

        pfile = self.ui.pfile_inp.displayText()
        dfiles = [self.ui.dfile_inp.item(i).text() for i in
                  range(self.ui.dfile_inp.count())]
        ofile = self.ui.ofile_inp.displayText()

        # If no output file name is given, log warning and default to 'out.csv'
        if ofile == "":
            ofile = "out.csv"
            logger.warning("No output file specified. Defaulting to 'out.csv'")

        p = pydre.project.Project(pfile)
        pydre_path = os.path.dirname(inspect.getfile(pydre))
        file_list = [os.path.join(pydre_path, file) for file in dfiles]
        p.run(file_list)
        p.save(ofile)

    def run(self):
        """
        Displays the main window
        """

        self.show()
        self.app.exec_()


class JSONPopup(Popup):

    def __init__(self, project_file, *args, **kwargs):
        super().__init__("Project File", "icon.png", *args, **kwargs)
        self.project_file = project_file

        self.resize(400, 300)  # FIXME

        self.layout = QVBoxLayout()

        self.json_tree = QTreeWidget()
        self.json_tree.setHeaderLabels(['Project parameters'])
        self._build_tree()

        self.layout.addWidget(self.json_tree)
        self.setLayout(self.layout)

    def _build_tree(self):
        """
        FIXME
        """

        try:
            pfile = open(self.project_file)
            pfile_contents = json.load(pfile)
            for i in pfile_contents:
                parent = QTreeWidgetItem(self.json_tree, [i])
                metric = 1
                for j in pfile_contents[i]:
                    branch = QTreeWidgetItem(parent, ['{0} {1}'.format(i, metric)])
                    # child = QTreeWidgetItem(parent, ['{0}: {1}'.format(k, j[k]) for k in j])
                    for k in j:
                        child = QTreeWidgetItem(branch, ['{0}: {1}'.format(k, j[k])])
                    metric += 1
        except FileNotFoundError:
            print("File not found")

    def run(self):
        """
        Displays the JSON window
        """

        self.show()


if __name__ == '__main__':
    MainWindow().run()
