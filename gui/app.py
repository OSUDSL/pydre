# """
# Created by: Craig Fouts
# Created on: 9/17/2020
# """

from configparser import ConfigParser
from gui.windows import MainWindow
from os import path
from PySide2.QtWidgets import QApplication
import sys

config = ConfigParser()
PROJECT_PATH = path.dirname(path.abspath(__file__))
CONFIG_PATH = path.join(PROJECT_PATH, "config_files/config.ini")
config.read(CONFIG_PATH)


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

    app_icon = path.join(PROJECT_PATH, "images/icon.png")
    app_title = config.get("titles", "app")  # FIXME: Move paths to config
    app_ui = path.join(PROJECT_PATH, "ui_files/mainwindow.ui")
    app = Application(MainWindow, app_icon, app_title, app_ui, sys.argv)
    app.exec_()


if __name__ == '__main__':
    start()
