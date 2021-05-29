'''
Created by: Craig Fouts
Created on: 2/4/2021
'''

import logging
import os
from gui.config import Config
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDesktopWidget, QMainWindow, QWidget

config = Config()
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_PATH, 'config_files/config.ini')
config.read(CONFIG_PATH)

loader = QUiLoader()
logger = logging.getLogger('PydreLogger')


class Window(QMainWindow):
    '''Parent window class that configures window UI, icon, and title if given.

    '''

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ui_path = os.path.join(PROJECT_PATH, config.get('UI Files', name))
        self.ui_file = QFile(ui_path)
        self.ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(self.ui_file)
        icon_path = os.path.join(PROJECT_PATH, config.get('Icons', name))
        self.icon = QIcon(icon_path)
        self.ui.setWindowIcon(self.icon)

    def resize_and_center(self, width, height):
        '''Resizes and centers the window on the screen.

        '''

        self.ui.resize(width, height)
        frame = self.ui.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(screen_center)
        self.ui.move(frame.topLeft())

    def start(self):
        '''Displays the window given the associated UI file.

        '''

        self.ui.show()
