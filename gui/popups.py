"""
Created by: Craig Fouts
Created on: 2/4/2021
"""

from gui.config import Config
from gui.templates import Popup
from os import path

config = Config()
PROJECT_PATH = path.dirname(path.abspath(__file__))
CONFIG_PATH = path.join(PROJECT_PATH, "config_files/config.ini")
config.read(CONFIG_PATH)


class SavePopup(Popup):
    """
    TODO
    """

    def __init__(self, save, close, *args, **kwargs):
        self.icon_file = path.join(PROJECT_PATH, "images/icon.png")
        self.title = config.get("titles", "app")
        self.ui_file = path.join(PROJECT_PATH, "ui_files/savepopup.ui")
        super().__init__(self.icon_file, self.title, self.ui_file, *args, **kwargs)

        # TODO
        self.ui.save_btn.clicked.connect(lambda: self._save_and_close(save, close))
        self.ui.dsave_btn.clicked.connect(lambda: print("don't save"))
        self.ui.cancel_btn.clicked.connect(self.ui.close)

    def _save_and_close(self, save, close):
        """
        FIXME
        """

        save()
        self.ui.close()
        close()
