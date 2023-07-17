from PyQt5 import QtCore, QtGui, QtWidgets, uic
from ..models import Tt_manager, Tt_algo, Tt_algo_calc
from ..models.Tt_models import TimeTable as tt
import math


class LoadFrame(QtWidgets.QWidget):
    """ The loading widget with progressbars filling from min to max """
    def __init__(self, loading_text="Operation Loading..."):
        super().__init__()
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/loading.ui", self)
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)
        # Do not show just yet
        self.loading_label = self.findChild(QtWidgets.QLabel, "loading_label")
        self.loading_label.setText(loading_text)

        self.progressbars = [self.findChild(QtWidgets.QProgressBar, "progbar_1"), 
        self.findChild(QtWidgets.QProgressBar, "progbar_2")]

        self.show()

    def animate_progbars(self, val):
        """ sets val as the value to the progressbars """
        for progbar in self.progressbars:
            progbar.setValue(val)



class PerpetualLoadFrame(QtWidgets.QWidget):
    """ class that handles the mini frame that shows up when stuff is loading (with progressbars and stuff) """
    def __init__(self, time_interval=100, loading_text="A moment, please. Task loading in the background."):
        super().__init__()
        # Load the ui file
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/perpetual_loading.ui", self)
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)
        self.show()

        # get the progressbars in a dict
        self.progressbars = {
        1 : self.findChild(QtWidgets.QProgressBar, "progbar_1"),
        2 : self.findChild(QtWidgets.QProgressBar, "progbar_2"),
        3 : self.findChild(QtWidgets.QProgressBar, "progbar_3"),
        4 : self.findChild(QtWidgets.QProgressBar, "progbar_4"),
        5 : self.findChild(QtWidgets.QProgressBar, "progbar_5")
        }

        self.loading_label = self.findChild(QtWidgets.QLabel, "loading_label")
        self.loading_label.setText(loading_text)
        self.max_prog = 100
        self.step_k = 0.24
        self.steps, self.count = 10, 0

        # set the timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate_progbars)
        self.timer.start(time_interval)

        # define the equation of motion
    def EOM(self, time_count):
        """ Defines the "exponential" EOM to move the progressbars. time_t is an integer 1 <= time_t <= self.steps """
        return 1.1*self.max_prog*(1 - math.e**(-1*self.step_k*time_count))


    def animate_progbars(self):
        """ Does all the work of setting values to these progbars """
        self.count = (self.count % self.steps) + 1
        
        for k_int, progbar in self.progressbars.items():
            # change up if k_int is even
            val = self.max_prog - self.EOM(self.count) if k_int % 2 == 0 else self.EOM(self.count)
            val = round(val)
            progbar.setValue(val)


    def stop_animation(self):
        """ stops the animation of the progressbars """
        self.timer.stop()
        self.count = 0

        for progbar in self.progressbars.values():
            # change up if k_int is even
            progbar.setValue(0)
        # close the this entire QWidget
        self.close()



