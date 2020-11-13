# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget


class Window(QMainWindow):
    """
    TODO
    """

    def __init__(self, window_ui, icon_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configurations
        self.setWindowIcon(QIcon(icon_file))

        # UI configurations
        self.ui = window_ui()
        self.ui.setupUi(self)


class Popup(QWidget):
    """
    TODO
    """

    def __init__(self, popup_ui, title, icon_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Window configurations
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_file))

        # UI configurations
        try:
            self.ui = popup_ui()
            self.ui.setupUi(self)
        except TypeError:
            pass
