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
    '''Primary application that handles command-line arguments and launches the
    given Window object.
    '''

    def __init__(self, window, *args, **kwargs):
        '''Constructor
        @param window: Window object responsible for layout and functionality
        '''

        super().__init__(*args, **kwargs)
        self.window = window(self)
        GUIHandler.window = self.window
        self._configure_app()
        self.window.start()

    def _configure_app(self):
        '''Convenience method for configuring default app settings.
        '''

        self.setFont(QFont('Arial', 10))


def start():
    '''Launches the application with default configuration settings.
    '''

    app = Application(MainWindow, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start()
