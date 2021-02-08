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

    def __init__(self, icon_file, title, ui_file, *args, **kwargs):
        super().__init__(icon_file, title, ui_file, *args, **kwargs)


