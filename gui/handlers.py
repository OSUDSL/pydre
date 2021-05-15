'''
Created by: Craig Fouts
Created on: 9/17/2020
'''

import inspect
import logging
from os import path
import pydre.project

logger = logging.getLogger('PydreLogger')


class Pydre:
    '''PyDre handler that mediates all pydre functionality accessed by the GUI.

    '''

    @staticmethod
    def run(project_file, data_files, output_file):
        '''Runs PyDre conversion and saves the resulting output file.

        '''

        pydre_path = path.dirname(inspect.getfile(pydre))
        file_list = [path.join(pydre_path, file) for file in data_files]
        project = pydre.project.Project(project_file)
        if not output_file.strip():
            output_file = "out.csv"
        project.run(file_list)
        project.save(output_file)
