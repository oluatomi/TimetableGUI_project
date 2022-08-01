# - ************************************************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA. APRIL, 2022.

# -- All rights (whichever applies) reserved!
# **************************************************************************************************************

# ----------  IMPORTANT NOTICE :---
# -------everywhere DEPARTMENT is used in the app, it really refers to FACULTY in the code.
# -------every where SUBJECT/COURSE is used in the app, it refers to DEPARTMENT (dept) in the code.
# -------
# -------This could be very confusing, I know.
# -------This is because when i started writing the code, i had used department to denote the Subject/course and so
# -------had to use FACULTY to denote the DEPARTMENT from which the subject hails... I only changed my mind later, but my code was 
# ------- already to complex to be changes by a find and replace  shortcut.

# ------- Also, CLASS CATEGORY in the GUI is the CLASSGROUP. For the same reason as above.

# -------
# -------Bear with me.
# -------                    - Olu'tomi Owoeye.

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
import Tt_manager
from Tt_manager import get_obj_from_param as object_getter
from Tt_gui_handler import load_manual
from Tt_GuiExtras import WidgetTree


# class MyHighlighter(QtGui.QSyntaxHighlighter):

#     def __init__(self, parent=None, format_text):
#         super().__init__(parent, format_text)


class TtSplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(TtSplashScreen, self).__init__()

    # Load the ui file
        uic.loadUi("Splashscreen.ui", self)
        self.setWindowTitle("Olutomi's Timetable")
        self.counter = 0
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.load_progressbar)
        self.timer.start(40)


    def load_progressbar(self):
        progress_bar = self.findChild(QtWidgets.QProgressBar, "progressBar")

        progress_bar.setValue(self.counter)

        if self.counter > 100:
            # close splashscreen and open mainwindow
            self.close()
            self.timer.stop()

            # open mainwindow
            self.tt_mainwindow = UITimetable()
            self.tt_mainwindow.show()

        self.counter += 2

# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
# --------------- THE MAIN APP GUI ----------------------

class UITimetable(QtWidgets.QMainWindow):
    def __init__(self):
        super(UITimetable, self).__init__()

    # Load the ui file
        uic.loadUi("Timetable_GUI.ui", self)
        self.setWindowTitle("Olutomi's Timetable")
        self.setWindowIcon(QtGui.QIcon('../Icons-mine/App_logo.png'))

        self.load_manual_into_toolbox()
        self.menubar_colour()        

        # The working timetable instance
        self.Timetable = Tt_manager.TimeTableManager()
    
    # -----------------------------------------------------------------------------------------------
        # The previous and next arrow btns for flipping through the main stacked widget box
        self.next_btn = self.findChild(QtWidgets.QPushButton, "next_stacked_page")
        self.prev_btn = self.findChild(QtWidgets.QPushButton, "prev_stacked_page")

        self.next_btn.clicked.connect(lambda :self.switch_mainstacked(1))
        self.prev_btn.clicked.connect(lambda :self.switch_mainstacked(-1))

    # ----------------------------------------------------------------------------------------------
        self.reg_dept = self.findChild(QtWidgets.QPushButton, "reg_deptfac_btn")
        self.reg_dept.clicked.connect(self.register_deptfac)

    # ----------------------------------------------------------------------------------------
    # Tab design buttons
        self.font_colour_btn = self.findChild(QtWidgets.QPushButton, "font_colour_btn")
        self.font_colour_btn.clicked.connect(self.colourDialog)

        self.font_design_btn = self.findChild(QtWidgets.QPushButton, "font_design_btn")
        self.font_design_btn.clicked.connect(self.fontDialog)

