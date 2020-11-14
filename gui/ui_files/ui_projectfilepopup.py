# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'projectfilepopup.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 261)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pfile_tree = QTreeWidget(Form)
        __qtreewidgetitem = QTreeWidgetItem(self.pfile_tree)
        __qtreewidgetitem.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.pfile_tree.setObjectName(u"pfile_tree")

        self.verticalLayout.addWidget(self.pfile_tree)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_2.addWidget(self.pushButton_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        ___qtreewidgetitem = self.pfile_tree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Form", u"1", None));

        __sortingEnabled = self.pfile_tree.isSortingEnabled()
        self.pfile_tree.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.pfile_tree.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Form", u"Project parameters", None));
        self.pfile_tree.setSortingEnabled(__sortingEnabled)

        self.pushButton.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Save", None))
    # retranslateUi

