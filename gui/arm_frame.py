# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'arm_frame.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(125, 90)
        Frame.setMinimumSize(QtCore.QSize(125, 90))
        Frame.setMaximumSize(QtCore.QSize(125, 90))
        Frame.setStyleSheet("QFrame{\n"
"    border:0.9px solid black;\n"
"}\n"
"\n"
"\n"
"QFrame[objectName=\"Frame\"]{\n"
"    border:2.5px solid #000059;\n"
"    border-radius:5px;\n"
"    background:#fcfcfc;\n"
"}\n"
"\n"
"\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(Frame)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(Frame)
        self.scrollArea.setStyleSheet("QScrollBar{\n"
"    width:6px;\n"
"    height:6px;\n"
"    background:transparent;\n"
"}\n"
"\n"
"QScrollBar::handle{\n"
"    background:#787878;\n"
"    border-radius:3px;\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 115, 80))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.title_frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.title_frame.setStyleSheet("QLabel{\n"
"    color:#000062;\n"
"    font-weight:bold;\n"
"}\n"
"\n"
"QWidget{\n"
"    border:none;\n"
"}")
        self.title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.title_frame.setObjectName("title_frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.title_frame)
        self.verticalLayout_4.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.title_frame)
        self.label_2.setStyleSheet("padding:2px;")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.verticalLayout_2.addWidget(self.title_frame)
        self.arm_or_day_fr = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.arm_or_day_fr.sizePolicy().hasHeightForWidth())
        self.arm_or_day_fr.setSizePolicy(sizePolicy)
        self.arm_or_day_fr.setStyleSheet("QLabel{\n"
"    color:#824100;\n"
"    font-weight:bold;\n"
"    font-size:8pt;\n"
"}\n"
"\n"
"QWidget{\n"
"    border:none;\n"
"    border-top:2px solid #000059;\n"
"}")
        self.arm_or_day_fr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.arm_or_day_fr.setFrameShadow(QtWidgets.QFrame.Raised)
        self.arm_or_day_fr.setObjectName("arm_or_day_fr")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.arm_or_day_fr)
        self.verticalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.arm_or_day_fr)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.arm_or_day_fr)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.label_2.setText(_translate("Frame", "Day or Class arm"))
        self.label.setText(_translate("Frame", "arm_name or_day_name"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Frame = QtWidgets.QFrame()
    ui = Ui_Frame()
    ui.setupUi(Frame)
    Frame.show()
    sys.exit(app.exec_())