class ATPGSettingsWindow(QtWidgets.QWidget):
    """ The window that shows the ATPG parameter names and weighted values to be set """
    def __init__(self, mother_window):
        super().__init__()
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/preferences_window.ui", self)
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)

        self.mother_window = mother_window
        # self.load_atpg_func = load_atpg_func
        # self.message_func = message_func
        # self.workrate_func = workrate_func
        
        # Get the lineEdits
        self.analytic_lineEdit = self.findChild(QtWidgets.QLineEdit, "analytic_lineEdit")
        self.theoretical_lineEdit = self.findChild(QtWidgets.QLineEdit, "theoretical_lineEdit")
        self.practical_lineEdit = self.findChild(QtWidgets.QLineEdit, "practical_lineEdit")
        self.grammatical_lineEdit = self.findChild(QtWidgets.QLineEdit, "grammatical_lineEdit")

        # get the values to the spinboxes
        self.analytic_spinbox = self.findChild(QtWidgets.QSpinBox, "analytic_spinbox")
        self.theoretical_spinbox = self.findChild(QtWidgets.QSpinBox, "theoretical_spinbox")
        self.practical_spinbox = self.findChild(QtWidgets.QSpinBox, "practical_spinbox")
        self.grammatical_spinbox = self.findChild(QtWidgets.QSpinBox, "grammatical_spinbox")
        self.set_atpg_btn = self.findChild(QtWidgets.QPushButton, "set_atpg_btn")

        self.busy_checkbox = self.findChild(QtWidgets.QCheckBox, "busy_checkbox")
        self.busy_frame = self.findChild(QtWidgets.QFrame, "busy_frame")
        self.busy_spinbox = self.findChild(QtWidgets.QSpinBox, "busy_spinbox")
        self.set_busy_btn = self.findChild(QtWidgets.QPushButton, "set_busy_btn")
        self.close_btn = self.findChild(QtWidgets.QPushButton, "close_btn")

        self.set_atpg_btn.clicked.connect(self.set_atpg)
        self.set_busy_btn.clicked.connect(self.set_workrate_inflexion)
        self.busy_checkbox.stateChanged.connect(self.busy_frame.setEnabled)
        self.close_btn.clicked.connect(lambda: self.close())


    def set_atpg(self):
        analytic_name = "Analytic" if not self.analytic_lineEdit.text() else self.analytic_lineEdit.text()
        theoretical_name = "Theoretical" if not self.theoretical_lineEdit.text() else self.theoretical_lineEdit.text()
        practical_name = "Practical" if not self.practical_lineEdit.text() else self.practical_lineEdit.text()
        grammatical_name = "Grammatical" if not self.grammatical_lineEdit.text() else self.grammatical_lineEdit.text()

        analytic_val = self.analytic_spinbox.value()
        theoretical_val = self.theoretical_spinbox.value()
        practical_val = self.practical_spinbox.value()
        grammatical_val = self.grammatical_spinbox.value()

        self.mother_window.Timetable.set_ATPG_parameters((analytic_name, analytic_val), (theoretical_name, theoretical_val), 
            (practical_name, practical_val), (grammatical_name, grammatical_val))
        
        self.mother_window.load_atpg()
        self.mother_window.messagebox(title="ATPG modification success.", text="ATPG preferences successfully registered and displayed on the top tab", icon="Information")


    def set_workrate_inflexion(self):
        workrate_val = self.busy_spinbox.value()
        self.mother_window.Timetable.set_workrate_inflexion_num(workrate_val)
        self.mother_window.load_workrate()
        self.mother_window.messagebox(title="Workrate modification success.", 
            text=f"Work-Rate percentage of <strong>{workrate_val}</strong> successfully registered.", icon="Information")


# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def get_detailed_info_from_fac_or_dept(model_obj, identifier):
    """ STR. Returns an HTML string of detailed info from 'model_obj' depending on whether it is a department (faculty) object
    or a dept (subject) """

    # If it is a faculty object
    style = """
        font-family:arial;
    """
    if 'fac' in identifier:
        return f"""
            <html>
            <style>{style}</style>
            <p style="font: 10pt arial">Department name: {model_obj.full_name}. </p>
            <p>Head of department: <strong>{model_obj.HOD}</strong></p>
            <p>Number of constituent subjects: {len(model_obj.depts_list)}.</p>
            <p>Description: {model_obj.description} </p>
            </html>
            """
    # Else, if it is a subject
    return f"""
            <html>
            <style>{style}</style>
            <p style="font: 10pt arial;">Subject/course ID and full name: <strong>{model_obj.full_name}</strong></p>
            <p>Headed by: <strong>{model_obj.hos}</strong>
            <p>Mother Department: <strong>{model_obj.faculty.full_name}</strong></p>
            <p>This subject, based on its structural attributes, weighs <strong>{model_obj.dept_ATPG()}</strong> on the ATPG-
            course structure scale.
            <br>
            <p style="font: 8pt arial;">N.B: The ATPG scale is not by any means a measure of the importance of a subject/course. Such judgement 
            is reserved for the presiding institution. This rating simply helps sort the subjects.</p>
            <p>Number of resident teachers: <strong>{len(model_obj.teachers_list)}</strong></p>
            </html>
            """


# ------------------------------------------------------------------------------------------------------------------
class WidgetTree(QtWidgets.QWidget):
    """Class to generate the widgets which would go into the trees in the gui, rather than mere text"""
    def __init__(self,icon_path="TIMETABLE/Icons-mine/teacher.png",icon_width=14, icon_height=16,
        label_text="", extra_text="", with_checkbox=False):
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



