# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Administrator\Desktop\pbf\updateDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_updateDialog(object):
    def setupUi(self, updateDialog):
        updateDialog.setObjectName("updateDialog")
        updateDialog.resize(400, 300)
        updateDialog.setStyleSheet("")
        self.label = QtWidgets.QLabel(updateDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 110, 40))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(updateDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 54, 12))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(updateDialog)
        self.label_3.setGeometry(QtCore.QRect(10, 100, 60, 12))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(updateDialog)
        self.label_4.setGeometry(QtCore.QRect(10, 120, 60, 12))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(updateDialog)
        self.label_5.setGeometry(QtCore.QRect(10, 80, 54, 12))
        self.label_5.setObjectName("label_5")
        self.versionBtn = QtWidgets.QLabel(updateDialog)
        self.versionBtn.setGeometry(QtCore.QRect(80, 60, 170, 12))
        self.versionBtn.setObjectName("versionBtn")
        self.nameBtn = QtWidgets.QLabel(updateDialog)
        self.nameBtn.setGeometry(QtCore.QRect(80, 80, 170, 12))
        self.nameBtn.setObjectName("nameBtn")
        self.timeBtn = QtWidgets.QLabel(updateDialog)
        self.timeBtn.setGeometry(QtCore.QRect(80, 100, 300, 12))
        self.timeBtn.setObjectName("timeBtn")
        self.descriptionBtn = QtWidgets.QLabel(updateDialog)
        self.descriptionBtn.setGeometry(QtCore.QRect(80, 120, 300, 130))
        self.descriptionBtn.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.descriptionBtn.setObjectName("descriptionBtn")
        self.groupBox = QtWidgets.QGroupBox(updateDialog)
        self.groupBox.setGeometry(QtCore.QRect(260, 10, 120, 101))
        self.groupBox.setObjectName("groupBox")
        self.installBtn = QtWidgets.QPushButton(self.groupBox)
        self.installBtn.setGeometry(QtCore.QRect(20, 40, 75, 23))
        self.installBtn.setObjectName("installBtn")
        self.cancelBtn = QtWidgets.QPushButton(self.groupBox)
        self.cancelBtn.setGeometry(QtCore.QRect(20, 70, 75, 23))
        self.cancelBtn.setObjectName("cancelBtn")
        self.label_10 = QtWidgets.QLabel(updateDialog)
        self.label_10.setGeometry(QtCore.QRect(10, 260, 380, 12))
        self.label_10.setObjectName("label_10")

        self.retranslateUi(updateDialog)
        QtCore.QMetaObject.connectSlotsByName(updateDialog)

    def retranslateUi(self, updateDialog):
        _translate = QtCore.QCoreApplication.translate
        updateDialog.setWindowTitle(_translate("updateDialog", "新版本发布"))
        self.label.setText(_translate("updateDialog", "版本更新"))
        self.label_2.setText(_translate("updateDialog", "版本号："))
        self.label_3.setText(_translate("updateDialog", "发布时间："))
        self.label_4.setText(_translate("updateDialog", "版本描述："))
        self.label_5.setText(_translate("updateDialog", "版本名："))
        self.versionBtn.setText(_translate("updateDialog", "TextLabel"))
        self.nameBtn.setText(_translate("updateDialog", "TextLabel"))
        self.timeBtn.setText(_translate("updateDialog", "TextLabel"))
        self.descriptionBtn.setText(_translate("updateDialog", "TextLabel"))
        self.groupBox.setTitle(_translate("updateDialog", "操作"))
        self.installBtn.setText(_translate("updateDialog", "安装/更新"))
        self.cancelBtn.setText(_translate("updateDialog", "取消"))
        self.label_10.setText(_translate("updateDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">请前往官网：<a href=\"https://qb.xzy.center/pbfl\"><span style=\" text-decoration: underline; color:#0000ff;\">https://qb.xzy.center/pbfl</span></a>下载更新</p></body></html>"))
