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
        MainWindow.resize(500, 268)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setWindowOpacity(1.000000000000000)
        MainWindow.setStyleSheet(u"")
        self.pfile_act = QAction(MainWindow)
        self.pfile_act.setObjectName(u"pfile_act")
        self.pfile_act.setEnabled(False)
        self.new_action = QAction(MainWindow)
        self.new_action.setObjectName(u"new_action")
        self.open_action = QAction(MainWindow)
        self.open_action.setObjectName(u"open_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.page_stack = QStackedWidget(self.centralwidget)
        self.page_stack.setObjectName(u"page_stack")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_stack.sizePolicy().hasHeightForWidth())
        self.page_stack.setSizePolicy(sizePolicy)
        self.page_stack.setAcceptDrops(True)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_7 = QVBoxLayout(self.page)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_3 = QGroupBox(self.page)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.open_pfile_btn = QPushButton(self.groupBox_3)
        self.open_pfile_btn.setObjectName(u"open_pfile_btn")

        self.verticalLayout_10.addWidget(self.open_pfile_btn)

        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_10.addWidget(self.label_2)


        self.verticalLayout_4.addWidget(self.groupBox_3)


        self.verticalLayout_6.addLayout(self.verticalLayout_4)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        self.page_stack.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_9 = QVBoxLayout(self.page_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.splitter = QSplitter(self.page_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeWidget = QTreeWidget(self.splitter)
        self.treeWidget.setObjectName(u"treeWidget")
        self.splitter.addWidget(self.treeWidget)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pfile_tab = QTabWidget(self.groupBox_2)
        self.pfile_tab.setObjectName(u"pfile_tab")
        self.pfile_tab.setFocusPolicy(Qt.TabFocus)
        self.pfile_tab.setTabShape(QTabWidget.Rounded)
        self.pfile_tab.setTabsClosable(True)
        self.pfile_tab.setMovable(True)

        self.verticalLayout_3.addWidget(self.pfile_tab)

        self.splitter.addWidget(self.groupBox_2)

        self.verticalLayout_9.addWidget(self.splitter)

        self.page_stack.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_2 = QVBoxLayout(self.page_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.page_3)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_8.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.listWidget = QListWidget(self.groupBox)
        self.listWidget.setObjectName(u"listWidget")

        self.horizontalLayout.addWidget(self.listWidget)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_5.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_5.addWidget(self.pushButton_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_5)


        self.verticalLayout_8.addLayout(self.horizontalLayout)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_8.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout_8.addWidget(self.lineEdit)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_3 = QPushButton(self.page_3)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_3.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.page_3)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.pushButton_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.page_stack.addWidget(self.page_3)

        self.verticalLayout.addWidget(self.page_stack)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 500, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuRun = QMenu(self.menuBar)
        self.menuRun.setObjectName(u"menuRun")
        self.menuRun.setEnabled(False)
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())
        self.menuFile.addAction(self.new_action)
        self.menuFile.addAction(self.open_action)

        self.retranslateUi(MainWindow)

        self.page_stack.setCurrentIndex(0)
        self.pfile_tab.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyDre", None))
        self.pfile_act.setText(QCoreApplication.translate("MainWindow", u"Project File", None))
        self.new_action.setText(QCoreApplication.translate("MainWindow", u"New...", None))
        self.open_action.setText(QCoreApplication.translate("MainWindow", u"Open...", None))
        self.groupBox_3.setTitle("")
        self.open_pfile_btn.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Drop files here to open", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));
        self.groupBox_2.setTitle("")
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Data files", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Add file", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Output file (out.csv by default)", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuRun.setTitle(QCoreApplication.translate("MainWindow", u"Run", None))
    # retranslateUi