class ModelDetailWindow(QtWidgets.QDialog):
    """This class handles the small window that would show details for arm, teachers, subjects etc on click"""
    def __init__(self, tt_manager):
        super().__init__()
        self.tt_obj = tt_manager.Timetable_obj
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/model_info_window.ui", self)
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
    """ Handles the generating the details of models (in HTML) 
    to be shown on the GUI with the appropriate QSS styling. """
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


    def _css_style(self):
        """ Returns a string of the css styles needed to make the text presentable """
        return """
        h4{color: #373737; font-size: 11pt; font-weight:bold; font-family: cambria, sans-serif;}
        h5{color: #373737; font-size: 9pt; font-weight:bold; font-family: cambria, sans-serif;}
        p{color:#242424; font-size:8pt; font-family: calibri, tahoma;}
        .emphasis{color: #4848ff; font-weight:normal; font-size:8pt;}
        .mid-emphasis{color:#5c5c5c; font-size:6pt; font-weight:normal; font-family: calibri, tahoma;}
        .soft-emphasis{color:#5b5bff; font-size:5pt; font-weight:normal; font-family: calibri, tahoma;}
        """


    def get_class_categories_details(self):
        """ Returns details about all class_categories created to be displayed on the GUI """
        class_groups = self.tt_obj.list_of_school_class_groups
        class_group_classes = {class_group:[clss.full_name for clss in class_group.school_class_list]
                            for class_group in class_groups}
        class_group_names = [class_group.full_name for class_group in class_group_classes]

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
        <style>{self._css_style()}</style>
        <h4>CLASS CATEGORY DETAILS</h4>
        <p>Typically, Class categories (or Class groups) house school classes and in the turn the class arms underneath each of its resident school classes.
         The already created class categories are as follows:</p> 
        {self._bulleted_items_from_list(class_group_names, ordered=True)}
        <p>Total class categories in all: {len(class_group_classes)}</p>
        <hr>
        <h5>The resident classes under each of these class categories (groups) are listed below</h5>
        {class_group_classes_str}
        <br>
        <p class="emphasis">Total number of classes: <strong>{class_count}</strong></p>
         """
        return detail_text


    def get_school_classes_details(self):
        """ Returns details about all the school classes created """
        all_classes = self.tt_obj.list_of_school_classes
        classes_and_arms = {clss:[arm.full_name for arm in clss.school_class_arm_list]
                        for clss in all_classes}
        classes_names = [clss.full_name for clss in classes_and_arms]

        arms_count = 0
        classes_arms_str = ""
        for clss, arms_list in classes_and_arms.items():
            arms_count += len(arms_list)
            classes_arms_str += f"""
            {clss.full_name}
            {self._bulleted_items_from_list(arms_list, ordered=False)}
            <hr>
            """

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>CLASS/GRADE/LEVEL DETAILS</h4>
        <p>Typically, the school class houses class arms.The already created classes are as follows:</p>
        {self._bulleted_items_from_list(classes_names, ordered=True)}
        <p>Total: {len(classes_names)} classes in all.</p>
        <hr>
        <h5>The resident class arms under each of the classes are listed below</h5>
        {classes_arms_str}
        <br>
        <p class="emphasis">Total number of class arms: <strong>{arms_count}</strong></p>

        """
        return detail_text


    def get_school_class_arms_details(self):
        """ Returns the details of all the school class arms created """
        all_arms = [arm.full_name for arm in self.tt_obj.list_of_school_class_arms]

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>CLASS ARM DETAILS</h4>
        <p>The class arms created so far are listed below:</p>
        {self._bulleted_items_from_list(all_arms, ordered=True)}
        <p class="emphasis">Total: <strong>{len(all_arms)}</strong> in all.</p>
        """
        return detail_text


    def get_days_details(self):
        all_days = [day.full_name for day in self.tt_obj.list_of_days]
        len_all_days = len(all_days)

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>SCHOOL WEEK DETAILS</h4>
        <p>The school week so far created consists of the following days listed in chronological order:</p>
        {self._bulleted_items_from_list(all_days, ordered=True)}
        <p class="emphasis">Total: <strong>{len_all_days}</strong> in all.</p>
        """
        return detail_text



    def get_teachers_details(self):
        """ Returns a string of details for all the teachers so far created """
        all_teachers = self.tt_obj.list_of_all_teachers
        full_time_teachers = [teacher.full_name for teacher in all_teachers if teacher.regularity]
        part_time_teachers = [teacher.full_name for teacher in all_teachers if not teacher.regularity]

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>STAFF DETAILS</h4>
        <p>Below is the list of all the teachers created so far, categorized by their regularity (consistency).</p>
        <hr>
        <h5>FULL-TIME STAFF</h5>
        {self._bulleted_items_from_list(full_time_teachers, ordered=True)}
        <p>Total of full-time staff: {len(full_time_teachers)}</p>
        <hr>
        <h5>PART-TIME STAFF</h5>
        {self._bulleted_items_from_list(part_time_teachers, ordered=True)}
        <p>Total of part-time staff: {len(part_time_teachers)}</p>
        <br>
        <p class="emphasis">Total number of staff (full-time and part-time): <strong>{len(all_teachers)}</strong></p>
        """
        return detail_text


    def get_depts_details(self):
        """ Returns HTML details for all the subjects created """
        all_subjs = self.tt_obj.list_of_departments
        subjs_non_para = [f'{subj.full_name}<p class="mid-emphasis">Sporting an ATPG rating of: <strong>{subj.dept_ATPG()}</strong></p>' for subj in all_subjs if not subj.is_parallel]
        subjs_para = [f'{subj.full_name}<p class="mid-emphasis">Sporting an ATPG value of: <strong>{subj.dept_ATPG}</strong></p><p>Constituent subjects: {len(subj.parallel_names)}</p>'
        for subj in all_subjs if subj.is_parallel]

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>SUBJECTS/COURSES DETAILS</h4>
        <p>The subjects/courses created so far for this timetable are listed below; the non-parallel subjects first then the parallel subjects.</p>
        <h5>NORMAL (NON-PARALLEL) SUBJECTS/COURSES</h5>
        {self._bulleted_items_from_list(subjs_non_para, ordered=True)}
        <hr>
        <h5>PARALLEL SUBJECTS/COURSES</h5>
        {self._bulleted_items_from_list(subjs_para, ordered=True)}
        <hr>
        <p class="emphasis">Total number of subjects/courses created: <strong>{len(all_subjs)}</strong></p>
        """
        return detail_text


    def get_faculty_details(self):
        all_faculties = [fac.full_name for fac in self.tt_obj.list_of_faculties]

        detail_text = f"""
        <style>{self._css_style()}</style>
        <h4>DEPARTMENTS DETAILS</h4>
        <p>The following are the departments created so far</p>
        {self._bulleted_items_from_list(all_faculties, ordered=True)}
        <hr>
        <p class="emphasis">Departments created so far: {len(all_faculties)}</p>
        """
        return detail_text


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



