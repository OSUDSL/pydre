# """
# Created by: Craig Fouts
# Created on: 01/05/2021
# """

from configparser import ConfigParser
import gui
import inspect
from os import path


class Config(ConfigParser):
    """
    Custom config class for convenience methods.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.module_path = path.dirname(inspect.getfile(gui))
        self.config_path = self.module_path + r"./config_files/config.ini"

    def update(self):
        """
        Updates the config file with any changes stored in the config variable.
        """

        with open(self.config_path, "w") as configfile:
            self.write(configfile)
