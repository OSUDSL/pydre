"""
Created by: Craig Fouts
Created on: 9/17/2020
"""

from PySide6.QtWidgets import QApplication
from pydre.gui.config import Config, config_filename
from pydre.gui.gui_log import GUILogHandler

config = Config()
config.read(config_filename)


class Application(QApplication):
    """Primary application class responsible for handling command-line arguments
    and launching the given window object.

    Usage:
        window = MainWindow()
        app = Application(window, sys.argv)
        app.exec_()

    :param window: Window object responsible for GUI layout and functionality
    """

    def __init__(self, window, *args, **kwargs):
        """Constructor."""

        super().__init__(*args, **kwargs)
        self.window = window(self)
        GUILogHandler.window = self.window
        self.window.start()
