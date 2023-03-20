# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'period_frame.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class PeriodFrame(QtWidgets.QFrame):
    def __init__(self, height=90):
        super().__init__()

        self.setupUi(height)
        # self.show()

    def setupUi(self, height):
        self.teacher_str = None
        self.dept = None
        self.faculty = None

        # ----------------------------
        # QSS stylesheet to apply to the self.subj_fr (subject self), whether this self has been tracked or not. 
        self.styles_on_track = {
        "tracked": "QWidget{\n"
            "background: #6fff93;\n"
            "border:none; \n"
            "border-top:1.5px solid #004a13;\n"
            "color:#004a13;"
            "}",
        "untracked": "QWidget{\n"
            "border:none;\n"
            "border-top: 1.5px solid #000059;\n"
            "}"
        }


        self.setObjectName("self")
        self.height = height
        self.resize(145, self.height)
        self.setMinimumSize(QtCore.QSize(145, 90))
        self.setMaximumSize(QtCore.QSize(145, 90))
        self.setStyleSheet("QFrame[objectName=\"self\"]{\n"
"    border-radius:5px;\n"
"    border:2.5px solid #000059;\n"
"}\n"
"\n"
"QFrame > QFrame{\n"
"    border:0.7px solid #808080;    \n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setStyleSheet("QScrollBar{\n"
"    background:#fff;\n"
"    height:6px;\n"
"    width:6px;\n"
"    \n"
"}\n"
"\n"
"QScrollBar::handle{\n"
"    background:#797979;\n"
"    border-radius:3px;\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -8, 129, 92))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(134, 16777215))
        self.scrollAreaWidgetContents.setStyleSheet("")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.p_name_fr = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.p_name_fr.setStyleSheet("QWidget{\n"
"    background:qlineargradient(spread:pad, x1:0.0266364, y1:0.523, x2:0.968, y2:0.535, stop:0.147727 rgba(42, 0, 127, 255), stop:0.8125 rgba(0, 0, 0, 255));\n"
"    color:#f9f9f9;\n"
"    font-weight:bold;\n"
"}")
        self.p_name_fr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.p_name_fr.setFrameShadow(QtWidgets.QFrame.Raised)
        self.p_name_fr.setObjectName("p_name_fr")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.p_name_fr)
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.p_name_fr)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.p_name_fr)
        self.p_dur_fr = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.p_dur_fr.setStyleSheet("QWidget{\n"
"    color: #934900;\n"
"    font-weight:bold;\n"
"    border:none;\n"
"}")
        self.p_dur_fr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.p_dur_fr.setFrameShadow(QtWidgets.QFrame.Raised)
        self.p_dur_fr.setObjectName("p_dur_fr")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.p_dur_fr)
        self.horizontalLayout_2.setContentsMargins(1, 3, 1, 3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.p_dur_fr)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout_2.addWidget(self.p_dur_fr)
        self.subj_fr = QtWidgets.QFrame(self.scrollAreaWidgetContents)

        # Set the subject self to untracked upon initialization
        self.subj_fr.setStyleSheet(self.styles_on_track["untracked"])

        self.subj_fr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.subj_fr.setFrameShadow(QtWidgets.QFrame.Raised)
        self.subj_fr.setObjectName("subj_fr")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.subj_fr)
        self.verticalLayout_3.setContentsMargins(0, 2, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.textEdit = QtWidgets.QTextEdit(self.subj_fr)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 35))
        self.textEdit.setStyleSheet("QTextEdit{\n"
"background:transparent;\n"
"}")
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_3.addWidget(self.textEdit)
        self.verticalLayout_2.addWidget(self.subj_fr)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "self"))
        self.label.setText(_translate("self", "period name (Acad or No)"))
        self.label_2.setText(_translate("self", "Period duration"))
        self.textEdit.setHtml(_translate("self", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p></body></html>"))
        self.textEdit.setPlaceholderText(_translate("self", "FREE"))


    def add_name_duration_content(self, name_id, duration_str, dept_name):
        """ Method to add name, duration and name of subject to the period_frame widget """
        self.label.setText(name_id)
        self.label_2.setText(duration_str)
        self.textEdit.setHtml(f"""
            <html>
                <p style="text-align:center; color:#161616;font-size:8.5pt;
                font-family: calibri; font-weight:bold;">{dept_name}</p>
            </html>
            """)

    def add_teacher_dept_fac_str(self, teacher_str, dept_str, fac_str):
        """ sets the self.teacher variable to the full name (str) of the teacher object.
        Purposefully put here for tracking or None if the teacher does not exist """
        self.teacher = teacher_str
        self.dept = dept_str
        self.faculty = fac_str


    def _colour_based_on_track(self, tracked=False):
        """ Method to change the design of this frame if it happens to carry a tracked item """
        tracked_key = "tracked" if tracked else "untracked"
        self.subj_fr.setStyleSheet(self.styles_on_track[tracked_key])


    def _string_matches(self, match_str):
        """ BOOL. Returns whether or not 'match_str' matches any of this instance's dept, teacher, or faculty values """
        return match_str in (self.teacher, self.dept, self.faculty)


    def match_and_colour_based_on_track(self, match_str):
        """ Matches 'match_str' with the dept, teacher, faculty parameters and colours the subj_fr if there is 
        a match """
        match = self._string_matches(match_str)
        self._colour_based_on_track(tracked=match)



# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
class ArmFrame(QtWidgets.QFrame):
    def __init__(self, width=125, height=90):
        super().__init__()

        self.setupUi(width, height)
        # self.show()

    def setupUi(self, width, height):
        self.setObjectName("self")
        self.resize(width, height)
        self.setMinimumSize(QtCore.QSize(125, 90))
        self.setMaximumSize(QtCore.QSize(125, 90))
        self.setStyleSheet("QFrame{\n"
"    border:0.9px solid black;\n"
"}\n"
"\n"
"\n"
"QFrame[objectName=\"self\"]{\n"
"    border:2.5px solid #000059;\n"
"    border-radius:5px;\n"
"    background:#fcfcfc;\n"
"}\n"
"\n"
"\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self)
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

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "self"))
        self.label_2.setText(_translate("self", "Day or Class arm"))
        self.label.setText(_translate("self", "arm_name or_day_name"))


    def add_arm_fullname(self, fullname_str):
        """ Changes the label title into the name of the arm """
        self.label.setText(fullname_str)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # Frame = QtWidgets.QFrame()
    ui = ArmFrame()
    # ui.add_teacher_dept_fac_str("teacher_str", "dept_str", "fac_str")
    # ui.match_and_colour_based_on_track("dept_str")
    # ui.setupUi()
    # ui.show()
    # Frame.show()
    sys.exit(app.exec_())