# ----------------------------------------------------------------------------
        self.faculty_list_combobox = self.findChild(QtWidgets.QComboBox, "department_combobox")
    
    # -------------------------  current_main-stacked index
        self.main_stacked_curr_index = 0
        self.page_label = self.findChild(QtWidgets.QLabel, "page_counter")
        self.mainStackedWidget = self.findChild(QtWidgets.QStackedWidget, "mainStackedWidget")
        self.mainStackedWidget.setCurrentIndex(self.main_stacked_curr_index)
        self.page_label.setText(f"Page 1 of {self.mainStackedWidget.count()}")

    # ---------------------------------------------------------------------
    # -------- The register subject/course (department in the code)
        self.register_course_btn = self.findChild(QtWidgets.QPushButton, "register_subj_btn")
        self.register_course_btn.clicked.connect(self.register_course)

        self.analytic_slider = self.findChild(QtWidgets.QSlider, "analytic_slider")
        self.practical_slider = self.findChild(QtWidgets.QSlider, "practical_slider")
        self.theoretical_slider = self.findChild(QtWidgets.QSlider, "theoretical_slider")
        self.grammatical_slider = self.findChild(QtWidgets.QSlider, "grammatical_slider")

        self.analytic_label = self.findChild(QtWidgets.QLabel, "Analytic_val")
        self.practical_label = self.findChild(QtWidgets.QLabel, "Practical_val")
        self.theoretical_label = self.findChild(QtWidgets.QLabel, "Theoretical_val")
        self.grammatical_label = self.findChild(QtWidgets.QLabel, "Grammatical_val")

        self.analytic_slider.valueChanged.connect(lambda val: self.analytic_label.setText(str(val)))
        self.practical_slider.valueChanged.connect(lambda val: self.practical_label.setText(str(val)))
        self.theoretical_slider.valueChanged.connect(lambda val: self.theoretical_label.setText(str(val)))
        self.grammatical_slider.valueChanged.connect(lambda val: self.grammatical_label.setText(str(val)))

            # ------------Non academic departments ------------------
        self.acad_or_not = self.findChild(QtWidgets.QComboBox, "acad_combobox")
        self.non_acad_depts_listwidget = self.findChild(QtWidgets.QListWidget, "nonacad_listwidget")

        self.acad_or_not.currentIndexChanged.connect(self.nonacad_fields)

    # ---------------------------------------------------------------------------------------------
    # ---------- The blackboard (and the treewidget) on the register department and course page
        self.fac_courses_treewidget = self.findChild(QtWidgets.QTreeWidget, "depts_subject_tree")
        self.board = self.findChild(QtWidgets.QTextEdit, "blackboard_textedit")
        self.fac_courses_treewidget.itemClicked.connect(self.fac_courses_tree_clicked)

    #------------------------------------------------------------------------------------------------
    # --------- The class group(category) and class and class arm tree widget
        self.classgroup_class_arm_tree = self.findChild(QtWidgets.QTreeWidget, "cat_class_arm_tree")
        self.create_classgroupbtn = self.findChild(QtWidgets.QPushButton, "class_cat_btn")
        self.create_classgroupbtn.clicked.connect(self.register_class_group)

    # --------------------------- create school class-----------------------------------------
        self.combo_with_classgroup = self.findChild(QtWidgets.QComboBox, "create_class_combo")
        self.create_sch_class_btn = self.findChild(QtWidgets.QPushButton, "create_sch_class_btn")

        self.create_sch_class_btn.clicked.connect(self.register_school_class)

    # ------------------------ generate class arms -----------------------------------------------
        self.gen_arms_btn = self.findChild(QtWidgets.QPushButton, "generate_arms_btn")
        self.combo_class = self.findChild(QtWidgets.QComboBox, "arms_class_combo")

        self.gen_arms_btn.clicked.connect(self.generate_arms)

    # ----------------------------Create Days ---------------------------------------------------------------
        self.day_btn = self.findChild(QtWidgets.QPushButton, "create_day_btn")
        self.day_btn.clicked.connect(self.register_day)
        self.day_list = self.findChild(QtWidgets.QListWidget, "day_list")

        self.day_checkbox = self.findChild(QtWidgets.QCheckBox, "day_position_chbox")
        self.day_position_spinbox = self.findChild(QtWidgets.QSpinBox, "position_spinbox")

        self.day_checkbox.stateChanged.connect(self.day_check_spin_box)

    # ----------------------- The Department(faculty) and Generated Teachers ----------------------
        self.dept_and_teachers_tree = self.findChild(QtWidgets.QTreeWidget, "faculty_course_teacher_tree")
        self.gen_teachers_btn = self.findChild(QtWidgets.QPushButton, "gen_teachers_btn")
        self.gen_teachers_combobox = self.findChild(QtWidgets.QComboBox, "gen_teachers_combobox")
        self.gen_teachers_btn.clicked.connect(self.generate_teachers)
        # Also get the groupbox which has all the working days by teacher
        self.gen_teachers_days_listwidget = self.findChild(QtWidgets.QListWidget, "gen_teacher_days_listwidget")

        # The button to mark courses in bulk
        self.mark_btn = self.findChild(QtWidgets.QPushButton, "mark_courses_btn")

        self.mark_btn.pressed.connect(self.enable_mark_depts)

        self.try_btn = self.findChild(QtWidgets.QPushButton, "try_btn")

    # ---------------------------- Generate all staff table (and details) -------------------------------
        self.all_staff_table = self.findChild(QtWidgets.QTableWidget, "all_staff_tablewidget")

        
    # ------------------ LOADS ALLTHE TREES especially for when app is starting from an existing file ------------------
        # Loads the faculty/department-courses tree widget
        self.load_fac_courses_tree()
        self.load_group_class_arm_tree()
        self.load_days_list()
        self.load_faculty_dept_teachers_tree()
        self.load_gen_teachers_day_chboxes()


    # -------------------------------------------------------------------------------------------------------------
    # -------------------------------- PRIMARILY THE GUI OPERATION FUNCTIONS --------------------------------------
    def load_manual_into_toolbox(self):
        # Find the toolbox widget
        # Get the scrollarea housing the toolbox to be built
        tool_scroll = self.findChild(QtWidgets.QScrollArea, "manual_scrollarea")
        # tool_box = self.findChild(QtWidgets.QToolBox, "manual_toolbox")

        tool_box = QtWidgets.QToolBox()

        # Empty the tool_box
        for i in range(tool_box.count()):
            tool_box.removeItem(i)
            # tool_box.removeIt

        manual = load_manual()
        
        topics = manual.keys() 
        # widget = QtWidgets.QWidgets()        

        widgets_list = []
        for topic in topics:
            # Make a textedit inserted into a layout inserted into a widget in all the below
            textEdit = QtWidgets.QTextEdit()
            textEdit.setHtml(manual[topic])
            textEdit.setReadOnly(True)
            v_layout = QtWidgets.QVBoxLayout()
            v_layout.addWidget(textEdit)
            mother_widget = QtWidgets.QWidget()
            mother_widget.setLayout(v_layout)

            widgets_list.append(mother_widget)


        for topic,widg in zip(topics,widgets_list):
            tool_box.addItem(widg, topic)

        tool_box.setStyleSheet("""
            font-size: 11pt;
            font-family:Times New Roman;
            background:white;
            }
            """)

        tool_scroll.setWidget(tool_box)
    

    def menubar_colour(self):
        tool_bar = self.findChild(QtWidgets.QToolBar,"toolBar")
        menu_bar = self.findChild(QtWidgets.QMenuBar,"menuBar")

        style = """

            background:qlineargradient(spread:pad, x1:0.04, y1:0.499, x2:0.95, y2:0.501, 
            stop:0.0568182 rgba(0, 0, 0, 255), stop:0.855114 rgba(0, 0, 0, 255), 
            stop:0.995222 rgba(94, 94, 94, 255));

            """

        tool_bar.setStyleSheet(style + "height:7px;")
        # menu_bar.setStyleSheet(style + "height:20px; color: #fff;")


    def switch_mainstacked(self, int_num):
        """Switches between pages of the stacked widget for different operations"""
        self.mainStackedWidget = self.findChild(QtWidgets.QStackedWidget, "mainStackedWidget")
        num_pages = self.mainStackedWidget.count()

        index = (self.main_stacked_curr_index + int_num) % num_pages
        self.main_stacked_curr_index = index

        # set the current mainstacked widget to the widget with index index
        self.mainStackedWidget.setCurrentIndex(self.main_stacked_curr_index)
        self.page_label.setText(f"Page {self.main_stacked_curr_index + 1} of {num_pages}")


    def colourDialog(self):
        """Colours the font of the highlighted part of the text edit in the finished version"""
        colour = QtWidgets.QColorDialog.getColor()
        text_edit = self.findChild(QtWidgets.QTextEdit, "temp_text_edit")
        text_edit.setTextColor(colour)


    def fontDialog(self):
        """handles font design such as font-face, size and bold"""
        text_edit = self.findChild(QtWidgets.QTextEdit, "temp_text_edit")
        font, ok = QtWidgets.QFontDialog().getFont()

        if ok:
            text_edit.setCurrentFont(font)
            
    # --------------------------------------------------------------------------------------------------
    # ------------------------------- BACKEND-INTO-GUI FUNCTIONS ---------------------------------------
    def register_deptfac(self):
        """Collects the data for registering a faculty (A DEPARTMENT in the GUI !!!) from the GUI"""
        fac_name = self.findChild(QtWidgets.QLineEdit, "deptfac_name")
        HOD_name = self.findChild(QtWidgets.QLineEdit, "deptfac_HOD")
        description = self.findChild(QtWidgets.QPlainTextEdit, "deptfac_description")

        fac_name_text = fac_name.text().strip()
        HOD_name_text = HOD_name.text().strip()
        description_text = description.toPlainText().strip()

        
        # check if fields are filled else raise an error message box
        if UITimetable.check_fields_or_error(fields_values_list=[fac_name_text, description_text]):
            self.Timetable.create_faculty(fac_name_text, HOD=HOD_name_text, description=description_text)

            # Clear the input fields
            fac_name.clear()
            HOD_name.clear()
            description.clear()

        else:
           UITimetable.messagebox(title="Fields error",icon="critical",text="Required field(s) left blank, please fill them.")

        
        # Load up up the faculties created!
        self.load_fac_courses_tree()
        self.load_faculty_dept_teachers_tree()


    def nonacad_fields(self):
        """This function disables certain fields in the registration page, based on thether or not the course(dept) is academic"""

        acad_text = self.acad_or_not.currentText()
        head_subject = self.findChild(QtWidgets.QLineEdit, "hos_lineedit")
        atpg_wrapper_box = self.findChild(QtWidgets.QGroupBox, "atpg_wrapper")

        # Render them invalid or not
        if acad_text == "Academic":
            head_subject.setEnabled(True)
            atpg_wrapper_box.setEnabled(True)
            self.faculty_list_combobox.setEnabled(True)
        else:
            head_subject.setEnabled(False)
            atpg_wrapper_box.setEnabled(False)
            self.faculty_list_combobox.setEnabled(False)


    def register_course(self):
        """Registers a course (a dept) in the code"""
        course_name = self.findChild(QtWidgets.QLineEdit, "course_name_lineedit")
        
        head_subject = self.findChild(QtWidgets.QLineEdit, "hos_lineedit")
        # self.faculty_combo_val = self.findChild(QtWidgets.QComboBox, "department_combobox")

        # Now get the values from these QObjects
        course_name_text = course_name.text().strip()
        acad_or_not_text = self.acad_or_not.currentText().strip()
        head_subject_text = head_subject.text().strip()
        department_text = self.faculty_list_combobox.currentText().strip()
        analytic_slider_val = int(self.analytic_slider.value())
        practical_slider_val = int(self.practical_slider.value())
        theoreticai_slider_val = int(self.theoretical_slider.value())
        grammatical_slider_val = int(self.grammatical_slider.value())


        # Check for empty fields for those required
        if UITimetable.check_fields_or_error(fields_values_list=[course_name_text]):
            if acad_or_not_text == "Academic":
                if UITimetable.check_fields_or_error(fields_values_list=[department_text]):
                    
                    # Create a department under that faculty
                    self.Timetable.create_department(course_name_text,faculty=department_text,
                        A=analytic_slider_val, T=theoreticai_slider_val, P=practical_slider_val, G=grammatical_slider_val)

                    # Return the sliders to 1,1,1,1
                    self.analytic_slider.setValue(1)
                    self.practical_slider.setValue(1)
                    self.theoretical_slider .setValue(1)
                    self.grammatical_slider.setValue(1)


                else:
                    # one of the fields have not been filled. display error message
                    UITimetable.messagebox(title="Fields error",icon="critical",text="The 'Department' field is empty")
            else:
                # If it is a non-academic department
                self.Timetable.create_special_department(course_name_text)

        else:
            UITimetable.messagebox(title="Empty field error",icon="critical",text="You have not entered the name of the course.")

        course_name.clear()
        
        head_subject.clear()
        self.faculty_list_combobox.clear()

        # Load up up the faculties created!
        self.load_fac_courses_tree()
        self.load_nonacad_courses_list()
        # Load the tree containing faculty, couses and teachers
        self.load_faculty_dept_teachers_tree()



    def load_fac_courses_tree(self):
        """This method handles putting registered faculties and depts/courses on the TreeWidget on the screen and also loading
        them"""
        
        # treewidget.setColumnCount(1)
        self.fac_courses_treewidget.clear()
        self.faculty_list_combobox.clear()

        for faculty in self.Timetable.Timetable_obj.list_of_faculties:
            # Adds the list of all the registered to the combobox for 
            self.faculty_list_combobox.addItem(faculty.full_name)

            # Load the faculty name into the tree widget
            item = QtWidgets.QTreeWidgetItem([f"{faculty.full_name}"])
            self.fac_courses_treewidget.addTopLevelItem(item)

            for dept in faculty.course_list:
                # Create a nested node in each faculty for the department
                dept_tree_item = QtWidgets.QTreeWidgetItem([dept.full_name])
                item.addChild(dept_tree_item)


    def load_nonacad_courses_list(self):
        """Loads the Listwidget displaying all the created non-academic courses, e.g. break"""
        self.non_acad_depts_listwidget.clear()

        all_nonacad = [nonacad.full_name for nonacad in self.Timetable.Timetable_obj.list_of_nonacad_depts]

        self.non_acad_depts_listwidget.addItems(all_nonacad)



    def fac_courses_tree_clicked(self):
        """This function fires when any element in the Department-subject tree widget is clicked"""
        current_item = self.fac_courses_treewidget.currentItem()
        c_text = current_item.text(0)

        obj = "list_of_departments" if current_item.parent() else "list_of_faculties"

        cast_ = lambda obj:getattr(self.Timetable.Timetable_obj, obj)
        # print(f"This is cast: {cast_}")

        obj_in_question = object_getter(cast_(obj), "full_name", c_text)

        # self.board.clear()
        self.board.setHtml(obj_in_question.detailed_info)


