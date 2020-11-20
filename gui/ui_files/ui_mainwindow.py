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
        MainWindow.resize(650, 500)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        MainWindow.setWindowOpacity(1.000000000000000)
        MainWindow.setStyleSheet(u"")
        self.pfile_act = QAction(MainWindow)
        self.pfile_act.setObjectName(u"pfile_act")
        self.pfile_act.setEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
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
        self.switch_btn = QPushButton(self.page)
        self.switch_btn.setObjectName(u"switch_btn")

        self.verticalLayout_4.addWidget(self.switch_btn)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)


        self.verticalLayout_6.addLayout(self.verticalLayout_4)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(self.page_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeWidget = QTreeWidget(self.splitter)
        self.treeWidget.setObjectName(u"treeWidget")
        self.splitter.addWidget(self.treeWidget)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setFocusPolicy(Qt.TabFocus)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.treeWidget_2 = QTreeWidget(self.tab)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeWidget_2.setHeaderItem(__qtreewidgetitem)
        self.treeWidget_2.setObjectName(u"treeWidget_2")

        self.verticalLayout_2.addWidget(self.treeWidget_2)

        self.tabWidget.addTab(self.tab, "")
        self.splitter.addWidget(self.tabWidget)

        self.verticalLayout_3.addWidget(self.splitter)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 650, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menuBar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuRun = QMenu(self.menuBar)
        self.menuRun.setObjectName(u"menuRun")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyDre", None))
        self.pfile_act.setText(QCoreApplication.translate("MainWindow", u"Project File", None))
        self.switch_btn.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Drop files here to open", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuRun.setTitle(QCoreApplication.translate("MainWindow", u"Run", None))
    # retranslateUi

