'''
Created by: Craig Fouts
Created on: 2/4/2021
'''

import os
from gui.config import Config
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMessageBox, QProgressBar, QProgressDialog

config = Config()
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_PATH, 'config_files/config.ini')
config.read(CONFIG_PATH)


class SavePopup(QMessageBox):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._configure_popup()

    def _configure_popup(self):
        '''TODO

        '''

        icon_path = os.path.join(PROJECT_PATH, config.get('Icons', 'main'))
        self.icon = QIcon(icon_path)
        self.setWindowIcon(self.icon)
        self.setWindowTitle('PyDre')
        self.setIcon(QMessageBox.Warning)
        buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        self.setStandardButtons(buttons)
        self.setDefaultButton(QMessageBox.Yes)

    def _callback(self, callback, e):
        '''TODO

        '''

        if e.text() == '&Yes':
            callback(True)
        elif e.text() == '&No':
            callback(False)
        self.buttonClicked.disconnect()

    def show_(self, text, callback):
        '''TODO

        '''

        self.setText(text)
        self.buttonClicked.connect(lambda e: self._callback(callback, e))
        self.show()
        return self


class FunctionPopup(QMessageBox):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon_path = os.path.join(PROJECT_PATH, config.get('Icons', 'main'))
        self.icon = QIcon(icon_path)
        self.setWindowIcon(self.icon)
        self.setWindowTitle('PyDre')
        self._configure_popup()

    def _configure_popup(self):
        '''TODO

        '''

        self.setIcon(QMessageBox.Warning)
        buttons = QMessageBox.Yes | QMessageBox.No
        self.setStandardButtons(buttons)
        self.setDefaultButton(QMessageBox.Yes)

    def _callback(self, callback, e):
        '''TODO

        '''

        if e.text() == '&Yes':
            callback(True)
        elif e.text() == '&No':
            callback(False)
        self.buttonClicked.disconnect()

    def show_(self, text, callback):
        '''TODO

        '''

        self.setText(text)
        self.buttonClicked.connect(lambda e: self._callback(callback, e))
        self.show()
        return self


class OutputPopup(QMessageBox):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon_path = os.path.join(PROJECT_PATH, config.get('Icons', 'main'))
        self.icon = QIcon(icon_path)
        self.setWindowIcon(self.icon)
        self.setWindowTitle('PyDre')
        self._configure_popup()

    def _configure_popup(self):
        '''TODO

        '''

        self.setIcon(QMessageBox.Warning)
        buttons = QMessageBox.Yes | QMessageBox.No
        self.setStandardButtons(buttons)
        self.setDefaultButton(QMessageBox.Yes)

    def _callback(self, callback, e):
        '''TODO

        '''

        if e.text() == '&Yes':
            callback(True)
        elif e.text() == '&No':
            callback(False)
        self.buttonClicked.disconnect()

    def show_(self, text, callback):
        '''TODO

        '''

        self.setText(text)
        self.buttonClicked.connect(lambda e: self._callback(callback, e))
        self.show()
        return self


class ProgressPopup(QProgressDialog):
    '''TODO

    '''

    def __init__(self, app, auto_close=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self._configure_popup(auto_close)

    def _configure_popup(self, auto_close):
        '''TODO

        '''

        self._configure_geometry(500, 170)
        self.setWindowTitle('PyDre')
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setAutoClose(auto_close)

    def _configure_geometry(self, width, height):
        '''TODO

        '''

        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

    def show_(self, text, _=None):
        '''TODO

        '''

        self.setLabelText(text)
        self.show()
        self.app.processEvents()
        return self
