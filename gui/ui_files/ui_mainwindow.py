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
        MainWindow.setEnabled(True)
        MainWindow.resize(600, 296)
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
        self.run_action = QAction(MainWindow)
        self.run_action.setObjectName(u"run_action")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedu = QAction(MainWindow)
        self.actionRedu.setObjectName(u"actionRedu")
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        self.actionCut = QAction(MainWindow)
        self.actionCut.setObjectName(u"actionCut")
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        self.actionAdvanced = QAction(MainWindow)
        self.actionAdvanced.setObjectName(u"actionAdvanced")
        self.actionFind = QAction(MainWindow)
        self.actionFind.setObjectName(u"actionFind")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(MainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionSave_all = QAction(MainWindow)
        self.actionSave_all.setObjectName(u"actionSave_all")
        self.actionRevert_FILE_NAME = QAction(MainWindow)
        self.actionRevert_FILE_NAME.setObjectName(u"actionRevert_FILE_NAME")
        self.actionClose_2 = QAction(MainWindow)
        self.actionClose_2.setObjectName(u"actionClose_2")
        self.actionTool_windows = QAction(MainWindow)
        self.actionTool_windows.setObjectName(u"actionTool_windows")
        self.actionTheme = QAction(MainWindow)
        self.actionTheme.setObjectName(u"actionTheme")
        self.actionLog = QAction(MainWindow)
        self.actionLog.setObjectName(u"actionLog")
        self.actionRecent = QAction(MainWindow)
        self.actionRecent.setObjectName(u"actionRecent")
        self.actionRecently_changed = QAction(MainWindow)
        self.actionRecently_changed.setObjectName(u"actionRecently_changed")
        self.actionRun = QAction(MainWindow)
        self.actionRun.setObjectName(u"actionRun")
        self.actionEdit_configurations = QAction(MainWindow)
        self.actionEdit_configurations.setObjectName(u"actionEdit_configurations")
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
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.vsplitter = QSplitter(self.page_2)
        self.vsplitter.setObjectName(u"vsplitter")
        self.vsplitter.setOrientation(Qt.Vertical)
        self.splitter = QSplitter(self.vsplitter)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.hsplitter = QSplitter(self.groupBox_2)
        self.hsplitter.setObjectName(u"hsplitter")
        self.hsplitter.setOrientation(Qt.Horizontal)
        self.treeWidget = QTreeWidget(self.hsplitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeWidget.setHeaderItem(__qtreewidgetitem)
        self.treeWidget.setObjectName(u"treeWidget")
        self.hsplitter.addWidget(self.treeWidget)
        self.pfile_tab = QTabWidget(self.hsplitter)
        self.pfile_tab.setObjectName(u"pfile_tab")
        self.pfile_tab.setFocusPolicy(Qt.TabFocus)
        self.pfile_tab.setTabShape(QTabWidget.Rounded)
        self.pfile_tab.setTabsClosable(True)
        self.pfile_tab.setMovable(True)
        self.hsplitter.addWidget(self.pfile_tab)

        self.verticalLayout_9.addWidget(self.hsplitter)

        self.splitter.addWidget(self.groupBox_2)
        self.vsplitter.addWidget(self.splitter)
        self.groupBox = QGroupBox(self.vsplitter)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.verticalLayout_11.addWidget(self.lineEdit_2)

        self.textBrowser = QTextBrowser(self.groupBox)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_11.addWidget(self.textBrowser)

        self.vsplitter.addWidget(self.groupBox)

        self.verticalLayout_3.addWidget(self.vsplitter)

        self.page_stack.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_2 = QVBoxLayout(self.page_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pfile_label = QLabel(self.page_3)
        self.pfile_label.setObjectName(u"pfile_label")

        self.verticalLayout_2.addWidget(self.pfile_label)

        self.run_box = QGroupBox(self.page_3)
        self.run_box.setObjectName(u"run_box")
        self.verticalLayout_8 = QVBoxLayout(self.run_box)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label = QLabel(self.run_box)
        self.label.setObjectName(u"label")

        self.verticalLayout_8.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.listWidget = QListWidget(self.run_box)
        self.listWidget.setObjectName(u"listWidget")

        self.horizontalLayout.addWidget(self.listWidget)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pushButton = QPushButton(self.run_box)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_5.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.run_box)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_5.addWidget(self.pushButton_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_5)


        self.verticalLayout_8.addLayout(self.horizontalLayout)

        self.label_3 = QLabel(self.run_box)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_8.addWidget(self.label_3)

        self.lineEdit = QLineEdit(self.run_box)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout_8.addWidget(self.lineEdit)


        self.verticalLayout_2.addWidget(self.run_box)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.cancel_btn = QPushButton(self.page_3)
        self.cancel_btn.setObjectName(u"cancel_btn")

        self.horizontalLayout_3.addWidget(self.cancel_btn)

        self.pushButton_4 = QPushButton(self.page_3)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.pushButton_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.page_stack.addWidget(self.page_3)

        self.verticalLayout.addWidget(self.page_stack)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menu_bar = QMenuBar(MainWindow)
        self.menu_bar.setObjectName(u"menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 600, 21))
        self.file_menu = QMenu(self.menu_bar)
        self.file_menu.setObjectName(u"file_menu")
        self.edit_menu = QMenu(self.menu_bar)
        self.edit_menu.setObjectName(u"edit_menu")
        self.view_menu = QMenu(self.menu_bar)
        self.view_menu.setObjectName(u"view_menu")
        self.run_menu = QMenu(self.menu_bar)
        self.run_menu.setObjectName(u"run_menu")
        self.run_menu.setEnabled(True)
        MainWindow.setMenuBar(self.menu_bar)

        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.edit_menu.menuAction())
        self.menu_bar.addAction(self.view_menu.menuAction())
        self.menu_bar.addAction(self.run_menu.menuAction())
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actionSave)
        self.file_menu.addAction(self.actionSave_as)
        self.file_menu.addAction(self.actionSave_all)
        self.file_menu.addAction(self.actionRevert_FILE_NAME)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.actionClose_2)
        self.edit_menu.addAction(self.actionUndo)
        self.edit_menu.addAction(self.actionRedu)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actionPaste)
        self.edit_menu.addAction(self.actionCopy)
        self.edit_menu.addAction(self.actionCut)
        self.edit_menu.addAction(self.actionDelete)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actionFind)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.actionAdvanced)
        self.view_menu.addAction(self.actionTool_windows)
        self.view_menu.addAction(self.actionTheme)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.actionLog)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.actionRecently_changed)
        self.view_menu.addAction(self.actionRecent)
        self.run_menu.addAction(self.run_action)
        self.run_menu.addAction(self.actionRun)
        self.run_menu.addSeparator()
        self.run_menu.addAction(self.actionEdit_configurations)

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
        self.run_action.setText(QCoreApplication.translate("MainWindow", u"Run -", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.actionRedu.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
        self.actionCut.setText(QCoreApplication.translate("MainWindow", u"Cut", None))
        self.actionDelete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.actionAdvanced.setText(QCoreApplication.translate("MainWindow", u"Advanced...", None))
        self.actionFind.setText(QCoreApplication.translate("MainWindow", u"Find...", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_as.setText(QCoreApplication.translate("MainWindow", u"Save as...", None))
        self.actionSave_all.setText(QCoreApplication.translate("MainWindow", u"Save all", None))
        self.actionRevert_FILE_NAME.setText(QCoreApplication.translate("MainWindow", u"Revert -", None))
        self.actionClose_2.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionTool_windows.setText(QCoreApplication.translate("MainWindow", u"Tool windows...", None))
        self.actionTheme.setText(QCoreApplication.translate("MainWindow", u"Appearance...", None))
        self.actionLog.setText(QCoreApplication.translate("MainWindow", u"Log", None))
        self.actionRecent.setText(QCoreApplication.translate("MainWindow", u"Recent changes", None))
        self.actionRecently_changed.setText(QCoreApplication.translate("MainWindow", u"Recently changed", None))
        self.actionRun.setText(QCoreApplication.translate("MainWindow", u"Run...", None))
        self.actionEdit_configurations.setText(QCoreApplication.translate("MainWindow", u"Edit configurations...", None))
        self.groupBox_3.setTitle("")
        self.open_pfile_btn.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Drop files here to open", None))
        self.groupBox_2.setTitle("")
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Log", None))
        self.pfile_label.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.run_box.setTitle("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Data files", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Add file", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Output file (out.csv by default)", None))
        self.cancel_btn.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.file_menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.edit_menu.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.view_menu.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.run_menu.setTitle(QCoreApplication.translate("MainWindow", u"Run", None))
    # retranslateUi

