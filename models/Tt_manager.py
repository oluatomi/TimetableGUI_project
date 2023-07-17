#--THIS DOES NOT TAKE CARE OF THE ALGORITHM TO SORT, BUT PROVIDES VITAL INFORMATION FOR THE MODULE THAT HANDLES THE ALGORITHM FOR SORTING.
#-- THE 'cls_pers' MODULE HANDLES THE OBJECTS 
#-- (MOSTLY), WITH ITS STATIC METHODS DOING SOME OF THE NEEDED (SMALL)
#--CALCULATIONS THAT ARE ALBEIT STILL NEEDED.
#--THOSE METHODS COULD HAVE BEEN PUT HERE, BUT I FEEL THEY SHOULD SHIP DIRECTLY WITH THE 'Tt_models'
#--MODULE -- THE MODULE THAT HANDLES THE TIMETABLE OBJECT.


# -- THIS IS THE OFFICIAL FORM OF THE TESTING_SETUP.PY MODULE

from collections import namedtuple
from .Tt_models import TimeTable
from inspect import isfunction
from .Tt_algo import TimetableSorter
import string, re, pickle, math
from . import Tt_exceptions
from ..gui import Tt_GuiExtras
from TIMETABLE.reports import Tt_docx_reports
from TIMETABLE.reports import Tt_html_reports


subj_freq_chunk = namedtuple("subj_freq_chunk", "dept frequency chunk")

