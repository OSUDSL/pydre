'''
Created by: Craig Fouts
Created on: 01/05/2021
'''

import os
from configparser import ConfigParser
from pathlib import Path
from gui.app import CONFIG_PATH


class Config(ConfigParser):
    '''Custom config class for convenience methods.

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self):
        '''Updates the config file with any changes stored in the config 
        variable.

        '''

        with open(CONFIG_PATH, 'w') as config_file:
            self.write(config_file)
