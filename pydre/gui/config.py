'''
Created by: Craig Fouts
Created on: 01/05/2021
'''

import os
from configparser import ConfigParser
from pathlib import Path
import importlib.resources


PROJECT_PATH = Path().resolve()
GUI_PATH = os.path.join(PROJECT_PATH, 'gui')
config_filename = os.path.join(PROJECT_PATH, 'config.ini')



class Config(ConfigParser):
    '''Custom configuration parser class for implementing proprietary
    convenience methods.

    Usage:
        config = Config()
        config.read(<configuration file path>)
    '''

    def __init__(self, *args, **kwargs):
        '''Constructor.
        '''

        super().__init__(*args, **kwargs)

    def update(self):
        '''Updates the application configuration file with any changes stored in 
        the configuration variable.
        '''

        with open(config_filename, 'w') as config_file:
            self.write(config_file)
