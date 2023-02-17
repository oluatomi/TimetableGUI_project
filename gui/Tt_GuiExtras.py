from PyQt5 import QtCore, QtGui, QtWidgets, uic
from ..models import Tt_manager, Tt_algo
from ..models.Tt_models import TimeTable as tt
from . import Tt_period_widgets


# def widget_for_tree(icon_path="../Icons-mine/teacher.png",label_text="", with_checkbox=False):
    # """Function to generate the widgets which would go into the trees in the gui, rather than mere text"""


# ------------------------------------------------------------------------------------------------------------------
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
    


class IndivPeriodsWidget(QtWidgets.QFrame):
    """ Class to model each widget that bears the period details of each class arm per day.
    FOR THE TABLWWIDGET THAT SHOWS PERIODS AFTER THEY HAVE BEEN CREATED """
    style_count = 0

    def __init__(self, period_obj=None, index=0):
        super().__init__()

        # self.resize(100, 25)
        self.setMaximumSize(120, 38)
        self.setMinimumSize(120, 38)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setContentsMargins(1,1,1,1)
        self.vbox.setSpacing(2)
        self.period_start = tt.to_time_str(period_obj.start) if period_obj else "None"
        self.period_end = tt.to_time_str(period_obj.end) if period_obj else "None"

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
            background-color:#e1e1e1;}
            QLabel{
            color:#191919;
            font-size:7pt;}
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


class ModelDetailWindow(QtWidgets.QDialog):
    def __init__(self, tt_obj):
        super().__init__()
        self.tt_obj = tt_obj
        uic.loadUi("TIMETABLE/gui/info_window.ui", self)
        self.setWindowTitle("display Information")
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)

        self.cancel_btn = self.findChild(QtWidgets.QPushButton, "cancel_btn")
        self.textEdit = self.findChild(QtWidgets.QTextEdit, "textEdit")

        self.cancel_btn.clicked.connect(lambda :self.close())
        self.show()

    def get_details_load_on_dialog(self, str_arg):
        """ Loads the model_details from the ModelDetails class """
        model_detail = ModelDetails(self.tt_obj)
        self.textEdit.setHtml(model_detail.get_model_details_by_key(str_arg))


class ModelDetails:
    """ Handles the generating the details of models (in HTML) to be shown on the gui with the appropriate QSS styling"""
    def __init__(self, tt_obj):
        self.tt_obj = tt_obj


    def _bulleted_items_from_list(self, iterable, ordered=False):
        """ Takes each item in a list (or an iterable, really) and makes them into HTML list items """
        ordered_tag_open = "<ol>" if ordered else "<ul>"
        ordered_tag_close = "</ol>" if ordered else "</ul>"

        bulleted_list = f"""{ordered_tag_open}"""
        
        for elem in iterable:
            bulleted_list += f"""<li>{elem}</li>"""
        
        bulleted_list += f"""{ordered_tag_close}"""
        return bulleted_list


    def get_class_categories_details(self):
        """ Returns details about all class_categories created to be displayed on the GUI """
        class_groups = self.tt_obj.list_of_school_class_groups
        
        class_group_classes = {class_group:[clss.get_school_class_name for clss in class_group.school_class_list]
                            for class_group in class_groups}
        class_group_names = [class_group.class_group_name for class_group in class_group_classes]

        class_count = 0
        class_group_classes_str = ""
        for class_group, classes_list in class_group_classes.items():
            class_count += len(classes_list)
            class_group_classes_str += f"""
            {class_group.class_group_name}
            {self._bulleted_items_from_list(classes_list, ordered=False)}
            <hr>
            """

        detail_text = f"""
        <h4>CLASS CATEGORY DETAILS</h4>
        <p>Typically, Class categories (or Class groups) house school classes and in the turn the class arms underneath each of its resident school classes.
         The already created class categories are as follows:</p> 
        {self._bulleted_items_from_list(class_group_names, ordered=True)}
        <p>Total: {len(class_group_classes)} class categories in all.</p>
        <hr>
        <h5>The resident classes under each of these class categories (groups) are listed below</h5>
        {class_group_classes_str}
        <br>
        <p>Total number of classes: {class_count}.</p>
         """
        return detail_text


    def get_school_classes_details(self):
        """ Returns details about all the school classes created """
        all_classes = self.tt_obj.list_of_school_classes
        classes_and_arms = {clss:[arm.__repr__() for arm in clss.school_class_arm_list]
                        for clss in all_classes}
        classes_names = [clss.get_school_class_name for clss in classes_and_arms]

        arms_count = 0
        classes_arms_str = ""
        for clss, arms_list in classes_and_arms.items():
            arms_count += len(arms_list)
            classes_arms_str += f"""
            {clss.get_school_class_name}
            {self._bulleted_items_from_list(arms_list, ordered=False)}
            <hr>
            """

        detail_text = f"""
        <h4>CLASS/GRADE/LEVEL DETAILS</h4>
        <p>Typically, the school classes houses class arms.The already created classes are as follows:</p>
        {self._bulleted_items_from_list(classes_names, ordered=True)}
        <p>Total: {len(classes_names)} classes in all.</p>
        <hr>
        <h5>The resident class arms under each of the classes are listed below</h5>
        {classes_arms_str}
        <br>
        <p>Total number of class arms: {arms_count}</p>

        """
        return detail_text


    def get_school_class_arms_details(self):
        """ Returns the details of all the school class arms created """
        all_arms = self.tt_obj.list_of_school_class_arms

        detail_text = f"""
        <h4>CLASS ARM DETAILS</h4>
        <p>The class arms represents the literal classroom in which students take lessons handled by the teachers.
        The class arms created up to this point are listed below:</p>
        {self._bulleted_items_from_list([arm.__repr__() for arm in all_arms], ordered=True)}
        <p>Total: {len(all_arms)} in all.</p>
        """
        return detail_text


    def get_days_details(self):
        pass


    def get_teachers_details(self):
        pass


    def get_depts_details(self):
        pass

    def get_faculty_details(self):
        pass

    def make_details_into_dict(self):
        """ stores the details of the above function into a dictionary """
        return {
        "class_cats":self.get_class_categories_details(),
        "classes": self.get_school_classes_details(),
        "class_arms":self.get_school_class_arms_details(),
        "days": self.get_days_details(),
        "teachers": self.get_teachers_details(),
        "subjects":self.get_depts_details(),
        "faculties": self.get_faculty_details()
        }

    def get_model_details_by_key(self, str_arg):
        """ Returns details to be displayed on the GUI screen according to the string_argument sent from
        the button """
        return self.make_details_into_dict().get(str_arg)




