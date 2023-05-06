# - ************************************************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA. JANUARY, 2022.

# -- All rights (whichever applies) reserved!
# **************************************************************************************************************

# ----------  IMPORTANT NOTICE :---
# -------everywhere DEPARTMENT is used in the GUI, it really refers to FACULTY in the code.
# -------every where SUBJECT/COURSE is used in the GUI, it refers to DEPARTMENT (dept) in the code.
# -------
# -------This could be very confusing, I know.
# -------This is because when i started writing the code, i had used department to denote the Subject/course and so
# -------had to use FACULTY to denote the DEPARTMENT from which the subject hails... I only changed my mind later, but my code was 
# ------- already to complex to be changed by a find and replace  shortcut.

# ------- Also, CLASS CATEGORY in the GUI is the CLASSGROUP in the code. For the same reason as above.

# -------
# -------Bear with me.
# -------                    - Olu'tomi Owoeye.

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from TIMETABLE.models import Tt_manager, Tt_exceptions
from TIMETABLE.models.Tt_manager import get_obj_from_param as object_getter
from . import Tt_threads
from .Tt_gui_handler import load_manual
from .Tt_GuiExtras import (WidgetTree, MySpinBox, PeriodsContainer, ModelDetailWindow, load_packeting_details_html_into_textedit,
    load_sort_details_html_into_textedit, PeriodsDisplayFrame, LoadingFrame, get_detailed_info_from_fac_or_dept)
from collections import namedtuple
from PyQt5.QtCore import Qt


Author = "Owoeye, Oluwatomilayo Inioluwa"
app = None

# Dictionary to hold the title and details to be displayed on the Page Info textEdit
# beside every page



class TtSplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(TtSplashScreen, self).__init__()

    # Load the ui file
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/Splashscreen.ui", self)
        self.setWindowFlags(QtCore.Qt.SplashScreen|QtCore.Qt.FramelessWindowHint)
        self.counter = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.load_progressbar)
        self.timer.start(40)


    def load_progressbar(self):
        """ Fills up the progressbar on the splashscreen """
        progress_bar = self.findChild(QtWidgets.QProgressBar, "progressBar")
        progress_bar.setValue(self.counter)

        if self.counter > 100:
            # close splashscreen and open mainwindow
            self.close()
            self.timer.stop()

            # open mainwindow
            self.tt_mainwindow = UITimetable()
            self.tt_mainwindow.show()
            return

        self.counter += 1

# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
# --------------- THE MAIN APP GUI ----------------------

