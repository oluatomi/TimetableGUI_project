from PyQt5 import QtCore, QtGui, QtWidgets
from ..models import Tt_manager


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



class PeriodsContainer(QtWidgets.QFrame):
    count = 0
    def __init__(self, class_arm_fullname, day_fullname, width=122, height=42):
        """ class arm fullname and day_fullname could either be the fullname strings or the actual objects """
        super().__init__()

        # self.resize(, 50)
        # self.setMinimumSize(QtCore.QSize(100, 28))

        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.setSpacing(1)
        self.class_arm = Tt_manager.get_object_from_list_by_fullname("arms", class_arm_fullname) if isinstance(class_arm_fullname, str) else class_arm_fullname
        self.day = Tt_manager.get_object_from_list_by_fullname("days", day_fullname) if isinstance(day_fullname, str) else day_fullname

        # in the event that the arm does not offer today, so no periods
        try:
            self.period_objs_list = self.class_arm.periods[self.day]
        except KeyError:
            self.period_objs_list = []

        track_count = PeriodsContainer.count
        # renders the periods in widget form
        self.children = [IndivPeriodsWidget(period_obj=period, index=track_count)
            for period in self.period_objs_list]

        # Add this widget children into the hbox
        for child in self.children:
            self.hbox.addWidget(child)

        self.hbox.setSpacing(3)
        self.hbox.setContentsMargins(1,1,1,1)
        # Width of one child widget
        self.width = width
        self.height = height
        self.setMinimumSize(QtCore.QSize(self.width*len(self.children), self.height))
        self.setMaximumSize(QtCore.QSize(self.width*len(self.children), self.height))


        PeriodsContainer.count += 1
        PeriodsContainer.count = PeriodsContainer.count % 2

        # self.setStyleSheet("""
        #     background:red;
        #     """)

    @property
    def period_count(self):
        """ Gets number of periods for this class arm today """
        return str(len(self.period_objs_list)) if self.period_objs_list else "None today"

    @property
    def total_width(self):
        return self.width*len(self.children)
    



# 
class IndivPeriodsWidget(QtWidgets.QFrame):
    """ Class to model each widget that bears the period details of each class arm per day """
    style_count = 0

    def __init__(self, period_obj=None, index=0):
        super().__init__()

        # self.resize(100, 25)
        self.setMaximumSize(120, 38)
        self.setMinimumSize(120, 38)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setContentsMargins(1,1,1,1)
        self.vbox.setSpacing(2)
        self.period_start = self.to_time_str(period_obj.start) if period_obj else "None"
        self.period_end = self.to_time_str(period_obj.end) if period_obj else "None"

        self.span_label = QtWidgets.QLabel(self)
        self.span_label.setText(f"{self.period_start} - {self.period_end}")
        self.span_label.setAlignment(QtCore.Qt.AlignCenter)

        self.period_name_label = QtWidgets.QLabel(self)
        self.period_name_label.setAlignment(QtCore.Qt.AlignCenter)

        # Demarcation line
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        if period_obj:
            self.period_name_label.setText("Academic" if period_obj.is_acad else period_obj.nonacad_title.dept_name)
        else:
            self.period_name_label.setText("No period exists yet")

        self.vbox.addWidget(self.span_label)
        self.vbox.addWidget(self.line)
        self.vbox.addWidget(self.period_name_label)
        

        style1 = """
            QWidget{
            background-color:#e1e1e1;
            }
            QLabel{
            color:#191919;
            font-size:7pt;
            }
        """
        style2 = """
            QWidget{
            background:#f4f4f4;
            }
            QLabel{
            color:#191919;
            font-size:7pt;
            }
        """ 

        styles_list = [style1, style2]
        curr_index = (index + IndivPeriodsWidget.style_count) % len(styles_list)
        self.setStyleSheet(styles_list[curr_index])

        IndivPeriodsWidget.style_count += 1
        IndivPeriodsWidget.style_count = IndivPeriodsWidget.style_count % 2

        # If this period is not academic, make some slight changes to its appearance
        if period_obj:
            if not period_obj.is_acad:
                # stylesheet = self.styleSheet()
                self.setStyleSheet("""
                    QWidget{
                    background:#c8d8fd;
                    }
                    QLabel{
                    color:#052d87;
                    }
                    """)

    def to_time_str(self, t_tuple):
        """ Converts the time tuple passed into ot into a string of format hh:mm:ss """
        t_str = str(t_tuple)
        # Strip it of the beginning and ending brackets
        t_str = t_str.strip("()")
        # Split based on commas -- returns a list
        t_str_list = t_str.split(",")
        t_str_list = [k.strip().zfill(2) for k in t_str_list]

        # Now build up the time string with colons as a delimiter
        time_str = ":".join(t_str_list)
        return time_str



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    per_container = IndivPeriodsWidget()
    per_container.show()
    # ui = Ui_Form()
    # ui.setupUi(Form)
    # Form.show()
    # widget_for_tree()

    sys.exit(app.exec_())