# -------------------------------------------------------------------------------------------------------------
    def register_class_group(self):
        """This function handles the registration of a school_class_group"""

        class_group_name = self.findChild(QtWidgets.QLineEdit, "class_cat_lineedit")
        class_group_abbrev = self.findChild(QtWidgets.QLineEdit, "class_cat_abbrev_lineedit")
           # Description of the school class category
        class_group_desc = self.findChild(QtWidgets.QTextEdit, "class_cat_desc_textedit")

        # retrieve all the texts
        name,abbrev,desc = class_group_name.text(),class_group_abbrev.text(),class_group_desc.toPlainText()

        if UITimetable.check_fields_or_error(fields_values_list=[name, desc]):
            # Create the class group
            self.Timetable.create_school_class_group(name,description=desc, abbrev=abbrev)

            # Clear the fields
            class_group_name.clear()
            class_group_abbrev.clear()
            class_group_desc.clear()
        else:
            # spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="Required field(s) have not been filled!")

        # load the treewidget function to display newly registered class group, class and arm
        self.load_group_class_arm_tree()


    def register_school_class(self):
        """Handles the registration of a school class under a school class category"""
        
        sch_class_name_lineedit = self.findChild(QtWidgets.QLineEdit, "class_name_lineedit")
        class_group,class_name = self.combo_with_classgroup.currentText().strip(), sch_class_name_lineedit.text().strip()

        # Verify fields and create class
        if UITimetable.check_fields_or_error(fields_values_list=[class_group, class_name]):
            # Create class
            
            self.Timetable.create_school_class(class_name, class_group)

            # clear the fields
            sch_class_name_lineedit.clear()

        else:
            # Ring out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="No class category specified under which to make class.")

        self.load_group_class_arm_tree()


    def generate_arms(self):
        """Generates class arms for a chosen out of the classes in a school class group"""

        # the input from the spin_box as to the number of arms to generate
        spin_id = self.findChild(QtWidgets.QSpinBox, "arm_num_spinbox")
        alphabetized = self.findChild(QtWidgets.QComboBox, "alphabetized_combo")
        

        alpha_or_not = alphabetized.currentText()
        school_class_text = self.combo_class.currentText()     #The full name of the school class

        if UITimetable.check_fields_or_error(fields_values_list=[school_class_text]):
        # Whether alphabetically or with numbers
            is_alpha = True if alpha_or_not == "Alphabetized" else False
            
            self.Timetable.generate_school_class_arms(school_class_text, frequency=spin_id.value(), as_alpha=is_alpha)
        else:
            # Spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="No school class to generate arms for.")


        # Clear the fields, the spinbox in this case
        spin_id.setValue(1)
        # Load the classgroup-class-arm tree widget
        self.load_group_class_arm_tree()


    def load_group_class_arm_tree(self):
        """This function loads the classgroup-class arm-arm tree"""

        self.classgroup_class_arm_tree.clear()
        self.combo_with_classgroup.clear()
        self.combo_class.clear()
        # the class reg combox will also be cleared too below!

        for class_group in self.Timetable.Timetable_obj.list_of_school_class_groups:
            # Load the  class group(category) name into the tree widget
            item = QtWidgets.QTreeWidgetItem([f"{class_group.full_name}"])

            # Add the class group to the comcobox for school class registration
            self.combo_with_classgroup.addItem(class_group.full_name)
            
            self.classgroup_class_arm_tree.addTopLevelItem(item)

            for clss in class_group.school_class_list:
                # add this sch_class into the combo_class combobox (The combobox to aid thegeneration of class arms)
                self.combo_class.addItem(clss.full_name)

                # Create a nested node in each faculty for the department
                class_tree_item = QtWidgets.QTreeWidgetItem([clss.full_name])
                item.addChild(class_tree_item)

                for arm in clss.school_class_arm_list:
                    # Create a nested node in each faculty for the department
                    arm_tree_item = QtWidgets.QTreeWidgetItem([arm.full_name])
                    class_tree_item.addChild(arm_tree_item)


    # ------------------------------------------------------------------------------
    def day_check_spin_box(self):
        # If button has been checked,
        if self.day_checkbox.isChecked():
            self.day_position_spinbox.setEnabled(True)
            rating = self.day_position_spinbox.value()
            return rating

        self.day_position_spinbox.setEnabled(False)
        return None
        


    def register_day(self):
        """handles the resgistration of days"""

        day_name = self.findChild(QtWidgets.QLineEdit, "day_name")
        rating = self.day_check_spin_box()

        # Check if day_name_field is valid
        day_name_text = day_name.text()
        if UITimetable.check_fields_or_error(fields_values_list=[day_name_text]):
            # Create day_object
            self.Timetable.create_day(day_name_text, rating=rating)

        else:
            # Spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="Fill in the name of the day.")

        # Clear fields
        day_name.clear()
        self.day_position_spinbox.setValue(1)
        self.day_position_spinbox.setEnabled(False)
        
        self.load_days_list()
        # Load teachers days with checkboxes
        self.load_gen_teachers_day_chboxes()


    def load_days_list(self):
        """Loads the trww widget with created days on"""

        # treewidget.setColumnCount(1)
        self.day_list.clear()

        days_full_list = [f"{day_obj.full_name}" for day_obj in self.Timetable.Timetable_obj.list_of_days]
        self.day_list.addItems(days_full_list)

