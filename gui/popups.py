"""
Created by: Craig Fouts
Created on: 2/4/2021
"""

from gui.config import Config
from gui.templates import Popup
from os import path

config = Config()
PROJECT_PATH = path.dirname(path.abspath(__file__))


class SavePopup(Popup):
    """
    TODO
    """

    def __init__(self, icon_file, title, *args, **kwargs):  # FIXME: Icon and title not appearing (check in main too)
        self.ui_file = path.join(PROJECT_PATH, "ui_files/savepopup.ui")
        super().__init__(icon_file, title, self.ui_file, *args, **kwargs)