class IndivPeriodDisplayFrame(QtWidgets.QFrame):
    """ FOR THE FINISHED TIMETABLE. One of the (horizontal) frames across which the period widgets will sit on the FINISHED timetable.
    The first item in periods_list is the marker(day or arm) and the rest are the period items """
    def __init__(self, periods_list, padding=(2,2,2,2), spacing=4, period_height=90, period_width=145):
        super().__init__()
        self.periods_list = periods_list
        self.period_frame_height = period_height
        self.period_frame_width = period_width
        self.padding = padding
        self.spacing = spacing
        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.setContentsMargins(*self.padding)
        

    @property
    def width_height(self):
        """ Method to calculate the width and height of this frame to absolutely contain all the mini-period frames in it """
        spacing_count = 0 if len(self.periods_list) == 0 else len(self.periods_list) - 1
        width = (len(self.periods_list) * self.period_frame_width) + self.padding[1] + self.padding[3] + (spacing_count * self.spacing)
        height = self.period_frame_height + self.padding[0] + self.padding[2]

        return width, height


    def set_frame_size(self):
        """ Sets the widths of this frame to self.width """
        self.setMinimumSize(QtCore.QSize(*self.width_height))
        self.setMaximumSize(QtCore.QSize(*self.width_height))


    def _frame_setup(self, fr_widget):
        """ Private method to setup the arm and period frames """
        Frame = QtWidgets.QFrame()
        ui = fr_widget()
        ui.setupUi(Frame)
        return ui, Frame
        

    def return_period_frames(self):
        """ The method that populates this frame with the mini period frames """
        if not self.periods_list:
            return
        marker, *periods = self.periods_list
        # make the marker frame
        marker_frame_ui, marker_frame = self._frame_setup(Tt_period_widgets.ArmFrame)
        marker_frame_ui.add_arm_fullname(marker.full_name)
        # The list of widgets this function will eventually returns
        widgets_list = [marker_frame]

        # add in the rest of the periods
        for period in periods:
            period_frame_ui, period_frame = self._frame_setup(Tt_period_widgets.PeriodFrame)
            # Customize this period by adding the time-limits and title
            period_frame_ui.add_name_duration_content(period.period_title, 
                f"{tt.to_time_str(period.start)} - {tt.to_time_str(period.end)}", period.dept_content)

            # Add the teacher's full_name str if teacher exists
            teacher_str = period.teacher.full_name if period.teacher else None
            dept_str = period.dept.full_name if period.dept else None
            faculty_str = period.dept.faculty.full_name if period.dept else None

            period_frame_ui.add_teacher_dept_fac_str(teacher_str, dept_str, faculty_str)
            # period_frame_ui.match_and_colour_based_on_track(dept_str)
            widgets_list.append(period_frame)
        return widgets_list


    def add_period_widgets_to_frame(self):
        """ Method to add this widget items to the Frame (self) """
        for frame in self.return_period_frames():
            self.hbox.addWidget(frame)


    def run(self):
        """ Runs the entire process of calculating width, making frames and adding frames to the self """
        self.set_frame_size()
        # Below already run
        # self.return_period_frames()
        self.add_period_widgets_to_frame()



# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
class PeriodsDisplayFrame:
    """ The Mother class to generate the frame into which all the other period frames would be arranged
    vertically """
    def __init__(self, frame, spacing, padding):
        self.frame = frame if frame else QtWidgets.QFrame()
        self.spacing = spacing
        self.padding = padding
        self.vbox = QtWidgets.QVBoxLayout(self.frame)


    @property
    def child_height(self):
        """ Returns the height of the first child item in the child_frames list """
        return self.child_frames[0].width_height[1] if self.child_frames else 90


    @property
    def max_child_width(self):
        """ Returns the value of the widest frame in self.child_frames """
        widest_frame = max(self.child_frames, key=lambda frame: frame.width_height[0])
        return widest_frame.width_height[0]


    @property
    def child_frames(self):
        """ generates frmaes from the list returned from the self.get_periods_list (method to be defined in the subclasses) """
        child_frames = []
        for elem_list in self.get_periods_list():
            child_frame = IndivPeriodDisplayFrame(elem_list)
            child_frame.run()
            child_frames.append(child_frame)
        return child_frames


    def set_width_height(self):
        """ This methods sets the width (and height) of the frame. max_child_width (and num_children) is an INT which stands for the 
        largest width of the inside frames embedded within this frame (and the total number of these inner frames), 
        so we can wrap the frame around the whole thing. """
        v_spacing_count = 0 if not self.child_frames else len(self.child_frames) - 1
        height = (len(self.child_frames) * self.child_height) + (v_spacing_count * self.spacing) + self.padding[0] + self.padding[2]
        width = self.max_child_width + self.padding[1] + self.padding[3]
        self.frame.resize(width, height)


    def add_childframes_to_frame(self):
        """ Adds all the child frames into the vertical box layout of self.frame """
        for child_frame in self.child_frames:
            self.vbox.addWidget(child_frame)


    def run(self):
        """ Runs all the afore-defined functions accordingly. """
        self.set_width_height()
        self.add_childframes_to_frame()
        self.frame.show()


# --------------------------------------------------------------------------------
class PeriodsDisplayByDayFrame(PeriodsDisplayFrame):
    """ class to handle putting """
    def __init__(self, day, frame=None, spacing=6, padding=(2,2,2,2)):
        super().__init__(frame, spacing, padding)
        self.day = day
        
    def get_periods_list(self):
        """ extracts the period_list (that is, the list of all the class arms for today) from the self.day object in a list of lists
        it extracts it in the format that the IndivPeriodDisplayFrame class can use to generate the child frames"""
        arms_periods_today_list = []
        for class_arm in self.day.school_class_arms_today:
            arm_periods_list = [class_arm] + class_arm.periods[self.day]
            arms_periods_today_list.append(arm_periods_list)
        return arms_periods_today_list


# ----------------------------------------------------------------------------------
class PeriodsDisplayByArmFrame(PeriodsDisplayFrame):
    def __init__(self, class_arm, frame=None, spacing=6, padding=(2,2,2,2)):
        super().__init__(frame, spacing, padding)
        self.class_arm = class_arm

    def get_periods_list(self):
        """ extracts the period_list (that is, the list of the school days for this class arm) from the self.class_arm object in a list of lists
        it extracts it in the format that the IndivPeriodDisplayFrame class can use to generate the child frames"""
        days_periods_for_arm = []
        for day, periods_list in self.class_arm.periods.items():
            day_periods = [day] + periods_list
            days_periods_for_arm.append(day_periods)
        return days_periods_for_arm


# ----------------------------------------------------------------------------------------------------

