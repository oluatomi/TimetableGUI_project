#--THIS MODULE HANDLES THE MANAGEMENT OF THE 'cls_pers' MODULE
#--THIS DOES NOT TAKE CARE OF THE ALGORITHM TO SORT, BUT PROVIDES VITAL INFORMATION
#--FOR THE MODULE THAT HANDLES THE ALGORITHM FOR SORTING.
#-- THE 'cls_pers' MODULE HANDLES THE OBJECTS 
#-- (MOSTLY), WITH ITS STATIC METHODS DOING SOME OF THE NEEDED (SMALL)
#--CALCULATIONS THAT ARE ALBEIT STILL NEEDED.
#--THOSE METHODS COULD HAVE BEEN PUT HERE, BUT I FEEL THEY SHOULD SHIP DIRECTLY WITH THE 'Tt_models'
#--MODULE -- THE MODULE THAT HANDLES THE TIMETABLE OBJECT.


# -- THIS IS THE OFFICIAL FORM OF THE TESTING_SETUP.PY MODULE


from Tt_models import TimeTable
from inspect import isfunction
import string



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
                if getattr(item, attr).lower() == param.lower():
                    return item
    else:
        raise ValueError(f"{param} not found. No item has what you checked for.")


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
class TimeTableManager:
    """ This class serves as the intermediary between the GUI and the TimeTable (cls_pers) module """

    def __init__(self, time_t_obj = None):
        self.Timetable_obj = TimeTable() if not time_t_obj else time_t_obj
        self.object_getter = get_obj_from_param
        # In the event of an update to a model, the pre_existing model to be edited
        self.pre_existing = None


    def create_faculty(self, faculty_name, HOD="Esteemed HOD Sir/Ma'am", description="", update=False):
        #  ...
        #  ...
        pre_existing = self.pre_existing if update else None 
        self.Timetable_obj.create_faculty(faculty_name, HOD=HOD, description=description, update=update,preexisting_obj=pre_existing)
        # print(f"This is the fac_list{self.Timetable_obj.list_of_faculties}")


    def remove_faculty(self, id):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method removes all sorts of departments, special or not.
        #  ...
        self.Timetable_obj.del_faculty(dept_obj)


    def create_department(self, name, hos=None, faculty=None, A=1,T=1,P=1,G=1, update=False):
        #  ...

        pre_existing = self.pre_existing if update else None
        hos = "Unspecified" if not hos else hos
        faculty_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", faculty)
        self.Timetable_obj.create_department(name, faculty=faculty_obj, hos=hos, A=A, T=T,P=P,G=G, preexisting_obj=pre_existing, update=update)



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



    def create_special_department(self, name, update=None):
        #  ...
        pre_existing = self.pre_existing if update else None
        self.Timetable_obj.create_department(name, is_special=True, update=update, preexisting_obj=pre_existing)


    def edit_department(self, id, name, HOD="HOD Sir/Ma'am"):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method EDITS all sorts of departments, special or not.
        #  ...
        dept_obj.name = name
        dept_obj.HOD = HOD


    def remove_department(self, id):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method removes all sorts of departments, special or not.
        #  ...
        self.Timetable_obj.del_department(dept_obj)



    def create_school_class_group(self,class_group_name, description="Houses school classes of like properties", abbrev="", update=False):
        """ Handles the creation or update of the school class group, i.e. school class category """

        pre_existing = None if not update else self.pre_existing
        self.Timetable_obj.create_school_class_group(class_group_name, description=description, 
            abbrev=abbrev, update=update, preexisting_obj=pre_existing)



    def remove_school_class_group(self, clssgroup_name):
        #  ...
        #  ...
        #  ...
        classgroup_obj = self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", clssgroup_name)
        self.Timetable_obj.del_school_class_group(classgroup_obj)


    def create_school_class(self, name, class_group, update=False):
        #  ...
        
        # label_iden is None when it is creation (and not update) of class
        pre_existing_obj = None if not update else self.pre_existing

        classgroup_obj = self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", class_group)
        self.Timetable_obj.create_school_class(name,classgroup_obj, update=update, preexisting_obj=pre_existing_obj)


    def remove_school_class(self, id):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.del_school_class(sch_clss_obj)


    #-- ----SHOULD SCHOOL CLASS ARMS BE EDITABLE OR JUST DELETED OUTRIGHT?

    def generate_school_class_arms(self,class_fullname,frequency=1, as_alpha=True, override=False):
        #  ...
        #  ...
        #  ...
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



    def generate_teachers(self, dept_fullname, frequency=1, teaching_days=None):
        #  ...
        #  ...
        dept_obj = self.object_getter(self.Timetable_obj.list_of_departments, "full_name", dept_fullname)

        # get all the teaching day objects
        teaching_days_list = [self.object_getter(self.Timetable_obj.list_of_days, "full_name", day_fullname) for day_fullname in teaching_days] 

        for _ in range(frequency):
            self.Timetable_obj.create_teacher(dept_obj, teaching_days=teaching_days_list)
            

    def generate_multidept_teachers(self, depts_list=None, frequency=1, teaching_days=None):
        """This function handles the generation of teachers from across many departments (courses)"""

        depts = [self.object_getter(self.Timetable_obj.list_of_departments, "full_name", dept_fullname) for dept_fullname in depts_list]

        for dept_fullname in depts_list:
            self.generate_teachers(dept_fullname, frequency=frequency, teaching_days=teaching_days)



    def remove_teacher(self, id):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.del_school_class_group(teacher_obj)


    # -- MAKING PERIODS AND STUFF IS NEXT!

    def create_day(self,  day_name, rating=None, update=False):
        #  ...
        #  ...
        
        pre_existing_obj = None if not update else self.pre_existing
        # The rating parameter helps to situate the day in te list of days
        rating = rating - 1 if rating else None
        self.Timetable_obj.create_day(day_name, rating=rating, update=update, preexisting_obj=pre_existing_obj)


    def remove_day(self, id):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.del_day(day_obj)


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


    def periods_schoolclassarm_per_day(self,day, sch_clss_arm):
        #  ...
        #  ...
        #  ...
        """Assigns the day to each class arm and its list of periods. Parameters are the day"""
        pass