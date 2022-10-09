# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\WolongRun\GUI\SEEMS_Help_About.ui'
#
# Created: Wed Jun 10 17:06:37 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_SEEMS_help_about(object):
    def setupUi(self, SEEMS_help_about):
        SEEMS_help_about.setObjectName(_fromUtf8("SEEMS_help_about"))
        SEEMS_help_about.resize(475, 300)
        self.btn_OK = QPushButton(SEEMS_help_about)
        self.btn_OK.setGeometry(QtCore.QRect(180, 250, 112, 34))
        self.btn_OK.setObjectName(_fromUtf8("btn_OK"))
        self.lbl_SEEMS_about = QLabel(SEEMS_help_about)
        self.lbl_SEEMS_about.setGeometry(QtCore.QRect(10, 30, 451, 201))
        self.lbl_SEEMS_about.setObjectName(_fromUtf8("lbl_SEEMS_about"))

        self.retranslateUi(SEEMS_help_about)
        QtCore.QMetaObject.connectSlotsByName(SEEMS_help_about)

    def retranslateUi(self, SEEMS_help_about):
        SEEMS_help_about.setWindowTitle(_translate("SEEMS_help_about", "SEEMS - About", None))
        self.btn_OK.setText(_translate("SEEMS_help_about", "OK", None))
        self.lbl_SEEMS_about.setText(_translate("SEEMS_help_about", "<html><head/><body><p align=\"center\">SEEMS - Socio-Econ-Ecosystem Multipurpose Simulator</p><p align=\"center\">v 0.9.0</p><p align=\"center\">Created by Liyan Xu and Hongmou Zhang</p><p align=\"center\">@MIT</p><p align=\"center\">2015.6.9</p></body></html>", None))


# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui=Ui_SEEMS_help_about()
    main=QMainWindow()
    ui.setupUi(main)


    main.show()
    app.exec_()

