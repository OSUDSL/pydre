# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'startwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_StartWindow(object):
    def setupUi(self, StartWindow):
        if not StartWindow.objectName():
            StartWindow.setObjectName(u"StartWindow")
        StartWindow.resize(800, 600)
        self.centralwidget = QWidget(StartWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        StartWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(StartWindow)
        self.statusbar.setObjectName(u"statusbar")
        StartWindow.setStatusBar(self.statusbar)

        self.retranslateUi(StartWindow)

        QMetaObject.connectSlotsByName(StartWindow)
    # setupUi

    def retranslateUi(self, StartWindow):
        StartWindow.setWindowTitle(QCoreApplication.translate("StartWindow", u"MainWindow", None))
    # retranslateUi

