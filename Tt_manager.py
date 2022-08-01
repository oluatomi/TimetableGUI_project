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
        raise ValueError(f"No item has what you checked for.")




class TimeTableManager:
    """ This class serves as the intermediary between the GUI and the TimeTable (cls_pers) module """

    def __init__(self, time_t_obj = None):
        self.Timetable_obj = TimeTable() if not time_t_obj else time_t_obj
        self.object_getter = get_obj_from_param

    def create_faculty(self, faculty_name, HOD="Esteemed HOD Sir/Ma'am", description=""):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.create_faculty(faculty_name, HOD=HOD, description=description)
        # print(f"This is the fac_list{self.Timetable_obj.list_of_faculties}")


    def edit_faculty(self, id,new_faculty_name, HOD="Esteemed HOD Sir/Ma'am", description=""):
        ##  ... use the 'get_object_from_param' method to get the faculty object with the id
        #  ...
        #  ...
        fac_obj.name = new_faculty_name
        fac.HOD = HOD
        fac.description = description

    def remove_faculty(self, id):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method removes all sorts of departments, special or not.
        #  ...
        self.Timetable_obj.del_faculty(dept_obj)

    def create_department(self, name, faculty=None, A=1,T=1,P=1,G=1):
        #  ...
        #  ...
        #  ...
        faculty_obj = self.object_getter(self.Timetable_obj.list_of_faculties, "full_name", faculty)
        self.Timetable_obj.create_department(name, faculty=faculty_obj, A=A, T=T,P=P,G=G)



    def create_special_department(self, name):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.create_department(name, is_special=True)


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



    def create_school_class_group(self,class_group_name, description="Houses school classes of like properties", abbrev=""):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.create_school_class_group(class_group_name, description=description, abbrev=abbrev)


    def edit_school_class_group(self, id, class_group_name, description="None given for now",abbrev="Jnr, Snr High"):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method EDITS all sorts of departments, special or not.
        #  ...
        sch_class_group_obj.class_group_name = class_group_name
        sch_class_group_obj.description = description
        sch_class_group_obj.abbreviation = abbrev


    def remove_school_class_group(self, id):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.del_school_class_group(sch_clss_group_obj)



    def create_school_class(self, name, class_group):
        #  ...
        #  ...
        #  ...
        classgroup_obj = self.object_getter(self.Timetable_obj.list_of_school_class_groups, "full_name", class_group)
        self.Timetable_obj.create_school_class(name,classgroup_obj)


    def edit_school_class(self, id, sch_class_group_obj, level_iden=1):
        #  ... The "get_obj_from_list" method is called to get the department object with the id
        #  ... This method EDITS all sorts of departments, special or not.
        #  ...
        sch_class_obj.level = level_iden
        sch_class_obj.school_class_group = sch_class_group_obj


    def remove_school_class(self, id):
        #  ...
        #  ...
        #  ...
        self.TimeTable.del_school_class(sch_clss_obj)


    #-- ----SHOULD SCHOOL CLASS ARMS BE EDITABLE OR JUST DELETED OUTRIGHT?

    def generate_school_class_arms(self,class_fullname,frequency=1, as_alpha=True):
        #  ...
        #  ...
        #  ...
        school_class_obj = self.object_getter(self.Timetable_obj.list_of_school_classes, "full_name",class_fullname)
        for _ in range(frequency):
            self.Timetable_obj.create_school_class_arm(school_class_obj, as_alpha=as_alpha)


    def remove_school_class_arm(self, id):
        #  ... Removes school_class_arm objs whether named alphabetically or numerically.
        #  ...
        #  ...
        self.Timetable_obj.del_school_class_arm(sch_clss_group_arm)


    def generate_teachers(self, dept_fullname, frequency=1, teaching_days=None):
        #  ...
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

    def create_day(self,  day_name, rating=None):
        #  ...
        #  ...
        #  ...
        rating = rating - 1 if rating else None
        self.Timetable_obj.create_day(day_name, rating=rating)


    def remove_day(self, id):
        #  ...
        #  ...
        #  ...
        self.Timetable_obj.del_day(day_obj)


    def periods_schoolclassarm_per_day(self,day, sch_clss_arm):
        #  ...
        #  ...
        #  ...
        """Assigns the day to each class arm and its list of periods. Parameters are the day"""
        pass