# """
# Created by: Craig Fouts
# Created on: 9/17/2020
# """

from gui.windows import MainWindow
from PySide2.QtWidgets import QApplication
import sys


class Application(QApplication):
    """
    Primary application class that handles command-line arguments and launches
    the main window.
    """

    def __init__(self, window_class, ui_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = window_class(icon_file="images/icon.png", title="Pydre",
                                ui_file=ui_file)
        self.app.start()


if __name__ == '__main__':
    window = MainWindow
    file = "ui_files/mainwindow.ui"
    app = Application(window, file, sys.argv)
    app.exec_()
