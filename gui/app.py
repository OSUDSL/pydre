'''
Created by: Craig Fouts
Created on: 9/17/2020
'''

import sys
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication
from gui.config import Config, CONFIG_PATH
from gui.logger import GUIHandler
from gui.windows import MainWindow

config = Config()
config.read(CONFIG_PATH)


class Application(QApplication):
    '''Primary application class responsible for handling command-line arguments
    and launching the given window object.

    Usage:
        window = MainWindow()
        app = Application(window, sys.argv)
        app.exec_()

    :param window: Window object responsible for GUI layout and functionality
    '''

    def __init__(self, window, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)
        self.window = window(self)
        GUIHandler.window = self.window
        self.window.start()


def start(window):
    '''Launches the application with the given window configuration and
    command-line arguments.

    :param window: Window object responsible for GUI layout and functionality
    '''

    app = Application(window, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start(MainWindow)