# ------------------------------------------------------------------------------------------------------------------
# ---------------------- RENDERING THE WIDGETS IN THE GUI WITH TIMETABLE DETAILS -----------------------------------
# The period frames class

class PeriodFrame(QtWidgets.QFrame):
    def __init__(self, is_acad_bool, height=0):
        super().__init__()

        period_path = "acad_period_frame" if is_acad_bool else "non_acad_period_frame"
        uic.loadUi(f"TIMETABLE/gui/Tt_UI_files/{period_path}.ui", self)

        self.height = height
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
            "}\n"
        }

        # get the labels and textedit and all
        self.period_title_label = self.findChild(QtWidgets.QLabel, "period_title_label")
        self.period_duration_label = self.findChild(QtWidgets.QLabel, "period_duration_label")
        self.period_textedit = self.findChild(QtWidgets.QTextEdit, "period_textedit")

    def add_name_duration_content(self, name_id, duration_str, dept_name):
        """ Method to add name, duration and name of subject to the period_frame widget """
        self.period_title_label.setText(name_id)
        self.period_duration_label.setText(duration_str)
        self.period_textedit.setHtml(f"""
            <html>
                <p style="text-align:center; color:#161616;font-size:8pt;
                font-family: tahoma; font-weight:bold;">{dept_name}</p>
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
        return match_str in Tt_algo_calc.strip_list_wrapper([self.teacher, self.dept, self.faculty])

    def match_and_colour_based_on_track(self, match_str):
        """ Matches 'match_str' with the dept, teacher, faculty parameters and colours the subj_fr if there is 
        a match """
        match = self._string_matches(match_str)
        self._colour_based_on_track(tracked=match)



class ArmFrame(QtWidgets.QFrame):
    """ class that designs each of the individual arm or day period widgets, when the timetable is fully rendered """
    def __init__(self, height=90):
        super().__init__()
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/day_arm_frame.ui", self)
        self.height = height
        self.day_or_arm_label = self.findChild(QtWidgets.QLabel, "day_or_arm_label")
        self.day_or_arm_name_label = self.findChild(QtWidgets.QLabel, "day_or_arm_name_label")


    def add_arm_fullname(self, title_str, fullname_str):
        """ Changes the label title into the name of the arm """
        self.day_or_arm_label.setText(title_str)
        self.day_or_arm_name_label.setText(fullname_str)




# ---------------------------------------------------------------------------------------------------------
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


class IndivPeriodDisplayFrame(QtWidgets.QFrame):
    """ FOR THE FINISHED TIMETABLE. One of the (horizontal) frames across which the period widgets will sit on the FINISHED timetable.
    The first item in periods_list is the marker(day or arm) and the rest are the period items. Takes in the actual period items """
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


    # def _frame_setup(self, fr_widget):
    #     """ Private method to setup the arm and period frames """
    #     # Frame = QtWidgets.QFrame()
    #     Frame = fr_widget()
    #     # ui.setupUi(Frame)
    #     return Frame
        

    def return_period_frames(self, model_type_str, match_item):
        """ The method that populates this frame with the mini period frames """
        if not self.periods_list:
            return

        marker, *periods = self.periods_list
        # make the marker frame
        marker_frame = ArmFrame()
        marker_frame.add_arm_fullname(model_type_str, marker.full_name)

        # The list of widgets this function will eventually returns
        widgets_list = [marker_frame]

        # add in the rest of the periods
        for period in periods:
            period_frame = PeriodFrame(period.is_acad)
            # Customize this period by adding the time-limits and title
            period_frame.add_name_duration_content(period.period_title, period.period_boundary_time_str, period.dept_content)

            # Add the teacher's full_name str if teacher exists
            teacher_str = period.teacher if period.teacher else None
            dept_str = period.dept.full_name if period.dept else None
            faculty_str = period.dept.faculty.full_name if period.dept else None


            if not period.is_acad:
                print(f"Non-acad periods dept: {dept_str} || dept_content: {period.dept_content}")

            period_frame.add_teacher_dept_fac_str(teacher_str, dept_str, faculty_str)
            # match by an empty string if no match item is given; so no matches are found
            period_frame.match_and_colour_based_on_track(match_item)
            widgets_list.append(period_frame)
        return widgets_list


    def add_period_widgets_to_frame(self, model_type_str, match_item):
        """ Method to add this widget items to the Frame (self) """
        for frame in self.return_period_frames(model_type_str, match_item):
            self.hbox.addWidget(frame)


    def run(self, model_type_str, match_item):
        """ Runs the entire process of calculating width, making frames and adding frames to the self """
        self.set_frame_size()
        # Below already run
        # self.return_period_frames()
        self.add_period_widgets_to_frame(model_type_str, match_item)



# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
class PeriodsDisplayFrame:
    """ THE BIG FRAME IN THE GUI INTO WHICH ALL THE HORIZONTAL PERIOD FRAMES WILL BE DYNAMICALLY PUT IN. FOR THE FINISHED TIMETABLE
    PRO-TIP:
    1. add periods_list_data()
    2.set_width_height()
    3.add_widget_to_frames_vbox()

    """
    def __init__(self, frame=None, spacing=6, padding=(2,2,2,2)):
        self.frame = frame if frame else QtWidgets.QFrame()
        self.spacing = spacing
        self.padding = padding
        self.child_frames = []

        if self.frame.layout():
            # if there is a layout already, clear it
            self.clear_vert_layout()
        else:
            # if not, make one
            self.vbox = QtWidgets.QVBoxLayout(self.frame)

        
    
    def clear_vert_layout(self):
        """ clears the vertical layout on the self.frame widget so that new stuff can come in """
        for k in reversed(range(self.frame.layout().count())):
            self.frame.layout().itemAt(k).widget().setParent(None)


    def add_childframe_data(self, model_type_str, match_item, periods_data_list=None, padding=(2,2,2,2), spacing=4, period_height=90, period_width=145):
        """ takes in the periods_list data (identifier (day or arm:first mini-frame) and then the periods for the day od arm) to make an individual childframe and appends said frame to the list of child frames """
        if periods_data_list:
            child_frame = IndivPeriodDisplayFrame(periods_data_list, padding=(2,2,2,2), spacing=4, period_height=90, period_width=145)
            child_frame.run(model_type_str, match_item)
            self.child_frames.append(child_frame)
            # self.vbox.addWidget(child_frame)


    @property
    def child_height(self):
        """ Returns the height of the first child item in the child_frames list """
        return self.child_frames[0].width_height[1] if self.child_frames else 90


    @property
    def max_child_width(self):
        """ Returns the value of the widest frame in self.child_frames """
        widest_frame = max(self.child_frames, key=lambda frame: frame.width_height[0])
        return widest_frame.width_height[0]


    def set_width_height(self):
        """ This methods sets the width (and height) of the frame. max_child_width (and num_children) is an INT which stands for the 
        largest width of the inside frames embedded within this frame (and the total number of these inner frames), 
        so we can wrap the frame around the whole thing. """
        v_spacing_count = 0 if not self.child_frames else len(self.child_frames) - 1
        height = (len(self.child_frames) * self.child_height) + (v_spacing_count * self.spacing) + self.padding[0] + self.padding[2]
        width = self.max_child_width + self.padding[1] + self.padding[3]
        self.frame.resize(width, height)
            # yield beam_val


    def add_widget_to_frames_vbox(self):
        """ Adds any child_frame that hasn't been previously added to the v-box """
        for child_frame in self.child_frames:
            if child_frame not in self.frame.layout().children():
                self.frame.layout().addWidget(child_frame)



# ----------------------------------------------------------------------------------------------------
def sort_packet_stylesheet(topic_colour="#f4f4f4"):
    """ Returns styles to be used in the textEdit widgets for the packeting and sorting operations """         
    style = f""" 
            p, li{{\n 
            white-space: pre-wrap;\n
            color:#272727;\n
            font-size:8.5pt;\n
            font-family:arial;\n
            margin:0px;\n
            }}\n
            ul, ol{{\n
            margin:0px;\n
            padding:0px;\n
            }}\n
            body{{\n
            font-family:calibri;\n
            padding:3px;\n
            margin-top:0px;\n
            margin-bottom:0px;\n
            margin-left:0px;\n
            margin-right:0px;\n
            padding:0px;\n
            text-align:justify;\n
            }}\n
            #topic{{\n
            color:{topic_colour};\n
            font-weight:bold;\n
            text-align:center;\n
            font-size: 10pt;\n
            margin-top:5px;\n
            }}\n
            .item{{\n
                font-weight:bold;\n
                color:#2d2dff;\n
            }}\n
            .emphasis{{\n
                color:#2828ff;\n
            }}\n
            hr{{\n
                border:0.9px solid #3c3c3c;\n
            }}\n
            li hr{{\n
                border:0.8px solid #4a4aff;\n
                }}\n
            .indent-hr{{\n
                margin-left: 30px;\n
                padding-left:30px;\n
            }}\n
            """
    return style


def load_teacher_details_into_textEdit(teacher, textEdit_widget):
    """ Generates (searched) teacher's details and displays it in the textEdit widget """
    if teacher:
        topic_colour = "#2b2bff"
        comment = '<p id="topic">DETAILS</p><hr>'
        comment += f'<p>Consistency: {"Full-time" if teacher.regularity else "Part-time"}</p>'
        comment += f"<p>Subjects taught: <strong>{teacher.str_teacher_depts}</strong></p>"
        comment += "<hr>"
        comment += '<h3>Subject and class arms to which teacher has been assigned</h3>'
        comment += '<ol>'
        for dept, arm in teacher.dept_and_arms:
            comment += f'<li>Teaches <strong>{dept.full_name}</strong> to <strong>{arm.full_name}</strong>.</li>'
        comment += '<hr></ol>'
        comment += f'<p>A total of <strong>{len(teacher.dept_and_arms)}</strong> subject-class arm combinations.</p>'

    else:
        topic_colour = "#007100"
        comment = '<p id="topic">CANNOT RENDER DETAILS</p><hr>'
        comment += "<p>The details of a non-existent teacher/tutor cannot be rendered.</p>"

    # Generate the HTML string with the comment
    html_body = f"""
        <html>
        <head>
            <style type="text/css">
               {sort_packet_stylesheet(topic_colour)}
            </style>
        </head>
        <body>
            {comment}
        </body>
        </html>"""
    # Now load this html_body variable into the textEdit widget
    textEdit_widget.setHtml(html_body)



def load_packeting_details_html_into_textedit(details_list, textEdit_widget, len_all_subjs, len_all_days=5, beam_max_val=100):
    """ This function generates the details to be shown (especially for the errors!) on the textEdit for the packeting operation in HTML.
    'details' is the list (ot iterable, really) that carry all the defaulting (dept) objects that will be used to generate these details"""

    # If the list of defaulting dept objects is empty, the packeting process was successful! else not
    if details_list:
        topic_colour = "#ea0000"

        comment = f"""
        <p id="topic">PRE-ARRANGEMENT NOT (COMPLETELY) SUCCESSFUL!</p>\n
        <p>Due to an insufficiency in the number of teachers/handlers/tutors handling the following subject{'' if len(details_list) == 1 else 's'} across all of its offering class arms, the packeting operation has proven unsuccessful.</p>\n
        <p>Defaulting subjects: <span class="emphasis">{len(details_list)}</span></p>
        <p>Helpful details on the defaulting subjects read below.</p>\n
        <p>Packeting success: <span class="emphasis">{((len_all_subjs - len(details_list)) * 100 / len_all_subjs):.2f}%</span></p>\n
        <hr>\n
        <ol>\n
        """
        len_details_list = len(details_list)

        # ----- loop over all the subjects details to the comment string ----------
        for count, dept in enumerate(details_list, start=1):
            dept_full_name, (dept_min_teachers, dept_teachers_more) = dept.full_name, dept.how_many_more_teachers(all_days_len=len_all_days)

            # print("FAILED! RUNNING DEPT AND DEFICIENCIES")
            # print(dept_full_name, dept_min_teachers, dept_teachers_more)

            comment += f'<li><p class="item">{dept_full_name}</p>'
            comment += f"""<p>A minimum of <span class="emphasis">{dept_min_teachers}</span> teacher{'' if dept_min_teachers == 1 else 's'} required;"""
            comment += "based on the typical number of subjects handled by the existing number of teachers.</p>"
            comment += f"""<p>At least, <span class="emphasis">{dept_teachers_more}</span> more full-time teacher{'' if dept_teachers_more == 1 else 's'} needed.</p>"""
            comment += "<hr></li>"

            # beam_val = round(count * width / len_details_list)
            # yield beam_val + current_beam
            
        comment += "</ol>"

    # if packeting ran successfully
    else:
        topic_colour = "#007100"

        comment = '<p id="topic">PRE-ARRANGEMENT SUCCESSFUL!</p>' "<p>The teachers created for each subject are (up till this point) sufficient for each of the "\
        "offering class arms.</p> <p>Congratulations! On with the sorting.</p>"

        # yield round(0.9 * beam_max_val)


    # Generate the HTML string with the comment
    html_body = f"""
        <html>
        <head>
            <style type="text/css">
               {sort_packet_stylesheet(topic_colour)}
            </style>
        </head>
        <body>
            {comment}
        </body>
        </html>"""

    # Now load this html_body variable into the textEdit widget
    textEdit_widget.setHtml(html_body)


def load_sort_details_html_into_textedit(sort_details_dict, textEdit_widget, 
    num_all_teachers, num_all_subjects, num_all_arms):
    """ Generates the HTML content to be displayed on the textEdit_widget. Content on the displaced teachers
    and what subjects they must have taught """

    # -----------------------------------------------------------------------------------
    # If there were issues with the sorting and not all teachers were satisfied
    if sort_details_dict:
        topic_colour = "#d50000"
        len_displaced_teachers = len(sort_details_dict)

        comment = '<p id="topic">SORT OPERATION NOT (COMPLETELY) SUCCESSFUL</p>' "<p>Despite the robust (and rather lenient) sorting operation, the following "\
        f"teacher{' has' if len_displaced_teachers == 1 else 's have'} been all but stranded; their subjects/courses defying insertion into the periods of "\
        "their offering class arms enough to fulfill their weekly frequencies without clashing with any of their other periods or displacing another teacher's lesson period.</p>" '<p>According to the selected sort algorithm, '\
        f'the number of stranded teachers:<span class="emphasis">{len_displaced_teachers}</span></p>' 
        comment += "<ol>"

        erring_subjs_set, erring_arms_set = set(), set()

        for teacher, dict_of_days in sort_details_dict.items():
            teacher_full_name = teacher.full_name

            # dict_of_days is {day_obj: arm_dept_chunklist}
            arms_depts_set = set()
            for arm_dept_chunklist in dict_of_days.values():
                for arm, _, dept in arm_dept_chunklist:
                    arm_full_name, subj_full_name = arm.full_name, dept.full_name

                    # Add this subj and arm to the set defined up top for percentage calculations to be made
                    erring_subjs_set.add(subj_full_name)
                    erring_arms_set.add(arm_full_name)

                    if (arm_full_name, subj_full_name) not in arms_depts_set:
                        comment += f'<li><p>Teacher ID: <span class="item">{teacher_full_name}</span></p>'
                        comment += f'<p>Default info: <span class="emphasis">{subj_full_name}</span> for class arm <span class="emphasis">{arm_full_name}</span><hr class="indent-hr"></li>'
                        arms_depts_set.add((arm_full_name, subj_full_name))

        comment += "</ol>"
        comment += "<br>"

    # The sort operation was successful!
    else:
        topic_colour = "#00793d"

        comment = '<p id="topic">SORT OPERATION SUCCESSFUL!</p>' "<p>All the requirements for the teachers, class arms and subjects in all the "\
            "periods for every day have been completely met.</p>" "<p>Congratulations! On with the display and tracking.</p>"

    # -------------------------------------------------------------------------------------------------
    html_body = f"""
        <html>
        <head>
            <style type="text/css">
               {sort_packet_stylesheet(topic_colour)}
            </style>
        </head>
        <body>
            {comment}
        </body>
        </html>"""
    # Now load this html_body variable into the textEdit widget
    textEdit_widget.setHtml(html_body)


def load_sort_correction_details_textedit(extra_teachers_dict, textEdit_widget):
    """ If the user's sorting errors out, this function would load the details of the extra teachers created
     to make the timetable work """
    topic_colour = "#00793d"
    comment = '<p id="topic">AUTO-FIX REPORT: FIXES EFFECTED (TIMETABLE NOW OPERABLE).</p>'\
            '<p>The issue of teachers/handlers (and by extension, some of their subjects/courses) getting stranded i.e. unable to '\
            'fulfill their weekly quotas for their client class arms is solved (optimally) by the introduction of '\
            'a calculated number of extra (exclusive to each subject) full-time teacher objects which would lighten the load on the '\
            'previously created teacher objects.</p>'\
            '<p>The liberty has been taken to create the optimal number of the aforementioned <em>extra</em> teachers, assign them '\
            'class arms and teaching periods. Each of them is designated by "(Exclusive) Member of staff".'\
            '<br>The subjects and the extra teachers created for each are outlined below:</p>'

    comment += '<ol>'

    for dept, xtra_teacher_holder in extra_teachers_dict.items():
        comment += '<li><hr>'
        comment += f'<p><strong>{dept.full_name}</strong></p>'
        comment += f'<p>Extra teachers created: <span class="emphasis">{xtra_teacher_holder.created_teachers_num()}</span></p>'
        comment += '<br>'

        comment += "<strong>Teachers' Details</strong>"
        comment += '<ul>'
        for teacher in xtra_teacher_holder.xtra_created_teachers:
            comment += '<li>'
            comment += f'<p>Identity: <span class=emphasis>{teacher.full_name}</span></p>'
            comment += f'<p>Designation: <span class=emphasis>{teacher.designation}</span></p>'
            comment += f'<p>Class category specialization: <span class=emphasis>All</span></p>'
            comment += f'<p>Consistency: <span class=emphasis>Full-time</span></p>'
            comment += f'<p>Assigned class arms: <span class=emphasis>{teacher.classarms_taught_based_on_dept_str(dept)}</span></p>'
            comment += '</li>'
        comment += '</ul>'
        comment += '</li>'
    comment += '</ol>'

    comment += "<p>Congratulations.Timetable operable. Timetable viewable.</p>"
        
    # ---------
    html_body = f"""
    <html>
    <head>
        <style type="text/css">
           {sort_packet_stylesheet(topic_colour)}
        </style>
    </head>
    <body>
        {comment}
    </body>
    </html>"""
    # Now load this html_body variable into the textEdit widget
    textEdit_widget.setHtml(html_body)



def load_tracked_model_details(model_name, tracked_models_dict, textEdit_widget):
    """ Takes the models that have been tracked and loads their details into the textEdit widget on the GUI screen """
    topic_colour = "#3a4b9f"
    comment = """<p id="topic">TRACKED ITEM'S OCCURRENCES</p>"""
    comment += f"<p><strong>{model_name}</strong> can be found in the following day(s) in the following class arms</p>"

    count = 0
    for day_fullname, coords_list in tracked_models_dict.items():
        comment += f"{day_fullname}"
        comment += "<ul><hr>"
        for arm_full_name, period_id in coords_list:
            comment += f"<li>Occurs in <strong>{arm_full_name}, {Tt_algo_calc.nth_suffix(period_id)} period</strong>.</li>"
            count += 1
        comment += "</ul>"

    comment += f"<br><p><strong>{count}</strong> occurrences found for <strong>{model_name}</strong> across the entire timetable.</p>"


    html_body = f"""
    <html>
    <head>
        <style type="text/css">
           {sort_packet_stylesheet(topic_colour)}
        </style>
    </head>
    <body>
        {comment}
    </body>
    </html>"""
    textEdit_widget.setHtml(comment)




def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # per_container = IndivPeriodsWidget()
    # per_container.show()
    model_win = TimetableDisplayFrame()
    model_win.show()
    
    sys.exit(app.exec_())
