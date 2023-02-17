# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'check_lineedit.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(265, 159)
        self.lineEdit = QtWidgets.QSpinBox(Form)
        self.lineEdit.setGeometry(QtCore.QRect(30, 45, 113, 20))
        self.lineEdit.setFrame(True)
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(55, 105, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.print_lineedit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lineEdit.setPlaceholderText(_translate("Form", "tomi is a boy"))
        self.pushButton.setText(_translate("Form", "check"))

    def print_lineedit(self):
        print(" spinboxis below")
        print(self.lineEdit.value())
        print(type(self.lineEdit.value()))
        print(bool(self.lineEdit.value()))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
