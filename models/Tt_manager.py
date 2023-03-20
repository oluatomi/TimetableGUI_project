#--THIS MODULE HANDLES THE MANAGEMENT OF THE 'cls_pers' MODULE
#--THIS DOES NOT TAKE CARE OF THE ALGORITHM TO SORT, BUT PROVIDES VITAL INFORMATION
#--FOR THE MODULE THAT HANDLES THE ALGORITHM FOR SORTING.
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
from TIMETABLE.reports.Tt_docx_reports import Reporter


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
    """ This class serves as the intermediary between the GUI and the Tt_models and Tt_algo modules """

    def __init__(self, tt_obj=None):
        self.Timetable_obj = TimeTable() if not tt_obj else tt_obj
        self.TimetableSorter = TimetableSorter(tt_obj=self.Timetable_obj)
        self.object_getter = get_obj_from_param
        # In the event of an update to one of the arm or teacher, etc models, the pre_existing model to be edited
        self.pre_existing = None
        self.regex_time_pattern = "\d+:\d+:\d+"
        self.regex_position_pattern = "^(\d+,?)+$"

        # A dictionary, containing all the prequisites for the sorting process to be carried out (keys) and booleans as values
        self.prerequisites = {"assigned":False, "packeted":False, "sorted": False}

    
    # ---------------------------- SAVE AND LOAD FILES ---------------------------------
    def save(self, project_file_path):
        """ Pickles the timetable object into a file """
        self.Timetable_obj.save(project_file_path)


    def load_from_file(self, project_file_path):
        """ loads an existing timetable object from a .tmtb file """
        import os

        if os.path.exists(project_file_path) and os.path.splitext(project_file_path)[1] == ".tmtb":
            with open(project_file_path, 'rb') as file:
                tt_object = pickle.load(file)
            return tt_object


    def stash_general_info(self, info_dict):
        """ passes the general info details from the GUI to the timetable object and back """
        self.Timetable_obj.commit_general_info(info_dict)


    def get_general_info(self):
        """ Retrieves the general info details from the Timetable object, to pass on to the GUI """
        return self.Timetable_obj.get_general_info()


    def get_model_items(self, model_name):
        """ Returns list of type model_name from the timetable object. Model_name rendered in plural """
        if model_name in ["depts", "courses", "subjects"]:
            mod_list = self.Timetable_obj.list_of_departments
        elif model_name in ["class_groups", "class_cats", "class_categories"]:
            mod_list = self.Timetable_obj.list_of_school_class_groups
        elif model_name == "nonacads":
            mod_list = self.Timetable_obj.list_of_nonacad_depts
        elif model_name == "faculties":
            mod_list = self.Timetable_obj.list_of_faculties
        elif model_name in ["teachers", "staff"]:
            mod_list = self.Timetable_obj.list_of_all_teachers
        elif model_name in ["classes", "school_classes"]:
            mod_list = self.Timetable_obj.list_of_school_classes
        elif model_name in ["arms", "class_arms"]:
            mod_list = self.Timetable_obj.list_of_school_class_arms
        elif model_name == "days":
            mod_list = self.Timetable_obj.list_of_days
        else:
            raise ValueError(f"{model_name} not legal!!")

        # returns a tuple of the below
        return [item.full_name for item in mod_list], mod_list


    def get_object_from_list_by_fullname(self, model_name, object_fullname):
        """ Returns an object (arm, or dept, etc) from its list. serves as a substitute for self.object_getter. More suitable for functions
        that may call for objects outside this module """
        mod_list = self.get_model_items(model_name)[1]

        for obj in mod_list:
            if obj.full_name == object_fullname:
                return obj
        return ValueError(f"{object_fullname} not found in model list")


    # -------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------UTILITY FUNCTIONS ABOVE, MODEL FUNCTIONS BELOW -----------------------------------------------------------
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
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False

        pre_existing = self.pre_existing if update else None 
        self.Timetable_obj.create_faculty(faculty_name, HOD=HOD, description=description, update=update,preexisting_obj=pre_existing)


    def create_department(self, name, hos=None, is_parallel=False, faculty=None, A=1,T=1,P=1,G=1, update=False):
        #  ...
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False

        pre_existing = self.pre_existing if update else None
        hos = "Unspecified" if not hos else hos
        faculty_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", faculty)
        self.Timetable_obj.create_department(name, faculty=faculty_obj, hos=hos, is_parallel=is_parallel, A=A, T=T,P=P,G=G, preexisting_obj=pre_existing, update=update)



    def create_special_department(self, name, update=None):
        """ handles creation or update of a non-academic subject e.g. break-time """

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False
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
        self.prerequisites["assigned"] = False

        pre_existing = None if not update else self.pre_existing
        self.Timetable_obj.create_school_class_group(class_group_name, description=description, 
            abbrev=abbrev, update=update, preexisting_obj=pre_existing)


    def create_school_class(self, name, class_group, update=False):
        #  ...
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False
        
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
        #  ...
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        
        # self.prerequisites["assigned"] = False

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

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False
        #  ...

        teacher_obj_list = [self.object_getter(self.Timetable_obj.list_of_all_teachers, "full_name", teacher_) for teacher_ in teachers_list]
        for teacher in teacher_obj_list:
            self.Timetable_obj.del_teacher(teacher)


    # ------------ MAKING PERIODS AND STUFF IS NEXT!
    def create_day(self, day_name, rating=None, update=False):
        """ Creates (or updates) the day object """
        #  ...
        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False
        #  ...
        
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


    # -----------------------------------------------------------------------------------------
    # ----------------------------- PERIOD GENERATION SECTION ---------------------------------
    def add_days_to_selected_classarms(self, selected_arms_list=None, selected_days_list=None):
        """ This method add each of the days to each of the class arms in the arms_list """

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False
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

        #  set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False

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

        # print(f"nonacad_tuple_list: {nonacad_tuple_list}")


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


        # 2. Compile list of tuples bearing: (arm_fullnames, periods sum, frequency_sum, feasible)
        for arm in arm_objs:
            full_name = arm.full_name
            periods_sum = arm.period_count_total()
            frequency_sum = total_frequency
            feasible_bool = arm.total_period_contains_freq(total_frequency)
            feasible = str(feasible_bool)
            # An extra parameter to help colour the entry in the table
            feasible_colour = "#000" if feasible_bool else "#df0000"
            # populate the table_data list
            # table_data.append((full_name, periods_sum, frequency_sum, feasible, feasible_colour))

            # Now packet the "iterable_from_gui" into each arm if it is feasible, i.e. arm's number of periods can contain it
            if feasible_bool:
                # Store thids particulrs in the arm
                arm.store_iterable_from_gui(iterable_from_gui)
                arm.store_arms_feasible_table_data([periods_sum, frequency_sum, feasible, feasible_colour])

        # Add the courses in iterable_from_gui to the class arm
        self.iterable_from_gui = iterable_from_gui
        self.add_depts_to_selected_classarms(arm_objs_list=arm_objs, iterable_from_gui=self.iterable_from_gui)



    def get_arms_feasible_table_data(self):
        """ Returns the arms_feasible_table_data for every class arm to be used in the GUI """
        return [arm.get_arms_feasible_table_data() for arm in self.Timetable_obj.list_of_school_class_arms]



