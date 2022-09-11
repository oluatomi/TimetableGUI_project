from PyQt5 import QtCore, QtGui, QtWidgets


# def widget_for_tree(icon_path="../Icons-mine/teacher.png",label_text="", with_checkbox=False):
    # """Function to generate the widgets which would go into the trees in the gui, rather than mere text"""

class WidgetTree(QtWidgets.QWidget):
    """Class to generate the widgets which would go into the trees in the gui, rather than mere text"""
    def __init__(self,icon_path="../Icons-mine/teacher.png",icon_width=14, icon_height=16, label_text="", with_checkbox=False):
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


    def get_checkbox(self):
        """Gets the checkbox"""
        return self.checkBox

    
    # Instantiate this mini-class
    # my_widget = WidgetTree(with_checkbox=with_checkbox)
    # return my_widget


class MyFontDialog(QtWidgets.QFontDialog, QtWidgets.QMainWindow):
    def __init__(self, title="Timetable Dialog", icon_path="../Icons-mine/App_logo.png"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.show()


class MyColourDialog(QtWidgets.QColorDialog, QtWidgets.QMainWindow):
    def __init__(self, title="Timetable Dialog", icon_path="../Icons-mine/App_logo.png"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.show()




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
