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
        StartWindow.setStyleSheet(u"background-color: rgb(70, 80, 80)")
        self.centralwidget = QWidget(StartWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.hsplitter = QSplitter(self.centralwidget)
        self.hsplitter.setObjectName(u"hsplitter")
        self.hsplitter.setOrientation(Qt.Horizontal)
        self.widget = QWidget(self.hsplitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: rgb(220, 220, 220);\n"
"background-color: rgb(50, 60, 60);\n"
"padding-left: 4px;\n"
"padding-top: 8px;\n"
"padding-bottom: 8px;\n"
"font: 75 10pt \"Arial\";")
        self.label_2.setIndent(-1)

        self.verticalLayout_2.addWidget(self.label_2)

        self.listView = QListView(self.widget)
        self.listView.setObjectName(u"listView")
        self.listView.setStyleSheet(u"background-color: rgb(220, 220, 220)")
        self.listView.setFrameShadow(QFrame.Plain)

        self.verticalLayout_2.addWidget(self.listView)

        self.hsplitter.addWidget(self.widget)
        self.widget1 = QWidget(self.hsplitter)
        self.widget1.setObjectName(u"widget1")
        self.horizontalLayout = QHBoxLayout(self.widget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(24, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.widget1)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"background-color: rgb(50, 60, 60);")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setStyleSheet(u"background-color: rgb(220, 220, 220);\n"
"font: 75 10pt \"Arial\";")
        self.pushButton.setFlat(False)

        self.verticalLayout_4.addWidget(self.pushButton)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"color: rgb(220, 220, 220);\n"
"font: 75 10pt \"Arial\";")

        self.verticalLayout_4.addWidget(self.label)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer_2 = QSpacerItem(25, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.hsplitter.addWidget(self.widget1)

        self.verticalLayout_3.addWidget(self.hsplitter)

        StartWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(StartWindow)

        QMetaObject.connectSlotsByName(StartWindow)
    # setupUi

    def retranslateUi(self, StartWindow):
        StartWindow.setWindowTitle(QCoreApplication.translate("StartWindow", u"Pydre", None))
        self.label_2.setText(QCoreApplication.translate("StartWindow", u"Recent files", None))
        self.groupBox.setTitle("")
        self.pushButton.setText(QCoreApplication.translate("StartWindow", u"Open file", None))
        self.label.setText(QCoreApplication.translate("StartWindow", u"Drop file here to open", None))
    # retranslateUi

