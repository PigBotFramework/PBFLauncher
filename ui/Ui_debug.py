# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Administrator\Desktop\pbf\ui\debug.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_debugDialog(object):
    def setupUi(self, debugDialog):
        debugDialog.setObjectName("debugDialog")
        debugDialog.resize(400, 449)
        self.groupBox = QtWidgets.QGroupBox(debugDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 381, 250))
        self.groupBox.setObjectName("groupBox")
        self.exec = QtWidgets.QLineEdit(self.groupBox)
        self.exec.setGeometry(QtCore.QRect(80, 40, 113, 20))
        self.exec.setObjectName("exec")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 40, 60, 12))
        self.label.setObjectName("label")
        self.threadBox = QtWidgets.QCheckBox(self.groupBox)
        self.threadBox.setGeometry(QtCore.QRect(20, 70, 220, 31))
        self.threadBox.setObjectName("threadBox")
        self.execBtn = QtWidgets.QPushButton(self.groupBox)
        self.execBtn.setGeometry(QtCore.QRect(270, 30, 75, 61))
        self.execBtn.setObjectName("execBtn")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(20, 130, 330, 100))
        self.textEdit.setObjectName("textEdit")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(20, 110, 54, 12))
        self.label_2.setObjectName("label_2")
        self.groupBox_2 = QtWidgets.QGroupBox(debugDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 280, 381, 140))
        self.groupBox_2.setObjectName("groupBox_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setGeometry(QtCore.QRect(10, 40, 360, 90))
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(debugDialog)
        QtCore.QMetaObject.connectSlotsByName(debugDialog)

    def retranslateUi(self, debugDialog):
        _translate = QtCore.QCoreApplication.translate
        debugDialog.setWindowTitle(_translate("debugDialog", "Debug????????????"))
        self.groupBox.setTitle(_translate("debugDialog", "????????????"))
        self.label.setText(_translate("debugDialog", "???????????????"))
        self.threadBox.setText(_translate("debugDialog", "??????Thread????????????????????????"))
        self.execBtn.setText(_translate("debugDialog", "??????"))
        self.textEdit.setPlaceholderText(_translate("debugDialog", "????????????????????????????????????????????????????????????????????????????????????"))
        self.label_2.setText(_translate("debugDialog", "????????????"))
        self.groupBox_2.setTitle(_translate("debugDialog", "????????????"))
