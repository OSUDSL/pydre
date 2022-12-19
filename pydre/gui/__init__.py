
import sys

from pydre.gui import app
from pydre.gui.windows import MainWindow
import logging
from pydre.gui.logger import GUIHandler


def start():
    '''Launches the application with the given window configuration and
    command-line arguments.

    :param window: Window object responsible for GUI layout and functionality
    '''

    main_app = app.Application(MainWindow, sys.argv)

    logger = logging.getLogger("pydre")
    GUIHandler.window = MainWindow

    logger.addHandler(GUIHandler)

    main_app.exec_()

