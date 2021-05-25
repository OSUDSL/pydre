'''
Created by: Craig Fouts
Created on: 2/4/2021
'''

from gui.config import Config
from os import path
from PySide2.QtWidgets import QMessageBox, QProgressBar, QProgressDialog

config = Config()
PROJECT_PATH = path.dirname(path.abspath(__file__))
CONFIG_PATH = path.join(PROJECT_PATH, 'config_files/config.ini')
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


class FunctionPopup(QMessageBox):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class OutputPopup(QMessageBox):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class ProgressPopup(QProgressDialog):
    '''TODO

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._configure_popup()

    def _configure_popup(self):
        '''TODO

        '''

        self.setMinimumWidth(400)
        self.setWindowTitle('PyDre')
        self.setLabelText('Converting...')
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setAutoClose(False)

    def show_(self):
        '''TODO

        '''

        self.show()
