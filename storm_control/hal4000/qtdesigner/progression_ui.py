# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progression.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(380, 312)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(360, 312))
        Dialog.setMaximumSize(QtCore.QSize(380, 312))
        self.progressionsBox = QtWidgets.QGroupBox(Dialog)
        self.progressionsBox.setGeometry(QtCore.QRect(10, 0, 361, 271))
        self.progressionsBox.setObjectName("progressionsBox")
        self.gridLayout = QtWidgets.QGridLayout(self.progressionsBox)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.progressionsBox)
        self.tabWidget.setObjectName("tabWidget")
        self.linearTab = QtWidgets.QWidget()
        self.linearTab.setObjectName("linearTab")
        self.channelLabel = QtWidgets.QLabel(self.linearTab)
        self.channelLabel.setGeometry(QtCore.QRect(10, 10, 46, 14))
        self.channelLabel.setObjectName("channelLabel")
        self.activeLabel = QtWidgets.QLabel(self.linearTab)
        self.activeLabel.setGeometry(QtCore.QRect(60, 10, 46, 14))
        self.activeLabel.setObjectName("activeLabel")
        self.startLabel = QtWidgets.QLabel(self.linearTab)
        self.startLabel.setGeometry(QtCore.QRect(120, 10, 46, 14))
        self.startLabel.setObjectName("startLabel")
        self.incrementLabel = QtWidgets.QLabel(self.linearTab)
        self.incrementLabel.setGeometry(QtCore.QRect(190, 7, 81, 20))
        self.incrementLabel.setObjectName("incrementLabel")
        self.framesLabel = QtWidgets.QLabel(self.linearTab)
        self.framesLabel.setGeometry(QtCore.QRect(260, 7, 46, 21))
        self.framesLabel.setObjectName("framesLabel")
        self.tabWidget.addTab(self.linearTab, "")
        self.expTab = QtWidgets.QWidget()
        self.expTab.setObjectName("expTab")
        self.framesLabel_2 = QtWidgets.QLabel(self.expTab)
        self.framesLabel_2.setGeometry(QtCore.QRect(260, 7, 46, 21))
        self.framesLabel_2.setObjectName("framesLabel_2")
        self.activeLabel_2 = QtWidgets.QLabel(self.expTab)
        self.activeLabel_2.setGeometry(QtCore.QRect(60, 10, 46, 14))
        self.activeLabel_2.setObjectName("activeLabel_2")
        self.startLabel_2 = QtWidgets.QLabel(self.expTab)
        self.startLabel_2.setGeometry(QtCore.QRect(120, 10, 46, 14))
        self.startLabel_2.setObjectName("startLabel_2")
        self.incrementLabel_2 = QtWidgets.QLabel(self.expTab)
        self.incrementLabel_2.setGeometry(QtCore.QRect(190, 7, 81, 20))
        self.incrementLabel_2.setObjectName("incrementLabel_2")
        self.channelLabel_2 = QtWidgets.QLabel(self.expTab)
        self.channelLabel_2.setGeometry(QtCore.QRect(10, 10, 46, 14))
        self.channelLabel_2.setObjectName("channelLabel_2")
        self.tabWidget.addTab(self.expTab, "")
        self.fileTab = QtWidgets.QWidget()
        self.fileTab.setObjectName("fileTab")
        self.powerLabel = QtWidgets.QLabel(self.fileTab)
        self.powerLabel.setGeometry(QtCore.QRect(10, 10, 61, 16))
        self.powerLabel.setObjectName("powerLabel")
        self.loadFileButton = QtWidgets.QPushButton(self.fileTab)
        self.loadFileButton.setGeometry(QtCore.QRect(250, 30, 75, 23))
        self.loadFileButton.setObjectName("loadFileButton")
        self.filenameLabel = QtWidgets.QLabel(self.fileTab)
        self.filenameLabel.setGeometry(QtCore.QRect(70, 10, 261, 16))
        self.filenameLabel.setObjectName("filenameLabel")
        self.tabWidget.addTab(self.fileTab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(256, 280, 75, 24))
        self.okButton.setObjectName("okButton")
        self.progressionsCheckBox = QtWidgets.QCheckBox(Dialog)
        self.progressionsCheckBox.setGeometry(QtCore.QRect(10, 280, 151, 18))
        self.progressionsCheckBox.setObjectName("progressionsCheckBox")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "HAL-4000 Power Progressions"))
        self.progressionsBox.setTitle(_translate("Dialog", "Power Progressions"))
        self.channelLabel.setText(_translate("Dialog", "Channel"))
        self.activeLabel.setText(_translate("Dialog", "Active"))
        self.startLabel.setText(_translate("Dialog", "Start"))
        self.incrementLabel.setText(_translate("Dialog", "Increment"))
        self.framesLabel.setText(_translate("Dialog", "Frames"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.linearTab), _translate("Dialog", "Linear"))
        self.framesLabel_2.setText(_translate("Dialog", "Frames"))
        self.activeLabel_2.setText(_translate("Dialog", "Active"))
        self.startLabel_2.setText(_translate("Dialog", "Start"))
        self.incrementLabel_2.setText(_translate("Dialog", "Multiplier"))
        self.channelLabel_2.setText(_translate("Dialog", "Channel"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.expTab), _translate("Dialog", "Exponential"))
        self.powerLabel.setText(_translate("Dialog", "Power File:"))
        self.loadFileButton.setText(_translate("Dialog", "Load File"))
        self.filenameLabel.setText(_translate("Dialog", "None"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fileTab), _translate("Dialog", "From File"))
        self.okButton.setText(_translate("Dialog", "Ok"))
        self.progressionsCheckBox.setText(_translate("Dialog", "Use Power Progressions"))

