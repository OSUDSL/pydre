# """
# Created by: Craig Fouts
# Created on: 01/05/2021
# """

from configparser import ConfigParser


class Config(ConfigParser):
    """
    Custom config class for convenience methods.
    """

    def update(self):
        """
        Updates the config file with any changes stored in the config variable.
        """

        with open("./config_files/config.ini", "w") as configfile:
            self.write(configfile)
