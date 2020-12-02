# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

import logging
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDesktopWidget, QMainWindow, QWidget

logger = logging.getLogger("PydreLogger")


class Window(QMainWindow):
    """
    Parent window class that configures window UI, icon, and title if given.
    """

    def __init__(self, icon_file, title, window_ui=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configurations
        self.setWindowIcon(QIcon(icon_file))
        self.setWindowTitle(title)

        # UI configurations
        if window_ui:
            self.ui = window_ui()
            self.ui.setupUi(self)

    def _resize_and_center(self, width, height):
        """
        Resizes and centers the window on the screen.

        args:
            width: New width of the window
            height: New height of the window
        """

        # Set window dimensions
        self.resize(width, height)

        # Center window on the screen
        frame = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(screen_center)
        self.move(frame.topLeft())


class Popup(QWidget):
    """
    Parent popup class that configures popup UI, icon, title, and geometry.
    """

    def __init__(self, icon_file, title, popup_ui=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configurations
        self.setWindowIcon(QIcon(icon_file))
        self.setWindowTitle(title)

        # UI configurations
        if popup_ui:
            self.ui = popup_ui()
            self.ui.setupUi(self)