class UITimetable(QtWidgets.QMainWindow):
    """ The main class QMainWindow class for the App """

    stacked_pages_title_and_details = {
    0: ("General information page", "<p>Enter the requested details to help personalize your timetable</p>"),
    1: ("Class and day creation page", "<p><strong>Note:</strong> When a class category is deleted, all of its descendants (school classes and class arms) also get deleted. The same also applies to a school class. Take caution.</p>"\
        "<hr/><p>To delete certain arms of a school class, simply activate the override radiobutton in the class arms generation section and reset to the number of your choice.</p>"),
    2: ("Department and subject creation page","<p><strong>Note:</strong> When a department gets deleted, all of its descendant subjects also get deleted. Take caution.</p>"),
    3: ("Periods and subject-to-arm mapping page", "<p></p>"),
    4: ("Generate teachers page", "<p>When a 'parallel' subject is selected, the same amount of 'x' teachers the user inputs is generated for all the sub-subjects making up the 'parallel' subject</p>"),
    5: ("Assign, packet, sort page", "<p>Assign (or unassign) subject teachers/handlers to class arms, Packet (or undo) subjects into days of the week for each class arm, and finally sort.</p>"\
        "<p><strong>Important:</strong> Should any alterations be made to any of the models (teachers, class arms, days), be sure to first Undo the sort (click the button), packeting and assignment operations, before assigning, packeting and sorting."\
        "This way, the new changes will be properly registered.</p>"),
    6: ("Timetable display page", "<p>Display the timetable on a day or class arm basis. You can also track a particular department, subject or teacher across the entire timetable to see where they exist (if they exist).</p>")
}


    def __init__(self, tt_obj=None):
        super(UITimetable, self).__init__()

    # Load the ui file
        uic.loadUi("TIMETABLE/gui/Tt_UI_files/Timetable_GUI.ui", self)
        self.setWindowIcon(QtGui.QIcon('TIMETABLE/Icons-mine/App_logo.jpg'))
        self.load_manual_into_toolbox()

        # The working timetable manager instance
        self.Timetable = Tt_manager.TimeTableManager(tt_obj=tt_obj)
        self.setWindowTitle(self.Timetable.Timetable_obj.project_file_name)

    # ------------------------ NAV-BAR ARCHIVE BUTTONS --------------------------------------------------
        self.class_cat_nav = self.findChild(QtWidgets.QPushButton, "class_cat_nav")
        self.class_nav = self.findChild(QtWidgets.QPushButton, "class_nav")
        self.class_arms_nav = self.findChild(QtWidgets.QPushButton, "class_arm_nav")
        self.days_nav = self.findChild(QtWidgets.QPushButton, "days_nav")
        self.depts_nav = self.findChild(QtWidgets.QPushButton, "subjs_nav")
        self.faculties_nav = self.findChild(QtWidgets.QPushButton, "departments_nav")
        self.teachers_nav = self.findChild(QtWidgets.QPushButton, "teachers_nav")

        # Connect these buttons to functions
        self.class_cat_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("class_cats"))
        self.class_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("classes"))
        self.class_arms_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("class_arms"))
        self.days_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("days"))
        self.depts_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("subjects"))
        self.faculties_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("faculties"))
        self.teachers_nav.clicked.connect(lambda :self.load_nav_dialog_with_details("teachers"))


    # --------------- SIDE-BAR: PREVIOUS AND NEXT BUTTONS -------------------------------------------------------------------------
        # The previous and next arrow btns for flipping through the main stacked widget box
        self.next_btn = self.findChild(QtWidgets.QPushButton, "next_stacked_page")
        self.prev_btn = self.findChild(QtWidgets.QPushButton, "prev_stacked_page")
        self.mainStackedWidget = self.findChild(QtWidgets.QStackedWidget, "mainStackedWidget")
        self.page_title_label = self.findChild(QtWidgets.QLabel, "page_title_label")
        self.page_info_box_textedit = self.findChild(QtWidgets.QTextEdit, "page_info_box_textedit")

        title, info = self.stacked_pages_title_and_details[0]
        self.page_title_label.setText(title.upper())
        self.page_info_box_textedit.setHtml(info)

        self.next_btn.clicked.connect(lambda :self.switch_mainstacked(1))
        self.prev_btn.clicked.connect(lambda :self.switch_mainstacked(-1))



    # --------------- SET/CHANGE ATPG PARAMETERS ------------------------
        self.atpg_btn = self.findChild(QtWidgets.QPushButton, "set_ATPG_btn")
        self.analytic_lineedit = self.findChild(QtWidgets.QLineEdit, "analytic_lineedit")
        self.theoretical_lineedit = self.findChild(QtWidgets.QLineEdit, "theoretical_lineedit")
        self.practical_lineedit = self.findChild(QtWidgets.QLineEdit, "practical_lineedit")
        self.grammatical_lineedit = self.findChild(QtWidgets.QLineEdit, "grammatical_lineedit")

        # ------- The spin_boxes containing the weight values
        self.analytic_spinbox = self.findChild(QtWidgets.QSpinBox, "analytic_spinbox")
        self.theoretical_spinbox = self.findChild(QtWidgets.QSpinBox, "theoretical_spinbox")
        self.practical_spinbox = self.findChild(QtWidgets.QSpinBox, "practical_spinbox")
        self.grammatical_spinbox = self.findChild(QtWidgets.QSpinBox, "grammatical_spinbox")

        # ------ The parameter labels from the GUI
        self.analytic_marker = self.findChild(QtWidgets.QLabel, "analytic_marker")
        self.theoretical_marker = self.findChild(QtWidgets.QLabel, "theoretical_marker")
        self.practical_marker = self.findChild(QtWidgets.QLabel, "practical_marker")
        self.grammatical_marker = self.findChild(QtWidgets.QLabel, "grammatical_marker")

        self.atpg_btn.clicked.connect(self.set_atpg)


    # ------------------------- FILE NEW, SAVE, SAVE AS, OPEN,RECENT, RESET, AND QUIT FUNCTIONALITY -----------------------------------
        # --------- file new -------------------
        self.shortcut_new = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+N'), self)
        self.new_btn = self.findChild(QtWidgets.QPushButton, "new_btn")

        # ----- file save --------
        self.shortcut_save = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self)
        self.save_btn = self.findChild(QtWidgets.QPushButton, "save_btn")

        # ----- file save as ------------
        self.shortcut_save_as = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Shift+S'), self)
        self.save_as_btn = self.findChild(QtWidgets.QPushButton, "save_as_btn")

        # ---------- file open --------------
        self.shortcut_open = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+O'), self)
        self.open_btn = self.findChild(QtWidgets.QPushButton, "open_btn")

        # --------- Recent files -----------------
        # The toolbutton to set a dropdown that displays all x most recent files
        self.recent_files_toolbtn = self.findChild(QtWidgets.QToolButton, "recent_files_toolbtn")
        self.recent_files_menu = QtWidgets.QMenu()
        # Add the menu items?
        self.load_recent_files()
        self.recent_files_menu.triggered.connect(lambda x: self.load_recent_file_in_window(x.text()))
        self.recent_files_toolbtn.setMenu(self.recent_files_menu)

        # ---------- file reset ----------------
        self.shortcut_reset = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Shift+R'), self)
        self.reset_btn = self.findChild(QtWidgets.QPushButton, "reset_btn")

        # ------ file quit ------------
        self.shortcut_quit = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
        self.shortcut_alt_quit = QtWidgets.QShortcut(QtGui.QKeySequence('Alt+F4'), self)
        self.exit_btn = self.findChild(QtWidgets.QPushButton, "exit_btn")
        
        # ------------------ Connect these shortcuts and buttons to slots --------------
        self.shortcut_save.activated.connect(self.save_file)
        self.save_btn.clicked.connect(self.save_file)

        self.shortcut_save_as.activated.connect(self.save_file_as)
        self.save_as_btn.clicked.connect(self.save_file_as)

        self.shortcut_open.activated.connect(self.open_file)
        self.open_btn.clicked.connect(self.open_file)

        self.shortcut_new.activated.connect(self.new_file)
        self.new_btn.clicked.connect(self.new_file)

        self.exit_btn.clicked.connect(lambda :app.quit())
        self.shortcut_quit.activated.connect(lambda :app.quit())
        self.shortcut_alt_quit.activated.connect(lambda :app.quit())

        self.reset_btn.clicked.connect(self.reset_timetable)
        self.shortcut_reset.activated.connect(self.reset_timetable)


    # --------------- GENERAL INFORMATION PAGE ------------------------
        self.institution = self.findChild(QtWidgets.QLineEdit, "institution_lineedit")
        self.director = self.findChild(QtWidgets.QLineEdit, "director_lineedit")
        self.session_or_year = self.findChild(QtWidgets.QLineEdit, "session_lineedit")
        self.acronym = self.findChild(QtWidgets.QLineEdit, "acronym_lineedit")
        self.extra_info = self.findChild(QtWidgets.QPlainTextEdit, "extra_info_plaintextedit")
        self.logo_path = "TIMETABLE/Icons-mine/App_logo.png"

        self.browse_for_logo = self.findChild(QtWidgets.QPushButton, "browse_for_logo_btn")
        self.gen_info_commit = self.findChild(QtWidgets.QPushButton, "gen_info_commit")
        self.gen_info_edit = self.findChild(QtWidgets.QPushButton, "gen_info_edit")

        self.gen_info_commit.clicked.connect(self.commit_general_info)
        self.gen_info_edit.clicked.connect(self.edit_general_info)
        self.browse_for_logo.clicked.connect(self.dialog_for_logo)

        # -------------- general info labels
        self.institution_label = self.findChild(QtWidgets.QLabel, "institution_label")
        self.session_label = self.findChild(QtWidgets.QLabel, "session_label")
        self.acronym_label = self.findChild(QtWidgets.QLabel, "acronym_label")
        self.extra_info_label = self.findChild(QtWidgets.QLabel, "extra_info_label")
        self.director_label = self.findChild(QtWidgets.QLabel, "director_label")
        self.pre_logo_pic_label = self.findChild(QtWidgets.QLabel, "pre_logo_pic_label")
        self.logo_pic_label = self.findChild(QtWidgets.QLabel, "logo_pic_label")


    # ------------------- REGISTER FACULTY ----------------------------------
        self.reg_dept = self.findChild(QtWidgets.QPushButton, "reg_deptfac_btn")
        self.reg_dept.clicked.connect(self.register_deptfac)

    # ----------------------------------------------------------------------
        self.faculty_list_combobox = self.findChild(QtWidgets.QComboBox, "department_combobox")
    
    # -------------------------  current_main-stacked index
        self.main_stacked_curr_index = 0
        self.page_label = self.findChild(QtWidgets.QLabel, "page_counter")
        self.mainStackedWidget = self.findChild(QtWidgets.QStackedWidget, "mainStackedWidget")
        self.mainStackedWidget.setCurrentIndex(self.main_stacked_curr_index)
        self.page_label.setText(f"Page 1 of {self.mainStackedWidget.count()}")

    # ---------------------------------------------------------------------
    # -------- The REGISTER SUBJECT/COURSE (department in the code)
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
    # --------------- THE CLASS GROUP(category) and class and class arm tree widget
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


    # ---------------------------------------------------------------------------------------------------
    # ----------------------------CREATE DAYS ---------------------------------------------------------------
        self.day_btn = self.findChild(QtWidgets.QPushButton, "create_day_btn")
        self.day_btn.clicked.connect(self.register_day)
        self.day_list = self.findChild(QtWidgets.QListWidget, "day_list")

        # --------- The modify-day radiobutton
        self.day_radbtn = self.findChild(QtWidgets.QRadioButton, "day_radbtn")
        self.day_radbtn.toggled.connect(lambda :self.pull_model(self.day_radbtn, "day"))

        self.day_checkbox = self.findChild(QtWidgets.QCheckBox, "day_position_chbox")
        self.day_position_spinbox = self.findChild(QtWidgets.QSpinBox, "position_spinbox")

        self.day_checkbox.stateChanged.connect(self.day_check_spin_box)


    # -----------------MODIFY CLASS CAT, CLASS AND DAYS ----------------------
        # Identifier for when class models are being edited or created
        self.class_createedit_label = self.findChild(QtWidgets.QLabel, "class_create_edit")
        self.class_cat_radbtn = self.findChild(QtWidgets.QRadioButton, "class_cat_radbtn")
        self.class_radbtn = self.findChild(QtWidgets.QRadioButton, "class_radbtn")

        self.class_cat_radbtn.toggled.connect(lambda :self.pull_model(self.class_cat_radbtn, "classcat"))
        self.class_radbtn.toggled.connect(lambda :self.pull_model(self.class_radbtn, "class"))

        self.classday_models_combobox = self.findChild(QtWidgets.QComboBox, "class_day_models_combo")
        self.classmodel_gbox = self.findChild(QtWidgets.QGroupBox, "classmodel_gbox")

        # This button handles pulling of the model from its list and displaying it in its fields in the GUI
        self.pull_class_day_model_btn = self.findChild(QtWidgets.QPushButton, "pull_class_day_model_btn")
        self.pull_class_day_model_btn.clicked.connect(self.pull_render)

        self.del_class_day = self.findChild(QtWidgets.QPushButton, "del_classday_model_btn")
        self.del_class_day.clicked.connect(self.del_classday_model)

        # -------------------- buttons on top of the classcat treewidget and day listwidgets --------------------
        self.mark_class_btn = self.findChild(QtWidgets.QPushButton, "mark_class_btn")
        self.mark_day_btn = self.findChild(QtWidgets.QPushButton, "mark_days_btn")

        self.class_markall_btn = self.findChild(QtWidgets.QPushButton, "class_markall_btn")
        self.day_markall_btn = self.findChild(QtWidgets.QPushButton, "day_markall_btn")

        # Button to expand or contract the class-class arm tree widget when clcicked
        self.class_expand_btn = self.findChild(QtWidgets.QPushButton, "expand_class_tree_btn")
        self.class_expand_btn.clicked.connect(self.class_expand_contract)

        self.mark_class_btn.clicked.connect(self.mark_class)
        self.mark_day_btn.clicked.connect(self.mark_day)

        self.class_markall_btn.clicked.connect(self.class_mark_all)
        self.day_markall_btn.clicked.connect(self.day_mark_all)

        # if None radiobutton is clicked
        self.class_none_radbtn = self.findChild(QtWidgets.QRadioButton, "class_none_radbtn")

        self.class_none_radbtn.toggled.connect(lambda : self.classday_models_combobox.clear())


    # ----------------------------------------------------------------------------------------------
    # ----------------------- THE DEPARTMENT (FACULTY), SUBJECT AND GENERATED TEACHERS ----------------------
        self.dept_and_teachers_tree = self.findChild(QtWidgets.QTreeWidget, "faculty_course_teacher_tree")
        self.gen_teachers_btn = self.findChild(QtWidgets.QPushButton, "gen_teachers_btn")

        # List widget holding all the coujrses registered so teacher can be generated
        self.gen_teachers_courselist = self.findChild(QtWidgets.QListWidget, "gen_teachers_courselist")

        self.gen_teachers_btn.clicked.connect(self.generate_teachers)
        # Also get the groupbox which has all the working days by teacher
        self.gen_teachers_days_listwidget = self.findChild(QtWidgets.QListWidget, "gen_teachers_days_listwidget")

        # The combobox for teacher's specialty
        self.specialty_combobox = self.findChild(QtWidgets.QComboBox, "specialty_combobox")
        # Teacher's designation
        self.designation_lineedit = self.findChild(QtWidgets.QLineEdit, "designation_lineedit")

        # Button to expand or contract the treewidget showing faculties(departments), subjects/courses and teachers
        self.expand_fac_course_teachers_tree_btn = self.findChild(QtWidgets.QPushButton, "expand_fac_courses_teachers_tree_btn")
        self.expand_fac_course_teachers_tree_btn.clicked.connect(self.expand_fac_courses_teachers_tree)

        # The button to mark courses in bulk
        self.mark_btn = self.findChild(QtWidgets.QPushButton, "mark_courses_btn")
        # self.mark_btn.pressed.connect(self.enable_mark_depts_teachers)
        self.try_btn = self.findChild(QtWidgets.QPushButton, "try_btn")

        # --- Radiobuttons for the modify section -------------
        self.faculty_radbtn = self.findChild(QtWidgets.QRadioButton, "faculty_radbtn")
        self.subj_radbtn = self.findChild(QtWidgets.QRadioButton, "subj_radbtn")
        self.nonacad_radbtn = self.findChild(QtWidgets.QRadioButton, "nonacad_radbtn")
        self.dept_none_radbtn = self.findChild(QtWidgets.QRadioButton, "subj_none_radbtn")

        # Add slots to these radiobuttons
        self.faculty_radbtn.toggled.connect(lambda :self.deptmodel_pull(self.faculty_radbtn))
        self.subj_radbtn.toggled.connect(lambda :self.deptmodel_pull(self.subj_radbtn))
        self.nonacad_radbtn.toggled.connect(lambda :self.deptmodel_pull(self.nonacad_radbtn))

    # ---------------------------- Generate all staff table (and details) -------------------------------
        self.all_staff_table = self.findChild(QtWidgets.QTableWidget, "all_staff_tablewidget")


        # --------------- MODIFY DEPT MODELS (FACULTY, SUBJECT (NOT TEACHERS)) ---------------------------
        self.dept_model_gbox = self.findChild(QtWidgets.QGroupBox, "dept_model_gbox")
        self.dept_model_combobox = self.findChild(QtWidgets.QComboBox, "dept_model_combo")
        self.pull_dept_btn = self.findChild(QtWidgets.QPushButton, "pull_dept_model_btn")
        self.del_depts_btn = self.findChild(QtWidgets.QPushButton, "del_dept_model")

        self.dept_create_update_label = self.findChild(QtWidgets.QLabel, "dept_create_edit")

        # To pull the details of a dept model to the screen
        self.pull_dept_btn.clicked.connect(self.deptmodel_pullrender)

        # Delete dept models
        self.del_depts_btn.clicked.connect(self.del_deptmodels)

        #------------------ the Mark buttons on the dept models tree and list widgets (NO TEACHERS INVOLVED) --------------------
        self.mark_subj_btn = self.findChild(QtWidgets.QPushButton, "mark_subj")
        self.mark_nonacad_btn = self.findChild(QtWidgets.QPushButton, "mark_nonacad")
        self.markall_subj_btn = self.findChild(QtWidgets.QPushButton, "markall_subj")
        self.markall_nonacad_btn = self.findChild(QtWidgets.QPushButton, "markall_nonacad")

        self.mark_subj_btn.clicked.connect(self.enable_mark_fac_subj)
        self.mark_nonacad_btn.clicked.connect(self.enable_mark_nonacad)

        self.markall_subj_btn.clicked.connect(self.markall_subjs)
        self.markall_nonacad_btn.clicked.connect(self.markall_nonacads)


    # --------------------- MODIFY TEACHERS ----------------------------
        # the checkbox to enable fetching teacher from the checkbox
        self.teacher_from_combo_checkbox = self.findChild(QtWidgets.QCheckBox, "teacher_from_combo_checkbox")
        self.teacher_from_spinbox = self.findChild(QtWidgets.QSpinBox, "get_teacher_from_spinbox")
        self.search_teacher_btn = self.findChild(QtWidgets.QPushButton, "search_teacher_btn")
        self.combo_with_teachers = self.findChild(QtWidgets.QComboBox, "combo_with_teacher")
        self.pull_teacher_btn = self.findChild(QtWidgets.QPushButton, "pull_teacher_btn")
        self.teacher_found_label = self.findChild(QtWidgets.QLabel, "teacher_name_label")
        self.search_teacher_gbox = self.findChild(QtWidgets.QGroupBox, "search_teacher_gbox")
        self.del_teacher_btn = self.findChild(QtWidgets.QPushButton, "del_teacher_btn")
        self.mark_teachers_btn = self.findChild(QtWidgets.QPushButton, "mark_teachers_btn")
        self.markall_teachers_btn = self.findChild(QtWidgets.QPushButton, "markall_teachers_btn")
        self.gen_edit_teacher_label = self.findChild(QtWidgets.QLabel, "gen_update_teacher_label")
        self.teacher_freq_gbox = self.findChild(QtWidgets.QGroupBox, "gen_teacher_freq_gbox")

        # start coupling the buttons to methods ----------------------------------
        self.teacher_from_combo_checkbox.stateChanged.connect(self.load_teachers_into_combobox)
        self.search_teacher_btn.clicked.connect(self.search_teacher_by_ID)

        # Render teachers full_name in a label on screen from combobox (Not with his full details yet)
        self.combo_with_teachers.activated.connect(self.render_teacher_from_combobox)

        self.pull_teacher_btn.clicked.connect(self.pull_teacher)
        self.mark_teachers_btn.clicked.connect(self.mark_teachers_in_staff_table)
        self.markall_teachers_btn.clicked.connect(self.mark_all_teachers_in_staff_table)
        self.del_teacher_btn.clicked.connect(self.del_teacher)


    # ---------------------------------------------------------------------------------------------------------
    # ------------------ HANDLES PERIODS MAPPING DEPTS TO CLASS ARMS AND HANDLES THEIR CHUNK VALUES --------------------

        self.subj_freq_chunk_table = self.findChild(QtWidgets.QTableWidget, "subject_freq_chunk_table")
        self.arms_for_chunk_tree = self.findChild(QtWidgets.QTreeWidget, "arms_for_chunk_tree")

        # self.subj_freq_chunk_table.setEditable(False)
        self.adjust_table_columns(self.subj_freq_chunk_table, column_width_cont=[(0,200),(1,70),(2,70)])
        

        # ----------------------- PERIOD GENERATION ------------------------------
        # Grab the radiobuttons
        self.duration_radbtn = self.findChild(QtWidgets.QRadioButton, "duration_radbtn")
        self.day_startend_radbtn = self.findChild(QtWidgets.QRadioButton, "day_startend_radbtn")
        self.abs_day_startend_radbtn = self.findChild(QtWidgets.QRadioButton, "abs_day_startend_radbtn")
        self.duration_gbox = self.findChild(QtWidgets.QGroupBox, "duration_gbox")
        self.day_startend_gbox = self.findChild(QtWidgets.QGroupBox, "day_startend_gbox")
        self.abs_startend_gbox = self.findChild(QtWidgets.QGroupBox, "abs_startend_gbox")
        self.gen_periods_btn = self.findChild(QtWidgets.QPushButton, "gen_periods_btn")
        self.nullify_dayperiods_for_arm_btn = self.findChild(QtWidgets.QPushButton, "nullify_dayperiods_for_arm_btn")
        self.subj_chunk_freq_btn = self.findChild(QtWidgets.QPushButton, "subj_chunk_freq_btn")

        # --- non-academic tables
        self.nonacad_table1 = self.findChild(QtWidgets.QTableWidget, "nonacad_table1")
        self.nonacad_table2 = self.findChild(QtWidgets.QTableWidget, "nonacad_table2")
        self.nonacad_table3 = self.findChild(QtWidgets.QTableWidget, "nonacad_table3")
        self.refresh_period_display_btn = self.findChild(QtWidgets.QPushButton, "refresh_period_display_btn")

        self.gen_periods_btn.clicked.connect(self.generate_periods)
        self.nullify_dayperiods_for_arm_btn.clicked.connect(self.nullify_day_and_periods_from_arms)

        # Button to map (dept, frequency and chunk) to arms
        self.subj_chunk_freq_btn.clicked.connect(self.map_deptfreqchunk_to_arms)

        # Restructure the table's columns
        self.adjust_table_columns(self.nonacad_table1, column_width_cont=[(0,170),(1,60),(2,60)])
        self.adjust_table_columns(self.nonacad_table2, column_width_cont=[(0,170),(1,60),(2,60)])
        self.adjust_table_columns(self.nonacad_table3, column_width_cont=[(0,170),(1,60),(2,60)])


        self.days_for_arms_listwidget = self.findChild(QtWidgets.QListWidget, "days_for_arms_listwidget")
        self.arms_feasible_table = self.findChild(QtWidgets.QTableWidget, "arms_feasible_table")
        self.arms_periods_table = self.findChild(QtWidgets.QTableWidget, "arms_periods_table")
        self.feasibility_btn = self.findChild(QtWidgets.QPushButton, "feasibility_btn")
        self.days_combobox_for_chunk = self.findChild(QtWidgets.QComboBox, "days_combobox_for_chunk")

        self.days_combobox_for_chunk.activated.connect(self.display_periods_in_table)
        self.refresh_period_display_btn.clicked.connect(self.display_periods_in_table)

        self.adjust_table_columns(self.arms_feasible_table, column_width_cont=[(0,175),(1,60),(2,60),(3,60)])
        # self.adjust_table_columns(self.arms_periods_table, column_width_cont=[(1, 550)])

        # -----------------------------------------------
        #  first period groupbox box that is not disabled
        self.period_gbox = self.duration_gbox
        # -----------------------------------------------

        # Connect signals to deactivate other gboxes when radiobutton is clicked
        self.duration_radbtn.toggled.connect(lambda boole, gbox=self.duration_gbox: self.disable_period_boxes(gbox))
        self.day_startend_radbtn.toggled.connect(lambda boole, gbox=self.day_startend_gbox: self.disable_period_boxes(gbox))
        self.abs_day_startend_radbtn.toggled.connect(lambda boole, gbox=self.abs_startend_gbox: self.disable_period_boxes(gbox))


    # ----------------------- ASSIGN SUBJECT TEACHERS TO CLASS ARMS ----------------------------------------
        # the frame that contains the progressbars that show when teachers are being assigned.
        self.load_assignment_frame = self.findChild(QtWidgets.QFrame, "load_assignment_fr")

        self.auto_assign_btn = self.findChild(QtWidgets.QPushButton, "auto_assign_btn")
        self.manual_assign_btn = self.findChild(QtWidgets.QPushButton, "manual_assign_btn")
        self.undo_assign_btn = self.findChild(QtWidgets.QPushButton, "undo_assign_btn")
        self.pull_arm_btn = self.findChild(QtWidgets.QPushButton, "pull_arm_btn")

        self.assign_teacher_combobox = self.findChild(QtWidgets.QComboBox, "assign_teacher_combobox")
        self.assign_arm_combobox = self.findChild(QtWidgets.QComboBox, "assign_arm_combobox")
        self.assign_subj_combobox = self.findChild(QtWidgets.QComboBox, "assign_subj_combobox")
        self.arm_id_container = self.findChild(QtWidgets.QFrame, "arm_id_container")

        self.arm_from_combo_chbox = self.findChild(QtWidgets.QCheckBox, "arm_from_combo_chbox")
        self.arm_combobox = self.findChild(QtWidgets.QComboBox, "arm_combobox")
        self.arm_id_spinbox = self.findChild(QtWidgets.QSpinBox, "arm_id_spinbox")
        self.arm_by_id_search_btn = self.findChild(QtWidgets.QPushButton, "arm_by_id_search_btn")

        self.arm_not_found_label = self.findChild(QtWidgets.QLabel, "arm_not_found_label")
        self.arm_label = self.findChild(QtWidgets.QLabel, "arm_label")
        self.arm_class_label = self.findChild(QtWidgets.QLabel, "arm_class_label")
        self.arm_classcat_label = self.findChild(QtWidgets.QLabel, "arm_classcat_label")
        self.assign_subj_teacher_table = self.findChild(QtWidgets.QTableWidget, "assign_subj_teacher_table")

        # Adjust the columns of the tablewidget
        self.adjust_table_columns(self.assign_subj_teacher_table, [(0, 140), (1, 110), (2, 50), (3, 50)])
        self.arm_not_found_label.hide()

        # ------------- Add signals and stuff ----------
        self.load_assignment_frame.hide()
        self.arm_from_combo_chbox.stateChanged.connect(self.load_arms_into_combobox)
        self.pull_arm_btn.clicked.connect(self.pull_up_classarm)
        self.auto_assign_btn.clicked.connect(self.auto_assign_teachers_to_arms)
        self.undo_assign_btn.clicked.connect(self.undo_auto_assign_teachers_to_arms)
        # The credential for the arm that would be pulled up
        self.arm_cred = None


    # ---------------------- PACKETING (AND UNDOING) AND SORTING BUTTONS ----------------------------
        # frame to come on when packeting process is loading
        self.load_packeting_frame = self.findChild(QtWidgets.QFrame, "load_packeting_fr")
        self.packet_btn = self.findChild(QtWidgets.QPushButton, "packet_btn")
        self.sort_btn = self.findChild(QtWidgets.QPushButton, "sort_btn")
        self.undo_packet_btn = self.findChild(QtWidgets.QPushButton, "undo_packet_btn")
        self.ref_day_combobox = self.findChild(QtWidgets.QComboBox, "ref_day_combobox")
        self.ref_arm_combobox = self.findChild(QtWidgets.QComboBox, "ref_arm_combobox")
        self.refresh_ref_day_arm_btn = self.findChild(QtWidgets.QPushButton, "refresh_ref_day_arm_btn")


        # The sorting frame with the progressbars that come alive when an operation is loading
        self.load_sorting_frame = self.findChild(QtWidgets.QFrame, "load_sorting_fr")
        
        self.load_packeting_frame.hide()
        self.load_sorting_frame.hide()

        # --- Add slots to the above buttons ---
        self.packet_btn.clicked.connect(self.packet)
        self.undo_packet_btn.clicked.connect(self.undo_packet)
        self.refresh_ref_day_arm_btn.clicked.connect(self.refresh_day_arm)
        # ------ The sort operation -------
        self.sort_btn.clicked.connect(self.full_sort)



    # --------------------------------------------------------------------------------------------------------------------
    # --------------------------- THE ADVANCED SECTION (WITH TEACHERS' SPACING IMPLICIT) ---------------------------------
        self.teachers_spacing_btn = self.findChild(QtWidgets.QPushButton, "teachers_spacing_btn")
        self.teachers_spacing_btn.clicked.connect(self.teachers_spacing)


    # -----------------------------------------------------------------------------------------------------------------
    # .................. DIALS AND FRAMES, AND TRACKING: SEMI-FINISH: DISPLAY SORT RESULTS IN FRAME WITH THE DIALS AND STUFF ------------------
        # Get the frame with containing the radiobuttons for displaying content b arm or day
        # NOT ALL WIDGETS DEFINED HERE, SOME DEFINED IN THE METHODS TO BE RUN AS SLOTS
        self.match_item = "Nil"

        self.display_by_frame = self.findChild(QtWidgets.QFrame, "display_by_fr")
        self.track_models_by_frame = self.findChild(QtWidgets.QFrame, "track_models_by_fr")
        self.display_by_btn = self.findChild(QtWidgets.QPushButton, "display_by_btn")
        self.track_by_btn = self.findChild(QtWidgets.QPushButton, "track_by_btn")
        self.untrack_by_btn = self.findChild(QtWidgets.QPushButton, "untrack_by_btn")
        
        self.track_btn = self.findChild(QtWidgets.QPushButton, "track_btn")

        # The frames housing dials and scroll btns both for periods display and tracking
        self.display_dial_and_btns_frame = self.findChild(QtWidgets.QFrame, "display_dial_and_btns_frame")
        self.track_dial_and_btns_frame = self.findChild(QtWidgets.QFrame, "track_dial_and_btns_frame")
        # -------------
        # frames for the progressbars for display and track
        self.load_track_frame = self.findChild(QtWidgets.QFrame, "load_track_fr")
        self.load_display_frame = self.findChild(QtWidgets.QFrame, "load_display_fr")
        # ------------------------
        self.model_type_label = self.findChild(QtWidgets.QLabel, "model_type_label")
        self.model_item_label = self.findChild(QtWidgets.QLabel, "model_item_label")
        self.track_item_label = self.findChild(QtWidgets.QLabel, "track_item_label")
        self.track_model_type_label = self.findChild(QtWidgets.QLabel, "track_model_type_label")
        self.timetable_title_label = self.findChild(QtWidgets.QLabel, "timetable_title_label")

        self.periods_display_frame = self.findChild(QtWidgets.QFrame, "periods_display_frame")
        self.display_in_frame_btn = self.findChild(QtWidgets.QPushButton, "display_in_frame_btn")

        self.items_dial = self.findChild(QtWidgets.QDial, "items_dial")
        self.next_item_btn = self.findChild(QtWidgets.QPushButton, "next_item_btn")
        self.prev_item_btn = self.findChild(QtWidgets.QPushButton, "prev_item_btn")

        self.track_dial = self.findChild(QtWidgets.QDial, "track_dial")
        self.track_next_item_btn = self.findChild(QtWidgets.QPushButton, "track_next_item_btn")
        self.track_prev_item_btn = self.findChild(QtWidgets.QPushButton, "track_prev_item_btn")

        # ---------- connect the signals to slots --------------
        self.display_dial_and_btns_frame.setEnabled(False)
        self.track_dial_and_btns_frame.setEnabled(False)

        self.load_display_frame.hide()
        self.load_track_frame.hide()


        self.display_by_btn.clicked.connect(self.display_by_arm_or_day)
        self.items_dial.valueChanged.connect(lambda :self.get_item_from_dial_value(self.items_dial, self.model_item_label, self.model_type_label))
        # display periods in the frame
        self.display_in_frame_btn.clicked.connect(self.show_finished_periods_in_frame)
        # self.display_in_frame_btn.clicked.connect(self.test_func)
        self.next_item_btn.clicked.connect(lambda : self.scroll_model_item_by_btn(self.items_dial, self.model_item_label, self.model_type_label, 1))
        self.prev_item_btn.clicked.connect(lambda :self.scroll_model_item_by_btn(self.items_dial, self.model_item_label, self.model_type_label, -1))

        # -------------- slots for tracking ----------------
        self.track_dial.valueChanged.connect(lambda :self.get_item_from_dial_value(self.track_dial, self.track_item_label, self.track_model_type_label))
        self.track_next_item_btn.clicked.connect(lambda : self.scroll_model_item_by_btn(self.track_dial, self.track_item_label, self.track_model_type_label, 1))
        self.track_prev_item_btn.clicked.connect(lambda : self.scroll_model_item_by_btn(self.track_dial, self.track_item_label, self.track_model_type_label, -1))

        self.track_by_btn.clicked.connect(self.retrieve_track_model)
        self.untrack_by_btn.clicked.connect(self.deselect_track_models)
        self.track_btn.clicked.connect(self.track_model_item)


    # ------------------------------------------------------------------------------------------------------------------------
    # ------------------------------- FINISHED REPORT AND DIAGNNOSTICS REPORT GENERATION -------------------------------------
        self.get_dir_btn = self.findChild(QtWidgets.QPushButton, "get_dir_btn")
        self.report_basis_combobox = self.findChild(QtWidgets.QComboBox, "report_basis_combobox")
        self.report_format_combobox = self.findChild(QtWidgets.QComboBox, "report_format_combobox")

        # Add slots to buttons
        self.get_dir_btn.clicked.connect(self.generate_finished_report)

    # ------------------ LOADS ALLTHE TREES especially for when app is starting from an existing file ------------------
        # Loads the faculty/department-courses tree widget
        self.load_all_models()


    # ------------------------------------------------------------------------------------------------------------------------
    # ------------------ PRIMARILY THE GUI OPERATION FUNCTIONS (SAVE, SAVEAS, OPEN, NEW and other settings ) -----------------
    def new_file(self):
        """ handles the creation of a new timetable file """
        run_app_anew()


    def save_file(self):
        """ Handles saving the timetable file (NOT THE GENERATED REPORTS!) """

        # Check to see if this file has not been saved before, by checking the Timetable objects project_file_path attribute
        if self.Timetable.Timetable_obj.project_file_path == '':
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save your timetable file", "", "Shelva timetable file(*tmtb)")       
            if file_path:
                file_path = QtCore.QDir.toNativeSeparators(file_path)
        else:
            file_path = self.Timetable.Timetable_obj.project_file_path
        self.Timetable.save(file_path)
        # Reset the window title to the files name
        self.setWindowTitle(self.Timetable.Timetable_obj.project_file_name)
        self.statusBar().showMessage("File saved successfully", 1000)


    def save_file_as(self):
        """ Fires when the save as button or shortcut is triggered """
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save your timetable file as", "", "Shelva timetable file(*tmtb)")       
        if file_path:
            file_path = QtCore.QDir.toNativeSeparators(file_path)
        self.Timetable.save(file_path)
        self.setWindowTitle(self.Timetable.Timetable_obj.project_file_name)
        self.statusBar().showMessage("Save your file as", 1000)



    def open_file(self, file_path_input=None):
        """ Opens a previously created file and loads its contents on the GUI screen """

        # If a file path input was given as an argument, make that the file_path, else open a Qdialog box
        if file_path_input:
            file_path = file_path_input + ".tmtb" if not file_path_input.endswith(".tmtb") else file_path_input
        else:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open a timetable file", "", "Shelva timetable file(*tmtb)")

        if file_path:
            file_path = QtCore.QDir.toNativeSeparators(file_path)
            tt_obj = self.Timetable.load_tt_obj_from_file(file_path)

            # if the timetable retrieved exists
            if tt_obj is not None:
                run_app_anew(tt_obj)


    def load_recent_file_in_window(self, recent_file_path):
        """ Loads the recent file clicked into THIS window, not another """
        # Load up the timetable object from the 'recent_file_path'
        if not recent_file_path.endswith(".tmtb"):
            recent_file_path += ".tmtb"
            
        tt_obj = self.Timetable.load_tt_obj_from_file(recent_file_path)
        self.Timetable = Tt_manager.TimeTableManager(tt_obj=tt_obj)

        # Now load all the models
        self.statusBar().showMessage("Loading up a recent timetable file", 3000)
        self.load_all_models()





    def load_recent_files(self):
        """ Loads the dropdown menu for the 'recent' toolbutton """
        def _load_items_into_menu(items_list):
            for item in items_list:
                self.recent_files_menu.addAction(item)
        # -------------------------------
        recent_files = self.Timetable.load_recent_projects()
        for project in recent_files:
            self.recent_files_menu.addAction(project)

        self.statusBar().showMessage("Load up a recent file", 1000)


    def reset_timetable(self):
        """ Fires when the reset button is clicked, but not without raising a messagebox first """

        def reset(button):
            """ Actually resets the timetable, gets passed into the messagebox method as a callback. Takes as an
            argument the messagebox button """
            if "ok" in button.text().lower():
                self.Timetable.reset_tt_obj()
                self.load_all_models()

        self.messagebox(text="You clicked the reset button. Are you sure you want to proceed?", 
            icon="warning" ,title="Reset confirmation", callback=reset)
        self.statusBar().showMessage("Timetable has been reset", 2000)


    def set_atpg(self):
        """ This slot fires in order to set atpg values and parameter names """
        # Get the inputs of the widgets
        analytic_name = self.analytic_lineedit.text()
        theoretical_name = self.theoretical_lineedit.text()
        practical_name = self.practical_lineedit.text()
        grammatical_name = self.grammatical_lineedit.text()

        analytic_val = self.analytic_spinbox.value()
        theoretical_val = self.theoretical_spinbox.value()
        practical_val = self.practical_spinbox.value()
        grammatical_val = self.grammatical_spinbox.value()
        
        analytic_name = analytic_name if analytic_name else "Analytic"
        theoretical_name = theoretical_name if theoretical_name else "Theoretical"
        practical_name = practical_name if practical_name else "Practical"
        grammatical_name = grammatical_name if grammatical_name else "Grammatical"
        
        # Pass in these values  as tuple arguments to the timetable manager's set_ATPG_parameters method
        self.Timetable.set_ATPG_parameters((analytic_name, analytic_val), (theoretical_name, theoretical_val), 
            (practical_name, practical_val), (grammatical_name, grammatical_val))

        self.analytic_marker.setText(analytic_name)
        self.theoretical_marker.setText(theoretical_name)
        self.practical_marker.setText(practical_name)
        self.grammatical_marker.setText(grammatical_name)



    def load_nav_dialog_with_details(self, str_arg):
        """ Loads the dialog box when any of the buttons in the archive tab on the nav bar is clicked """
        ModelDetailWindow(self.Timetable.Timetable_obj).get_details_load_on_dialog(str_arg)


    def load_all_models(self):
        """Loads up all the trees and lists and whatnot at once"""

        self.load_fac_courses_tree()
        self.load_group_class_arm_tree()
        self.load_days_list()
        self.load_faculty_courses_teachers_tree()
        self.load_gen_teachers_day_chboxes()
        self.gen_arms_freq_chunk_tree(expand= True)
        self.load_days_for_arms_listwidget()
        self.load_days_for_arms_listwidget()
        self.load_subjects_freq_chunk_table()
        self.load_arms_feasible_table()
        self.load_gen_teachers_courselist()
        self.load_gen_teachers_day_chboxes()
        self.load_faculty_courses_teachers_tree(markable=False, expanded=True)
        self.load_all_staff_table(with_checkbox=False, check_all=False)
        


    def load_manual_into_toolbox(self):
        # Find the toolbox widget
        # Get the scrollarea housing the toolbox to be built
        tool_scroll = self.findChild(QtWidgets.QScrollArea, "manual_scrollarea")
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
            textEdit.setStyleSheet(""" 
                padding:10px;
                background:#f9f9fb;
             """)
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
            }
            """)

        tool_scroll.setWidget(tool_box)
    

    # def menubar_colour(self):
    #     tool_bar = self.findChild(QtWidgets.QToolBar,"toolBar")
    #     menu_bar = self.findChild(QtWidgets.QMenuBar,"menuBar")

    #     style = """

    #         background:qlineargradient(spread:pad, x1:0.04, y1:0.499, x2:0.95, y2:0.501, 
    #         stop:0.0568182 rgba(0, 0, 0, 255), stop:0.855114 rgba(0, 0, 0, 255), 
    #         stop:0.995222 rgba(94, 94, 94, 255));

    #         """

    #     tool_bar.setStyleSheet(style + "height:7px;")
        # menu_bar.setStyleSheet(style + "height:20px; color: #fff;")


    def switch_mainstacked(self, int_num):
        """Switches between pages of the stacked widget for different operations"""
        num_pages = self.mainStackedWidget.count()

        index = (self.main_stacked_curr_index + int_num) % num_pages
        self.main_stacked_curr_index = index

        # set the current mainstacked widget to the widget with index index
        self.mainStackedWidget.setCurrentIndex(self.main_stacked_curr_index)
        self.page_label.setText(f"Page {self.main_stacked_curr_index + 1} of {num_pages}")

        # Get the title and info to be displayed on the textedit, paga by page
        title, info = self.stacked_pages_title_and_details[self.main_stacked_curr_index]
        self.page_title_label.setText(title.upper())
        self.page_info_box_textedit.setHtml(info)


    # --------------------------------------------------------------------------------------------------
    # ------------------------------- BACKEND-INTO-GUI FUNCTIONS ---------------------------------------
    def enable_all_in_widget(self, widget, enable=True):
        """ Renders all the widgets in mother widget active or inactive"""
        for child in widget.children():
            if isinstance(child, QtWidgets.QWidget):
                child.setEnabled(enable)


    def dialog_for_logo(self):
        """ This function fires when the browse button is clicked (to open a dialog from which to select a logo picture) """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select your school/institution's logo (JPEG or PNG)",
            "", "JPEG files(*.jpg);; JPEG files(*.JPEG);;PNG files(*.png)")

        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            self.logo_path = filename
            self.pre_logo_pic_label.setPixmap(QtGui.QPixmap(filename))


    def commit_general_info(self):
        """ Registration OR UPDATE of all the general info fields"""
        institution = self.institution.text().strip()
        director = self.director.text().strip()
        session = self.session_or_year.text().strip()
        acronym = self.acronym.text().strip() if self.acronym.text() else "PROJECT-SHELVA"
        extra_info = self.extra_info.toPlainText().strip()

        # Something interesting happens with self.logo_path; a dialog box is opened.

        # Send these values to the manager
        self.Timetable.stash_general_info({
            "institution":institution,
            "director":director,
            "session_or_year":session,
            "acronym":acronym,
            "extra_info":extra_info,
            "logo_path":self.logo_path
            })

        # Clear the fields
        self.institution.clear()
        self.director.clear()
        self.session_or_year.clear()
        self.acronym.clear()
        self.extra_info.clear()


        values_gotten = self.Timetable.get_general_info()
        self.institution_label.setText(values_gotten["institution"] if values_gotten["institution"] else "None provided.")
        self.session_label.setText(values_gotten["session_or_year"] if values_gotten["session_or_year"] else "None provided.")
        self.acronym_label.setText(values_gotten["acronym"] if values_gotten["acronym"] else "None provided.")
        self.director_label.setText(values_gotten["director"] if values_gotten["director"] else "None provided.")
        self.extra_info_label.setText(values_gotten["extra_info"] if values_gotten["extra_info"] else "None provided.")
        self.logo_pic_label.setPixmap(QtGui.QPixmap(values_gotten["logo_path"]))

        # ALSO ENABLE THE LOGO. THE LABEL FOR IT HAS BEEN DEFINED UP TOP!

        self.gen_info_edit.setEnabled(True)


    def edit_general_info(self):
        """ This function simply pulls all the general info details on to the lineedit widgets on the GUI screen """
        values_gotten = self.Timetable.get_general_info()

        self.institution.setText(values_gotten["institution"])
        self.session_or_year.setText(values_gotten["session_or_year"])
        self.acronym.setText(values_gotten["acronym"])
        self.director.setText(values_gotten["director"])
        self.extra_info.insertPlainText(values_gotten["extra_info"])


    def register_deptfac(self):
        """Collects the data for registering a faculty (A DEPARTMENT in the GUI !!!) from the GUI"""

        update = True if "update" in self.dept_create_update_label.text().lower() else False
        
        fac_name = self.findChild(QtWidgets.QLineEdit, "deptfac_name")
        HOD_name = self.findChild(QtWidgets.QLineEdit, "deptfac_HOD")
        description = self.findChild(QtWidgets.QPlainTextEdit, "deptfac_description")


        fac_name_text = fac_name.text().strip()
        HOD_name_text = HOD_name.text().strip()
        description_text = description.toPlainText().strip()
         
        # check if fields are filled else raise an error message box
        if UITimetable.check_fields_or_error(fields_values_list=[fac_name_text, description_text]):

            self.Timetable.create_faculty(fac_name_text, HOD=HOD_name_text, description=description_text, update=update)
            # Clear the input fields
            fac_name.clear()
            HOD_name.clear()
            description.clear()

        else:
           UITimetable.messagebox(title="Fields error",icon="critical",text="Required field(s) left blank, please fill them.")

        # Adjust the label to "Create Department mmodels"
        self.dept_create_update_label.setText("Create Department Models")
        # Load up up the faculties created!
        self.load_fac_courses_tree()
        self.load_faculty_courses_teachers_tree()

        # ----------------------------
        # Set the modify section radiobutton to None
        self.dept_none_radbtn.setChecked(True)
        # Clear the modify combobox
        self.dept_model_combobox.clear()


    def nonacad_fields(self):
        """This function disables certain fields in the registration page, based on whether or not the course(dept) is academic"""

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
        """Registers a subject/course (a dept) in the code. Suitable for both parallel(concurrent) and non-parallel
        dept objects """

        # Enable all the widgets in the reg_subject groupbox
        update = True if "update" in self.dept_create_update_label.text().lower() else False
        self.enable_all_in_widget(self.findChild(QtWidgets.QGroupBox, "reg_subject"))

        course_name = self.findChild(QtWidgets.QLineEdit, "course_name_lineedit")
        head_subject = self.findChild(QtWidgets.QLineEdit, "hos_lineedit")

        parallel_checkbox = self.findChild(QtWidgets.QCheckBox, "parallel_checkbox")

        # Now get the values from these QObjects
        course_name_text = course_name.text().strip()
        acad_or_not_text = self.acad_or_not.currentText().strip()
        parallel_or_no = parallel_checkbox.isChecked()

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
                    self.Timetable.create_department(course_name_text,faculty=department_text, hos=head_subject_text, A=analytic_slider_val, 
                        T=theoreticai_slider_val, P=practical_slider_val, G=grammatical_slider_val, is_parallel= parallel_or_no, update=update)

                    # Return the sliders to 1,1,1,1
                    self.analytic_slider.setValue(1)
                    self.practical_slider.setValue(1)
                    self.theoretical_slider .setValue(1)
                    self.grammatical_slider.setValue(1)


                else:
                    # one of the fields have not been filled. display error message
                    UITimetable.messagebox(title="Fields error",icon="critical",text="No Department under which to create subject/course")
            
            # -------------------------- BELOW IS FOR NON-ACAD REGISTRATION -------------------------------------
            else:
                # If it is a non-academic department
                self.Timetable.create_special_department(course_name_text, update=update)
                # Load this non-academic department into the first if three period tables
                self._load_nonacad_tables(self.findChild(QtWidgets.QTableWidget, "nonacad_table1"))

        else:
            UITimetable.messagebox(title="Empty field error",icon="critical",text="You have not entered the name of the course.")

        course_name.clear()
        
        head_subject.clear()
        self.faculty_list_combobox.clear()

        self.acad_or_not.setCurrentIndex(0)
        # Load up up the faculties created!
        self.load_fac_courses_tree()
        self.load_nonacad_courses_list()
        # table for imputtimg subjects frequency and chunk values
        self.load_subjects_freq_chunk_table()
        # Load the tree containing faculty, couses and teachers
        self.load_faculty_courses_teachers_tree()

        self.load_gen_teachers_courselist()

        # self.load_depts_for_map_to_arms()

        # ----------- set text back to "creating models" ----
        self.dept_create_update_label.setText("Create Department Models")
        # ----------------------------
        # Set the modify section radiobutton to None
        self.dept_none_radbtn.setChecked(True)
        # Clear the modify combobox
        self.dept_model_combobox.clear()


    def load_fac_courses_tree(self, with_checkbox=False, expanded=False):
        """This method handles putting registered faculties and depts/courses on the TreeWidget on the screen and also loading
        them. No teachers involved. Lives on the fac creation modification page."""
        
        # treewidget.setColumnCount(1)
        self.fac_courses_treewidget.clear()
        self.faculty_list_combobox.clear()

        for faculty in self.Timetable.Timetable_obj.list_of_faculties:
            # Adds the list of all the registered to the combobox for
            self.faculty_list_combobox.addItem(faculty.full_name)

            # Load the faculty name into the tree widget
            faculty_item = QtWidgets.QTreeWidgetItem()
            faculty_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/department.png",icon_width=18,
                label_text=faculty.full_name, with_checkbox=with_checkbox)

            self.fac_courses_treewidget.addTopLevelItem(faculty_item)
            faculty_item.setExpanded(expanded)
            self.fac_courses_treewidget.setItemWidget(faculty_item, 0, faculty_widg)

            for dept in faculty.depts_list:
                # Create a nested node in each faculty for the department(subject/course)
                subject_item = QtWidgets.QTreeWidgetItem()
                subject_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/subject.png",icon_width=14, icon_height=16,
                    label_text=dept.full_name, with_checkbox=with_checkbox)

                faculty_item.addChild(subject_item)
                self.fac_courses_treewidget.setItemWidget(subject_item, 0, subject_widg)


    def load_nonacad_courses_list(self, with_checkbox=False):
        """Loads the Listwidget displaying all the created non-academic courses, e.g. break"""
        self.non_acad_depts_listwidget.clear()

        for nonacad in self.Timetable.Timetable_obj.list_of_nonacad_depts:
            list_item = QtWidgets.QListWidgetItem()
            nonacad_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/nonacad.png", icon_width=16, icon_height=14, 
                label_text=nonacad.full_name, with_checkbox=with_checkbox)

            self.non_acad_depts_listwidget.addItem(list_item)
            self.non_acad_depts_listwidget.setItemWidget(list_item, nonacad_widg)


    def fac_courses_tree_clicked(self):
        """ This function fires when any element in the Department-subject tree widget is clicked
        and loads their details onto the blackboard icon """
        current_item = self.fac_courses_treewidget.currentItem()
        c_text = self.fac_courses_treewidget.itemWidget(current_item, 0)

        c_text = c_text.full_name_label.text()

        obj_basis = "depts" if current_item.parent() else "faculties"
        # print(f"c_text: {c_text} obj_id: {obj_identifier}")
        obj_in_question = self.Timetable.get_model_item_object(obj_basis, c_text)

        info_html_str = get_detailed_info_from_fac_or_dept(obj_in_question, obj_basis)
        # self.board.clear()
        self.board.setHtml(info_html_str)

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ---------- This section reserved for modifying dept models (faculty, depts(subjects) and teachers)----
    def which_dept_model_radbtn(self):
        """ This function returns the radiobutto  that is checked for in the groupbox containing dept models """
        for child in self.dept_model_gbox.children():
            if isinstance(child, QtWidgets.QRadioButton) and child.isChecked():
                return child


    def deptmodel_pull(self, model):
        """ Pulls up the appropriate list of models to the combobox in the modify section of the dept models. """

        self.dept_model_combobox.clear()

        # Get the radiobutton clicked
        radbtn_clicked_text = model.text()
        # Pull the model up
        models_list = self.Timetable.pull_dept_model_list(radbtn_clicked_text)
        # Now display the models on the screen
        self.dept_model_combobox.addItems(models_list)


    # Pulls dept model (Department(faculty) or course onto the GUI screen for edit)
    def deptmodel_pullrender(self):
        """ Fetches the selected dept model item to edit and displays its details out on GUI fields screen """

        radbtn = self.which_dept_model_radbtn()
        radbtn = radbtn.text()

        # if combobox is empty, there is nothing to update, so display error messagebox
        if not self.dept_model_combobox.currentText():
            UITimetable.messagebox(icon="critical", title="No model items", text="Modification cannot be done", extratext="You cannot modify items you have yet to create.")
            return
        
        #--- sends radbtn and the currenttext of combobox in as a tuple 
        item_details = self.Timetable.pull_deptmodel_item((radbtn,self.dept_model_combobox.currentText()))

        if radbtn == "Department":
            # put it in the values into the fields
            fac_name = self.findChild(QtWidgets.QLineEdit, "deptfac_name")
            HOD_name = self.findChild(QtWidgets.QLineEdit, "deptfac_HOD")
            description = self.findChild(QtWidgets.QPlainTextEdit, "deptfac_description")

            fac_name.setText(item_details["name"])
            HOD_name.setText(item_details["HOD"])
            description.insertPlainText(item_details["description"])

        elif radbtn == "Subject/Course":

            course_name = self.findChild(QtWidgets.QLineEdit, "course_name_lineedit")
            head_subject = self.findChild(QtWidgets.QLineEdit, "hos_lineedit")

            course_name.setText(item_details["name"])
            head_subject.setText(item_details["hos"])

            # Display "Academic" on the combobox
            self.faculty_list_combobox.itemText(0)
            # Render it invalid
            self.faculty_list_combobox.setEnabled(False)

            self.analytic_slider.setValue(item_details["A"])
            self.practical_slider.setValue(item_details["P"])
            self.theoretical_slider.setValue(item_details["T"])
            self.grammatical_slider.setValue(item_details["G"])

        else:
            course_name = self.findChild(QtWidgets.QLineEdit, "course_name_lineedit")
            atpg_wrapper_box = self.findChild(QtWidgets.QGroupBox, "atpg_wrapper")

            course_name.setText(item_details["name"])
            self.acad_or_not.setCurrentIndex(1)
            self.acad_or_not.setEnabled(False)
            # Render the below invalid
            self.faculty_list_combobox.setEnabled(False)
            atpg_wrapper_box.setEnabled(False)
            head_subject = self.findChild(QtWidgets.QLineEdit, "hos_lineedit")
            head_subject.setEnabled(False)


        # Chenge the label uptop to "Updating..."
        self.dept_create_update_label.setText("Update Department Models")


    def enable_mark_fac_subj(self):
        """ Enables mark department (faculty) and subjects (the tree without the teachers) """

        # If "mark" button has been clicked
        if "Mark" in self.mark_subj_btn.text():
            self.load_fac_courses_tree(with_checkbox=True,expanded=True)
            self.mark_subj_btn.setText("Unmark")
            self.markall_subj_btn.setEnabled(True)
        else:
            self.load_fac_courses_tree(expanded=True)
            self.mark_subj_btn.setText("Mark for delete")
            self.markall_subj_btn.setEnabled(False)


    def enable_mark_nonacad(self):
        """ Enables mark operation for nonacad depts in the listwidget """

        # If "mark" button has been clicked
        if "Mark" in self.mark_nonacad_btn.text():
            self.load_nonacad_courses_list(with_checkbox=True)
            self.mark_nonacad_btn.setText("Unmark")
            self.markall_nonacad_btn.setEnabled(True)
        else:
            self.load_nonacad_courses_list()
            self.mark_nonacad_btn.setText("Mark for delete")
            self.markall_nonacad_btn.setEnabled(False)
        

    def markall_subjs(self):
        """ mark all department(faculty) or subject model items in the faculty_courses tree. No teachers involved """

        # Get the treewidget for fac_csubjects, (no teachers involved)
        root = self.fac_courses_treewidget.invisibleRootItem()
        child_count = root.childCount()

        for k in range(child_count):
            fac_item = root.child(k)
            fac_widg = self.fac_courses_treewidget.itemWidget(fac_item, 0)     #Custom WidgetTree instance
            # Check the checkbox in the fac_widget
            fac_widg.get_checkbox().setCheckState(QtCore.Qt.Checked)

            for i in range(fac_item.childCount()):
                subj_item = fac_item.child(i)
                subj_widg = self.fac_courses_treewidget.itemWidget(subj_item, 0)
                subj_widg.get_checkbox().setCheckState(QtCore.Qt.Checked)


    def markall_nonacads(self):
        """ marks all the nonacad subjects in the list """

        for k in range(self.non_acad_depts_listwidget.count()):
            nonacad_item = self.non_acad_depts_listwidget.item(k)
            nonacad_widg = self.non_acad_depts_listwidget.itemWidget(nonacad_item)

            nonacad_widg.get_checkbox().setCheckState(QtCore.Qt.Checked)


    def del_deptmodels(self):
        """ The big-boy method to handle deletion of faculty or subject items """

        # Get which radiobutton has been clicked
        rad_clicked = self.which_dept_model_radbtn()
        mod_name = rad_clicked.text()


        if mod_name == "None":
            # Raise error messagebox. No model type specified
            return

        selected_items = []
        # If the mark button is clicked
        if self.mark_subj_btn.text() == "Unmark":
            if mod_name== "Department":
                root = self.fac_courses_treewidget.invisibleRootItem()
                child_count = root.childCount()

                for k in range(child_count):
                    fac_item = root.child(k)
                    fac_widg = self.fac_courses_treewidget.itemWidget(fac_item, 0)     #Custom WidgetTree instance
                    # Check if the checkbox in the fac_widget is checked

                    if fac_widg.get_checkbox().isChecked():
                        selected_items.append(fac_widg.full_name_label.text())


            elif mod_name == "Subject/Course":

                root = self.fac_courses_treewidget.invisibleRootItem()
                child_count = root.childCount()

                for k in range(child_count):
                    fac_item = root.child(k)
                    fac_widg = self.fac_courses_treewidget.itemWidget(fac_item, 0)     #Custom WidgetTree instance
                    # Check if the checkbox in the fac_widget is checked

                    for m in range(fac_item.childCount()):
                        subj_item = fac_item.child(m)
                        subj_widg = self.fac_courses_treewidget.itemWidget(subj_item, 0)  
                    
                        if subj_widg.get_checkbox().isChecked():
                            selected_items.append(subj_widg.full_name_label.text())

            else:
                for k in range(self.non_acad_depts_listwidget.count()):
                    nonacad_item = self.non_acad_depts_listwidget.item(k)
                    nonacad_widg = self.non_acad_depts_listwidget.itemWidget(nonacad_item)

                    if nonacad_widg.get_checkbox().isChecked():
                        selected_items.append(nonacad_widg.full_name_label.text())

        else:
            # If the mark button was not clicked, pick from the combobox
            selected_items.append(self.dept_model_combobox.currentText())

    

        # -------------------------------------------------------------------------------
        # -------------- AFTER THE IF-STATEMENTS MUST HAVE RUN -------------
        # check if selected items is empty, raise an error messagebox if
        if UITimetable.check_fields_or_error(fields_values_list=selected_items):
        # Carry out the delete from the GUI manager. The model_name is also passed in with the selected items in a dictionary
        
        # --------------------------------------------------------------
        #-------- REAL DELETION OPERATION TAKES PLACE HERE! ------------
            # But just before, display messagebox warning of the consequences
            def go_or_no(btn_clicked):
                """defining the callback function whether or not user clicks okay to delete"""
                self.go_ahead = True if btn_clicked.text() == "OK" else False
            # ----------------------------------------------------------

            self.go_ahead = False

            UITimetable.messagebox(title="FYI", icon="warning", text=f"When a {mod_name} is deleted, all its child items get deleted.",
                extratext="Would you still like to proceed?", callback=go_or_no)

            if self.go_ahead:
                self.Timetable.delete_models({mod_name:selected_items})

                # ------------------------------------------------------------
                # LOAD UP THE TABLES AFTER DELETION
                if mod_name == "Department" or mod_name == "Subject/Course":
                    self.load_fac_courses_tree()
                else:
                    self.load_nonacad_courses_list()

                # Set the dept model radiobutton to None
                self.dept_none_radbtn.setChecked(True)

        else:
            UITimetable.messagebox(title="No selections",icon="critical",text=f"No {mod_name.lower()} items selected.")

                