def get_obj_from_param(g_list, attr, param):
    """ This helper function searches through a given list "g_list" and 
    checks for the object that has the attribute "attr" if it is equal to "param"
    and then returns it.

    "param" has to be string. So also "attr".
     """
    for item in g_list:
        if hasattr(item, attr):
            if isfunction(getattr(item, attr)):
                if getattr(item, attr)().lower() == param.lower():
                    return item
            else:
                if str(getattr(item, attr)).lower() == param.lower():
                    return item
    else:
        raise ValueError(f"{param} not found. No item has what you checked for.")


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
class TimeTableManager:
    """ This class serves as the intermediary between the GUI and the Tt_models and Tt_algo and also the GUI modules """
    extension = '.tmtb'
    recent_files_path = 'TIMETABLE/gui/TimeTable Extras/File_paths_for_recent.txt'
    conversion_constants_dict = {"I": 1, "P": 96, "C": 2.54, "M": 25.4}
    def __init__(self, tt_obj=None):
        self.Timetable_obj = TimeTable() if not tt_obj else tt_obj
        self.TimetableSorter = TimetableSorter(tt_obj=self.Timetable_obj)
        self.object_getter = get_obj_from_param
        # In the event of an update to one of the arm or teacher, etc models, the pre_existing model to be edited
        self.pre_existing = None
        self.regex_time_pattern = "\d+:\d+:\d+"
        self.regex_position_pattern = "^(\d+,?)+$"
        


    def _authorize_assign_op(self):
        """ BOOL. Checks if all criteria have been met for assignment operation to be carried out """
        return bool(self.get_model_items("arms")[1]) and bool(self.get_model_items("teachers")[1])
        

    def _authorize_packet_op(self):
        """ BOOL. Checks if all criteria have been met for packeting operation operation to be carried out """
        return self.Timetable_obj.can_packet and self._authorize_assign_op()


    def _authorize_sort_op(self):
        """ BOOL. Checks if all criteria have been met for sort operation to be carried out """
        return self.Timetable_obj.can_sort and self._authorize_packet_op()


    # --------------------------------------------------------------------------------------
    # ---------------------------- SAVE AND LOAD FILES -------------------------------------
    def save(self, project_file_path):
        """ Pickles the timetable object into a file """
        self.Timetable_obj.save(project_file_path)
        self.add_project_to_recent(project_file_path)

        # Add this project to the list of recent files
        self.add_project_to_recent(project_file_path)


    def add_project_to_recent(self, project_file_path):
        """ The file that holds recent project_file_paths can hold a 'limit' amount of files and hoists the new 
        file path to the top of the list. This method manages the input of a new project file into the file such that
         'limit' is not exceeded, and there are no repititions. A simple python list is used. No need for a LIFO queue """
        
        limit = 10
        project_file_path = project_file_path if project_file_path.endswith(self.extension) else project_file_path + self.extension
        # Read any already stored paths from the external file
        with open(self.recent_files_path, 'r') as file:
            recent_paths = file.readlines()
        recent_file_paths_list = [] if recent_paths == ["\n"] else [path.strip("\n") for path in recent_paths]

        # Now add to the beginning of the list. and check for if it was already in the list before and add it to the front
        # of the list, whether or not
        if project_file_path in recent_file_paths_list:
            recent_file_paths_list.remove(project_file_path)
        recent_file_paths_list.insert(0, project_file_path)

        # Now check if the list exceeds 'limit' and clip off any trespassing items
        len_recent_paths_list = len(recent_file_paths_list)
        if len_recent_paths_list > limit:
            recent_file_paths_list[limit - len_recent_paths_list:] = []

        # Now load back into the external file
        with open(self.recent_files_path, 'w') as file:
            for line in recent_file_paths_list:
                file.writelines(line + "\n")


    def load_recent_projects(self):
        """ returns a list of all the recent files """
        with open(self.recent_files_path, 'r') as file:
            recent_paths = file.readlines()
        recent_file_paths_list = [] if recent_paths == ["\n"] else [path.strip("\n") for path in recent_paths]
        return recent_file_paths_list


    def load_tt_obj_from_file(self, project_file_path):
        """ loads an existing timetable object from a '.tmtb' file and returns said object """
        import os

        if os.path.exists(project_file_path) and os.path.splitext(project_file_path)[1] == self.extension:
            with open(project_file_path, 'rb') as file:
                try:
                    tt_object = pickle.load(file)
                except Exception:
                    raise Tt_exceptions.SomethingWentWrong(f"A problem arose in loading file {project_file_path}. The file is compromised.")
            return tt_object


    def clear_recent_files(self):
        """ Clears the file that carries the list of the recent files. Replaces the text inside with an empty string """
        with open(self.recent_files_path, 'w') as file:
            file.writelines("")


    def reset_tt_obj(self):
        """ resets the timetable object """
        self.Timetable_obj.reset_timetable()

    # ----------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    def stash_general_info(self, info_dict):
        """ passes the general info details from the GUI to the timetable object and back """
        self.Timetable_obj.commit_general_info(info_dict)


    def get_general_info(self):
        """ Retrieves the general info details from the Timetable object, to pass on to the GUI """
        return self.Timetable_obj.get_general_info()


    def get_model_items(self, model_name):
        """ Returns list of type model_name from the timetable object. Model_name rendered in plural """
        if model_name in ("depts", "courses", "subjects"):
            mod_list = self.Timetable_obj.list_of_departments
        elif model_name in ("class_groups", "class_cats", "class_categories"):
            mod_list = self.Timetable_obj.list_of_school_class_groups
        elif model_name == "nonacads":
            mod_list = self.Timetable_obj.list_of_nonacad_depts
        elif model_name in ("facs", "faculties"):
            mod_list = self.Timetable_obj.list_of_faculties
        elif model_name in ("teachers", "staff"):
            mod_list = self.Timetable_obj.list_of_all_teachers
        elif model_name in ("classes", "school_classes"):
            mod_list = self.Timetable_obj.list_of_school_classes
        elif model_name in ("arms", "class_arms"):
            mod_list = self.Timetable_obj.list_of_school_class_arms
        elif model_name == "days":
            mod_list = self.Timetable_obj.list_of_days
        else:
            raise ValueError(f"{model_name} not legal!!")

        # returns a tuple of the below
        return [item.full_name for item in mod_list], mod_list


    def get_model_item_object(self, model_name, identifier):
        """ Returns a model item, class arm, class cat, teacher etc. given an identifier. Identifier can be
        fullname or id. """

        # search by its fullname if it is a sring else by its number ID
        attr = "full_name" if isinstance(identifier, str) else "id"
        model_list = self.get_model_items(model_name)[1]
        # in case the arm_cred does not match any teacher
        try:
            model_obj = self.object_getter(model_list, attr, str(identifier))
        except ValueError:
            raise Tt_exceptions.SomethingWentWrong(f"None amongst {model_name} with ID: {identifier}")
        return model_obj


    # -------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------UTILITY FUNCTIONS ABOVE, MODEL FUNCTIONS BELOW -----------------------------------------------------------
    def set_workrate_inflexion_num(self, inflx_num):
        """ (Re-)Sets the workrate inflexion number on the timetable object """
        self.Timetable_obj.set_workrate_inflexion(inflx_num)


    def get_workrate_coefficient(self):
        """ Retrieves the timetable object's workrate_inflexion_coefficient for the GUI """
        return str(self.Timetable_obj.workrate_inflexion_coefficient)


    def get_ATPG_parameters(self):
        """ (Tuple of tuples) Gets the ATPG paramters (and weights) from the timetable object """
        return self.Timetable_obj.analytic, self.Timetable_obj.theoretical, self.Timetable_obj.practical, self.Timetable_obj.grammatical


    def set_ATPG_parameters(self, analytic_tuple, theoretical_tuple, practical_tuple, grammatical_tuple):
        """ Set the timetable object's ATPG parameters """

        # unpack the arguments
        analytic_name, analytic_val = analytic_tuple
        theoretical_name, theoretical_val = theoretical_tuple
        practical_name, practical_val = practical_tuple
        grammatical_name, grammatical_val = grammatical_tuple

        self.Timetable_obj.set_ATPG_parameters((analytic_name, analytic_val), (theoretical_name, theoretical_val), 
            (practical_name,practical_val), (grammatical_name, grammatical_val))


    def create_faculty(self, faculty_name, HOD="Esteemed HOD Sir/Ma'am", description="", update=False):
        #  ...
        pre_existing = self.pre_existing if update else None 
        self.Timetable_obj.create_faculty(faculty_name, HOD=HOD, description=description, update=update,preexisting_obj=pre_existing)


    def create_department(self, name, hos=None, is_parallel=False, faculty=None, A=1,T=1,P=1,G=1, update=False):
        #  ...

        pre_existing = self.pre_existing if update else None
        hos = "Unspecified" if not hos else hos
        faculty_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", faculty)
        self.Timetable_obj.create_department(name, faculty=faculty_obj, hos=hos, is_parallel=is_parallel, A=A, T=T,P=P,G=G, preexisting_obj=pre_existing, update=update)


    def create_special_department(self, name, update=False):
        """ handles creation or update of a non-academic subject e.g. break-time """
        pre_existing = self.pre_existing if update else None
        self.Timetable_obj.create_department(name, is_special=True, update=update, preexisting_obj=pre_existing)



    def pull_classmodel(self, model_type, curr_model_name):
        """This function pulls out a model of type model_type and full_name of curr_name """

        if model_type == "Day":
            models_list = self.Timetable_obj.list_of_days
            choice_model = self.object_getter(models_list, "full_name", curr_model_name)
            args = {"name":choice_model.day}

        elif model_type == "Class":
            models_list = self.Timetable_obj.list_of_school_classes
            choice_model = self.object_getter(models_list, "full_name", curr_model_name)
            # You only need edit the name, not the class group. if you want a different classgroup, delete and remake, just adding the classgroup
            # for adding sake
            args = {"name":choice_model.level, "classcat":choice_model.school_class_group.full_name}

        elif model_type == "Class Category":
            models_list = self.Timetable_obj.list_of_school_class_groups
            choice_model = self.object_getter(models_list, "full_name", curr_model_name)
            args = {"name":choice_model.class_group_name, "description":choice_model.description, "abbrev":choice_model.abbreviation}

        self.pre_existing = choice_model
        return args


    def pull_dept_model_list(self, radbtn_clicked_text):
        """ Pulls up model list whether it is a faculty or subject """
        if radbtn_clicked_text == "Department":
            return [fac.full_name for fac in self.Timetable_obj.list_of_faculties]
        elif radbtn_clicked_text == "Subject/Course":
            return [dept.full_name for dept in self.Timetable_obj.list_of_departments]

        # If it falls through the above return list non-acad departments
        return [nonacad.full_name for nonacad in self.Timetable_obj.list_of_nonacad_depts]


    def pull_deptmodel_item(self, radbtn_text_tuple):
        """ This method fetches the model item itself and sends its attributes to the GUI controller for display on the screen """

        mod, itemfullname = radbtn_text_tuple

        if mod == "Department":
            # find "item" object in its list. This is really "faculty" in the code.
            item_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", itemfullname)
            item_object_dict = {"name":item_obj.name, "HOD": item_obj.HOD, "description": item_obj.description}

        elif mod == "Subject/Course":
            item_obj = self.object_getter(self.Timetable_obj.list_of_departments, "full_name", itemfullname)
            item_object_dict = {"name":item_obj.dept_name, "hos": item_obj.hos, "A": item_obj.analytic, 
            "T":item_obj.theoretical, "P":item_obj.practical, "G": item_obj.grammatical}

        elif mod == "Non-Academic Subject":
            item_obj = self.object_getter(self.Timetable_obj.list_of_nonacad_depts, "full_name", itemfullname)
            item_object_dict = {"name":item_obj.dept_name}

        self.pre_existing = item_obj
        return item_object_dict


    def create_school_class_group(self,class_group_name, description="Houses school classes of like properties", abbrev="", update=False):
        """ Handles the creation or update of the school class group, i.e. school class category """

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done


        pre_existing = None if not update else self.pre_existing
        self.Timetable_obj.create_school_class_group(class_group_name, description=description, 
            abbrev=abbrev, update=update, preexisting_obj=pre_existing)


    def create_school_class(self, name, class_group, update=False):
        #  ...
        
        # label_iden is None when it is creation (and not update) of class
        pre_existing_obj = None if not update else self.pre_existing

        classgroup_obj = self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", class_group)
        self.Timetable_obj.create_school_class(name,classgroup_obj, update=update, preexisting_obj=pre_existing_obj)


    def generate_school_class_arms(self, class_fullname, frequency=1, as_alpha=True, override=False):
        """ Generates a 'frequency' amount of class arms for the school class with 'class_fullname' """

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        
        # self.prerequisites["assigned"] = False

        school_class_obj = self.object_getter(self.Timetable_obj.list_of_school_classes, "full_name",class_fullname)
        # If we want this newly generated class to override previously generated ones
        if override:
            # From the class, remove the arms from the list of arms, and also from the .list_of_school_class_arms
            for arm in school_class_obj.school_class_arm_list:
            # ----- Remove from the school class' list of arms
                # school_class_obj.remove_arm_from_class(arm)
                self.Timetable_obj.list_of_school_class_arms.remove(arm)
            
            # Absolutely empty out this school class list of arms
            school_class_obj.school_class_arm_list = [] 

        for _ in range(frequency):
            self.Timetable_obj.create_school_class_arm(school_class_obj, as_alpha=as_alpha)


    def generate_teachers(self, frequency=1, teaching_days=None, specialty="All", designation="Member of staff", course_list=None, update=False):
        #  ...

        dept_objs_list = [self.object_getter(self.Timetable_obj.list_of_departments, "full_name", course_fullname) for course_fullname in course_list]
        # get all the teaching day objects
        teaching_days_list = [self.object_getter(self.Timetable_obj.list_of_days, "full_name", day_fullname) for day_fullname in teaching_days]
        designation = designation if designation else "Member of staff"
        # ----------------------------------------------
        if specialty == "All":
            specialty = self.Timetable_obj.list_of_school_class_groups
        else:
            specialty = [self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", specialty)]
        
        # ----------------------------------------------
        if not update:
            # Create teacher with the first course hence, simply add the other courses to the teacher
            # for _ in range(frequency):
            self.Timetable_obj.create_teacher(frequency=frequency, dept_objs_list=dept_objs_list, teaching_days=teaching_days_list, 
                specialty=specialty, designation=designation)
            return
        
        # ---IF UPDATE: WHEN UPDATE IS BEING MADE
        self.Timetable_obj.create_teacher(dept_objs_list=dept_objs_list, teaching_days=teaching_days_list, 
            specialty=specialty, designation=designation, update=True, preexisting_obj=self.pre_existing)


    def search_out_teacher(self, ID):
        """ searches teacher out from the list of teachers by ID """

        for teacher in self.Timetable_obj.list_of_all_teachers:
            if teacher.id == ID:
                return teacher
        # Else returns None by default. PERFECTO!
    

    def pull_teacher(self, teacher_fullname):
        """ Extracts the teacher's courses and teaching days from the timetable class """

        # extract he teacher object
        teacher_obj = self.object_getter(self.Timetable_obj.list_of_all_teachers, "full_name", teacher_fullname)
        courses = teacher_obj.teachers_depts_list
        tdays = teacher_obj.teaching_days
        designation = teacher_obj.designation
        specialty = teacher_obj.specialty

        # specialty_text = "All" if set(specialty) == set(self.Timetable_obj.list_of_school_class_groups) else specialty[0].full_name

        # Slap courses into a dictionary (key) and whether they should be checked or not as the value
        courses_for_gui = {course.full_name:False for course in self.Timetable_obj.list_of_departments}
        days_for_gui = {day.full_name:False for day in self.Timetable_obj.list_of_days}

        # Update the values to true if the teacher takes the dept(course)
        for course in courses:
            courses_for_gui[course.full_name] = True

        # Update the values to true if the teacher teachers on that day
        for day in tdays:
            days_for_gui[day.full_name] = True

        # send both out to the GUI class
        self.pre_existing = teacher_obj
        return courses_for_gui, days_for_gui, designation


    def delete_teacher(self, teachers_list):
        """ Completely deletes a teacher and any references to it """

        teacher_obj_list = [self.object_getter(self.Timetable_obj.list_of_all_teachers, "full_name", teacher_) for teacher_ in teachers_list]
        for teacher in teacher_obj_list:
            self.Timetable_obj.del_teacher(teacher)


    # ------------ MAKING PERIODS AND STUFF IS NEXT!
    def create_day(self, day_name, rating=None, update=False):
        """ Creates (or updates) the day object """
        #  ...
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        pre_existing_obj = None if not update else self.pre_existing
        # The rating parameter helps to situate the day in te list of days
        rating = rating - 1 if rating else None
        self.Timetable_obj.create_day(day_name, rating=rating, update=update, preexisting_obj=pre_existing_obj)


    # --------------- delete models, class group, class, day, dept, teacher. e.t.c
    def delete_models(self, dict_arg):
        """ delete models, class group, class, day, dept, teacher.
        The dict_arg contains the model_name (classgroup, school class or no) as key and the selected items as the values
        e.t.c """
        
        mod_name_key = list(dict_arg.keys())[0]
        selected_items = dict_arg[mod_name_key]

        if mod_name_key == "Day":

            for day_fullname in selected_items:
                day_obj = self.object_getter(self.Timetable_obj.list_of_days, "full_name", day_fullname)
                self.Timetable_obj.del_day(day_obj)

        elif mod_name_key == "Class":

            for class_fullname in selected_items:
                class_obj = self.object_getter(self.Timetable_obj.list_of_school_classes, "full_name", class_fullname)
                self.Timetable_obj.del_school_class(class_obj)
        
        elif mod_name_key == "Class Category":
            # for the class group (class category)
            for classcat_fullname in selected_items:
                classcat_obj = self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", classcat_fullname)
                self.Timetable_obj.del_school_class_group(classcat_obj)

        elif mod_name_key == "Department":
            # To delete faculty objects
            for fac_fullname in selected_items:
                fac_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", fac_fullname)
                self.Timetable_obj.del_faculty(fac_obj)


        elif mod_name_key == "Subject/Course":
            # Delete depts(courses)
            for subj_fullname in selected_items:
                subj_obj = self.object_getter(self.Timetable_obj.list_of_departments, "full_name", subj_fullname)
                self.Timetable_obj.del_department(subj_obj)

        elif mod_name_key == "Non-Academic Subject":
            # Delete non-academic subjects
            for nonacad_fullname in selected_items:
                nonacad_obj = self.object_getter(self.Timetable_obj.list_of_nonacad_depts, "full_name", nonacad_fullname)
                self.Timetable_obj.del_nonacad_department(nonacad_obj)



    # --------------- FUNCTION REGARDING DETAILS TO BE DISPLAYED IN THE TAB 
    def day_range(self, day_fullname_str):
        """ Retrieves the day range (DAY START AND DAY END) from the timetable object.
        To be displayed in the top tab bar of the GUI """
        day_obj = self.get_model_item_object("days", day_fullname_str)
        return self.Timetable_obj.day_range(day_obj)


    def periods_total(self, day_fullname_str):
        """ Returns a tuple (acads, non-acads, total) """
        day_obj = self.get_model_item_object("days", day_fullname_str)
        total, acads, non_acads = self.Timetable_obj.periods_total(day_obj)
        return str(total), str(acads), str(non_acads)



    def average_num_periods(self, day_fullname_str):
        """ INT. Returns the average of all the periods today """
        day_obj = self.get_model_item_object("days", day_fullname_str)
        return str(self.Timetable_obj.average_num_periods(day_obj))


    def arm_with_max_periods(self, day_fullname_str):
        """ (INT, list(class_arm_obj)) class arm_obj or None """
        day_obj = self.get_model_item_object("days", day_fullname_str)
        arms_today_len = int(day_obj.class_arms_today(as_int_str=True))
        max_val, arms_len = self.Timetable_obj.arm_with_max_periods(day_obj)

        if arms_len == arms_today_len:
            arm_comment = "All arms today"
        elif arms_today_len // 2 < arms_len < arms_today_len:
            arm_comment = "A majority (class arms) today"
        elif arms_len == arms_today_len // 2:
            arm_comment = "About half (class arms) today"
        elif arms_len < arms_len_today // 2:
            arm_comment = f"A few arms today"
        return str(max_val), arm_comment


    def arm_with_min_periods(self, day_fullname_str):
        """ Calls a function that returns two INTs. One for the max (or min) value, and the other
        for number of class arms today that actually have that number of periods """
        day_obj = self.get_model_item_object("days", day_fullname_str)
        arms_today_len = int(day_obj.class_arms_today(as_int_str=True))
        min_val, arms_len = self.Timetable_obj.arm_with_min_periods(day_obj)

        if arms_len == arms_today_len:
            arm_comment = "All arms today"
        elif arms_today_len // 2 < arms_len < arms_today_len:
            arm_comment = "A majority"
        elif arms_len == arms_today_len // 2:
            arm_comment = "About half"
        elif arms_len < arms_len_today // 2:
            arm_comment = "A few"
        return str(min_val), arm_comment



    # -----------------------------------------------------------------------------------------
    # ----------------------------- PERIOD GENERATION SECTION ---------------------------------
    def add_days_to_selected_classarms(self, selected_arms_list=None, selected_days_list=None):
        """ This method add each of the days to each of the class arms in the arms_list """

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        # self.prerequisites["assigned"] = False
        # .......................................................................
        # Add each day object to each arm
        for arm in selected_arms_list:
            # Empty out the days_list of the arm before filling it again
            self.Timetable_obj.unmap_all_depts_from_arm(arm)
            for day in selected_days_list:
                self.Timetable_obj.map_day_to_arm(arm, day)


    def add_depts_to_selected_classarms(self, arm_objs_list=None, iterable_from_gui=None):
        """ This method adds the courses from the iterable_from_gui into the selected arms. iterable_from_gui is
        a list of (dept, freq, chunk) tuples (namedtuples?) """

        for arm in arm_objs_list:
            for detail in iterable_from_gui:
                dept, freq, chunk = detail
                self.Timetable_obj.map_dept_to_arm(arm, dept, freq, chunk)


    def generate_periods_for_classarms(self, g_box_id, selected_arms_list=None, selected_days_list=None, acad_periods_dict=None, nonacad_tuple_list=None):
        """ This method generates periods for all the arms for all the days that have been selected from the GUI """
        
        if g_box_id == "by_duration":
            for arm in selected_arms_list:
                for day in selected_days_list:
                    self.TimetableSorter.generate_periods_given_duration(arm, day, acad_periods_dict=acad_periods_dict, nonacad_tuple_list=nonacad_tuple_list)
        elif g_box_id == "by_acadspan":
            for arm in selected_arms_list:
                for day in selected_days_list:
                    self.TimetableSorter.generate_periods_given_acadspan(arm, day, acad_periods_dict=acad_periods_dict, nonacad_tuple_list=nonacad_tuple_list)
        else:
            for arm in selected_arms_list:
                for day in selected_days_list:
                    self.TimetableSorter.generate_periods_given_abs_constraints(arm, day, acad_periods_dict=acad_periods_dict, nonacad_tuple_list=nonacad_tuple_list)



    def pin_day_generate_periods(self, g_box_id, selected_arms_list=None, selected_days_list=None, normal_periods_dict=None, nonacad_tuple_list=None):
        """ Handles adding days selected to class arms selected and generates periods from the GUI """
        
        def _to_time_tuple(time_str):
            """ Convers string of format hh:mm:ss to the time tuple to be used in calculations """
            var = time_str.split(":")
            ret_list = [int(k) for k in var]
            return tuple(ret_list)

        def _to_int_list(pos_str):
            """ converts the string items in positio list to al list of integers """
            var = pos_str.split(",")
            return [int(k) for k in var]

        # --------------------------------------------------------------------------------------------------
        # ----------- First, validate the necessary fields with the regular expressions pattern
        # Validate all the elements normal_periods_dict except the freq and see if they all match to true

        match_list = []
        for field, val in normal_periods_dict.items():
            if field == "freq":
                continue
            match = re.match(self.regex_time_pattern, val)
            match_list.append(match)

        # Also validate the nonacad_tuple
        for name, duration, pos_list in nonacad_tuple_list:
            match = re.match(self.regex_time_pattern, duration)
            rematch = re.match(self.regex_position_pattern, pos_list)
            match_list.append(match)
            match_list.append(rematch)

        # If all these fields (acad and non-acad) are not of the right pattern, ERROR OUT!!
        if not all(match_list):
            return "Invalid field input"

        # Morphe normal_periods_dict and nonacad_tuple from mere strings into the accepted formats
        for field, val in normal_periods_dict.copy().items():
            if field == "freq":
                continue
            normal_periods_dict[field] = _to_time_tuple(val)
        
        # --- And
        for index, elem in enumerate(nonacad_tuple_list.copy()):
            name, duration, positions = elem
            # Get the non-acad dept object and re-assign to 'name' variable
            name = self.object_getter(self.Timetable_obj.list_of_nonacad_depts, "full_name", name)
            nonacad_tuple_list[index] = (name, _to_time_tuple(duration), _to_int_list(positions))



        arm_objs = [self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", arm_fullname) for arm_fullname in selected_arms_list]
        day_objs = [self.object_getter(self.Timetable_obj.list_of_days, "full_name", day_fullname) for day_fullname in selected_days_list]
        # ------------------------------------------------
        # Add days to class arm
        self.add_days_to_selected_classarms(selected_arms_list=arm_objs, selected_days_list=day_objs)
        # Generate periods for the days established
        self.generate_periods_for_classarms(g_box_id, selected_arms_list=arm_objs, selected_days_list=day_objs,
            acad_periods_dict=normal_periods_dict, nonacad_tuple_list=nonacad_tuple_list)



    def nullify_day_and_periods_from_arms(self, selected_arms_list, selected_days_list):
        """ This method handles removing the day and periods generated therein from each class arm in the list """
        arm_objs = [self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", arm_fullname) for arm_fullname in selected_arms_list]
        day_objs = [self.object_getter(self.Timetable_obj.list_of_days, "full_name", day_fullname) for day_fullname in selected_days_list]

        for classarm in arm_objs:
            for day in day_objs:
                self.Timetable_obj.unmap_day_from_arm(classarm, day)


    def map_arms_to_chunkfreq_details(self, selected_arms_list, iterable_from_gui):
        """ This method receives the dept and chunk details (freq and chunk) along with all the arms from the GUI.
        iterable_from_gui is a list of tuples (dept, freq, chunk). DEPTS WILL BE ADDED TO THE CLASS ARMS IN HERE """

        arm_objs = [self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", arm_fullname) for arm_fullname in selected_arms_list]
        # subj_freq_chunk = namedtuple("dept_freq_chunk", "dept frequency chunk")

        # 1. Morphe the iterable_from_gui list of tuples into a list of namedtuples to be used in the TimetableSorter
        total_frequency = 0
        for index, details in enumerate(iterable_from_gui.copy()):
            # dept is initially a string
            dept, freq, chunk = details
            total_frequency += freq
            # Get the real dept object for the dept variable
            dept = self.object_getter(self.Timetable_obj.list_of_departments, "full_name", dept)

            # Replace the items in the list of tuples (from the GUI) with the namedtuples
            # This is the iterable_from_gui in the TimetableSorter code
            iterable_from_gui[index] = subj_freq_chunk(dept, freq, chunk)


        # Add the courses in iterable_from_gui to the class arm
        self.iterable_from_gui = iterable_from_gui
        self.add_depts_to_selected_classarms(arm_objs_list=arm_objs, iterable_from_gui=iterable_from_gui)

    

    def get_arms_viable_table_data(self):
        """ Returns the arms_viable_table_data for every class arm to be used in the GUI """
        return [arm.get_arms_viable_table_data() for arm in self.Timetable_obj.list_of_school_class_arms]


# --------------------------------------------------------------------------------------------------------
# -------------------------- ASSIGN TEACHERS TO TEACH SUBJECTS IN CLASS ARMS -------------------------
    def auto_assign_teachers_to_arms(self):
        """ calls the Tt_models module and automatically assigns teacher to arm """
        if self._authorize_assign_op():
            assign_teachers = self.Timetable_obj.auto_assign_teachers_to_all_arms()
            self.Timetable_obj.can_packet = True
            return assign_teachers,


    def undo_assign_teachers_to_arms(self):
        """ Calls the Tt_models module to strips each class arm of its subject teacher """
        if self._authorize_assign_op():
            undo_assign = self.Timetable_obj.undo_assign_teachers_to_arms()
            self.Timetable_obj.can_packet = False
            return undo_assign,
       

# ---------------------------------------------------------------------------------------------------------
# ----------------------------------- PACKETING AND SORTING OPERATION -------------------------------------
    def packeting_repacketing(self):
        """ handles the 'packeting' and 'repacketing' of subject teachers into days of the week returns None if 
        prerequisites aren't met """
        # ...................................
        if self._authorize_packet_op():
            packet = self.TimetableSorter.packet_depts_into_arms_per_day()
            repacket = self.TimetableSorter.repacket_teachers()
            self.Timetable_obj.can_sort = True
            return packet, repacket


    def undo_packeting_repacketing(self):
        """ Handles undoing the packet_repacketing process """
        if self._authorize_packet_op():
            undo_packet_operation = self.TimetableSorter.undo_packeting()
            self.Timetable_obj.can_sort = False
            return undo_packet_operation,


    def algosort_handle_cleanup_periodmap(self, algorithm_text, ref_day, ref_arm):
        """ MEGA METHOD. Handles the sorting, handling displaced teachers, clean up and maps the result to arms' periods """
        if self._authorize_sort_op():
            ref_day_obj = self.object_getter(self.Timetable_obj.list_of_days, "full_name", ref_day.strip()) 
            ref_arm_obj = self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", ref_arm.strip())

            algosort = self.TimetableSorter.initial_algosort(algorithm_text, reference_day=ref_day_obj, reference_arm=ref_arm_obj)
            handle = self.TimetableSorter.handle_displaced_teachers()
            cleanup = self.TimetableSorter.clean_out_displaced_teachers()
            map_to_period = self.TimetableSorter.map_chunk_to_arms_periods()
            return algosort, handle, cleanup, map_to_period


    def create_sort_xtra_teachers_for_balance(self):
        """ Faciltitates the extra teachers needed if there were initially displaced teachers """
        xtra_teachers_for_balance = self.TimetableSorter.xtra_teachers_for_balance()
        map_to_period = self.TimetableSorter.map_chunk_to_arms_periods(beam_max_value=40, prev_max_value=60)
        map_to_teacher = self.TimetableSorter.map_finished_arm_chunk_dept_to_teacher()
        return xtra_teachers_for_balance, map_to_period, map_to_teacher


    def return_xtra_teachers_dict(self):
        """ Returns the dict of {dept: extra_teachers} """
        return self.TimetableSorter.xtra_teachers_dict


    def clear_out_jobless_teachers(self):
        """ Calls on the sorter object to clear out any teachers who does not teacher any class arm """
        self.TimetableSorter.clear_out_jobless_teachers()


    def undo_sort_operation(self):
        """ Returns a generator. Nullifies the sort operation. """
        undo_sort = self.TimetableSorter.unsort_operation_gen(beam_max_value=100)
        return undo_sort,


    # def undo_sort_packeting_func(self):
    #     """ Method (not generator) to undo sorting and packeting
    #     WHEN A MODELS IS ABOUT TO BE DELETED? """
        



# -----------------------------------------------------------------------------------------------------------
# ------------------ HANDLES THE 'ADVANCED' SECTION, WITH TEACHERS'SPACING ETC ------------------------------
    # def teachers_relative_spacing_per_algorithm(self, ref_day, ref_arm):
    #     """ Handles the inner function that calculates the teacher's spacing """
    #     # try:
    #     ref_day_obj = self.object_getter(self.Timetable_obj.list_of_days, "full_name", ref_day.strip()) 
    #     ref_arm_obj = self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", ref_arm.strip())
    #     self.TimetableSorter.calc_teachers_spacing_per_algorithm(ref_arm_obj, ref_day_obj)
        


#--------------------------------------------------------------------------------------------------------------- 
# ------------------ RESPOND TO THE DIALS TO LOAD PERIODS INTO FRAMES AFTER SORTING IS DONE --------------------
    def dial_value_to_index(self, dial_value, model_length, min_=1, max_=100):
        """ This function converts the value passed in from the QDial into the index (int) of the model_object """
        index = math.ceil(dial_value * model_length/(max_ - min_ + 1)) - 1
        return index

    def index_to_dial_value(self, index, model_length, min_=1, max_=100):
        """ Converts the value of the index to its QDial value on the GUI. Returns the QDial value """
        dial_value = math.floor((index + 1)*(max_ - min_ + 1)/model_length)
        return dial_value

    def model_list_for_dial(self, model_type_str, index=0):
        """ Makes ready a model_list, be it class arms or days. iIndex is 0 or 1 based on whether the object itself
        or its fullname shuld be returned """

        if "arms" in model_type_str.lower():
            param = "arms"
        elif "teacher" in model_type_str.lower():
            param = "teachers"
        elif "subject" in model_type_str.lower():
            param = "depts"
        elif "department" in model_type_str.lower():
            param = "faculties"
        else:
            param = "days"       
        return self.get_model_items(param)[index]


    def return_item_from_dial_value(self, by_day_or_arm_str, dial_val):
        """ Takes the dial value, does some things to it and returns the corresponding model item to it """

        # ------- HERE. CREATE A CAN_DISPLAY ATTRIBUTE ON THE TIMETABLE CLASS ITSELF TO HELP CHECK
        model_list = self.model_list_for_dial(by_day_or_arm_str)
        model_list_length = len(model_list)
        index = self.dial_value_to_index(dial_val, model_list_length, min_=1, max_=100)
        return model_list[index]

    # --------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------


    def load_period_frames(self, frame_from_gui, details_tuple):
        """ Loads the period frames (AFTER ALL THE SORTING IS DONE!) FOR A CHOSEN ARM OR DAY into the GUI_frame (here represented as 'frame_from_gui').
        details_dict is a tuple that contains [0] => "arm" or "day" (raw_string) and the [1] => model_item_full_name.
        the details_tule can only contain CLASSARM OR DAY objects. """

        model_type_str, model_item = details_tuple
        model_list = self.model_list_for_dial(model_type_str, index=1)
        try:
            model_object = self.object_getter(model_list, "full_name", model_item)
        except ValueError:
            # raise Tt_exceptions.SomethingWentWrong(f"No such model item exists")
            return
        
        frame_class = Tt_GuiExtras.PeriodsDisplayByArmFrame if isinstance(model_object, self.Timetable_obj.SchoolClassArm) else Tt_GuiExtras.PeriodsDisplayByDayFrame
        my_frame = frame_class(model_object, frame=None, spacing=6, padding=(2,2,2,2))
        return my_frame


    def loads_periods_frames(self, frame_from_gui, details_tuple):

        my_frame = self.load_period_frames(frame_from_gui, details_tuple)
        frame = my_frame.run()
        return frame,


    def yield_arm_or_days_period_data(self, model_type_str, model_item_str, match_item="Nil",beam_max_val=100):
        """ GENERATOR. This method retirves the period data (plus the identifier period, that is, the first period) in a generator to be used 
        in the thread workers. Match_item """

        # Get the list of model_objects using the mode_type_str("days" or "class arms")
        
        model_list = self.model_list_for_dial(model_type_str, index=1)
        try:
            model_object = self.object_getter(model_list, "full_name", model_item_str)
        except ValueError:
            raise Tt_exceptions.SomethingWentWrong(f"No such model item exists")

        # if the model object is a class_arm
        if isinstance(model_object, self.Timetable_obj.SchoolClassArm):
            # Get the length of the periods dictionary
            len_arms_periods_dict = len(model_object.periods)

            for count, (day, periods_list) in enumerate(model_object.periods.items(), start=1):
                day_periods = [day] + periods_list
                beamed_val = round(count * beam_max_val / len_arms_periods_dict)
                # print("YIELD FOR SCHOOL CLASS ARM")
                yield beamed_val, tuple(day_periods)

        # If the model object is a day
        else:
            len_arms_today = len(model_object.school_class_arms_today)

            for count, classarm in enumerate(model_object.school_class_arms_today, start=1):
                arm_periods_list = [classarm] + classarm.periods[model_object]
                beamed_val = round(count * beam_max_val / len_arms_today)
                yield beamed_val, tuple(arm_periods_list)


    def get_kth_item_and_dial_value(self, model_type_str, model_item_fullname_str, k_val):
        """ gets the kth item of the list of objects of the model_type_str """
        
        model_list = self.model_list_for_dial(model_type_str, index=0)
        # Just return None and manage that in the method in the GUI file
        if not model_item_fullname_str in model_list:
            return
        # Add k in modulo form so it kth_item sweeps back and forth, but not exceeding the list, thus causing an error
        index_of_kth_item = (model_list.index(model_item_fullname_str) + k_val) % len(model_list)
        kth_item = model_list[index_of_kth_item]
        dial_value = self.index_to_dial_value(index_of_kth_item, len(model_list), min_=1, max_=100)

        return kth_item, dial_value


    def track_item_throughout_frame(self, model_item_str, mother_frame_widget, beam_max_val=100):
        """ Tracks the model_item_str in the bunch of frames to shown on the gui """

        # Loop through all the 
        len_widgets = mother_frame_widget.layout().count()

        for count, hor_frame in enumerate(mother_frame_widget.children(), start=1):
            # if this hor_frame widget is a frame (a horizontal frame)
            if type(hor_frame) == type(mother_frame_widget):
                # check through the children of each horizontal frame except the first one, i.e. the marker frame (for arm or day)
                # the '_' is for the period frame, but it is not used here
                for frame_item in hor_frame.children():
                    if type(frame_item) == type(hor_frame):
                        try:
                            # Try to match on any child frame -- only errors out on the first frame i.e. the marker frame (ArmFrame() instance)
                            period_frame_ui.match_and_colour_based_on_track(model_item_str)
                        except Exception:
                            pass

            beam_val = round(count * beam_max_val / len_widgets)
            yield beam_val


    def track_item_throughout(self, model_item_str):
        """ {day_fullname: (arm_full_name, period)}Tracks the model_item_str throughout the entire timetable (through the backend) """
        return model_item_str, self.TimetableSorter.track_model_item_thru_backend(model_item_str)



    def inch_cm_mm_convert(self, unit, max_coeff=1.5, min_coeff=0.5):
        """ Calcultates the max, min and the current value for 'val' given unit.
        useful for setting the widgets to set margin to docx reports. """
        key = unit[0].upper()
        max_val = round(max_coeff * self.conversion_constants_dict[key],2)
        min_val = round(min_coeff * self.conversion_constants_dict[key],2)
        curr_val = round(self.conversion_constants_dict[key],2)
        return max_val, min_val, curr_val



    def generate_timetable_file(self, file_path, format_, basis, margins_tuple):
        """ Handles generating the .docx, html or PDF files for the timetable. The 'basis' argument is what the report files will
        be based on, (days, class category or departments) and format is whether it is PDF, DOCX or HTML """
        print(f"Margins tuple in Manager: {margins_tuple}")
        if "docx" in format_.lower():
            report = Tt_docx_reports.Reporter(self.Timetable_obj, margins_tuple)
            report.runs_models_by_basis(basis, file_path, convert_to_pdf=False)

        elif "pdf" in format_.lower():
            report = Tt_docx_reports.Reporter(self.Timetable_obj, margins_tuple)
            report.runs_models_by_basis(basis, file_path, convert_to_pdf=True)

        elif "html" in format_.lower():
            Tt_html_reports.HTMLReporter(self.Timetable_obj, basis, file_path)
             

