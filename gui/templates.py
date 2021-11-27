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
        self.window_size = None

    def resize_and_center(self, width, height):
        '''Resizes and centers the window on the screen.

        '''

        if self.window_size is None or (not self.ui.isMaximized() and self.window_size == (float(self.ui.width()), float(self.ui.height()))):
            # TODO: FIX SIZING STUFF HERE (ALLOW RESIZING BY MOUSE WITHOUT MESSING IT UP ON PAGE SWITCH)
            print('test')
            self.window_size = (width, height)
            self.frame.setWidth(width)
            self.frame.setHeight(height)
            self.ui.resize(width, height)
            self.frame.moveCenter(self.screen_center)
            self.ui.move(self.frame.topLeft())

    def start(self):
        '''Displays the window given the associated UI file.

        '''

        self.ui.show()
