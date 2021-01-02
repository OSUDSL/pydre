# """
# Created by: Craig Fouts
# Created on: 9/17/2020
# """

from configparser import ConfigParser
from gui.windows import MainWindow
from PySide2.QtWidgets import QApplication
import sys

config = ConfigParser()
config.read("./config_files/config.ini")


class Application(QApplication):
    """
    Primary application class that handles command-line arguments and launches
    the main window.
    """

    def __init__(self, window, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = window(icon_file, title, ui_file)
        self.app.start()


def start():
    """
    Starts the application with default config settings.
    """

    app_icon = config.get("icons", "app")
    app_title = config.get("titles", "app")
    app_ui = config.get("uis", "app")
    app = Application(MainWindow, app_icon, app_title, app_ui, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start()
