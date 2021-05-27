'''
Created by: Craig Fouts
Created on: 9/17/2020
'''

import os
import sys
from configparser import ConfigParser
from gui.windows import MainWindow
from PySide2.QtWidgets import QApplication

config = ConfigParser()
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_PATH, 'config_files/config.ini')
config.read(CONFIG_PATH)


class Application(QApplication):
    '''Primary application that handles command-line arguments and launches the 
    given window.

    '''

    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.window = window(self)
        self.window.start()


def start():
    '''Starts the application with default configuration settings.

    '''

    app_window = MainWindow
    app = Application(app_window, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start()
