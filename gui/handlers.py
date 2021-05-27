'''
Created by: Craig Fouts
Created on: 9/17/2020
'''

import inspect
import logging
import os
import pydre.project

logger = logging.getLogger('PydreLogger')


class Pydre:
    '''PyDre handler that mediates all pydre functionality accessed by the GUI.

    '''

    @staticmethod
    def run(app, project_file, data_files, output_file, progress_bar):
        '''Runs PyDre conversion and saves the resulting output file.

        '''

        pydre_path = os.path.dirname(inspect.getfile(pydre))
        file_list = [os.path.join(pydre_path, file) for file in data_files]
        project = pydre.project.Project(app, project_file, progress_bar)
        output_file = "out.csv" if not output_file.strip() else output_file
        project.run(file_list)
        project.save(os.path.join('output', output_file))