# --------------------------------------------------------------------------------------------------------
# -------------------------- ASSIGN TEACHERS TO TEACH SUBJECTS IN CLASS ARMS -------------------------
    def auto_assign_teachers_to_arms(self):
        """ calls the Tt_models module and automatically assigns teacher to arm """
        # First loads the teachers generators to produce teachers for assignment

        #  set the prerequisite[assigned] dict to True.
        
        # set prerequisite to assign teachers to True if both teachers and class arms exist
        if self.get_model_items("teachers")[0] and self.get_model_items("arms")[0]:
            self.prerequisites["assigned"] = True

        if self.prerequisites["assigned"]:
            self.Timetable_obj.load_teachers_from_all_depts(ascending=True)
            assign_teachers = self.Timetable_obj.auto_assign_teachers_to_all_arms()
            return assign_teachers,


    def undo_assign_teachers_to_arms(self):
        """ Calls the Tt_models module to strips each class arm of its subject teacher """

        if self.prerequisites["assigned"]:
            undo_assign = self.Timetable_obj.undo_assign_teachers_to_arms()
            return undo_assign,
        # set the prerequisite[assigned] dict to False, so sorting or packeting cannot be done
        self.prerequisites["assigned"] = False


    # ---to display details of class arm and assignec teacher snd frequency
    def get_arm_object(self, arm_cred):
        """ Returns tha arm object with full_name of arm_fullname.
        SPECIALLY FOR THE BUTTON THAT FINDS (pulls up) CLASS ARMS AND UPLOADS THEIR DETAILS TO THE TABLEWIDGET IN THE GUI """
        attr = "full_name" if isinstance(arm_cred, str) else "id"
        # in case the arm_cred does not match any teacher
        try:
            arm_obj = self.object_getter(self.Timetable_obj.list_of_school_class_arms, attr, str(arm_cred))
        except ValueError:
            raise Tt_exceptions.SomethingWentWrong(f"No class arm with ID: {arm_cred}")
        return arm_obj


