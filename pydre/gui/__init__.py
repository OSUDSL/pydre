
import sys

from pydre.gui import app
from pydre.gui.windows import MainWindow
import logging
from pydre.gui.gui_log import GUILogHandler


def start():
    '''Launches the application with the given window configuration and
    command-line arguments.

    :param window: Window object responsible for GUI layout and functionality
    '''

    main_app = app.Application(MainWindow, sys.argv)

    logger = logging.getLogger()

    h = GUILogHandler(main_app.window)
    logger.addHandler(h)

    main_app.exec_()

