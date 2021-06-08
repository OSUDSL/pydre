'''
Created by: Craig Fouts
Created on: 6/8/2021
'''

from logging import Handler


class GUIHandler(Handler):

    def emit(self, record):
        print(f'{record.msg}')
