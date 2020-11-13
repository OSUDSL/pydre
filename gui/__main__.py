# """
# Created by: Craig Fouts
# Created on: 9/17/2020
# """


from PySide2.QtWidgets import QApplication
import sys
from gui.windows import MainWindow


class Application(QApplication):
    """
    TODO
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main = MainWindow()
        self.main.show()


if __name__ == '__main__':
    Application(sys.argv).exec_()