# -------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
    def register_class_group(self):
        """This function handles the registration of a school_class_group i.e. aSchool class category"""

        update = False if "Creation" in self.class_createedit_label.text().strip().split() else True

        class_group_name = self.findChild(QtWidgets.QLineEdit, "class_cat_lineedit")
        class_group_abbrev = self.findChild(QtWidgets.QLineEdit, "class_cat_abbrev_lineedit")
           # Description of the school class category
        class_group_desc = self.findChild(QtWidgets.QTextEdit, "class_cat_desc_textedit")

        # retrieve all the texts
        name,abbrev,desc = class_group_name.text(),class_group_abbrev.text(),class_group_desc.toPlainText()

        if UITimetable.check_fields_or_error(fields_values_list=[name, desc]):
            # Create the class group
            self.Timetable.create_school_class_group(name,description=desc, abbrev=abbrev, update=update)

            # Clear the fields
            class_group_name.clear()
            class_group_abbrev.clear()
            class_group_desc.clear()

            # Uncheck te edit radiobuttons
            self.day_radbtn.setChecked(False)
            self.class_radbtn.setChecked(False)
            self.class_cat_radbtn.setChecked(False)
            self.class_none_radbtn.setChecked(True)

            self.class_createedit_label.setText("Creation of class and day models")
        else:
            # spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="Required field(s) have not been filled!")

        # load the treewidget function to display newly registered class group, class and arm
        self.load_group_class_arm_tree()
        # Generate tree of arms for chunk and freq
        self.gen_arms_freq_chunk_tree()
        # set the None radiobutton to True
        self.class_none_radbtn.setChecked(True)


    def register_school_class(self):
        """ Handles the registration of a school class under a school class category. Whether it is an update or fresh """

        update = False if "Creation" in self.class_createedit_label.text().strip().split() else True
                
        sch_class_name_lineedit = self.findChild(QtWidgets.QLineEdit, "class_name_lineedit")
        class_group,class_name = self.combo_with_classgroup.currentText().strip(), sch_class_name_lineedit.text().strip()

        # Verify fields and create class
        if UITimetable.check_fields_or_error(fields_values_list=[class_group, class_name]):
            # Enable the school class cat combobox if we disabled it b4 for updating
            self.combo_with_classgroup.setEnabled(True)

            # Create school class
            self.Timetable.create_school_class(class_name, class_group, update=update)
            # clear the fields
            sch_class_name_lineedit.clear()

        else:
            # Ring out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="No class category specified under which to make class.")

        self.load_group_class_arm_tree()
        # Generate tree of arms for chunk and freq
        self.gen_arms_freq_chunk_tree()

        self.class_createedit_label.setText("Creation of class and day models")

        # set the None radiobutton to True
        self.class_none_radbtn.setChecked(True)


    def generate_arms(self):
        """Generates class arms for a chosen out of the classes in a school class group"""

        # the input from the spin_box as to the number of arms to generate
        spin_id = self.findChild(QtWidgets.QSpinBox, "arm_num_spinbox")
        alphabetized = self.findChild(QtWidgets.QComboBox, "alphabetized_combo")

        override_gbox = self.findChild(QtWidgets.QGroupBox, "arms_append_override_gbox")

        append_var = None
        for child in override_gbox.children():
            if isinstance(child, QtWidgets.QRadioButton):
                if child.isChecked():
                    append_var = child.text()


        override = False if append_var.strip() == "Append" else True
        alpha_or_not = alphabetized.currentText()
        school_class_text = self.combo_class.currentText()     #The full name of the school class

        if UITimetable.check_fields_or_error(fields_values_list=[school_class_text]):
        # Whether alphabetically or with numbers
            is_alpha = True if alpha_or_not == "Alphabetized" else False
            
            self.Timetable.generate_school_class_arms(school_class_text, frequency=spin_id.value(), as_alpha=is_alpha, override=override)
        else:
            # Spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="No school class to generate arms for.")


        # Clear the fields, the spinbox in this case
        spin_id.setValue(1)
        # Load the classgroup-class-arm tree widget
        self.load_group_class_arm_tree()
        # Generate tree of arms for chunk and freq
        self.gen_arms_freq_chunk_tree()

        # Enable bulk marking of arms when a class is clicked
        root = self.arms_for_chunk_tree.invisibleRootItem()
        child_count = root.childCount()

        
        # -------------------------------------
        self.gen_arms_freq_chunk_tree()

        # If it has no parents, that is it is the class clicked and not the class arm
        # for index in range(child_count):
        #     class_item = root.child(index)
        #     class_widget = self.arms_for_chunk_tree.itemWidget(class_item, 0)
        #     # The above returns the widgetTree class I defined myself
        #     class_checkbox = class_widget.get_checkbox()

        #     # Add a signal to the class_checkBox
        #     class_checkbox.stateChanged.connect(lambda checked, tree_item=class_item: self.bulk_mark_class_arms(checked=checked, tree_item=tree_item))


    # ------------------- CLASS AND DAY MODEL METHODS ---------------------------
    # -----------------------------------------------------------------------------------------------------------

    def class_expand_contract(self):
        """Method to expand or contract the class-classarm tree widget upon click"""

        if "expand" in self.class_expand_btn.text().lower():
            # Expand the tree
            self.load_group_class_arm_tree(expanded=True)
            self.class_expand_btn.setText("Contract")
        else:
            self.load_group_class_arm_tree()
            self.class_expand_btn.setText("Expand")


    def pull_model(self,source, param):
        """ This method pulls out the list of the requested models and displays it in a combobox for editing """
        
        self.classday_models_combobox.clear()
        if param == "day":
            models = self.Timetable.Timetable_obj.list_of_days
        elif param == "class":
            models = self.Timetable.Timetable_obj.list_of_school_classes
        elif param == "classcat":
            models = self.Timetable.Timetable_obj.list_of_school_class_groups

        model_list = [model.full_name for model in models]
        # Populate the combobox with models
        self.classday_models_combobox.addItems(model_list)


    # Pulls class models details up on GUI screen for edit
    def pull_render(self):
        """ This method pulls out the model to be edited and places its attributes in its fields on the GUI screen """

        self.class_createedit_label.setText("Update of class and day models")
        # See which radiobtn has been checked from the groupbox holding them
        mod_name = None
        for child in self.classmodel_gbox.children():
            if isinstance(child, QtWidgets.QRadioButton) and child.isChecked():
                mod = child.text()

            # -----------------------------------------------------------------
                if mod != "None":
                    if mod == "Class Category":
                        root = self.classgroup_class_arm_tree.invisibleRootItem()
                        child_count = root.childCount()

                        for i in range(child_count):
                            cat_item = root.child(i)
                            # The below returns the WidgetTree class i defined myself
                            cat_widget = self.classgroup_class_arm_tree.itemWidget(cat_item, 0)
                            curr_model = cat_widget.full_name_label.text()


                    elif mod == "Class":
                        root = self.classgroup_class_arm_tree.invisibleRootItem()
                        child_count = root.childCount()

                        for i in range(child_count):
                            item = root.child(i)
                            # The below returns the WidgetTree I defined

                            for j in range(item.childCount()):
                                class_item = item.child(j)
                                class_widget = self.classgroup_class_arm_tree.itemWidget(class_item, 0)
                                curr_model = class_widget.full_name_label.text()


                    elif mod == "Day":
                        for index in range(self.gen_teachers_days_listwidget.count()):
                            # child = self.gen_teachers_days_listwidget.item(index)
                            item = self.gen_teachers_days_listwidget.item(index)
                            day_widget = self.gen_teachers_days_listwidget.itemWidget(item)
                            curr_model = day_widget.full_name_label.text()


                    # Get the current model that has been pulled up
                    curr_model_item = self.classday_models_combobox.currentText()
                    # Does the real work of looking for the model object and handing it to the manager

                    # -------------------------------------------------------------
                    # check if curr_model is not empty, raise an error message if
                    if UITimetable.check_fields_or_error(fields_values_list=[curr_model_item]):
                        renderable = self.Timetable.pull_classmodel(mod, curr_model_item)
                    else:
                        UITimetable.messagebox(icon="warning", title="Model item empty",text=f"No {mod} items to pull. You can only pull {mod} items that exist.")
                        return

                    # if Pull from the manager is successful,
                    if mod == "Day":
                        day_name = self.findChild(QtWidgets.QLineEdit, "day_name")
                        day_name.setText(renderable["name"])

                    elif mod == "Class":
                        class_name = self.findChild(QtWidgets.QLineEdit, "class_name_lineedit")
                        # Disable the combobox for classgroup (Not needed)
                        self.combo_with_classgroup.setCurrentText(renderable["classcat"])
                        self.combo_with_classgroup.setEnabled(False)
                        class_name.setText(renderable["name"])

                    elif mod == "Class Category":
                        cat_name = self.findChild(QtWidgets.QLineEdit, "class_cat_lineedit")
                        cat_abbrev = self.findChild(QtWidgets.QLineEdit, "class_cat_abbrev_lineedit")
                        cat_description = self.findChild(QtWidgets.QTextEdit, "class_cat_desc_textedit")

                        # Insert values into fields
                        cat_name.setText(renderable["name"])
                        cat_abbrev.setText(renderable["abbrev"])
                        cat_description.setText(renderable["description"])

                else:
                    # If mod is none, that is the None radiobutton is clicked
                    # Pull the error messagebox
                    UITimetable.messagebox(icon="critical", title="Selection Error", text="No models selected to pull")
                break


    def mark_day(self):
        """ Enables marking of all the day items in the list widget containing the registered days """

        mark = True if "Mark" in self.mark_day_btn.text().strip().split() else False
        # load the tree widget with the class group (category), class and class arm
        self.load_days_list(with_checkbox=mark)
        mark_btn_text = "Unmark" if mark else "Mark to delete"
        self.mark_day_btn.setText(mark_btn_text)

        # If the mark button (i.e. if mark is false) has been clicked enable the mark all button, else disable it
        self.day_markall_btn.setEnabled(mark)


    def day_mark_all(self):
        """ Fires when the markall button is clicked. It marks all the items of the model clicked """

        for k in range(self.day_list.count()):
            item = self.day_list.item(k)
            #The WidgetTree object I defined
            item = self.day_list.itemWidget(item)
            item.get_checkbox().setCheckState(QtCore.Qt.Checked)


    def class_mark_all(self):
        """ Enable mark all items of either a class group(category) or school class """

        # check to see which of the classmodel_groupbox in the GUI's radiobuttons have been clicked
        for child in self.classmodel_gbox.children():
            # Get the radiobutton that has been clicked if it is not None or Day
            if isinstance(child, QtWidgets.QRadioButton) and child.isChecked() and child.text() != "None" and child.text() != "Day":
                mod_id = child.text()

                # ------------------------------------------------------------------------------------
                # ---------------- Uncheck all the boxes in the tree widget first --------------------

                # Check all the class cat and class models' boxes in the treewidget
                root = self.classgroup_class_arm_tree.invisibleRootItem()
                child_count = root.childCount()

                for k in range(child_count):
                    classgroup_item = root.child(k)
                    classgroup_widget = self.classgroup_class_arm_tree.itemWidget(classgroup_item, 0)
                    classgroup_widget.get_checkbox().setCheckState(False)

                    for n in range(classgroup_item.childCount()):
                        class_item = classgroup_item.child(n)
                        class_widg = self.classgroup_class_arm_tree.itemWidget(class_item, 0)
                        class_widg.get_checkbox().setCheckState(False)

                # ----------------------------------------------------------------------------
                # ----------------------------------------------------------------------------

                if mod_id == "Class Category":                    
                    # Sniff through the tree to mark all class groups!
                    for x in range(child_count):
                        classgroup_item = root.child(x)
                        # my custom widgetTree object
                        classgroup_widg = self.classgroup_class_arm_tree.itemWidget(classgroup_item, 0)

                        # Check this widget
                        classgroup_widg.get_checkbox().setCheckState(QtCore.Qt.Checked)

                else:
                    # Sniff through the tree and check school class models
                    for x in range(child_count):
                        classgroup_item = root.child(x)

                        for y in range(classgroup_item.childCount()):
                            class_item = classgroup_item.child(y)
                            class_widg = self.classgroup_class_arm_tree.itemWidget(class_item, 0)
                            # check all of these class_items'check boxes
                            class_widg.get_checkbox().setCheckState(QtCore.Qt.Checked)
                break

        # load the self.classgroup_class_arm_tree expanded and checked!
        # self.load_group_class_arm_tree(with_checkbox=True, expanded=True)


    def mark_class(self):
        """ Enables marking of all the class model items in the list widget containing the registered days and also changes
        the mark button's contents """

        mark = True if "Mark" in self.mark_class_btn.text().strip() else False
        # load the tree widget with the class group (category), class and class arm
        self.load_group_class_arm_tree(with_checkbox=mark, expanded=mark)
        mark_btn_text = "Unmark" if mark else "Mark to delete"
        self.mark_class_btn.setText(mark_btn_text)

        # If the mark button (i.e. if mark is false) has been clicked enable the mark all button, else disable it
        self.class_markall_btn.setEnabled(mark)


    def del_classday_model(self):
        """ Deletes either class models (class group, class) or day items """
        for child in self.classmodel_gbox.children():
            # check the radiobutton which has been clicked (except the one with caption None)
            if isinstance(child, QtWidgets.QRadioButton) and child.isChecked() and child.text():
                model_name = child.text()
                break

        # As long as the caption on the radiobutton does not read "None"...
        if model_name != "None":

            # select items to delete either from marking or from the combobox
            selected_items = []

            if model_name == "Day":
                # Check if mark has been enabled
                if self.mark_day_btn.text() == "Unmark":
                    # Scour through the days list widget and pick the selected items

                    for k in range(self.day_list.count()):
                        day_item = self.day_list.item(k)
                        day_widg = self.day_list.itemWidget(day_item)

                        # Check if it is checked
                        if day_widg.get_checkbox().isChecked():
                            selected_items.append(day_widg.full_name_label.text())

                else:
                    # If model item is to be chosen from the combobox
                    selected_items.append(self.classday_models_combobox.currentText())


            elif model_name == "Class":

                #  if the mark button has been clicked
                if self.mark_class_btn.text() == "Unmark":
                    # Scour through the tree and pick out the class items selected
                    root = self.classgroup_class_arm_tree.invisibleRootItem()
                    child_count = root.childCount()

                    for k in range(child_count):
                        classcat = root.child(k)

                        for n in range(classcat.childCount()):
                            classitem = classcat.child(n)
                            classitem_widg = self.classgroup_class_arm_tree.itemWidget(classitem, 0)

                            # Ckeck if the classitem_widg has been checked
                            if classitem_widg.get_checkbox().isChecked():
                                selected_items.append(classitem_widg.full_name_label.text())

                else:
                    # If model item is to be chosen from the combobox
                    selected_items.append(self.classday_models_combobox.currentText())
                

            elif model_name == "Class Category":
                # If the mark buttin has been clicked
                if self.mark_class_btn.text() == "Unmark":
                    root = self.classgroup_class_arm_tree.invisibleRootItem()
                    child_count = root.childCount()

                    for k in range(child_count):
                        classcat = root.child(k)
                        classcat_widg = self.classgroup_class_arm_tree.itemWidget(classcat, 0)

                        # check if the widget has been checked
                        if classcat_widg.get_checkbox().isChecked():
                            selected_items.append(classcat_widg.full_name_label.text())

                else:
                    # If model item is to be chosen from the combobox
                    selected_items.append(self.classday_models_combobox.currentText())


        # ------------------------------------------------------------------------------
            # ----------- AFTER THE ABOVE IF-STATEMENTS HAVE RUN

            # check if selected items is empty, raise an error messagebox if
            if UITimetable.check_fields_or_error(fields_values_list=selected_items):
            # Carry out the delete from the GUI manager. The model_name is also passed in with the selected items in a dictionary
            # --------------------------------------------------------------
            #-------- REAL DELETION OPERATION TAKES PLACE HERE! ------------
                # But just before, display messagebox warning of the consequences

                def go_or_no(btn_clicked):
                    """defining the callback function whether or not user clicks okay to delete"""
                    self.go_ahead = True if btn_clicked.text() == "OK" else False
                # ----------------------------------------------------------

                self.go_ahead = False


                UITimetable.messagebox(title="FYI", icon="warning", text=f"When a {model_name} is deleted, all its child items get deleted.",
                    extratext="Would you proceed notwithstanding?", callback=go_or_no)

                if self.go_ahead:
                    self.Timetable.delete_models({model_name:selected_items})

                    # ------------------------------------------------------------
                    # LOAD UP THE TABLES AFTER DELETION
                    if "Class" in model_name:
                        self.load_group_class_arm_tree()
                    else:
                        self.load_days_list()

            else:
                UITimetable.messagebox(title="No selections",icon="critical",text=f"No {model_name.lower()} items selected.")


        # If radiobutton has caption "None"
        else:
            # Raise Error Messagebox. RadioButton reads "None"
            UITimetable.messagebox(title="No Models",icon="critical",text="No class or day models pulled up for modification.")
            pass


    def load_group_class_arm_tree(self, with_checkbox=False, expanded=False):
        """This function loads the classgroup-class arm-arm tree"""

        self.classgroup_class_arm_tree.clear()
        self.combo_with_classgroup.clear()
        self.combo_class.clear()
        # the class reg combox will also be cleared too below!

        for class_group in self.Timetable.Timetable_obj.list_of_school_class_groups:
            # Load the  class group(category) name into the tree widget
            item = QtWidgets.QTreeWidgetItem()
            class_group_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/classgroup.png", icon_width=20, icon_height=15, label_text=class_group.full_name, with_checkbox=with_checkbox)

            # Add the class group to the combobox for school class registration
            self.combo_with_classgroup.addItem(class_group.full_name)
            self.classgroup_class_arm_tree.addTopLevelItem(item)
            self.classgroup_class_arm_tree.setItemWidget(item, 0, class_group_widg)
            item.setExpanded(expanded)

            for clss in class_group.school_class_list:
                # add this sch_class into the combo_class combobox (The combobox to aid thegeneration of class arms)
                self.combo_class.addItem(clss.full_name)
                # Create a nested node in each faculty for the department
                class_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/class.png",icon_width=18, icon_height=10, label_text=clss.full_name, with_checkbox=with_checkbox)
                class_tree_item = QtWidgets.QTreeWidgetItem()
                item.addChild(class_tree_item)
                self.classgroup_class_arm_tree.setItemWidget(class_tree_item, 0, class_widg)
                class_tree_item.setExpanded(expanded)

                for arm in clss.school_class_arm_list:
                    # Create a nested node in each faculty for the department
                    arm_tree_item = QtWidgets.QTreeWidgetItem()
                    arm_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/arm.png",label_text=arm.full_name)
                    class_tree_item.addChild(arm_tree_item)

                    self.classgroup_class_arm_tree.setItemWidget(arm_tree_item, 0, arm_widg)


    # ----------------------------- REGISTER/MODIFY DAY MODELS -------------------------------------------------
    def day_check_spin_box(self):
        # If button has been checked,
        if self.day_checkbox.isChecked():
            self.day_position_spinbox.setEnabled(True)
            rating = self.day_position_spinbox.value()
            return rating

        self.day_position_spinbox.setEnabled(False)
        return None
        

    def register_day(self):
        """handles the registration of days"""

        update = False if "Creation" in self.class_createedit_label.text().strip().split() else True
        day_name = self.findChild(QtWidgets.QLineEdit, "day_name")
        rating = self.day_check_spin_box()

        # Check if day_name_field is valid
        day_name_text = day_name.text()
        if UITimetable.check_fields_or_error(fields_values_list=[day_name_text]):
            # Create day_object
            self.Timetable.create_day(day_name_text, rating=rating, update=update)
            self.class_createedit_label.setText("Creation of class and day models")

        else:
            # Spit out error message
            UITimetable.messagebox(title="Empty field error",icon="critical",text="Fill in the name of the day.")

        # Clear fields
        day_name.clear()
        self.day_position_spinbox.setValue(1)
        self.day_position_spinbox.setEnabled(False)
        self.day_checkbox.setCheckState(False)
        
        self.load_days_list()
        self.load_days_for_arms_listwidget()
        # Load days combobox in periods generation page
        self.load_day_combobox_for_periods()

        # Load teachers days with checkboxes
        self.load_gen_teachers_day_chboxes()

        # set the None radiobutton to True
        self.class_none_radbtn.setChecked(True)


    def load_days_list(self, with_checkbox=False):
        """Loads the trww widget with created days on"""

        # treewidget.setColumnCount(1)
        self.day_list.clear()
        
        for day_obj in self.Timetable.Timetable_obj.list_of_days:
            day_listwidget_item = QtWidgets.QListWidgetItem()
            day_widg = WidgetTree(label_text=day_obj.full_name, icon_path='TIMETABLE/Icons-mine/Day_icon.png', with_checkbox=with_checkbox)
            self.day_list.addItem(day_listwidget_item)
            self.day_list.setItemWidget(day_listwidget_item,day_widg)


