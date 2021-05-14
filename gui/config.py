'''
Created by: Craig Fouts
Created on: 01/05/2021
'''

from configparser import ConfigParser
from os import path


class Config(ConfigParser):
    '''Custom config class for convenience methods.

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        project_path = path.dirname(path.abspath(__file__))
        self.config_path = path.join(project_path, 'config_files/config.ini')

    def update(self):
        '''Updates the config file with any changes stored in the config 
        variable.

        '''

        with open(self.config_path, 'w') as config_file:
            self.write(config_file)
