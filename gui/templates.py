# """
# Created by: Craig Fouts
# Created on: 11/13/2020
# """

import logging
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget

logger = logging.getLogger("PydreLogger")


class Window(QMainWindow):
    """
    Parent window class that configures window UI, icon, and title if given.
    """

    def __init__(self, window_ui, icon_file, title):
        super().__init__()

        # UI configurations
        try:
            self.ui = window_ui()
            self.ui.setupUi(self)
        except AttributeError:
            logger.error("ERROR: Invalid window UI")
        except TypeError:
            pass

        # Window configurations
        self.setWindowIcon(QIcon(icon_file))
        self.setWindowTitle(title)


class Popup(QWidget):
    """
    Parent popup class that configures popup UI, icon, title, and geometry.
    """

    def __init__(self, popup_ui, icon_file, title):
        super().__init__()

        # UI configurations
        try:
            self.ui = popup_ui()
            self.ui.setupUi(self)
        except AttributeError:
            logger.error("ERROR: Invalid popup UI")
        except TypeError:
            pass

        # Window configurations
        self.setWindowIcon(QIcon(icon_file))
        self.setWindowTitle(title)
