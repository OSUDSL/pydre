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
import logging
import glob
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

        # Button callbacks
        self.ui.pfile_btn.clicked.connect(
            partial(self._get_file, self.ui.pfile_inp))
        self.ui.dfile_btn.clicked.connect(
            partial(self._get_file, self.ui.dfile_inp))
        self.ui.convert_btn.clicked.connect(self.run_pydre)

    def _get_file(self, file_inp):
        """
        Launches a file selection dialog for the given file type.

        args:
            file_inp: line editor corresponding to the desired file
        """
        path, filter_ = QFileDialog.getOpenFileName(self, "Open file", "..")

        if path:
            file_inp.setText(path)
        else:
            logger.warning("File path not found.")

    def run_pydre(self):
        """
        Runs PyDre and saves the resulting output file.
        """
        pfile = self.ui.pfile_inp.displayText()
        dfile = self.ui.dfile_inp.displayText()
        ofile = self.ui.ofile_inp.displayText()

        # If no output file name is given, log warning and default to 'out.csv'
        if ofile == "":
            ofile = "out.csv"
            logger.warning("No output file specified. Defaulting to 'out.csv'")

        p = pydre.project.Project(pfile)
        pydre_path = os.path.dirname(inspect.getfile(pydre))
        file_list = glob.glob(os.path.join(pydre_path, dfile))
        p.run(file_list)
        p.save(ofile)

    def run(self):
        self.show()
        self.app.exec_()


if __name__ == '__main__':
    MainWindow(Ui_MainWindow).run()
