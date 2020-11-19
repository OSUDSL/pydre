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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main = MainWindow()
        self.main.show()


if __name__ == '__main__':
    Application(sys.argv).exec_()
