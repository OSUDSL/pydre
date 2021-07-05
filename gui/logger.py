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
        self.window.add_to_log(msg)
        if level not in ('DEBUG', 'INFO', 'WARNING'):
            error_msg = f'{level}: {record.msg}'
            self.window.show_error(error_msg)
