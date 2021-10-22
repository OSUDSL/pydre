'''
Created by: Craig Fouts
Created on: 2/4/2021
'''

import logging
import os
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow
from gui.config import Config, CONFIG_PATH, GUI_PATH

config = Config()
config.read(CONFIG_PATH)

loader = QUiLoader()
logger = logging.getLogger('PydreLogger')


class Window(QMainWindow):
    '''Parent window class that configures window UI, icon, and title if given.

    '''

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ui_path = os.path.join(GUI_PATH, config.get('UI Files', name))
        self.ui_file = QFile(ui_path)
        self.ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(self.ui_file)
        icon_path = os.path.join(GUI_PATH, config.get('Icons', name))
        self.icon = QIcon(icon_path)
        self.ui.setWindowIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.screen = QApplication.primaryScreen()
        self.screen_center = QScreen.availableGeometry(self.screen).center()
        self.screen_width = QScreen.availableGeometry(self.screen).width()
        self.screen_height = QScreen.availableGeometry(self.screen).height()
        self.frame = self.ui.frameGeometry()


    def resize_and_center(self, width, height):
        '''Resizes and centers the window on the screen.

        '''

        self.frame.moveCenter(self.screen_center)
        self.ui.move(self.frame.topLeft())

    def start(self):
        '''Displays the window given the associated UI file.

        '''

        self.ui.show()
