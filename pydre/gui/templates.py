'''
Created by: Craig Fouts
Created on: 2/4/2021
'''

import logging
import os
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon, QScreen
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from pydre.gui.config import Config, config_filename

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

config = Config()
config.read(config_filename)
logger = logging.getLogger('PydreLogger')
loader = QUiLoader()


class Window(QMainWindow):
    '''Parent window class that configures window UI, icon, and title if given.
    '''

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        file = QFile(str(files("pydre.gui.ui_files").joinpath(config.get('UI Files', self.name))))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file)
        icon = QIcon(str(files("pydre.gui.images").joinpath(config.get('Icons', self.name))))
        self.ui.setWindowIcon(icon)
        self.setWindowIcon(icon)
        self.screen = QApplication.primaryScreen()
        self.screen_center = QScreen.availableGeometry(self.screen).center()
        self.screen_width = QScreen.availableGeometry(self.screen).width()
        self.screen_height = QScreen.availableGeometry(self.screen).height()
        self.frame = self.ui.frameGeometry()
        self.window_size = None

    def resize_and_center(self, width, height):
        '''Resizes and centers the child window on the current screen.

        :param width: Target window width
        :param height: Target window height
        '''

        current_size = (float(self.ui.width()), float(self.ui.height()))
        match = (not self.ui.isMaximized()) and self.window_size == current_size
        if self.window_size is None or match:
            self.window_size = (width, height)
            self.frame.setWidth(width)
            self.frame.setHeight(height)
            self.ui.resize(width, height)
            self.frame.moveCenter(self.screen_center)
            self.ui.move(self.frame.topLeft())

    def start(self):
        '''Displays the child window and initiates functionality.
        '''

        self.ui.show()
