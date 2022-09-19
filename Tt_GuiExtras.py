from PyQt5 import QtCore, QtGui, QtWidgets


# def widget_for_tree(icon_path="../Icons-mine/teacher.png",label_text="", with_checkbox=False):
    # """Function to generate the widgets which would go into the trees in the gui, rather than mere text"""

class WidgetTree(QtWidgets.QWidget):
    """Class to generate the widgets which would go into the trees in the gui, rather than mere text"""
    def __init__(self,icon_path="../Icons-mine/teacher.png",icon_width=14, icon_height=16, label_text="",extra_text="",with_checkbox=False):
        super().__init__()
        self.setGeometry(QtCore.QRect(20, 20, 194, 51))
        self.resize(31, 191)
        self.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(4, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setMaximumSize(QtCore.QSize(15, 19))
        self.checkBox.setText("")
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        self.checkBox.hide()

        self.extra_text = QtWidgets.QLabel(extra_text)
        # If checkbox is desired to be added
        if with_checkbox:
            self.checkBox.show()                

        self.label = QtWidgets.QLabel(self)
        self.label.setMaximumSize(QtCore.QSize(icon_width, icon_height))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(icon_path))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.full_name_label = QtWidgets.QLabel(self)
        self.full_name_label.setObjectName("full_name_label")
        self.full_name_label.setText(label_text)
        self.horizontalLayout.addWidget(self.full_name_label)
        self.horizontalLayout.addWidget(self.extra_text)


    def get_checkbox(self):
        """Gets the checkbox"""
        return self.checkBox

    def add_extra_text(self, txt, color="black"):
        """ Adds text to the self.extra_text label """
        self.extra_text.setText(txt)
        self.extra_text.setStyleSheet(f"""
            color:{color};
            """)


    

class MySpinBox(QtWidgets.QSpinBox):
    """ Generate the special kind of spinbox that sits in a table """
    def __init__(self, minimum=0, maximum=None, border="1px solid black",rad=0, color="black",
        background="white",padding="0px 0px 0px 0px", enabled=True):
        super().__init__()

        self.setMinimum(minimum)
        if maximum:
            self.setMaximum(maximum)

        self.setStyleSheet(f""" 
            border:{border};
            border-radius:{rad};
            color:{color};
            background:{background};
            padding:{padding};
         """)
        self.setEnabled(enabled)

    def render_enabled(self, enable=True):
        self.setEnabled(enable)
        styles = self.styleSheet()
        styles += f"color:{'#151515' if enable else '#b9b9b9'};"
        self.setStyleSheet(styles)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    fontd = MyFontDialog()
    fontd.show()
    # ui = Ui_Form()
    # ui.setupUi(Form)
    # Form.show()
    # widget_for_tree()

    sys.exit(app.exec_())
