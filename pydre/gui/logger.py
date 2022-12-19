'''
Created by: Craig Fouts
Created on: 6/8/2021
'''

import time
from logging import Handler

class GUIHandler(Handler):

    window = None

    def emit(self, record):
        '''TODO

        '''

        now = time.localtime()
        now_time = time.strftime('%H:%M:%S', now)
        level = record.levelname
        msg = f'{now_time} - {level}: {record.msg}'

        try:
            self.window.add_to_log(msg)
        except:
            print("Unable to add message to log.\n")

        try:
            if level not in ('DEBUG', 'INFO', 'WARNING'):
                error_msg = f'{level}: {record.msg}'
                self.window.show_error(error_msg)
        except:
            print("Unable to display error message.\n")