# ------------------------------------------------------------------------------------------
    # ----------------- GENERATE TEACHERS FOR ONE OR MULTIPLE DEPARTMENTS ---------------------
    def _load_specialty_combobox(self):
        """ This private function loads the class_cat span (specialty) of the teacher """
        checked_courses = self.checked_widgtree_in_listwidget(self.gen_teachers_courselist)

        # Get the live course objects.
        dept_objs = [self.Timetable.object_getter(self.Timetable.get_model_items("courses")[1], "full_name", course_name) 
        for course_name in checked_courses]

        specialty = ["All"]
        for dept_obj in dept_objs:
            for class_cat in dept_obj.class_group_span:
                if class_cat.full_name not in specialty:
                    specialty.append(class_cat.full_name)

        # Now add these class_group full_names to the specialty combobox
        self.specialty_combobox.clear()
        self.specialty_combobox.addItems(specialty)



    def load_gen_teachers_courselist(self):
        """ Loads the listwidget bearing all the courses registered so Teacher can be generated.
        Also calls a method that loads up the class_group_span of the courses clicked """

        # -----------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------
        self.gen_teachers_courselist.clear()
        for course in self.Timetable.Timetable_obj.list_of_departments:
            # The course widgettree
            course_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/subject.png",icon_width=16, label_text=course.full_name, with_checkbox=True)
            course_item = QtWidgets.QListWidgetItem()

            self.gen_teachers_courselist.addItem(course_item)
            self.gen_teachers_courselist.setItemWidget(course_item, course_widg)

            # Set signal to the checkbox of the widget to help load the combobox for
            # teacher's specialty
            course_widg.get_checkbox().stateChanged.connect(self._load_specialty_combobox)


    def load_gen_teachers_day_chboxes(self):
        """This loads the days Listwidget with checkboxes, in the big box where teachers are to be registered. Teachers can select
        which days of the week they work from here."""

        self.gen_teachers_days_listwidget.clear()

        for day_obj in self.Timetable.Timetable_obj.list_of_days:
            # Create a checkbox
            checkbox = WidgetTree(icon_path="TIMETABLE/Icons-mine/Day.png", label_text=day_obj.full_name, with_checkbox=True, icon_width=16)
            
            day_item = QtWidgets.QListWidgetItem()
            self.gen_teachers_days_listwidget.addItem(day_item)
            self.gen_teachers_days_listwidget.setItemWidget(day_item, checkbox)


    def load_faculty_courses_teachers_tree(self, markable=False, expanded=False):
        """ This function loads the tree showing each faculty, the depts
        under it, and the generated teachers under each dept"""

        self.dept_and_teachers_tree.clear()

        # the class reg combox will also be cleared too below!
        for faculty in self.Timetable.Timetable_obj.list_of_faculties:
            # Load the  class group(category) name into the tree widget
            item = QtWidgets.QTreeWidgetItem()
            fac_widg = WidgetTree(label_text=faculty.full_name, icon_path='TIMETABLE/Icons-mine/classgroup.png')  
            self.dept_and_teachers_tree.addTopLevelItem(item)
            item.setExpanded(expanded)
            self.dept_and_teachers_tree.setItemWidget(item, 0, fac_widg)

            # Go for each of the courses in the faculty's course list
            for dept_obj in faculty.depts_list:

                # Create a nested node in each faculty for the department (subject)
                dept_tree_item = QtWidgets.QTreeWidgetItem()
                
                dept_widg = WidgetTree(label_text=dept_obj.full_name, icon_path="TIMETABLE/Icons-mine/subject.png",with_checkbox=markable)
                item.addChild(dept_tree_item)
                self.dept_and_teachers_tree.setItemWidget(dept_tree_item, 0, dept_widg)
                dept_tree_item.setExpanded(expanded)

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


    def expand_fac_courses_teachers_tree(self):
        """ Reloads the faculty-course-teachers tree in expand or contract mode """
        expand = True if "expand" in self.expand_fac_course_teachers_tree_btn.text().lower() else False
        updated_btntext = "Reload-contract" if expand else "Reload-expand"

        # Load the tree with the above boolean parameters
        self.load_faculty_courses_teachers_tree(expanded=expand)
        # change the text on the button appropriately
        self.expand_fac_course_teachers_tree_btn.setText(updated_btntext)


    def pull_teacher(self):
        """ This method pulls out teachers details, the courses he offers and his teaching days and puts it on the screen
        with his courses and teaching days checked already """

        # No teacher displayed, raise error messagebox
        if "found" in self.teacher_found_label.text() or "none" in self.teacher_found_label.text().lower():
            UITimetable.messagebox(icon="critical", title="Empty field", text=" Cannot pull. No teacher selected.")
            return

        
        # Change label caption to editing teacher so so
        self.gen_edit_teacher_label.setText(f"Editing teacher: {self.teacher_found_label.text()}")
        self.gen_edit_teacher_label.setStyleSheet(f"""color:#0000ca""")

        # else pull the teacher's details from the timetable manager i.e. his courses and his teaching days
        teachers_courses, teaching_days, designation = self.Timetable.pull_teacher(self.teacher_found_label.text())
        # ----------------------------------
        # Load them up on the screen, the courselist first
        self.gen_teachers_courselist.clear()
        self.gen_teachers_days_listwidget.clear()

        # the course_fullname and whether or not it is checked
        for dept_fullname, yea in teachers_courses.items():
            checked = QtCore.Qt.Checked if yea else False     #Checked if it is True else false

            dept_item = QtWidgets.QListWidgetItem()
            dept_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/subject.png", icon_width=18,label_text=dept_fullname,with_checkbox=True)
            dept_widg.get_checkbox().stateChanged.connect(self._load_specialty_combobox)
            dept_widg.get_checkbox().setCheckState(checked)
            self.gen_teachers_courselist.addItem(dept_item)
            self.gen_teachers_courselist.setItemWidget(dept_item, dept_widg)


        for day_fullname, yea in teaching_days.items():
            checked = QtCore.Qt.Checked if yea else False     #Checked if it is True else false

            day_item = QtWidgets.QListWidgetItem()
            day_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/Day.png", icon_width=18,label_text=day_fullname,with_checkbox=True)
            day_widg.get_checkbox().setCheckState(checked)
            self.gen_teachers_days_listwidget.addItem(day_item)
            self.gen_teachers_days_listwidget.setItemWidget(day_item, day_widg)

        # ALso pull up teacher's designation
        self.designation_lineedit.setText(designation)

        # Change caption on the generate teacher button
        self.teacher_freq_gbox.setEnabled(False)
        self.gen_teachers_btn.setText("Commit")


    def generate_teachers(self):
        """Generates teachers for a chosen course or selected courses. Teachers are chosen for a course not a faculty."""
        
        # If we are generating teachers afresh
        selected_subjects = self.checked_widgtree_in_listwidget(self.gen_teachers_courselist)
        selected_days = self.checked_widgtree_in_listwidget(self.gen_teachers_days_listwidget)
        specialty = self.specialty_combobox.currentText()
        designation = self.designation_lineedit.text().strip().capitalize()

        if "generate" in self.gen_edit_teacher_label.text().lower():

            # Change caption of the label above ---------------
            # self.gen_edit_teacher_label.setText(f"Editing teacher: {self.teacher_found_label.text()}")
            self.gen_edit_teacher_label.setStyleSheet("color:#1c1cff")
            # ------------------------------------

            teachers_freq = self.findChild(QtWidgets.QSpinBox, "gen_teachers_spinbox")
            freq_val = teachers_freq.value()

            # Generate the teachers if the selected days and subjects are not empty
            if UITimetable.check_fields_or_error(fields_values_list=[selected_subjects, selected_days]):
                self.Timetable.generate_teachers(frequency=freq_val, teaching_days=selected_days, course_list=selected_subjects, 
                    designation=designation, specialty=specialty)


            else:
                UITimetable.messagebox(icon="critical", title="Empty fields", text="Either subjects/courses or teaching days have not been chosen.")

            teachers_freq.setValue(0)

        # ---------------------------------
        # If we are updating teacher
        else:
            # We update the teacher selected
            self.Timetable.generate_teachers(teaching_days=selected_days, course_list=selected_subjects, designation=designation,
                specialty=specialty, update=True)
            # Change the caption on the label
            self.gen_edit_teacher_label.setText("Generate Teachers")
            self.gen_edit_teacher_label.setStyleSheet("color:#000051")
            # Change caption on button
            self.gen_teachers_btn.setText("Generate")

        # Clear all the checkmarks from the listwidgets (courses and days)
        self.checkall_widgtree_in_listwidget(self.gen_teachers_courselist, checkall=False)
        self.checkall_widgtree_in_listwidget(self.gen_teachers_days_listwidget, checkall=False)
        # c;ear the designation lineedit
        self.designation_lineedit.clear()


        # Load the all_staff_table
        self.load_fac_courses_tree(with_checkbox=False, expanded=False)
        self.load_all_staff_table()
        self.enable_all_in_widget(self.findChild(QtWidgets.QFrame, "gen_teacher_frame"))
        self.teacher_found_label.setText("None")
        self.teacher_found_label.setStyleSheet("color:#000;")
        

    def load_all_staff_table(self, with_checkbox=False, check_all=False):
        """This method generates the table for all the members of staff and their details"""

        # Clear the contents of the table first
        self.all_staff_table.clearContents()

        # Reload the contents of table from scratch
        teacher_objs = self.Timetable.get_model_items("teachers")[1]
        self.all_staff_table.setRowCount(len(teacher_objs))

        for index,teacher in enumerate(teacher_objs):
            row = index
            # Sets the checked variable for the checkbox in the teacher widget
            checked = QtCore.Qt.Checked if check_all else check_all

            teacher_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/teacher.png", label_text=teacher.full_name, icon_width=17, with_checkbox=with_checkbox)
            teacher_widg.get_checkbox().setCheckState(checked)
            self.all_staff_table.setCellWidget(row, 0, teacher_widg)
            self.all_staff_table.setItem(row, 1, QtWidgets.QTableWidgetItem(teacher.str_teacher_depts))
            self.all_staff_table.setItem(row, 2, QtWidgets.QTableWidgetItem(teacher.specialization))
            self.all_staff_table.setItem(row, 3, QtWidgets.QTableWidgetItem(teacher.str_teaching_days(self.Timetable.Timetable_obj)))
            self.all_staff_table.setItem(row, 4, QtWidgets.QTableWidgetItem(teacher.regular_or_no(self.Timetable.Timetable_obj)))


    # ------------------------------------ MODIFY TEACHER OBJECT -------------------------------------------
    def load_teachers_into_combobox(self):
        """ If teacher to be modified is selected froma combobx (i.e.) the checkbox is clicked, add all the teacher objects available
        into the combobox """
        self.combo_with_teacher.clear()

        if self.teacher_from_combo_checkbox.isChecked():
            # Disable the search teacher box underneath. It is either this one or that.
            self.search_teacher_gbox.setEnabled(False)
            # load the combobox
            self.combo_with_teacher.addItems([teacher.full_name for teacher in self.Timetable.Timetable_obj.list_of_all_teachers])

        else:
            self.search_teacher_gbox.setEnabled(True)


    def render_teacher_from_combobox(self):
        """ .THIS IS NOT THE PULL OPERATION!!.This method fires when the state of the teachers combobox is changed. It puts the teachers full_name in the label on the screen
        (Not with his full details i.e. course taught or teaching days yet) """

        teacher_text = self.combo_with_teachers.currentText()

        self.teacher_found_label.setText(teacher_text)
        self.teacher_found_label.setStyleSheet("""color: #00008c""")


    def search_teacher_by_ID(self):
        """ When the search teacher button is clicked. it sniffs out the teacher object """

        teacher_id = self.teacher_from_spinbox.value()
        # pulls up the teacher with said ID
        teacher_obj = self.Timetable.search_out_teacher(teacher_id)
        teacher_text = teacher_obj.full_name if teacher_obj else "Not found. Doesn't exist."
        # Turn text color red if no teacher is found else dark blue. "found" in teacher text means the teacher's details were not displayed.
        teacher_text_colour = "red" if "found" in teacher_text else "#00008c"

        self.teacher_found_label.setText(teacher_text)
        self.teacher_found_label.setStyleSheet(f"""color:{teacher_text_colour};""")


    def mark_teachers_in_staff_table(self):
        """ Enables mark operation to be performed on all the teacher items in the table """

        self.all_staff_table.clear()
        if "unmark" in self.mark_teachers_btn.text().lower():
            self.load_all_staff_table()
            self.mark_teachers_btn.setText("Mark for delete")
            self.markall_teachers_btn.setEnabled(False)
        else:
            self.load_all_staff_table(with_checkbox=True)
            self.mark_teachers_btn.setText("Unmark")
            self.markall_teachers_btn.setEnabled(True)


    def mark_all_teachers_in_staff_table(self):
        """ checks the checkboxes in the widget tree object of all the teachers in the staff table """
        self.load_all_staff_table(with_checkbox=True, check_all=True)


    def del_teacher(self):
        """ Deletes the teacher object from the timetable. Teacher is either 
        picked as one or marked from the all staff list table """

        # If no teacher has been selected yet.
        if "none" in self.teacher_found_label.text().lower() and "Mark" in self.mark_teachers_btn.text():
            UITimetable.messagebox(icon="critical", title="Empty fields", text="No teacher selected to delete")
            return

        # If the mark button has been clicked
        selected_teachers = []
        if "unmark" in self.mark_teachers_btn.text().lower():
            # Go through and pick all the marked teachers in column 0 of the all staff table
            for k in range(self.all_staff_table.rowCount()):
                # item = self.all_staff_table.item(k, 0)
                # Get the item widget
                item_widg = self.all_staff_table.cellWidget(k,0)

                if item_widg.get_checkbox().isChecked():
                    selected_teachers.append(item_widg.full_name_label.text())

        # If the teacher has been selected from the pull operation, i.e. just one teachers
        else:
            teacher = self.teacher_found_label.text()
            selected_teachers.append(teacher)
            
            # Delete the teacher(s)
        self.Timetable.delete_teacher(selected_teachers)
        self.load_all_staff_table()
        self.mark_teachers_btn.setText("Mark for delete")


