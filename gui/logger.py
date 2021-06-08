'''
Created by: Craig Fouts
Created on: 6/8/2021
'''

from logging import Handler


class GUIHandler(Handler):

    window = None

    def emit(self, record):
        '''TODO

        '''

        print(f'{record.msg}')
        self.window.add_to_log(record.msg)
