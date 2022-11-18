
import sys
import gui.app
from gui.windows import MainWindow

def start():
    '''Launches the application with the given window configuration and
    command-line arguments.

    :param window: Window object responsible for GUI layout and functionality
    '''

    main_app = app.Application(MainWindow, sys.argv)
    main_app.exec_()