# --------------------------------------------------------------------------------------------------------------
# ---------------- PERIOD GENERATION AND MAPPING SUBJ, FREQ AND CHUNK TO ARM------------------------------------
    def _marked_classarms_from_tree(self, class_arm_tree):
        """ Method to return all the class arms whose checkboxes have been ticked from the class arms tree.
        class and arm is used here as dummy variables, though. """

        selected_arms = []

        root = class_arm_tree.invisibleRootItem()
        child_count = root.childCount()

        # Sniff through the tree for arms that have been clicked!
        for x in range(child_count):
            class_item = root.child(x)

            for y in range(class_item.childCount()):
                arm_item = class_item.child(y)
                arm_widget = class_arm_tree.itemWidget(arm_item, 0)
                # if the checkbox in the custom widget of the arm is checked,
                if arm_widget.get_checkbox().isChecked():
                    selected_arms.append(arm_widget.full_name_label.text())

        return selected_arms


    def _load_nonacad_tables(self, nonacad_table):
        """ populates one of th three nonacad tables in the period generation page """
        def disabled_tablewidgetitem(enable=False, placeholder="hh:mm:ss"):
            item = QtWidgets.QLineEdit()
            item.setPlaceholderText(placeholder)
            item.setStyleSheet("""
                border:none;
                padding:1px;
                """)
            item.setEnabled(enable)
            return item


        # Function to help enable or disable rows of each nonacad table when checked False
        def enable_nonacad_table_row(state, duration, position):
            style = f"""color: {"#1e1e1e" if state else "#858585"}; border:none;"""
            duration.setEnabled(state)
            duration.setStyleSheet(style)
            position.setEnabled(state)
            position.setStyleSheet(style)
        # ---------------------------------------------------
        
        nonacad_table.clearContents()
        # Get all the non-academic subjects
        nonacad_subjs = self.Timetable.get_model_items("nonacads")[0]
        # Reload the contents of table from scratch
        nonacad_table.setRowCount(len(nonacad_subjs))

        for index,nonacad in enumerate(nonacad_subjs):
            row = index
            # Sets the checked variable fir the checkbox in the teacher widget
            nonacad_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/nonacad.png", label_text=nonacad, icon_width=17, with_checkbox=True)
            duration = disabled_tablewidgetitem()
            position = disabled_tablewidgetitem(placeholder="e.g. 1,2,...")

            nonacad_table.setCellWidget(row, 0, nonacad_widg)
            nonacad_table.setCellWidget(row, 1, duration)
            nonacad_table.setCellWidget(row, 2, position)

            # set a signal for when the checkbox of the nonacad_widg checkbox is checked
            nonacad_widg.get_checkbox().stateChanged.connect(lambda state, duration=duration, position=position: enable_nonacad_table_row(state, duration, position))


    def _extract_nonacad_info(self, nonacad_table):
        """ Extracts the duration and position of nonacad periods from any one of the three tables in the GUI. """

        select = []
        # Extract non_acad periods columns if nonacad is checked True
        for k in range(nonacad_table.rowCount()):
            # The first column, and every row underneath to get the nonacad WidgetTree object and see if it has been checked.
            
            # t_item = nonacad_table.item(k, 0)
            widg = nonacad_table.cellWidget(k,0)
            # check if widg is checked
            if widg.get_checkbox().isChecked():
                # get the name, duration and position at this point
                nonacad_name = widg.full_name_label.text()
                duration = nonacad_table.cellWidget(k,1).text()
                positions = nonacad_table.cellWidget(k,2).text()
                # Append the corresponding duration(str) and positions(str) to the list as a tuple 
                select.append((nonacad_name, duration, positions))
        return select


    def load_days_for_arms_listwidget(self):
        """ Loads the day objects into the days_for_arms_listwidget in the page for period generation """
        self.days_for_arms_listwidget.clear()

        all_days = self.Timetable.get_model_items("days")[0]
        for day in all_days:
            item = QtWidgets.QListWidgetItem()
            widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/day.png",icon_width=16, icon_height=14, label_text=day, with_checkbox=True)
            self.days_for_arms_listwidget.addItem(item)
            self.days_for_arms_listwidget.setItemWidget(item, widg)


    def disable_period_boxes(self, gbox):
        """ For period generation, disables groupboxes based on what radio button is clicked """

        self.period_gbox = gbox

        # List of all the groupboxes
        all_list = {(1,self.duration_gbox), (3,self.abs_startend_gbox), (2,self.day_startend_gbox)}

        for num, g_box in all_list:
            # Now to populate the tables containing details of the non-academic subjects
            nonacad_table = self.findChild(QtWidgets.QTableWidget, f"nonacad_table{num}")
            nonacad_table.clearContents()

            if g_box == gbox:
                gbox.setEnabled(True)
                gbox.setStyleSheet("background:none;")

                # ----------------------------------------------------------------------------------------
                # Load the non-acad table
                self._load_nonacad_tables(nonacad_table)

            else:
                g_box.setEnabled(False)
                g_box.setStyleSheet("""QWidget{
                    color:#888888;
                    border-color:#bfbfbf;
                    }""")

        # Also, load the table


    def gen_arms_freq_chunk_tree(self, expand=True):
        """ Generate class arms (and classes) into the tree upon which selection for chunking would be carried out """

        # --------------------------------------------------------------------
        def _bulk_mark_class_arms(self, checked=False, tree_item=None):
            """ Specifically for school classes. It marks (checks) all the arms under it if is checked """

            check = QtCore.Qt.Checked if checked else checked   #QtChecked if checked is true else false
            child_count = tree_item.childCount()

            for i in range(child_count):
                arm_item = tree_item.child(i)
                # Locate the WidgetTree class I defined myself
                arm_widget = self.arms_for_chunk_tree.itemWidget(arm_item, 0)
                arm_widget.get_checkbox().setCheckState(check)
        # --------------------------------------------------------------------
        
        # clear the tree first
        self.arms_for_chunk_tree.clear()

        # Loop through all the school classes and sift out their arms
        for clss in self.Timetable.get_model_items("classes")[1]:

            clss_item = QtWidgets.QTreeWidgetItem()
            clss_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/classgroup.png",label_text=clss.full_name, with_checkbox=True)
            self.arms_for_chunk_tree.addTopLevelItem(clss_item)
            self.arms_for_chunk_tree.setItemWidget(clss_item, 0, clss_widg)

            # Connect the clss_widg checkbox to the bulk_class_arm slot
            clss_widg.get_checkbox().stateChanged.connect(lambda state, clss_item=clss_item: _bulk_mark_class_arms(self, checked=state, tree_item=clss_item))
            clss_item.setExpanded(expand)


            for arm in clss.school_class_arm_list:
                arm_item = QtWidgets.QTreeWidgetItem()
                arm_widg = WidgetTree(icon_path="TIMETABLE/Icons-mine/class.png",label_text=arm.full_name, with_checkbox=True)

                clss_item.addChild(arm_item)
                self.arms_for_chunk_tree.setItemWidget(arm_item, 0, arm_widg)
                # self.arms_for_chunk_tree.setItemWidget(arm_item, 1, QtWidgets.QLabel("Done")



    def load_subjects_freq_chunk_table(self):
        """This method handles the table bearing all the generated subjects and their frequencies and chunk values"""
        
        # Clear contents of the table
        def enable_adjacent_cells(checked, dept_, freq_, chunkval):
            """ The slot (function) for the checkboxes in the self.subj_freq_chunk_table. Renders them enabled only when checkbox is checked """
            freq_.render_enabled(enable=checked)
            chunkval.render_enabled(enable=checked)

        # -----------------------------------------------------------------------
        self.subj_freq_chunk_table.clearContents()
        # Make first column have a width of 140        

        all_depts = self.Timetable.Timetable_obj.list_of_departments
        self.subj_freq_chunk_table.setRowCount(len(all_depts))
        

        for index,dept in enumerate(all_depts):
            dept_widget = WidgetTree(icon_path="TIMETABLE/Icons-mine/subject.png",label_text=dept.full_name, with_checkbox=True)
            freq = MySpinBox(minimum=1,border="0.9px solid #b9b9b9", color="#b9b9b9", background="transparent",padding="0px 0px 0px 5px", enabled=False)
            chunk = MySpinBox(minimum=1,border="0.9px solid #b9b9b9", color="#b9b9b9", background="transparent",padding="0px 0px 0px 5px", enabled=False)

            # SET a widget into the first row of the cells of a table
            self.subj_freq_chunk_table.setCellWidget(index, 0, dept_widget)
            self.subj_freq_chunk_table.setCellWidget(index, 1, freq)
            self.subj_freq_chunk_table.setCellWidget(index, 2, chunk)
            # Add a signal and a slot to the dept widget's checkbox
            dept_widget.get_checkbox().stateChanged.connect(lambda checked, dept_widg=dept_widget, freq_=freq, chunkval=chunk: enable_adjacent_cells(checked, dept_widg, freq_,chunkval))

   
    def load_day_combobox_for_periods(self):
        """ Loads the combobox in the period page to help select periods for a certain day """
        self.days_combobox_for_chunk.clear()

        all_days = self.Timetable.get_model_items("days")[0]
        self.days_combobox_for_chunk.addItems(all_days)


    def generate_periods(self):
        """ Generates periods for the class arm """

        # ---------------------------------------------------------------------------
        # Pick selected class arms and selected days
        selected_arms = self._marked_classarms_from_tree(self.arms_for_chunk_tree)
        selected_days = self.checked_widgtree_in_listwidget(self.days_for_arms_listwidget)

        if not self.check_fields_or_error([selected_arms, selected_days]):
            self.messagebox(title="Empty field input", icon="critical", text="Class arms or days not selected")
            return

        if self.period_gbox == self.duration_gbox: 
            start = self.findChild(QtWidgets.QLineEdit, "start1").text()
            dur= self.findChild(QtWidgets.QLineEdit, "duration1").text()
            freq = self.findChild(QtWidgets.QSpinBox, "freq1").value()
            interval = self.findChild(QtWidgets.QLineEdit, "int1").text()

            periodgen_dict = {"start":start, "duration":dur, "freq":freq, "interval":interval}

            self.findChild(QtWidgets.QLineEdit, "start1").clear()
            self.findChild(QtWidgets.QLineEdit, "duration1").clear()
            self.findChild(QtWidgets.QSpinBox, "freq1").clear()
            self.findChild(QtWidgets.QLineEdit, "int1").clear()

            nonacad_table = self.findChild(QtWidgets.QTableWidget, "nonacad_table1")
            info = self._extract_nonacad_info(nonacad_table)
            g_box_id = "by_duration"


        elif self.period_gbox == self.day_startend_gbox:
            # Given start end, not constrained
            start = self.findChild(QtWidgets.QLineEdit, "start2").text()
            end = self.findChild(QtWidgets.QLineEdit, "end2").text()
            freq = self.findChild(QtWidgets.QSpinBox, "freq2").value()
            interval = self.findChild(QtWidgets.QLineEdit, "int2").text()

            periodgen_dict = {"start":start, "limit":end, "freq":freq, "interval":interval}

            self.findChild(QtWidgets.QLineEdit, "start2").clear()
            self.findChild(QtWidgets.QLineEdit, "end2").clear()
            self.findChild(QtWidgets.QSpinBox, "freq2").clear()
            self.findChild(QtWidgets.QLineEdit, "int2").clear()

            nonacad_table = self.findChild(QtWidgets.QTableWidget, "nonacad_table2")
            info = self._extract_nonacad_info(nonacad_table)
            g_box_id = "by_acadspan"

        else:
            # Given absolute start and end values
            start = self.findChild(QtWidgets.QLineEdit, "start3").text()
            end = self.findChild(QtWidgets.QLineEdit, "end3").text()
            freq = self.findChild(QtWidgets.QSpinBox, "freq3").value()
            interval = self.findChild(QtWidgets.QLineEdit, "int3").text()

            periodgen_dict = {"start":start, "end":end, "freq":freq, "interval":interval}

            self.findChild(QtWidgets.QLineEdit, "start3").clear()
            self.findChild(QtWidgets.QLineEdit, "end3").clear()
            self.findChild(QtWidgets.QSpinBox, "freq3").clear()
            self.findChild(QtWidgets.QLineEdit, "int3").clear()

            nonacad_table = self.findChild(QtWidgets.QTableWidget, "nonacad_table3")
            info = self._extract_nonacad_info(nonacad_table)
            g_box_id = "by_constrained_ends"

        # Insert this data into the manager
        gen_periods = self.Timetable.pin_day_generate_periods(g_box_id, selected_arms_list=selected_arms, selected_days_list=selected_days, normal_periods_dict=periodgen_dict, nonacad_tuple_list=info)

        # If running the above returns an invalid field input error...
        if gen_periods == "Invalid field input":
            # Send out a messagebox
            self.messagebox(title="Invalid field input", icon="critical", text="Incorrect format for one or more of your input values. Check again and make corrections", buttons="ok", callback=None)


    def display_periods_in_table(self):
        """ Displays all the generated periods in the table for each class arm by the day """

        # The button to enable display of the generated periods in the table
        arm_objs = self.Timetable.get_model_items("arms")[1]
        combobox_text = self.days_combobox_for_chunk.currentText()

        day = self.Timetable.get_model_item_object("days", combobox_text)
        # Roll out the custom widget objects to in sert into table
        self.arms_periods_table.setRowCount(len(arm_objs))
        max_width = 0
        for index,arm in enumerate(arm_objs):
            row = index
            # Instantiate the PeriodContainer object
            period_container = PeriodsContainer(arm, day) 
            if period_container.total_width > max_width:
                max_width = period_container.total_width
            # input the number of periods in the first row
            self.arms_periods_table.setRowHeight(row, 44)
            self.arms_periods_table.setItem(row, 0, QtWidgets.QTableWidgetItem(period_container.period_count))
            self.arms_periods_table.setCellWidget(row, 1, period_container)

        # Adjust the period info column to hold the class arms' period values
        self.adjust_table_columns(self.arms_periods_table, column_width_cont=[(1,max_width)])



    def nullify_day_and_periods_from_arms(self):
        """ This function removes the selected days (along with the periods generated) from the selected class arms. This is to edit
        the generate_periods function. """

        selected_arms = self._marked_classarms_from_tree(self.arms_for_chunk_tree)
        selected_days = self.checked_widgtree_in_listwidget(self.days_for_arms_listwidget)

        if not self.check_fields_or_error([selected_arms]):
            self.messagebox(title="Empty field input", icon="critical", text="No class arms selected.")
            return

        self.Timetable.nullify_day_and_periods_from_arms(selected_arms, selected_days)


    def map_deptfreqchunk_to_arms(self):
        """ This function maps the courses, frequencies and chunk that have been selected in the table to the class arms
        that have also been selected. """
        
        # get list of al selected arms from the arms_for_chunk_tree
        selected_arms = self._marked_classarms_from_tree(self.arms_for_chunk_tree)

        # If no arms are selected
        if not self.check_fields_or_error(selected_arms):
            self.messagebox(title="Empty field input", icon="critical", text="Class arms not selected")
            return

        dept_chunk_freq_list = []
        # Extract details from table
        for k in range(self.subj_freq_chunk_table.rowCount()):
            # The first column, and every row underneath to get the nonacad WidgetTree object and see if it has been checked.
            
            widg = self.subj_freq_chunk_table.cellWidget(k,0)
            # check if widg is checked
            if widg.get_checkbox().isChecked():

                # get the fullname, frequency and chunk if the arm is checked
                subj_name = widg.full_name_label.text()
                freq = self.subj_freq_chunk_table.cellWidget(k,1).value()
                chunk = self.subj_freq_chunk_table.cellWidget(k,2).value()
                
                # Append the namedtuple into the list
                dept_chunk_freq_list.append((subj_name, freq, chunk))

        # --------------------------------------------------------------------------------
        self.Timetable.map_arms_to_chunkfreq_details(selected_arms, dept_chunk_freq_list)
        # --------------------------------------------------------------------------------
        # Load the self.arms_feasible_table to display results
        self.load_arms_feasible_table()


 
    def load_arms_feasible_table(self):
        """ Loads the contents of the arms_feasible_table, i.e. the arms' names, total period, total frequency
        and whether it is feasible or not """

        self.arms_feasible_table.clearContents() 
        # gets the arm_feasible_data of all the class arms of the timetable
        table_data = self.Timetable.get_arms_feasible_table_data()


        self.arms_feasible_table.setRowCount(len(table_data))
        for index, details in enumerate(table_data):
            row = index
            full_name, periods_sum, frequency_sum, feasible, feasible_colour = details
            feasible_label = QtWidgets.QLabel()
            feasible_label.setText(str(feasible))
            feasible_label.setStyleSheet(f"color: {feasible_colour} padding-left:5px;")
            
            self.arms_feasible_table.setItem(row, 0, QtWidgets.QTableWidgetItem(full_name))
            self.arms_feasible_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(periods_sum)))
            self.arms_feasible_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(frequency_sum)))
            self.arms_feasible_table.setCellWidget(row, 3, feasible_label)