# ------------------------------------------------------------------------------------------
    # ----------------- Generate Teachers for department
    def load_faculty_dept_teachers_tree(self, markable=False, expanded=False):
        """This function loads the tree showing each faculty, the departments under it, and the geneatated teachers"""
        self.dept_and_teachers_tree.clear()
        self.gen_teachers_combobox.clear()

        # the class reg combox will also be cleared too below!
        for faculty in self.Timetable.Timetable_obj.list_of_faculties:
            # Load the  class group(category) name into the tree widget

            item = QtWidgets.QTreeWidgetItem()

            fac_widg = WidgetTree(label_text=faculty.full_name, icon_path='../Icons-mine/classgroup.png')
            
            self.dept_and_teachers_tree.addTopLevelItem(item)
            item.setExpanded(expanded)
            self.dept_and_teachers_tree.setItemWidget(item, 0, fac_widg)



            # Go for each of the courses in the faculty's course list
            for dept_obj in faculty.course_list:
                self.gen_teachers_combobox.addItem(dept_obj.full_name)

                # Create a nested node in each faculty for the department (subject)
                dept_tree_item = QtWidgets.QTreeWidgetItem()
                
                dept_widg = WidgetTree(label_text=dept_obj.full_name, icon_path="../Icons-mine/subject.png",with_checkbox=markable)
                item.addChild(dept_tree_item)
                self.dept_and_teachers_tree.setItemWidget(dept_tree_item, 0, dept_widg)


                for teacher in dept_obj.teachers_list:
                    # create custom widget for the teacher
                    # 
                    teacher_tree_item = QtWidgets.QTreeWidgetItem()
                    # teacher_widg = QtWidgets.QWidget()
                    # lab = QtWidgets.QLabel(teacher_widg)
                    # lab.setText("This is teacher!")
                    teacher_widg = WidgetTree(label_text=teacher.full_name)

                    # teacher_tree_item = QtWidgets.QTreeWidgetItem([teacher_widg])
                    dept_tree_item.addChild(teacher_tree_item)
                    self.dept_and_teachers_tree.setItemWidget(teacher_tree_item, 0, teacher_widg)



    def generate_teachers(self):
        """Generates teachers for a chosen course or selected courses. Teachers are chosen for a course not a faculty."""
        
        teachers_freq = self.findChild(QtWidgets.QSpinBox, "gen_teachers_spinbox")
        selected_days = []

        for index in range(self.gen_teachers_days_listwidget.count()):
            # child = self.gen_teachers_days_listwidget.item(index)
            item = self.gen_teachers_days_listwidget.item(index)
            widget = self.gen_teachers_days_listwidget.itemWidget(item)
            
            if widget.isChecked():
                selected_days.append(widget.text())


        # ------------------------------------------------------------------------------------------
        if self.mark_btn.text().strip() == "Mark":
            # -------------------------------------------------------------------------------------------------
            # If mark button is not selected, generate teachers only for the one dept(course) in the combobox

            dept_fullname = self.gen_teachers_combobox.currentText().strip()    #--- The course the teacher is teaching
            # Frequency of teachers

            # Verify if all fields are ok, spit out error if not
            if UITimetable.check_fields_or_error(fields_values_list=[dept_fullname, selected_days]):
                self.Timetable.generate_teachers(dept_fullname, frequency=teachers_freq.value(), teaching_days=selected_days)

                # Load the tree with faculty, dept and teachers
                self.load_faculty_dept_teachers_tree()

            else:
                # Spit out error message
                UITimetable.messagebox(title="Empty field error",icon="critical",text="No course for which to generate teachers")


        else:
            # ----------------------------------------------------------------------------------------------------------
            # If the mark button is clicked
            # """ Generates teachers for multiple courses selected from the day checkboxes with the mark button """
            selected_courses = []

            # ADDS ALL THE SELECTED DEPTS (COURSES) TO A LIST
            root = self.dept_and_teachers_tree.invisibleRootItem()
            child_count = root.childCount()

            for i in range(child_count):
                item = root.child(i)
                # The below returns the WidgetTree class i defined myself

                # Iterate through all the items under this the toplevel element

                for j in range(item.childCount()):
                    subj_item = item.child(j)

                    widget = self.dept_and_teachers_tree.itemWidget(subj_item, 0)
               
                    if widget.get_checkbox().isChecked():
                        selected_courses.append(widget.full_name_label.text())


            if UITimetable.check_fields_or_error(fields_values_list=[selected_courses, selected_days]):
                self.Timetable.generate_multidept_teachers(depts_list=selected_courses, frequency=teachers_freq.value(),
                 teaching_days=selected_days)

                #Load the tree widget again 
                self.load_faculty_dept_teachers_tree()
                self.generate_all_staff_table()

            else:
                UITimetable.messagebox(title="Empty field error",icon="critical",text="Either courses or days have not been specified")

        # Clear fields
        
        teachers_freq.setValue(0)
        

    def load_gen_teachers_day_chboxes(self):
        """This loads the days Listwidget with checkboxes, in the big box where teachers are to be registered"""

        self.gen_teachers_days_listwidget.clear()

        for day_obj in self.Timetable.Timetable_obj.list_of_days:
            # Create a checkbox
            checkbox = QtWidgets.QCheckBox(f"{day_obj.full_name}")
            checkbox.setCheckState(QtCore.Qt.Checked)
            
            day_item = QtWidgets.QListWidgetItem()
            self.gen_teachers_days_listwidget.addItem(day_item)
            self.gen_teachers_days_listwidget.setItemWidget(day_item, checkbox)


    def enable_mark_depts(self):
        """This method fires when when the mark button is clicked (to mark departments)"""
        if self.mark_btn.text().strip() == "Mark":
            self.load_faculty_dept_teachers_tree(markable=True, expanded=True)
            self.mark_btn.setText("Unmark")
            self.gen_teachers_combobox.clear()
            self.gen_teachers_combobox.setEnabled(False)
        else:
            self.load_faculty_dept_teachers_tree()
            self.mark_btn.setText("Mark")
            self.gen_teachers_combobox.setEnabled(True)



    def generate_all_staff_table(self):
        """This method generates the table for all the members of staff and their details"""

        self.all_staff_table.clear()

        self.all_staff_table.setRowCount(len(self.Timetable.Timetable_obj.list_of_all_teachers))

        for index,teacher in enumerate(self.Timetable.Timetable_obj.list_of_all_teachers):
            row = index
            self.all_staff_table.setItem(row, 0, QtWidgets.QTableWidgetItem(teacher.full_name))
            self.all_staff_table.setItem(row, 1, QtWidgets.QTableWidgetItem(teacher.str_teacher_depts))
            self.all_staff_table.setItem(row, 2, QtWidgets.QTableWidgetItem(teacher.str_teaching_days(self.Timetable.Timetable_obj)))
            self.all_staff_table.setItem(row, 3, QtWidgets.QTableWidgetItem(teacher.regular_or_no(self.Timetable.Timetable_obj)))



# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
    @staticmethod
    def check_fields_or_error(fields_values_list=None):
        """BOOLEAN. This method handles checking the given fields in a particular case. If any of the fields_VALUES (not the classes alone) are empty
        ring out an error with title 'error_title' """

        if all(fields_values_list) and isinstance(fields_values_list, list):
            return True
        return False


    @staticmethod
    def messagebox(title="Popup message", icon="Question", text="Something's the matter?", extratext="", buttons=None, callback=None):
        """ Generates message boxes (popup boxes of all kinds) of all kinds. Buttons is a LIST really of all the buttons (strings)
        for the message box.

        The callback function will be set. when already running. the callback (when defined in realtime) accepts an arg (i) which is
        the button clicked"""

        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)

        cast_ = lambda arg:getattr(QtWidgets.QMessageBox, arg.capitalize())

        # insert the icon to this message (and capitalizes it if it wasn't already)
        icon_type = cast_(icon)
        msg.setIcon(icon_type)

        # standard buttons
        ok, cancel = cast_("ok"), cast_("cancel")

        msg.setStandardButtons(ok|cancel)

        msg.setDefaultButton(cancel)
        msg.setInformativeText(extratext)

        if callback:
            msg.buttonClicked.connect(callback)

        x = msg.exec_()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Splash_and_mainwindow = TtSplashScreen()
    Splash_and_mainwindow.show()
    app.exec_()