def load_packeting_details_html_into_textedit(details_list, textEdit_widget, len_all_subjs, len_all_days=5, beam_max_val=100):
    """ This function generates the details to be shown (especially for the errors!) on the textEdit for the packeting operation in HTML.
    'details' is the list (ot iterable, really) that carry all the defaulting (dept) objects that will be used to generate these details"""

    # If the list of defaulting dept objects is empty, the packeting process was successful! else not
    if details_list:
        topic_colour = "#ea0000"

        comment = f"""\n
        <p id="topic">PACKETING UNSUCCESSFUL!</p>\n
        <p>Due to an insufficiency in the number of teachers/handlers/tutors handling the following subject{'' if len(details_list) == 1 else 's'} across\n
         all of its offering class arms, the packeting operation has proven unsuccessful.</p>\n
        <p>Helpful details on the defaulting subjects read below.</p><hr>\n
        <p>Packeting success: <span class="emphasis">{(len_all_subjs - len(details_list)) * 100 / len_all_subjs:.2f}%</span></p>\n
        <ol>\n
        """
        # current_beam = round(0.15 * beam_max_val)
        # yield current_beam

        len_details_list = len(details_list)
        width = round(0.75 * beam_max_val) - current_beam

        # ----- loop over all the subjects details to the comment string ----------
        for count, dept in enumerate(details_list, start=1):
            dept_full_name, (dept_min_teachers, dept_teachers_more) = dept.full_name, dept.how_many_more_teachers(all_days_len=len_all_days)

            # print("FAILED! RUNNING DEPT AND DEFICIENCIES")
            # print(dept_full_name, dept_min_teachers, dept_teachers_more)

            comment += f'<li><p class="sub-topic">{dept_full_name}</p>'
            comment += f"""<p>A minimum of <span class="emphasis">{dept_min_teachers}</span> teacher{'' if dept_min_teachers == 1 else 's'} required;"""
            comment += "based on the typical number of subjects handled by the existing number of teachers (if they handle more than one).</p>"
            comment += f"""<p>At least, <span class="emphasis">{dept_teachers_more}</span> more teacher{'' if dept_teachers_more == 1 else 's'} needed.</p>"""
            comment += "<hr></li>"

            # beam_val = round(count * width / len_details_list)
            # yield beam_val + current_beam
            
        comment += "</ol>"

    # if packeting ran successfully
    else:
        topic_colour = "#007100"
        print("ran successfully")

        comment = '<p id="topic">PACKETING SUCCESSFUL!</p>' "<p>The teachers created for each subject are (up till this point) sufficient for each of the "\
        "offering class arms.</p> <p>Congratulations! On with the sorting.</p>"

        # yield round(0.9 * beam_max_val)


    # Generate the HTML string with the comment
    html_body = f"""\n
        <html>\n
        <head>\n
            <meta name="qrichtext" content="1" />\n
            <style type="text/css">\n
                p, li {{\n 
                white-space: pre-wrap;\n
                }}\n
                p{{\n
                color:#272727;\n
                font-size:8pt;\n
                font-family:calibri;\n
                }}\n
                body{{\n
                    font-family:calibri;\n
                    padding:3px;\n
                    margin-top:0px;\n
                    margin-bottom:0px;\n
                    margin-left:0px;\n
                    margin-right:0px;\n
                    padding:0px;\n
                }}\n
                #topic{{\n
                    color:{topic_colour};\n
                    font-weight:bold;\n
                    text-align:center;\n
                    font-size: 10pt;\n
                }}\n
                .sub-topic{{\n
                    font-weight:bold;\n
                    color:#2d2dff;\n
                .sub-topic hr{{\n
                    margin-left:15px;\n
                }}\n
                }}\n
                .emphasis{{\n
                    color:#2828ff;\n
                }}\n
            </style>\n
        </head>\n
        <body>\n
            {comment}\n
        </body>\n
        </html>"""

    # Now load this html_body variable into the textEdit widget
    textEdit_widget.setHtml(html_body)
    # yield beam_max_val
    # print("---THIS IS COMMENT -----")
    # print(comment)



def load_sort_details_html_into_textedit(displ_teachers_dict, textEdit):
    """ Generates and loads the html rendering of the displaced teachers dictionary into the textedit to see where sorting failed. """
    pass



# if __name__ == "__main__":
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # per_container = IndivPeriodsWidget()
    # per_container.show()
    model_win = TimetableDisplayFrame()
    model_win.show()
    

    sys.exit(app.exec_())