# -----------------------------------------------------------------------------------------------------
# ------------------- ASSIGNMENT OF SUBJECT TEACHERS TO CLASS ARMS AND CLASS ARM DETAILS ------------------------------------
    def load_arms_into_combobox(self, checkstate):
        """ Loads class arms into the combobox (in order to show class arm details) """
        if checkstate:
            self.arm_combobox.setEnabled(True)
            self.arm_id_container.setEnabled(False)
            # Load up arms into combobx
            self.arm_combobox.addItems(self.Timetable.get_model_items("arms")[0])
        else:
            self.arm_combobox.clear()
            self.arm_combobox.setEnabled(False)
            self.arm_id_container.setEnabled(True)


    def auto_assign_teachers_to_arms(self):
        """ The method the auto-assign button calls to automatically pair subject teachers to class arms """
        def _finished(msg): 
            self.messagebox(title="Assignment Status", icon="Information", text=msg)
            self.load_assignment_frame.hide()

        def _error(err_msg):
            self.messagebox(title="Assignment Error", icon="Critical", text=err_msg)
            self.load_assignment_frame.hide()
        # ----------------------------------------------------------------

        self.load_assignment_frame.show()
        progbar_left = self.findChild(QtWidgets.QProgressBar, "assign_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "assign_progbar_right")

        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.auto_assign_teachers_to_arms
        assign_worker = Tt_threads.TtWorker(working_object, finished_string="Assignment operation completed successfully", 
            error_string="Error occurred during assignment operation", nil_error_string="Assignment not permitted.", 
            aux_function=self.load_assignment_frame.hide)

        # connect slots to the progressbars
        assign_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        assign_worker.signals.finished.connect(lambda msg: _finished(msg))
        assign_worker.signals.error.connect(lambda err_msg: _error(err_msg))
        assign_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Criteria not met", icon="Critical", text=nil_msg))
        self.threadpool.start(assign_worker)


    def undo_auto_assign_teachers_to_arms(self):
        """ Handles the undoing of the assignment of the teachers to class arms operation """

        def _finished(msg): 
            self.messagebox(title="Assignment Status", icon="Information", text=msg)
            self.load_assignment_frame.hide()
        def _error(err_msg):
            self.messagebox(title="Assignment Error", icon="Critical", text=err_msg)
            self.load_assignment_frame.hide()
        # --------------------------------------------------------------------------
        # --------------------------------------------------------------------------

        self.load_assignment_frame.show()
        # Store function to hide without running it in the variable below

        progbar_left = self.findChild(QtWidgets.QProgressBar, "assign_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "assign_progbar_right")

        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.undo_assign_teachers_to_arms
        assign_worker = Tt_threads.TtWorker(working_object, finished_string="Assignment successfully undone!", 
            error_string="Error occurred during undoing assignment operation", nil_error_string="Undoing assignment not permitted.", 
            aux_function=self.load_assignment_frame.hide)

        # connect slots to the progressbars
        assign_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        assign_worker.signals.finished.connect(lambda msg: _finished(msg))
        assign_worker.signals.error.connect(lambda err_msg: _error(err_msg))
        assign_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Criteria not met", icon="Critical", text=nil_msg))
        self.threadpool.start(assign_worker)



    def pull_up_classarm(self):
        """ Method called when the pull is called. Extracts the arm_cred from the GUI and and passes it to the 
        manager to fetch the object """

        # carries the credential for arm to be searched out
        self.arm_cred = self.arm_combobox.currentText() if self.arm_combobox.isEnabled() else self.arm_id_spinbox.value()

        try:
            arm = self.Timetable.get_model_item_object("arms", self.arm_cred)
            self.arm_not_found_label.hide()

        except Tt_exceptions.SomethingWentWrong as e:
            # if an invalid cred is entered
            self.arm_not_found_label.show()
            self.arm_not_found_label.setText(e.comment)
            return

        # Start populating the widgets on the GUI
        self.arm_label.setText(arm.full_name)
        self.arm_class_label.setText(arm.school_class.full_name)
        self.arm_classcat_label.setText(arm.school_class.school_class_group.full_name)

        # Load up the table
        self.assign_subj_teacher_table.setRowCount(len(arm.get_arm_dept_teacher_freq_chunk()))

        for row, (dept, _, frequency, chunk) in enumerate(arm.get_arm_dept_teacher_freq_chunk()):
            teachers_para_or_no = arm.get_teacher_fullname_str_for_dept(dept)

            self.assign_subj_teacher_table.setItem(row, 0, QtWidgets.QTableWidgetItem(dept.full_name if dept else "None"))
            self.assign_subj_teacher_table.setItem(row, 1, QtWidgets.QTableWidgetItem(teachers_para_or_no if teachers_para_or_no else "None"))
            self.assign_subj_teacher_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(frequency)))
            self.assign_subj_teacher_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(chunk)))


    # ------------------------------------------------------------------------------------------------------------
    # ---------------------------------- PACKETING AND THE REAL CHUNK-SORTING ------------------------------------
    def _set_progressbar_to_val(self, progressbar_tuple, int_val):
        """ semi-private method to set the progressbars in the tuple argument to the value of the int_val argument.
        could also be used for one progressbar in the tuple """
        for progbar in progressbar_tuple:
            progbar.setValue(int_val)


    def packet(self):
        """ This function instructs the manager to packet (and repacket) all the subjects into class arms and report any errors """
        # ------------------------------------------------------------------------------------------------------------
        def _finished(msg): 
            self.messagebox(title="Packet status", icon="Information", text=msg)
            # self.load_packeting_frame.hide()
            

        def _error(err_msg):
            self.messagebox(title="Packet error", icon="Critical", text=err_msg)
            # self.load_packeting_frame.hide()
            

        def _finally():
            # load in this function from the Tt_guiExtras module
            # print(list(range(1000)))
            load_packeting_details_html_into_textedit(packet_worker.comment, 
                packet_textedit, len_all_subjects, len_all_days=len_all_days)
            self.load_packeting_frame.hide()
                
        # -----------------------------------------------------------------------------------------------------------
        
        self.load_packeting_frame.show()

        # How many subjects in total, needed for the function to generate details on the textEdit screen
        len_all_subjects = len(self.Timetable.get_model_items("depts")[0])
        len_all_days = len(self.Timetable.get_model_items("days")[0])
        
        # get the progressbars
        progbar_left = self.findChild(QtWidgets.QProgressBar, "packet_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "packet_progbar_right")

        # The textedit widget to display packeting comments
        packet_textedit = self.findChild(QtWidgets.QTextEdit, "packet_textedit")
        
        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.packeting_repacketing
        packet_worker = Tt_threads.TtWorker(working_object, finished_string="Successful. Packeting operation complete",
            error_string="Packeting operation unsuccessful!", nil_error_string="Packeting not permitted. Assignment operation yet to be carried out", 
            aux_function=self.load_packeting_frame.hide)

        # connect slots to the progressbars
        packet_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        packet_worker.signals.finished.connect(lambda msg: _finished(msg))
        packet_worker.signals.error.connect(lambda err_msg: _error(err_msg))
        packet_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Operation error", icon="Critical", text=nil_msg))
        packet_worker.signals.deadend.connect(lambda: _finally())
        self.threadpool.start(packet_worker)

        

    def undo_packet(self):
        """ Handles undoing the packet operation by enabling the worker thread object. """

        def _finished(msg): 
            self.messagebox(title="Packet status", icon="Information", text=msg)
            # self.load_packeting_frame.hide()

        def _error(err_msg):
            self.messagebox(title="Packeting error", icon="Critical", text=err_msg)
            # self.load_packeting_frame.hide()
        # ----------------------------------------------------------------

        self.load_packeting_frame.show()
        # get the progressbars
        progbar_left = self.findChild(QtWidgets.QProgressBar, "packet_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "packet_progbar_right")
        
        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.undo_packeting_repacketing
        packet_worker = Tt_threads.TtWorker(working_object, finished_string="Packeting successfully undone!", 
            error_string="Error occured in undoing the packeting operation", nil_error_string="Sorry, undoing packeting not permitted.", 
            aux_function=self.load_packeting_frame.hide)

        # connect slots to the progressbars
        packet_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        packet_worker.signals.finished.connect(lambda msg: _finished(msg))
        packet_worker.signals.error.connect(lambda err_msg: _error(err_msg))
        packet_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Operation error", icon="Critical", text=nil_msg))
        packet_worker.signals.deadend.connect(lambda :self.load_packeting_frame.hide())
        self.threadpool.start(packet_worker)



    # ------------------------ THE SORTING OPERATION PROPER!!! -------------------------------
    def refresh_day_arm(self):
        """ This method fires when the button to refresh reference day and arm is clicked """

        # Get the list of the full_names of all the days and arms.
        all_days = self.Timetable.get_model_items("days")[0]
        all_arms = self.Timetable.get_model_items("class_arms")[0]

        # Load them into the comboboxes
        self.ref_day_combobox.addItems(all_days)
        self.ref_arm_combobox.addItems(all_arms)


    # ...............................THE SORTING METHOS ITSELF ..................................................
    
    def full_sort(self):
        """ THE BIG-BOY FUNCTION. Handles the entire sorting process and the progressbars to show the progress """

        def _finished(msg): 
            self.messagebox(title="Packet status", icon="Information", text=msg)

        def _error(err_msg):
            self.messagebox(title="Packeting error", icon="Critical", text=err_msg)
            
        def _finally():
            self.load_sorting_frame.hide()
            load_sort_details_html_into_textedit(sort_worker.comment, sort_textEdit, num_all_teachers, num_all_subjects, num_all_arms)
        # ----------------------------------------------------------------

        # Get the reference_day, reference_arm values and the sort algorithm
        ref_day_text, ref_arm_text = self.ref_day_combobox.currentText(), self.ref_arm_combobox.currentText()
        algorithm_text = self.findChild(QtWidgets.QComboBox, "sort_algo_combobox").currentText()

        # get the arguments for the function to load sort details onto the GUI
        num_all_teachers = len(self.Timetable.get_model_items("teachers")[0])
        num_all_arms = len(self.Timetable.get_model_items("arms")[0])
        num_all_subjects = len(self.Timetable.get_model_items("depts")[0])


        # check to see if ref_day_text and ref_arm_text are not empty
        if not self.check_fields_or_error(fields_values_list=[ref_day_text, ref_arm_text]):
            # Raise messagebox
            self.messagebox(title="Not permitted", icon="Warning", text="Criteria not met. Packeting has not been successfully carried out.", 
                buttons=None, callback=None)
            return


        self.load_sorting_frame.show()
        # ---  get the progressbar and sort textEdit widgets
        progbar_left = self.findChild(QtWidgets.QProgressBar, "sort_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "sort_progbar_right")
        sort_textEdit = self.findChild(QtWidgets.QTextEdit, "sort_textedit")
        
        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.algosort_handle_cleanup_periodmap
        sort_worker = Tt_threads.TtWorker(working_object, finished_string="Sorting successful!", 
            error_string="Error occured in the sorting operation", nil_error_string="Sorry, Sorting operation not permitted.", 
            aux_function=self.load_sorting_frame.hide)

        # ---- Run with whatever arguments are necessary
        sort_worker.run_working_object(algorithm_text, ref_day_text, ref_arm_text)
        # connect slots to the progressbars
        sort_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        sort_worker.signals.finished.connect(lambda msg: _finished(msg))
        sort_worker.signals.error.connect(lambda err_msg: _error(err_msg))
        sort_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Operation error", icon="Critical", text=nil_msg))
        sort_worker.signals.deadend.connect(_finally)
        self.threadpool.start(sort_worker)


    def undo_full_sort(self):
        """ Undoes the full sort method """
        pass

# ------------------------------------------------------------------------------------------------------------------------------
# ---------------------------- THE FULL 'ADVANCED' SECTION SPORTING TEACHERS SPACING ET AL -------------------------------------
    
    def teachers_spacing(self):
        """ TENTATIVE? prints out the spacing dictionary for the all the algorithms """
        ref_day_text, ref_arm_text = self.ref_day_combobox.currentText(), self.ref_arm_combobox.currentText()
        self.Timetable.teachers_relative_spacing_per_algorithm(ref_day_text, ref_arm_text)
    

# -------------------------------------------------------------------------------------------------------------
# ----------------------------- SEMI-FINISH: DISPLAY SORTED RESULTS INTO FRAME: DIALS AND STUFF TOO ---------------------------------
    def display_by_arm_or_day(self):
        """ This method fires when the display_by_btn is clicked and extracts the radiobutton that is checked from the frame """
        # Extract clicked radiobutton from the frame
        for child in self.display_by_frame.children():
            if isinstance(child, QtWidgets.QRadioButton) and child.isChecked():
                self.model_type_label.setText(child.text().strip())
                break
        # enable the frame containing the dials and buttons
        self.display_dial_and_btns_frame.setEnabled(True)
        # set the dial to 1, the min value
        dial_value = 1
        self.items_dial.setValue(dial_value)
        try:
            model_item_for_display = self.Timetable.return_item_from_dial_value(self.model_type_label.text(), dial_value)
            self.model_item_label.setText(model_item_for_display)
        except Exception:
            self.messagebox(title="Not permitted", icon="warning", text="Operation not permitted. Sorting operation yet to be carried out")


    def get_item_from_dial_value(self, dial_widget, display_mod_item_label, display_mod_type_label):
        """ This method retrieves the value from the dial (between 1 and 100) and transmits that to the manager to get the model item
        and then displays the item in the 'model_item_label' label """

        dial_value = dial_widget.value()
        # send the dial value to the manager for processing
        model_item_for_display = self.Timetable.return_item_from_dial_value(display_mod_type_label.text(), dial_value)
        display_mod_item_label.setText(model_item_for_display)
            
        


    def scroll_model_item_by_btn(self, dial_widget, display_mod_item_label, display_mod_type_label, k):
        """ this function fires when either the up or down buttons are pressed, it takes us to the next item on the list
        'k' is the integer to go up or down by """
    
        # Returns a tuple of the kth_item and the dial value
        kth_item_dial_value = self.Timetable.get_kth_item_and_dial_value(display_mod_type_label.text(), display_mod_item_label.text(), k)
        # If the model item was not found, simply do nothing
        if kth_item_dial_value is None:
            return
        kth_item, dial_value = kth_item_dial_value
        dial_widget.setValue(dial_value)
        display_mod_item_label.setText(kth_item)


    def show_finished_periods_in_frame(self):
        """ This method displays all the periods of each arm in frames on the GUI """

        def _make_frame(periods_data_list):
             # frame = PeriodsDisplayFrame(frame=self.periods_display_frame, spacing=6, padding=(2,2,2,2))
             model_marker = "Day" if "day" in self.model_type_label.text().lower() else "Class Arm"
             frame.add_childframe_data(model_marker, self.match_item, periods_data_list=periods_data_list)
             frame.set_width_height()
             frame.add_widget_to_frames_vbox()
        # --------------------------------------------------------------------
        # -------------------------------------------------------------------

        model_type_str = self.model_type_label.text()
        model_item_str = self.model_item_label.text()

        self.timetable_title_label.setText(model_item_str)

        # Get the progressbars
        progbar_left = self.findChild(QtWidgets.QProgressBar, "display_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "display_progbar_right")

        # The frame object on the gui
        frame = PeriodsDisplayFrame(frame=self.periods_display_frame, spacing=6, padding=(2,2,2,2))

        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.yield_arm_or_days_period_data

        display_fin_periods_worker = Tt_threads.WorkerForFrames(working_object, finished_string="Finished periods display successful!", 
            error_string="Error occured in periods display", nil_error_string="Sorry, Not permitted.", 
            aux_function=None)
        # ---- supply arguments for the working objects to run
        display_fin_periods_worker.run_working_object(model_type_str, model_item_str)
        # connect slots to the progressbars
        display_fin_periods_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        # display_fin_periods_worker.signals.finished.connect(lambda msg: _finished(msg))
        display_fin_periods_worker.signals.error.connect(lambda err_msg: self.messagebox(title="Operation error", icon="Critical", text=err_msg))
        display_fin_periods_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Operation error", icon="Critical", text=nil_msg))
        # display_fin_periods_worker.signals.deadend.connect(_finally)
        display_fin_periods_worker.signals.progress_with_info.connect(_make_frame)
        self.threadpool.start(display_fin_periods_worker)


    def retrieve_track_model(self):
        """ This signal fires when the track_by button is clicked in the tabwidget up-top in the app. It goes through all the radiobuttons
        in the track_models_by _frame widget to see which one has been clicked """

        for widget in self.track_models_by_frame.children():
            if isinstance(widget, QtWidgets.QRadioButton) and widget.isChecked():
                # enable the frame that holds the track dials and btns
                self.track_dial_and_btns_frame.setEnabled(True)
                # set the track_model_type label to the text of the radiobutton
                self.track_model_type_label.setText(widget.text().strip())
                return
    
        # if no breaking, i.e. no checked radiobuttons found
        self.messagebox(title="Empty fields", icon="Critical", text="No model type selected yet to track.", 
            extratext="Do select a model type so that tracking can be performed.")


    def deselect_track_models(self):
        """ This method deselects the items checked in the track_model_frame """
        for widget in self.track_models_by_frame.children():
            if isinstance(widget, QtWidgets.QRadioButton):
                widget.setChecked(False)
        self.match_item = "Nil"


    def track_model_item(self):
        """ This method calls the manager to track the item as given on the track frame on all the period widgets available on screen.
        the tracking and display on the screen is done here """

        def _make_frame(periods_data_list):
             # frame = PeriodsDisplayFrame(frame=self.periods_display_frame, spacing=6, padding=(2,2,2,2))
             model_marker = "Day" if "day" in self.model_type_label.text().lower() else "Class Arm"
             frame.add_childframe_data(model_marker, self.match_item, periods_data_list=periods_data_list)
             frame.set_width_height()
             frame.add_widget_to_frames_vbox()


        # model_type = self.track_model_type_label.text()
        self.match_item = self.track_item_label.text()

        model_type_str = self.model_type_label.text()
        model_item_str = self.model_item_label.text()

        self.timetable_title_label.setText(model_item_str)

        # Send these values to the manager and have it glow up every search with a packet_worker
        # ------------------
        progbar_left = self.findChild(QtWidgets.QProgressBar, "track_progbar_left")
        progbar_right = self.findChild(QtWidgets.QProgressBar, "track_progbar_right")

        self.load_track_frame.show()


        # The frame object on the gui
        frame = PeriodsDisplayFrame(frame=self.periods_display_frame, spacing=6, padding=(2,2,2,2))

        self.threadpool = QtCore.QThreadPool()
        working_object = self.Timetable.yield_arm_or_days_period_data

        track_worker = Tt_threads.WorkerForFrames(working_object, finished_string="Tracking successful! your selection appears in distinctive colouring.", 
            error_string="Error occured in the tracking operation", nil_error_string="Sorry, tracking operation not permitted.", 
            aux_function=self.load_track_frame.hide)

        # ---- supply arguments for the working objects to run
        track_worker.run_working_object(model_type_str, model_item_str)
        # connect slots to the progressbars
        track_worker.signals.progress.connect(lambda int_val: self._set_progressbar_to_val((progbar_left, progbar_right), int_val))
        track_worker.signals.finished.connect(lambda msg: self.messagebox(title="Tracking successful", icon="Information", text=msg))
        track_worker.signals.error.connect(lambda err_msg: self.messagebox(title="Operation error", icon="Critical", text=err_msg))
        track_worker.signals.nil_error.connect(lambda nil_msg: self.messagebox(title="Operation error", icon="Critical", text=nil_msg))
        # track_worker.signals.deadend.connect(_finally)
        track_worker.signals.progress_with_info.connect(_make_frame)
        self.threadpool.start(track_worker)


    # --------------------------------------------------------------------------------------------------------------
    # ------------------------ FINISHED REPORT AND DIAGNOSTICS REPORT GENERATION SECTION ---------------------------
    def generate_finished_report(self):
        """ This method serves as a slot for the gen_report_btn. It facilitates the generation of the finished
        timetable either into docx, PDF or HTML formats. """

        # basis is whether it is based on department or class arm
        basis = self.report_basis_combobox.currentText()
        format_ = self.report_format_combobox.currentText()

        if "docx" in format_.lower():
            file_ext = ".docx"
        elif "pdf" in format_.lower():
            file_ext = ".pdf"
        else:
            file_ext = ".html"


        # Open a dialog box and chose directory to work in
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Export file by {basis}", "", f"{format_}(*{file_ext})")
        
        if file_path:
            file_path = QtCore.QDir.toNativeSeparators(file_path)
            self.Timetable.generate_timetable_file(file_path, format_, basis)




# ---------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ---------------------------------------------  HELPER FUNCTIONS -----------------------------------------
    def checked_widgtree_in_listwidget(self, listwidget):
        """ Goes through all the WidgetTree (my custom widget) instances and picks which one has been checked into a list """
        selected = []

        for k in range(listwidget.count()):
            item = listwidget.item(k)
            item_widg = listwidget.itemWidget(item)

            if item_widg.get_checkbox().isChecked():
                selected.append(item_widg.full_name_label.text())
        return selected


    def adjust_table_columns(self,table, column_width_cont=None):
        """ Function to automate the width of the columns of 'table'. column_width_cont, is a list
        containing tuples of (column, width integer) """
        for col, width in column_width_cont:
            table.setColumnWidth(col, width)



    def checkall_widgtree_in_listwidget(self, listwidget, checkall=True):
        """ Goes through all the widgettree (my custom widget) instances in the 
        listwidget and checks or unchecks all their  checkboxes """

        check_all = QtCore.Qt.Checked if checkall else False
        for k in range(listwidget.count()):
            item = listwidget.item(k)
            item_widg = listwidget.itemWidget(item)
            item_widg.get_checkbox().setCheckState(check_all)


    @staticmethod
    def check_fields_or_error(fields_values_list=None):
        """BOOLEAN. This method handles checking whether all the items in the list are Truthy values. """
        return all(fields_values_list) and isinstance(fields_values_list, list)
            

    @staticmethod
    def messagebox(title="Popup message", icon="Question", text="Something's the matter?", extratext="", buttons=None, callback=None):
        """ Generates message boxes (popup boxes of all kinds) of all kinds. Buttons is a LIST really of all the buttons (strings)
        for the message box.
        The callback function will be set. when already running. the callback (when defined in realtime) accepts an arg (i) which is
        the button clicked. """

        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QtGui.QIcon("TIMETABLE/Icons-mine/App_logo.png"))
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


    

# ---------------------------------------------------------------------------------------
def run_app_anew(tt_obj=None):
    Timetable_mainwindow = UITimetable(tt_obj=tt_obj)
    Timetable_mainwindow.show()


def run_main():
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    Splash_and_mainwindow = TtSplashScreen()
    Splash_and_mainwindow.show()
    app.exec_()
