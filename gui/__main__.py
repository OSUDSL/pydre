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

# os.system("pyside2-uic mainwindow.ui > ui_mainwindow.py")

logger = logging.getLogger("PydreLogger")


class MainWindow(QMainWindow):
    app = QApplication(sys.argv)

    def __init__(self, window_ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = window_ui()
        self.ui.setupUi(self)

        self.setWindowIcon(QIcon("icon.png"))

        # Button callbacks
        self.ui.pfile_btn.clicked.connect(
            partial(self._add_file, self.ui.pfile_inp, "JSON (*.json)"))
        self.ui.dfile_btn.clicked.connect(
            partial(self._add_file, self.ui.dfile_inp, "DAT (*.dat)"))
        self.ui.remove_btn.clicked.connect(self._remove_file)
        self.ui.convert_btn.clicked.connect(self.run_pydre)

        # TODO
        self.ui.pfile_inp.textChanged.connect(self._enable_convert)
        self.ui.dfile_inp.itemSelectionChanged.connect(self._select_file)

    def _enable_convert(self):
        if not self.ui.pfile_inp.displayText() == "" and not \
                self.ui.pfile_inp.displayText().isspace() and \
                self.ui.dfile_inp.count() > 0:
            self.ui.convert_btn.setEnabled(True)
        else:
            self.ui.convert_btn.setEnabled(False)

    def _add_file(self, file_inp, file_type):
        """
        Launches a file selection dialog for the given file type.

        args:
            file_inp: line editor corresponding to the desired file
        """
        path, filter_ = QFileDialog.getOpenFileName(self, "Open file", "..",
                                                    file_type)

        if path:
            try:
                file_inp.addItem(path)
            except AttributeError:
                file_inp.setText(path)
        else:
            logger.warning("File path not found.")

        self._enable_convert()

    def _remove_file(self):
        self.ui.dfile_inp.takeItem(self.ui.dfile_inp.currentRow())

        if self.ui.dfile_inp.count() == 0:
            self.ui.remove_btn.setEnabled(False)

        self._enable_convert()

    def _select_file(self):
        self.ui.remove_btn.setEnabled(True)

    def run_pydre(self):
        """
        Runs PyDre and saves the resulting output file.
        """

        # convert_prg = QProgressBar(self.ui.centralWidget)
        # convert_prg.setMinimum(0)
        # convert_prg.setMaximum(100)
        # self.ui.verticalLayout.addWidget(QProgressBar())

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
        self.show()
        self.app.exec_()


if __name__ == '__main__':
    MainWindow(Ui_MainWindow).run()
