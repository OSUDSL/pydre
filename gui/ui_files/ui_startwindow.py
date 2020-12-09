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
        StartWindow.resize(600, 400)
        StartWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(StartWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.hsplitter = QSplitter(self.centralwidget)
        self.hsplitter.setObjectName(u"hsplitter")
        self.hsplitter.setOrientation(Qt.Horizontal)
        self.groupBox = QGroupBox(self.hsplitter)
        self.groupBox.setObjectName(u"groupBox")
        self.hsplitter.addWidget(self.groupBox)
        self.widget = QWidget(self.hsplitter)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(182, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout.addWidget(self.pushButton)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer_2 = QSpacerItem(182, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.hsplitter.addWidget(self.widget)

        self.verticalLayout_2.addWidget(self.hsplitter)

        StartWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(StartWindow)
        self.statusbar.setObjectName(u"statusbar")
        StartWindow.setStatusBar(self.statusbar)

        self.retranslateUi(StartWindow)

        QMetaObject.connectSlotsByName(StartWindow)
    # setupUi

    def retranslateUi(self, StartWindow):
        StartWindow.setWindowTitle(QCoreApplication.translate("StartWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("StartWindow", u"Recent files", None))
        self.pushButton.setText(QCoreApplication.translate("StartWindow", u"Open file", None))
        self.label.setText(QCoreApplication.translate("StartWindow", u"Drop file here to open", None))
    # retranslateUi

