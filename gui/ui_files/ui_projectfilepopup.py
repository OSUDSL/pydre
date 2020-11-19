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
        Form.resize(500, 400)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pfile_tree = QTreeWidget(Form)
        self.pfile_tree.setObjectName(u"pfile_tree")
        self.pfile_tree.setAnimated(True)

        self.verticalLayout.addWidget(self.pfile_tree)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.cancel_btn = QPushButton(Form)
        self.cancel_btn.setObjectName(u"cancel_btn")

        self.horizontalLayout_2.addWidget(self.cancel_btn)

        self.save_btn = QPushButton(Form)
        self.save_btn.setObjectName(u"save_btn")
        self.save_btn.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.save_btn)

        self.finish_btn = QPushButton(Form)
        self.finish_btn.setObjectName(u"finish_btn")
        self.finish_btn.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.finish_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        ___qtreewidgetitem = self.pfile_tree.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Form", u"Project parameters", None));
        self.cancel_btn.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.save_btn.setText(QCoreApplication.translate("Form", u"Save", None))
        self.finish_btn.setText(QCoreApplication.translate("Form", u"Finish", None))
    # retranslateUi

