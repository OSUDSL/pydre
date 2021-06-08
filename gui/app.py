'''
Created by: Craig Fouts
Created on: 9/17/2020
'''

import os
import sys
from pathlib import Path
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication
from gui.config import Config, CONFIG_PATH
from gui.logger import GUIHandler
from gui.windows import MainWindow

config = Config()
config.read(CONFIG_PATH)


class Application(QApplication):
    '''Primary application that handles command-line arguments and launches the 
    given window.

    '''

    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.window = window(self)
        GUIHandler.window = self.window
        self._configure_app()
        self.window.start()

    def _configure_app(self):
        '''TODO

        '''

        self.setFont(QFont('Arial', 10))


def start():
    '''Starts the application with default configuration settings.

    '''

    app_window = MainWindow
    app = Application(app_window, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start()
