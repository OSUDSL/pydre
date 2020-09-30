# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(600, 326)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setWindowOpacity(1.000000000000000)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.pfile_inp = QLineEdit(self.groupBox_2)
        self.pfile_inp.setObjectName(u"pfile_inp")

        self.horizontalLayout_8.addWidget(self.pfile_inp)

        self.pfile_btn = QToolButton(self.groupBox_2)
        self.pfile_btn.setObjectName(u"pfile_btn")
        self.pfile_btn.setStyleSheet(u"width: 75%;")

        self.horizontalLayout_8.addWidget(self.pfile_btn)


        self.verticalLayout_4.addLayout(self.horizontalLayout_8)

        self.line_2 = QFrame(self.groupBox_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line_2)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_4.addWidget(self.label_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.dfile_inp = QListWidget(self.groupBox_2)
        self.dfile_inp.setObjectName(u"dfile_inp")

        self.horizontalLayout_7.addWidget(self.dfile_inp)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.dfile_btn = QToolButton(self.groupBox_2)
        self.dfile_btn.setObjectName(u"dfile_btn")
        self.dfile_btn.setStyleSheet(u"width: 75%;")

        self.verticalLayout_2.addWidget(self.dfile_btn, 0, Qt.AlignTop)

        self.remove_btn = QToolButton(self.groupBox_2)
        self.remove_btn.setObjectName(u"remove_btn")
        self.remove_btn.setEnabled(False)
        self.remove_btn.setStyleSheet(u"width: 75%;")

        self.verticalLayout_2.addWidget(self.remove_btn, 0, Qt.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_7.addLayout(self.verticalLayout_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)

        self.line = QFrame(self.groupBox_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.verticalLayout_4.addWidget(self.label)

        self.ofile_inp = QLineEdit(self.groupBox_2)
        self.ofile_inp.setObjectName(u"ofile_inp")
        self.ofile_inp.setEnabled(True)

        self.verticalLayout_4.addWidget(self.ofile_inp)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.convert_btn = QPushButton(self.centralwidget)
        self.convert_btn.setObjectName(u"convert_btn")
        self.convert_btn.setEnabled(False)

        self.verticalLayout.addWidget(self.convert_btn)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 600, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyDre", None))
        self.groupBox_2.setTitle("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Project file", None))
        self.pfile_btn.setText(QCoreApplication.translate("MainWindow", u"Add File", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Data files", None))
        self.dfile_btn.setText(QCoreApplication.translate("MainWindow", u"Add File", None))
        self.remove_btn.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Output file (out.csv by default)", None))
        self.ofile_inp.setText("")
        self.convert_btn.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
    # retranslateUi

