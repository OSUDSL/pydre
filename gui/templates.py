"""
Created by: Craig Fouts
Created on: 2/4/2021
"""

import logging
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDesktopWidget, QMainWindow, QWidget

loader = QUiLoader()
logger = logging.getLogger("PydreLogger")


class Window(QMainWindow):
    """
    Parent window class that configures window UI, icon, and title if given.
    """

    def __init__(self, ui_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UI configurations
        self.ui_file = QFile(ui_file)
        self.ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(self.ui_file)

    def resize_and_center(self, width, height):
        """
        Resizes and centers the window on the screen.

        args:
            width: New width of the window
            height: New height of the window
        """

        # Set window dimensions
        self.ui.resize(width, height)

        # Center window on the screen
        frame = self.ui.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(screen_center)
        self.ui.move(frame.topLeft())

    def start(self):
        """
        Displays the window given the associated UI file.

        args:
            window_ui: Window UI file
        """

        self.ui.show()


class Popup(QWidget):
    """
    Parent popup class that configures popup UI, icon, title, and geometry.
    """

    def __init__(self, icon_file, title, ui_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UI configurations
        self.ui_file = QFile(ui_file)
        self.ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(self.ui_file)

        # Window configurations
        self.ui.setWindowIcon(QIcon(icon_file))
        self.ui.setWindowTitle(title)

    def start(self):
        """
        TODO
        """

        self.ui.show()