# ---------------------------------------------------------------------------------------------------------
# ----------------------------------- PACKETING AND SORTING OPERATION -------------------------------------
    def packeting_repacketing(self):
        """ handles the 'packeting' and 'repacketing' of subject teachers into days of the week returns None if 
        prerequisites aren't met """

        self.prerequisites["packeted"] = True

        if self.prerequisites["packeted"] and self.prerequisites["assigned"]:
            # ....................................
            packet = self.TimetableSorter.packet_depts_into_arms_per_day(self.iterable_from_gui)
            # Repacket will be adjusted later
            repacket = self.TimetableSorter.repacket_teachers()       
            return packet, repacket


    def undo_packeting_repacketing(self):
        """ Handles undoing the packet_repacketing process """
        if self.prerequisites["packeted"]:
            undo_packet_operation = self.TimetableSorter.undo_packeting()
            return (undo_packet_operation,)

        self.prerequisites["packeted"] = False


    def algosort_handle_cleanup_periodmap(self, algorithm_text, ref_day, ref_arm):
        """ MEGA METHOD. Handles the sorting, handling displaced teachers, clean up and maps the result to arms' periods """

        # Sets the sorted prerequisite to True, so we can sort
        self.prerequisites["sorted"] = True

        # If requirements for assignment, and packeting and sorting are all in place...
        if self.prerequisites["assigned"] and self.prerequisites["packeted"] and self.prerequisites["sorted"]:

            ref_day_obj = self.object_getter(self.Timetable_obj.list_of_days, "full_name", ref_day.strip()) 
            ref_arm_obj = self.object_getter(self.Timetable_obj.list_of_school_class_arms, "full_name", ref_arm.strip())

            algosort = self.TimetableSorter.initial_algosort(algorithm_text, reference_day=ref_day_obj, reference_arm=ref_arm_obj)
            handle = self.TimetableSorter.handle_displaced_teachers()
            cleanup = self.TimetableSorter.clean_out_displaced_teachers()
            map_to_period = self.TimetableSorter.map_chunk_to_arms_periods()

            return algosort, handle, cleanup, map_to_period


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
        # only do this if all prerequisites have been met, i.e. every item in the dictionary reads 'True'.
        # By doing the above, teachers and class arms would already have been created
        if all(self.prerequisites.values()):
            model_list = self.model_list_for_dial(by_day_or_arm_str)
            model_list_length = len(model_list)
            index = self.dial_value_to_index(dial_val, model_list_length, min_=1, max_=100)
            return model_list[index]


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
            # Gethe length of the periods dictionary
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


    def generate_timetable_file(self, file_path, format_, basis):
        """ Handles generating the .docx, html or PDF files for the timetable. The 'basis' argument is what the report files will
        be based on, (days, class category or departments) and format is whether it is PDF, DOCX or HTML """
        
        if "docx" in format_.lower():
            report = Reporter(self.Timetable_obj)
            report.runs_models_by_basis(basis, file_path, convert_to_pdf=False)

        elif "pdf" in format_.lower():
            report = Reporter(self.Timetable_obj)
            report.runs_models_by_basis(basis, file_path, convert_to_pdf=True)
            
