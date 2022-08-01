# - ************************************************************************

# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA. APRIL, 2022.

# -- All rights (whichever applies) reserved!

# **************************************************************************


# Main module for class definition of classes(school)
# ------------------------------------------

from collections import namedtuple
from Tt_exceptions import ProjectExceptions
import string, datetime
from queue import Queue
import itertools

#-----------------------------------------------------------------------------------
# --------------------------- THE TIMETABLE OBJECT ITSELF ----------------------------
#-----------------------------------------------------------------------------------
class TimeTable:
    '''The universal set for all operations 
    with regard to the time-table operation code'''

    # Timetable_list = Queue(maxsize=30)
    Timetable_list = []

    def __init__(self):
        # TimeTable.Timetable_list.put(self)
        TimeTable.Timetable_list.append(self)

        # Lists of Depts, classes and periods to help keep score
        self.list_of_departments = []
        # list of non-academic departments e.g break
        self.list_of_nonacad_depts = []
        self.list_of_all_teachers = []

        self.list_of_school_class_groups = []
        self.list_of_school_classes = []
        self.list_of_school_class_arms = []
        self.list_of_faculties = []
        self.list_of_days = []
        self.fac_id, self.dept_id, self.nonacad_id,self.teacher_id, self.clsgroup_id,self.cls_id,self.self,self.clsarm_id,self.day_id = 0,0,0,0,0,0,0,0,0


    
# ----------------------------------------------------------------------------------------------
# ------------ METHODS FOR CREATING AND DELETING THE MODEL CONTAINERS
# ----------------------------------------------------------------------------------------------
    # *************************************************************
    # def general_delete(self, any_obj):
    #     """This method deletes all the instances of a particular 'any_obj' from everywhere
    #     it might be in the timetable project."""

    #     All_instances = itertools.chain(self.list_of_departments, self.list_of_faculties,self.list_of_school_class_groups,
    #         self.list_of_school_classes, self.list_of_school_class_arms, self.list_of_days, self.list_of_all_teachers)

    #     for obj in All_instances:
    #         if obj == any_obj:
    #             pass


    def create_faculty(self, faculty_name, HOD="Esteemed HOD Sir/Ma'am", description=""):
        """Creates a faculty to hold departments"""
        faculty = self.Faculty(faculty_name, HOD=HOD, description=description)
        self.list_of_faculties.append(faculty)

        # Give the faculty id
        self.fac_id += 1
        faculty.id = self.fac_id

        # Just for testing
        return faculty


    def del_faculty(self, faculty_obj):
        TimeTable.remove_from_list(self.list_of_faculties, obj=faculty_obj)


    def create_department(self, name, faculty=None, is_special=False, A=1,T=1,P=1,G=1,):
        '''A function to instantiate the department object'''

        # # --Below checks if the subject already existed
        # for dept in self.list_of_departments:
        #     if name.lower() == dept.dept_name.lower():
        #         raise ProjectExceptions.SubjectAlreadyExists()

        if not is_special:
            department = self.Department(name,faculty=faculty,is_special=is_special, A=A,P=P,T=T,G=G)
            self.list_of_departments.append(department)
            # Set this department's id
            self.dept_id += 1
            department.id = self.dept_id
            return department
        
        # Creating the "special" non-academic period
        department = self.Department(name, is_special=is_special)
        self.list_of_nonacad_depts.append(department)
        self.nonacad_id += 1
        department.id = self.nonacad_id


    def del_department(self, dept_obj):
        TimeTable.remove_from_list(self.list_of_departments,obj=dept_obj)


    def create_school_class_group(self, class_group_name, description='', abbrev=None):
        """
            This function instantiates the school_class_group, i.e. maybe Junior school 
            or Senior school
        """
        class_group = self.SchoolClassGroup(class_group_name, class_group_description=description, abbrev=abbrev)
        self.list_of_school_class_groups.append(class_group)

        self.clsgroup_id += 1
        class_group.id = self.clsgroup_id

        return class_group


    def del_school_class_groups(self, clss_gr_obj):
        TimeTable.remove_from_list(self.list_of_school_class_groups, obj=clss_gr_obj)


    def create_school_class(self, name, class_group_obj):
        """ This function creates a school class considering the school class group 
        whether 'Junior' or 'Senior' school """
        school_class = self.SchoolClass(name, class_group_obj)
        self.list_of_school_classes.append(school_class)

        self.cls_id += 1
        school_class.id = self.cls_id
        return school_class


    def del_school_class(self, sch_class_obj):
        TimeTable.remove_from_list(self.list_of_school_classes, obj=sch_class_obj)


    def create_school_class_arm(self, school_class_obj, as_alpha=True):
        """ This function creates the arm for the school class passed in
        
        The 'num_id' parameter is kinda like the '1' behind 'Jss 1'. Helps to identify the class
         """

        try:
            class_arm = self.SchoolClassArm(school_class_obj, as_alpha=as_alpha)
        except Exception:
            raise ProjectExceptions.ClassArmCannotBeMade("num_id or school_class object missing")
        else:
            self.list_of_school_class_arms.append(class_arm)

        self.clsarm_id += 1

        class_arm.id = self.clsarm_id
        return class_arm

    
    def del_school_class_arm(self, sch_class_arm):
        # Removes a school class from the list todays list of class arms
        TimeTable.remove_from_list(self.list_of_school_class_arms, obj=sch_class_arm)


    def create_teacher(self, dept_obj, teaching_days=None):
        """Hangles the creation of a teacher object under a department dept_obj (Under a course, not faculty)"""

        teacher = dept_obj._add_teacher(self)   
        #-- Add teacher to the list of all teachers
        self.list_of_all_teachers.append(teacher)
        # -- create a personal id attr for teacher. It is their index on the list of all teachers + 1

        self.teacher_id += 1
        teacher.id = self.teacher_id

        # Add teachers days to  the teacher
        for day_obj in teaching_days:
            teacher.add_day_to_teacher(day_obj)


    def del_teacher(self, teacher_obj):
        TimeTable.remove_from_list(self.list_of_all_teachers, obj=teacher_obj)


    def create_day(self, day_name, rating=None):
        """ This is the function to create the day instance, with day_id being a unique identifier 
        in case two or more days share the same name (in the case where the time-table spans more 
        than a week) """

        day = self.Day(day_name=day_name, rating=rating)
        # Update the sort_id attr with the self.day_sort_num

        # if day.sort_id is not None, that is rating has been assigned a number from spin_box in GUI
        if day.sort_id or day.sort_id == 0:
            self.list_of_days.insert(rating, day)
        # Else, if rating is none, simply append
        else:
            self.list_of_days.append(day)
        # Retrieve the day's id

        self.day_id += 1
        day.id = self.day_id


    def del_day(self, day_obj):
        TimeTable.remove_from_list(self.list_of_days, obj=day_obj)


    def create_period(self, start=None, day=None, end=None, sch_class_arm_obj=None, 
        dept_=None, is_fav=False, duration=None,  spot=None, title_of_fav=None):
        '''This creates the periods, both the usual and the special period
        
        dept_, sch_class_ represent the department object and the 
        school class object respectively, if none is specified, an object is expected.

        if your dept doesn't exist yet, you should call the function to make it first
        '''

        dept_obj, sch_class_arm_obj, day_obj = dept_, sch_class_arm_obj, day


        if not sch_class_arm_obj or not day_obj:
            raise ProjectExceptions().SubjectOrClassNotRegistered("Period cannot be created! school class or "
             "subject(department) or the Day is missing")


        if not is_fav:
            # checking if it is OR isn't a special period
            indiv_period = self.Period().normal_period(day_obj, start, duration, sch_class_arm_obj,dept_obj=dept_obj, end=end)
        else:
            indiv_period = self.Period().fav_period(day_obj, duration, spot=spot, start=start, dept_obj=dept_obj, 
                sch_class_arm_obj=sch_class_arm_obj, title_of_fav=title_of_fav)


        return indiv_period

    def del_period(self, day_obj, class_arm, index):
        """deeltes the period of a school class arm on a particular day"""
        period_list = class_arm.periods[day_obj]
        del period_list[index]


    def tt_save(self, project_name):
        """ This big-boy function will handle storing all the important info to a database.
        
        More on that later.

        Maybe a pickle file, really.

        """
        self.time_table_project_name = project_name
        self.todays_date = datetime.date.today()
        # ...
        # ...


    # --------------------------------------------------------------------------------------------------
    # ----------- METHODs TO CARRY OUT OPERATIONS BETWEEN THE AFOREMENTIONED CONTAINERS -----------------
    # --------------------------------------------------------------------------------------------------

    def get_class_arm_periods_today(self, day_obj, class_arm_obj):
        # Returns the periods of a calss arm for a particular day
        if class_arm_obj in self.list_of_school_class_arms:
            #-- Validate class arm object 
            return day_obj.get_one_sch_class_periods(class_arm_obj)


    def get_class_arm_periods_thru_week(self, class_arm_obj):
        """
            This method gets and returns all the periods of a given class arm for all the days in the week.
        """
        val = []
        for day in self.list_of_days:
            self.get_class_arm_periods_today(day, class_arm_obj)
        return val


    def dept_assigns_teacher_to_arm(self, dept_obj, class_arm):
        """This method does all the labour of assigning a teacher to a class arm.
        It notifies the teacher, dept and class arm objects of this and satisfies all of them
        accordingly, no trouble."""

        if class_arm in dept_obj.teachers_for_client_class_arms:
                # The generated teacher
                gen_teacher = dept_obj.assign_teacher(descent=False, auto=True, teacher_index=None)
                # Add this class and the teacher to the department's records

                dept_obj.teachers_for_client_class_arms[class_arm] = gen_teacher

                # Add the department and teacher to the class' records
                class_arm.depts_and_teachers[dept_obj] = gen_teacher

                # Add the class arm to the teacher's list of class arms they are teaching
                gen_teacher.classes_taught.add(class_arm)
        else:
            raise ProjectExceptions.SomethingWentWrong("Teachers could not be assigned to class arm")



    # ------------------------------------------------------------------------------
    # ---------- FUNCTION DEFINITIONS ABOVE AND CLASS DEFINITIONS BELOW ------------
    # ------------------------------------------------------------------------------

    class Faculty:
        """ Merely a container fir related departments(courses). On the gui, it is referenced as "Department" """
        def __init__(self, faculty_name, HOD="", description=""):
            self.name = faculty_name.capitalize()
            self.HOD = HOD
            self.id = 0
            self.description = f"Department of {self.name}" if not description else description
            self.course_list = []

        def add_dept_to_course_list(self, dept_obj):
            self.course_list.append(dept_obj)

        def remove_dept_from_course_list(self, dept_obj):
            self.course_list.remove(dept_obj)

        @property
        def full_name(self):
            """The full name of the faculty as will be shown in the app"""
            return f"DEPT. ID:{self.id}  {self.name}"

        @property
        def detailed_info(self):
            return f"""
            <ul>
            <li>Department name: {self.full_name}.\n </li>
            <li>Department headed by: {self.HOD}.\n </li>
            <li>Child Subject Number: {len(self.course_list)}.\n </li>
            <li>Description: {self.description} </li>
            </ul>
            """
        
        def delete(self, tt_obj):
            """This function deletes the instance of this class from the any of the lists that house it"""
            tt_obj.list_of_faculties.remove(self)



    class Department:
        '''This is the Course/Subject class, where teachers come from
        This is referenced as "SUBJECT/COURSE" in the GUI
        '''  
    
        def __init__(self, name, faculty=None,is_special=False, A=None, T=None, P=None,G=None):
            """This is the department class. It is the SCHOOL SUBJECT to be 
            handled. However, it might not be an academic_class. It just 
            could be recess or what we call a special class.

            The 'is_special' argument helps to identify if the class is or isn't
            a special class"""

            self.dept_name = name.title()
            self.is_special = is_special

            self.id = 0

            # Rating on how critical, mathematical or otherwise this department is
            # This numerical value will help sort the department in the list of other departments

            self.info = f"Special subject: {self.dept_name}"

            if not self.is_special:
                # Works if this department is academic and NOT "Special" as in recess or extracurriculars

                # self.HOD = HOD
                self.faculty = faculty

                # Add this department to the course_list of its faculty since it is not a special period
                self.faculty.add_dept_to_course_list(self)
                self.info = f"Name of subject: {self.dept_name}"


                # Very important list, DONT TOUCH!
                self.teachers_list=[]       


                # This is a dictionary of each class arm object (the key) and the teacher (the value) from this department handling it
                self.teachers_for_client_class_arms = {}

                # ---------------------------------------------------------------------
                # The descriptive attributes of the department (on how analytic, theoretical and such)
                # Numerical values are added to help sort the departments or the teachers that teach 
                # this course as the case may be
                self.analytic = A
                self.theoretical = T
                self.practical = P
                self.grammatical = G


            # -- This is_para attr is to test whether this department should always feature 
            # in the timetable alongside another department during the same period.
            self.is_para = False


        def dept_ATPG(self, analytic=3, theoretical=2, practical=3,grammatical=2):
            """This method handles the calculation of assigning a weight to the course by the elements in the course description.
            ATPG is merely an acronym for analytic, theoretical... """

            weight = self.analytic * analytic + self.theoretical * theoretical + self.practical*practical + self.grammatical*grammatical
            return weight
                

        def teachers_rating_list(self, desc=False):
            """ This function, by default, rates the teachers according to how many classes they teach in ascending order.
             Descending order when the 'desc' (for descending) parameter is set to True """

            if not self.is_special:
                rating = namedtuple("Teachers_rating", "teacher_obj classes_taught")
                rating_list = [rating(teacher, teacher.classes_count) for teacher in self.teachers_list]

                if not desc:
                    # Sorts the list in ascending order
                    rating_list.sort(key=lambda item: item.classes_taught)
                else:
                    # In the descending order
                    rating_list.sort(key=lambda item: item.classes_taught, reverse=True)

                return rating_list

            raise ProjectExceptions.IsASpecialDept("This special subject does not possess teachers' info ")
            


        def _add_teacher(self, tt_self):
            """ This function CREATES A TEACHER from scratch as a member of the department.
            The function that adds the teacher to the list of teachers in the department
            is built into the "Teacher class", and so is not necessary here. 
            tt_self is the currently instantiated Timetable object"""

            teacher = tt_self.Teacher(self)
            # Add this teacher to the department's list of teachers
            # self.teachers_list.append(teacher)

            return teacher


        def add_ready_made_teacher(self, teacher_obj):
            """This methods adds an ALREADY-MADE teacher object to the teachers_list.
            This really is adding a teacher from another department, e.g a futher maths teacher to teach math"""

            self.teachers_list.append(teacher_obj)

            # ADD A NEW TEACHER TO A DEPARTMENT IN THE TEACHER OBJECT!!
            

        def assign_teacher(self, descent=False, auto=True, teacher_index=None):
            '''This function assigns a teacher already in 
            the list to a class.
            It simply gives the teacher with the lowest class rating'''


            # To rearrange the teachers according to the ratings_list sorting
            if not self.is_special:
                if auto:
                    self.teachers_list = [x.teacher_obj for x in self.teachers_rating_list(desc=descent)]
                    
                    return self.teachers_list[0]
                else:
                    if teacher_index:
                        return self.teachers_list[teacher_index]

                # --- the function to assign teacher returns False if it is a special period
            return False
            

        def __repr__(self):
            return f"{self.dept_name}, ID:{self.id}"

        @property
        def full_name(self):
            return f"COURSE ID:{self.id}: {self.dept_name}"

        @property
        def detailed_info(self):
            style = """<style>
                ul li{
                margin:0px; 
                padding:0px;}
                </style>
            """
            return f"""
            <html>
            {style}
            <ul>
            <li>Subject/course ID and full name: {self.full_name}.\n </li>
            <li>Mother Department: {self.faculty.full_name}.\n </li>
            <li>This course, based on the nature of its contents scores <strong>{self.dept_ATPG()}</strong> on the ATPG-
            course structure scale.
            <p>N.B:This rating is not at all a judge of how effective or important a course is; that judgement is within the sole descretion
            of the school or Ministry of Education (or the presiding institution(s) involved). This rating simply helps sort the courses.</p></li>
            <li>Number of resident teachers: {len(self.teachers_list)}</li>
            </ul>
            </html>
            """
        


        # ---------------------------------------------------------
        # Pro-Tip: first add a classarm using the function below before assigning a teacher
        # using the function below below

        def add_arm_to_dept(self, class_arm):
            """ To add a school class arm to the set of departments (client_classes) of the department """
            # below is a dictionary with 'arm' as key and 'teacher' as value
            self.teachers_for_client_class_arms[class_arm] = None


        def remove_arm_from_dept(self, class_arm):
            """Removes a class arm from a department. along with the teacher!"""

            del self.teachers_for_client_class_arms[class_arm]


        def assign_teachers_to_all_arms(self):
            """ This method makes sure teachers are assigned to all the depts in the class_arms. 
            (Those to whom teachers have been assigned yet)

            Should be called only when absolutely needed
            """

            for arm, teacher in self.teachers_for_client_class_arms.items():
                if not teacher:
                    # Assigns teacher to a class arm if it previously hadn't a teacher
                    self.assign_teacher_to_arm(arm)

            # Just to be sure
            return self.teachers_for_client_class_arms


        def remove_teacher_from_dept(self, teacher_obj):
            """Removes a teacher object from the department!"""

            self.teachers_list.remove(teacher_obj)

        def delete(self, tt_obj):
            """This function deletes the instance of this class from the any of the lists that house it"""
            tt_obj.list_of_departments.remove(self)
            self.faculty.course_list.remove(self)



    class Teacher:
        '''The teacher object which is in composition
        with the department object, i.e, "teacher has a department"
        he is from'''
        def __init__(self, dept_obj):

            self.id = 0

            self.teachers_department_list = [dept_obj]
            # self.teachers_department_set = set(self.teachers_department_list)


            # -------------------------------------------------------------------------------------------
            # -- Upon initialization, only one dept object is given thus teacher 
            # -- instance is given to its list of teachers

            self.teachers_department_list[0].add_ready_made_teacher(self)
            # the above stores the current teacher in the array of its department for easy referencing

            # SHOULD I USE A SET FOR THIS?
            # Used a set!
            self.classes_taught = set()

            # The set containing the days in which the teacher can teach
            self.teaching_days = []

        @property
        def teaching_days_s(self):
            # Returns the set form if the teaching day attr, so as to eradicate duplicates
            return set(self.teaching_days)

        @property
        def str_teacher_depts(self):
            """For GUI. This property method renders all the departments offered by the teacher as a string (for the GUI)"""
            return ", ".join([dept.full_name for dept in self.teachers_department_list])


        def str_teaching_days(self, tt_obj):
            """For GUI. This function checks if teacher teaches on all the registered days"""
            day_diff = set(tt_obj.list_of_days) - self.teaching_days_s

            if not day_diff:
                return "All"

            day_diff_list = [day.full_name for day in day_diff]
            return "All Except " ", ".join(day_diff_list)


        def regular_or_no(self, tt_obj):
            """Returns 'Regular' or 'Special' based on how many days taught."""
            reg_or_no = self.str_teaching_days(tt_obj)
            return "Regular" if reg_or_no == "All" else "Special"
        
        
           
        @property
        def classes_count(self):
            return len(self.classes_taught)


        @property
        def all_teacher_depts_id(self):
            # Get all the unique ids for the departments this oga is teaching as values 
            # and depts as keys

            self.teachers_dept_id = {dept: dept.id for dept in self.teachers_department_list}

            return self.teachers_dept_id


        def __repr__(self):
            return f"Teacher id: {self.id}"


        def add_dept_to_teacher(self, dept_obj):
            """Apparently, a teacher can teach in more than one department (e.g. math and further maths).
            This function adds a new unique department object to the list of departments owned by the teacher"""

            # -- To check to make sure no duplicates exist
            if dept_obj in self.teachers_department_list:
                raise ProjectExceptions().TeacherAlreadyGivenSaidSubject("Teacher has previously been assigned dept object")
            
            # To add this teacher to the list of teachers of the department that was added
            dept_obj.add_ready_made_teacher(self)
            
            # I CANT REMEMBER WHAT THE BELOW DOES
            # dept_obj.id_num += 1
            self.teachers_department_list.append(dept_obj)


        def remove_dept_from_teacher(self, dept_obj):
            """Removes a department object from the list of depts taught by the teacher"""

            # Remove dept from teachers list
            self.teachers_department_list.remove(dept_obj)

            # Remove teacher from the list of teachers of the department
            dept_obj.remove_teacher_from_dept(self)


        def add_day_to_teacher(self, day_obj):
            """Adds a day object (that already exists) to the 
            list of days in which the teacher can teach"""
            
            # the below used to be a set, but somewhere else in the code, the order of the days
            # is needed. sets do not preserve the order, so sets are no longer used
            
            if day_obj not in self.teaching_days:
                self.teaching_days.append(day_obj)


        def remove_day_from_teacher(self, day_obj):
            """Removes the day_obj from the self.teaching_days set"""
            self.teaching_days.remove(day_obj)

        @property
        def full_name(self):
            return f"ID: {self.id}. Member of staff"


        # ---------------------------------------
        def delete(self, tt_obj):
            """This function deletes the instance of this class from the any of the lists that house it"""
            tt_obj.list_of_all_teachers.remove(self)

            for dept in self.teachers_department_list:
                # remove teacher object
                dept.teachers_list.remove(self)


# ---------------------------------------------------------------------------------------
    class SchoolClassGroup:
        """ This py-class is the collection (container) of school classes of a certain kind.
        Could be thought of as the junior school or senior school which contains classes. """

        def __init__(self, class_group_name, class_group_description=None, abbrev=None):
            # -- the 'abbrev' parameter gives a short name for the school class group
            self.class_group_name = class_group_name.capitalize()
            self.description = class_group_description
            self.abbreviation = abbrev
            self.id = 0

            # -- contains all the school classes in the group
            self.school_class_list = []


        def remove_clss_from_clss_group(self, sch_clss):
            """ Removes a school class from the list held by the school class group """

            self.school_class_list.remove(sch_clss)
            

        def __repr__(self):
            return self.abbreviation if self.abbreviation else self.class_group_name

        @property
        def full_name(self):
            return self.__repr__()


        def delete(self, tt_obj):
            """This function deletes the instance of this class from the any of the lists that house it"""
            tt_obj.list_of_school_class_groups.remove(self)


    class SchoolClass:
        """ This class represents the school class.The 'level_iden' parameter implies that '1' might
         represent 'jss 1' and so on.
         """

        def __init__(self, name, school_class_group_obj):

            self.level = str(name).capitalize()
            self.school_class_group = school_class_group_obj
            self.school_class_arm_list = []
            self.school_class_group.school_class_list.append(self)
            self.id = 0
            

        @property
        def get_school_class_name(self):
            return f"{self.school_class_group.__repr__()}_{self.level}"


        def remove_arm_from_class(self, class_arm):
            """By default the class arm is added to the the school class upon initialisation.
            This function removes any class arm of choice!"""

            try:
                # in case the list is empty or the class arm isnt there
                self.school_class_arm_list.remove(class_arm)
            except Exception:
                pass

        def __repr__(self):
            return self.get_school_class_name + " object"

        @property
        def full_name(self):
            return f"Class ID: {self.id}. {self.school_class_group.full_name} - {self.level}"
        

    class SchoolClassArm:
        """ This class models every arm that a school class has. It can represent the arms 
        with letters or numbers.
        The 'as_alpha' parameter controls this. short for 'is_a_letter_of_the_alphabet' """

        def __init__(self,school_class_obj, as_alpha=True):

            # if as_alpha:
            #     self.arm_id = string.ascii_letters[int(num_id)].capitalize()
            # else:
            #     self.arm_id = num_id + 1

            self.school_class = school_class_obj
            self.id = 0

            # --A dictionary of all the periods for every day (the dict has a key-value pair of the day_obj: list of periods)
            self.periods = {}
            self.period_id_counter = {}
            self.school_class.school_class_arm_list.append(self)

            self.local_identifier = self.school_class.school_class_arm_list.index(self)

            if as_alpha:
                self.local_id = string.ascii_letters[self.local_identifier].capitalize()
            else:
                self.local_id = self.local_identifier + 1


            # -- This is the list of departments (str) that the school class arm offers
            self.depts_and_teachers = {}

            # --- Tentative dictionary (below) to hold the list of subjects offered per day
            #  'day' is the key and the list of subjects is the value. It is first put as None for ease
            self.temp_dept_holder_for_days = {x:None for x in self.get_class_arm_days}

            #-------------------------------------------------------- 
            # container for when a dept has been actively assigned 
            self.depts_assigned_by_algo_per_day = {}


        @property
        def full_arm_name(self):
            return f"{self.school_class.get_school_class_name} {self.local_id}"


        @property
        def get_class_arm_days(self):
            """Returns every school day for which the class runs"""
            
            days_for_classarm = [day for day in self.periods]
            days_for_classarm.sort(key=lambda day: day.rate_with())
            return days_for_classarm
        

        def add_dept_to_class_arm(self, dept_obj, descent=False, auto=True, teacher_index=None):
            """ Adds to the dictionary the department as the key and the teacher object as the value.
            The teacher is first set None.
            The 'get_teacher_for_department_in_arm method' is called to assign the teacher given by 
            the department to this subject for this class.

            This adds a new subject for learning to the class arm """

            if dept_obj in self.depts_and_teachers.keys():
                pass
            else:                
                # Now register the assigned teacher with the class arm
                self.depts_and_teachers[dept_obj] = None


        def remove_dept_from_class_arm(self, dept_obj):
            """ Removes a subject from the subjects stored by the class arm """

            del self.depts_and_teachers[dept_obj]


        def get_teacher_for_department_in_arm(self, dept_obj):
            """ The dept_obj is called to assign a teacher for the class_arm """

            dept_obj.add_arm_to_dept(self)
            # use the dept obj to assign a teacher to this class arm
            dept_obj.assign_teacher_to_arm(self, descent=False, auto=True, teacher_index=None)

            self.depts_and_teachers[dept_obj] = dept_obj.teachers_for_client_class_arms[self]


        def para_departments(self, *dept_names):
            """This method handles a group of two more departments in which one class occur simultaneously 
            as an alternative to the other"""

            # -- this is a tuple holding the para-departments

            # ----------------------------------------------------------------------------------
            #  I'D RATHER THINK OF IT AS TWO DEPARTMENTS ACTING AS ONE, THOUGH WITH TWO TEACHERS BUT THE TEACHER OF THE FIRST
            # GOES WITH THE TEACHER OF THE SECOND.

            self.para_depts = str(dept_names).strip("()")
            # --more on this later


        def all_teachers_for_class_arm(self):
            """ Returns a set of all the teachers teaching this particular arm
            from the self.depts_and_teachers attribute """

            return {teacher for teacher in self.depts_and_teachers.values()}


        def depts_offered_and_weights(self):
            """This function returns every subject/dept offered by the class arm 
            and how many periods(weights or frequencies, if you prefer) that they 
            take up for each per week """
            
            weight_dict = {}

            for dept in self.departments_offered:
                weight_dict[dept] = 0
            return weight_dict
            

        def add_algoassigned_dept_today(self, dept_obj, day_obj):
            """ Method ädds all department objects (subjects) that the algorithma assigns to 
            this class for today """

            if day_obj in self.depts_assigned_by_algo_per_day:
                # if day obj is in the dict, add dept to the already made set
                self.depts_assigned_by_algo_per_day[day_obj].add(dept_obj)
            else:
                # else create the set afresh
                self.depts_assigned_by_algo_per_day[day_obj] = {dept_obj}


        def remove_algoassigned_dept_today(self, dept_obj, day_obj):
            """This method removes a department from the container the algorithm assigns depts into or whaterver!"""
            try:
                self.depts_assigned_by_algo_per_day[day_obj].remove(dept_obj)
            except Exception:
                raise ValueError(f"{dept_obj} cannot be removed from the set !!")


        def __repr__(self):
            return self.get_full_arm_name

        @property
        def full_name(self):
            return f"Arm ID:{self.id}. {self.full_arm_name}"
        
        

    class Period:
        '''Model for every class period.
        it is owned by a school class ARM and has a teacher
        from a department (or not, if it is a special (favourite) period)'''

        def normal_period(self, day_obj, start, duration, sch_class_arm_obj, dept_obj=None, end=None):
            """   This is the model of a normal academic period  """

            # Just an attribute to indicate that this is a special 'favourite' period
            self.is_favourite = False


            # ------------------------------------------------
            self.subject = dept_obj # the department (subject)

            self.day = day_obj  # the day of the week, or the time period

            self.school_class_arm = sch_class_arm_obj
            self.teacher = None if not self.subject else self.subject.assign_teacher()
            # Doing this because it's very possible for the period to be free (without a department handling it!)

            # Add the class to the list of classes taught by the teacher
            if self.subject:
                self.teacher.classes_taught.append(self.school_class_arm)

                # -- The below is to register the class arm as one of the classes taught by the department
                # -- This could have been extracted from the teacher.classes_taught of each teacher in the department
                # -- But, what if the department (maybe break time e.g) has no teacher? its class arms would still need to be recorded
                self.subject.client_classes.add(self.school_class_arm)


                # -- adds the subject to the list of subjects taken by the class arm
                self.school_class_arm.list_of_all_subjects.append(self.subject)

            self.start = start  # The start time for the period


            if duration:
                # -- if duration is given, calculate the end from the duration
                self.duration = duration
                self.end = TimeTable.add_sub_time(start, duration)

            elif end:
                # -- if duration isn't given but end is

                self.end = end  # The end time for the period
                self.duration = TimeTable.add_sub_time(self.end, self.start, add=False)
                
            # self.school_class_arm.periods.append(self)

            self.day.school_class_arms_today.add(self.school_class_arm)

            self.period_name = f"'{self.subject.dept_name}' period for {self.school_class_arm}" if self.subject else "Free Period"
            

            self.add_to_armses_periods()

            # -- Update the period counter of the school_class arm
            # self.school_class_arm.period_id_counter += 1

            self.period_id = self.school_class_arm.period_id_counter

            return self



        def fav_period(self, day_obj, duration, spot=None, start=None, dept_obj=None, sch_class_arm_obj=None, title_of_fav=None):
            """Short for 'favourite period'. This is a period which MUST occupy a 
            particular spot on the time-table. A static period.

            'end' is not given here. just the 'start' and 'duration' parameters are needed

            START has to be a time tuple.
            so also DURATION.
            """

            self.day = day_obj

            # Just an attribute to indicate that this is a special 'favourite' period
            self.is_favourite = True

            if spot:
                # Put the period in the (spot-1)th spot of the period list
                pass
            else:
                if not start:
                    raise ProjectExceptions.CannotAssignFavPeriod("Cannot assign special period. Parameters have not been met")
                else:
                    self.duration = duration if duration else (0,0,0)
                    self.start = start if start else (0,0,0)
                    self.end = TimeTable.add_sub_time(self.start, self.duration)
                    self.school_class_arm = sch_class_arm_obj

                    if dept_obj:
                        self.subject = dept_obj
                        self.teacher = self.subject.assign_teacher()

                        # --Add the class arm to the list of arms taught by the teacher
                        self.teacher.classes_taught.append(self.school_class_arm)

                        # -- The below is to register the class arm as one of the classes taught by the department
                        # -- This could have been extracted from the teacher.classes_taught of each teacher in the department
                        # --But, what if the department (maybe break time e.g) has no teacher? its class arms would still need to be recorded
                        self.subject.client_classes.add(self.school_class_arm)
                    else:
                        self.subject = title_of_fav if title_of_fav else "Special static period"
                    # self.school_class_arm.periods.append(self)
                    self.period_name = f"Specially for {self.school_class_arm}"

            self.add_to_armses_periods()
            # self.school_class_arm.period_id_counter += 1
            self.period_id = self.school_class_arm.period_id_counter

            self.day.school_class_arms_today.add(self.school_class_arm)
            return self


        @property
        def get_period_name(self):
            num_name = f"{self.day.day_name} - {self.school_class_arm.periods[self.day].index(self) + 1}"
            return f"Period_{num_name}: {self.period_name}"


        def __repr__(self):
            return self.get_period_name


        def add_dept_to_period(self, dept_obj):
            """ If the period was initially created free,and it was decided as an afterthought 
            to add a subject to it, i.e. make it an academic class, this function does the needful 
            of providing a teacher and all the other below-mentioned things. """
           
            if self.subject:
                return

            self.subject = dept_obj
            self.teacher = self.subject.assign_teacher() if self.subject.is_special else "Teacher not needed"
            self.teacher.classes_taught.append(self.school_class_arm)


        def add_to_armses_periods(self):
            """ Method to add this period object to the dictionary of the school_class_arm
            adds a period one at a time """

            #  To update the list of periods
            if self.day in self.school_class_arm.periods.keys():
                self.school_class_arm.periods[self.day].append(self)
            else:
                self.school_class_arm.periods[self.day] = [self]


            # To update the period counter
            if self.day in self.school_class_arm.period_id_counter.keys():
                self.school_class_arm.period_id_counter[self.day] += 1
            else:
                self.school_class_arm.period_id_counter[self.day] = 1


    class Day:
        """
            This class represents all the days for which the timetable runs. This could be 5 days (
            the standard for schools) or other. 

            The 'rating' parameter in the init method is to help rank
            the objects of this class
        """
        
        def __init__(self, day_name="monday", rating=None):
            self.day = day_name.capitalize()
            # dummy value for id (has been changed in run-time)
            self.id = 0

            # This var below helps to sort the day in the list of days especially when rating is not None
            self.sort_id = rating

            self.school_class_arms_today = set()


        @property
        def arms_today_list(self):
            # Attribute to return the set of arms today in a list
            return list(self.school_class_arms_today)
        

        def add_sch_class_arm(self, clss_arm_obj):
            """ This function adds a schoolclass arm to the list held by the day object"""

            self.school_class_arms_today.add(clss_arm_obj)

            # -- Add the day object to the classarms list of periods
            if clss_arm_obj.periods[self] in clss_arm_obj.periods.keys():
                return

            # Add this day (as the key) to the periods dictionary of the class arm along with the list of periods
            # as the value
            clss_arm_obj.periods[self] = []


        def remove_sch_class_arm(self, clss_arm_obj):
            """Removes a school class arm from the records of the day object"""

            self.school_class_arms_today.remove(clss_arm_obj)

            # Remove the day object from the dictionary of the class arm along with the list of periods.

            del clss_arm_obj.periods[self]


        def get_one_sch_class_periods_for_today(self, class_arm_obj):
            """This function squeezes out all the periods for a 
            particular class arm today """

            return class_arm_obj.periods[self]
                        

        def all_sch_class_periods_for_today(self):
            '''This function squeezes out every period for every school class arm that has been instantiated.
            by going through the school class list and finding out every period associated with 
            that school class (that has already been instantiated) for that day and putting it into a dictionary
            with the key as the class_arm and the value as the list of periods today.
            '''
            classes_period_dict = {clss: self.get_one_sch_class_periods_for_today(clss) for clss in self.school_class_arms_today}
            return classes_period_dict


        def periods_per_class_arm(self, class_arm_obj):
            """ This method gets all the periods associated with a particular class arm """

            return {class_arm_obj: class_arm_obj.periods[self]}


        def get_depts_of_arm_today(self, class_arm, duplicate=True):
            """ Gets all the depts for today for a class arm
            if duplicate is False, it returns a list of a set of a list of the depts today"""

            return class_arm.temp_dept_holder_for_days[self] if duplicate else list(set(class_arm.temp_dept_holder_for_days[self]))


        def get_all_depts_today(self, duplicate=True):
            """ 
            This method gets all the assigned dept objs (from the chunk algorithm) for today
            in every class arm in the list (or dictionary) of today's classes
            Duplicate being true is for whether the depts appear according to thier chunk frequency or just uniquely
            """
            
            # List containing all the depts assigned by the algorithm used to packet depts into days
            all_depts = []

            for arm in self.school_class_arms_today:
                all_depts.extend(self.get_depts_of_arm_today(arm, duplicate=duplicate))

            return all_depts
            

        def get_arm_teachers_today_from_depts_assgn(self, clss_arm):
            """ When the chunk algorithm has been carried out and depts have been assigned to a day,
            This method extracts all the teachers that teach those depts today in the class arm """


            # returns all the teacher_objs associated with all the depts for a class arm

            # Maybe i should return a dictionary of teachers depts
            # Teacher is the key with depts (list) is the value
            # Yup! I did.

            teach_assgn_today = {}

            # the items in the below (a set, by the way) are intances of the DeptEncase class
            depts_today = self.get_all_depts_for_today()

            for dept in depts_today:
                teacher = dept.teachers_for_client_class_arms[clss_arm]

                # In the event that there is already a subject that has the teacher teaching it
                # (from another dept obviously), add it to the list
                if teacher in teach_assgn_today:
                    teach_assgn_today[teacher].append(dept)
                else:
                    teach_assgn_today[teacher] = [dept]


            # Returns a dictionary of the teacher (key) today and the list of dept (value) from which he comes
            return teach_assgn_today


        def get_all_teachers_today_from_depts_assgn(self):
            """
            gets all the assigned teachers (from the algorithm) from all the class_arms.
            it does so by calling the 'self.get_arm_teachers_today_from_depts_assgn' method (which happens on
             a class arm) on all the class arms
             """

            # A set is used here to avoid duplicates
            all_teachers = set()

            for arm in self.school_class_arms_today:
            # get teacher for each arm
                for teacher in self.get_arm_teachers_today_from_depts_assgn(arm):
                    all_teachers.add(teacher)

            # Returns just a set of all the teachers today
            return all_teachers


        def get_all_teachers_and_dept_dupli(self):
            """
                This method gets into a DICT all the teachers(keys) and all the (depts they teach and the arm)(values)
                considering all the duplicates.
            """
            
            teach_dept_dupli = {}

            # depts_today = self.get_all_depts_for_today()

            # every dept that features today
        

            for arm in self.school_class_arms_today:

                # For each dept in the container (dict) of the departments that were assigned to today by the packeting algorithm
                for dept in arm.temp_dept_holder_for_days[self]:
                    
                    teacher = dept.teachers_for_client_class_arms[arm]

                    # Now add teacher into the dictionary, but first check if it already exists
                    if teacher in teach_dept_dupli:
                        teach_dept_dupli[teacher].append((dept, arm))
                    else:
                        teach_dept_dupli[teacher] = [(dept, arm)]

            # finally return the dictionary with teachers (as keys) and the list of depts[as values]
            # for every class arm that features today

            return teach_dept_dupli



        def get_unique_teachers_depts_tday_assgn(self):
            """
            Returns a dictionay
            Gets all the teachers who teach today (key) and the depts they teach(values)
            Does not allow for duplicates. """


            # First get the teacher-deptlist dictionary from the first class arm today and update with the rest

            all_teachers_tday = {}

            for arm in self.school_class_arms_today:

                for dept in arm.temp_dept_holder_for_days[self]:
                    
                    teacher = dept.teachers_for_client_class_arms[arm]

                    # Now add teacher into the dictionary, but first check if it already exists
                    if teacher in all_teachers_tday:
                        all_teachers_tday[teacher].add((dept, arm))
                    else:
                        all_teachers_tday[teacher] = {(dept, arm)}

            

            # finally return the dictionary with teachers (as keys) and the list of depts and arms[as values]
            # for every class arm that features today

            return all_teachers_tday
            


        def get_all_teachers_for_today_from_periods(self):
            """ Extracts all the teacher objects from the departments offered of each school class arm 
            in the list of school class arms for today.

            It does this by sniffing through every period of said class arms and picking the teacher from there.
            This will not work if teachers if teachers havent already been sorted into periods per class arms.

            Hence, another method is defined (above) to extract teachers without sniffing through every period today."""

            today_teachers = []

            for arm in self.school_class_arms_today:
                for period in arm.periods[self]:
                    m = None if period.is_favourite else period.teacher
                    today_teachers.append(m)

            return today_teachers


        def get_all_depts_for_arm_today(self, class_arm):
            """Gets all the departments offered by a particular class arm on this day
            (as assigned by the algorithm)"""

            return class_arm.temp_dept_holder_for_days[self]

        def get_all_teachers_and_depts_for_arm_today(self, class_arm):
            pass


        # def rate_with(self):
        #     # The rating or sort id param helps to sort the days, so as to hav them following a particular order
        #     return self.rating if self.rating else self.sort_id


        def __repr__(self):
            return self.day_name

        @property
        def full_name(self):
            return f"Day ID:{self.id}. {self.day}"


#------------------------------------------------------------------------------------------
# --------- Below are the static class functions, that help make some
# -- calculation or the other.
# -----------------------------------------------------------------------------------------

    def _remove_obj_from_list(list_obj, obj=None, id=None):
        """This function removes an object from the list given"""
        if obj:
            list_obj.remove(obj)
        else:
            del list_obj[int(id)]



    def _tuple_to_absolute(tuple, base):
        '''Important function to convert all the numbers in a 
        tuple, say a time tuple to an integer, based on a certain base.
        this could be used to convert a time tuple (hours, mins, secs) to 
        a integer in seconds.
        This function will be used in the classes (or methods defined above)'''

        tup_len = len(tuple)
        ans = 0
        for i, item in enumerate(tuple):
            ans += item*(base**(tup_len -1 -i))
        return ans


    def _add_sub_time(time_tuple1, time_tuple2, add=True):
        '''
        Adds or subtracts two (hour, minute, seconds) tuples.
        time_tuple1 always is a tuple, 

        However, time_tuple2 could
        be an integer or a tuple, depending on if it is an actual time
        (rendered as a tuple) or duration.

        WORKS FOR BOTH TIME DIFFERENCE (BETWEEN TWO TIME TUPLES) 
        AND TIME AND DURATION (TIME TUPLE AND AN INTEGER)!

        time_tuple2 is the duration for the period or whatever
        '''

        if isinstance(time_tuple2, tuple):
            time2 = TimeTable.tuple_to_num(time_tuple2, 60)
        else:
            time2 = time_tuple2
        # the above unpacks the tuple arguments.

        time1 = TimeTable.tuple_to_num(time_tuple1, 60)
        
        # The above converts the time to absolute time in 
        # seconds
        if add:
            time3 = time1 + time2
        else:
            time3 = time1 - time2
        # Adds or subtracts the time depending on the add argument
        return TimeTable.num_to_tuple(time3, 60)


    def _boundary_split_into_periods(start, end, n):
        '''To split a given duration of time into "n" periods
        START and END are tuples and are to be given in 
        24-hr format. the tuples should be populated with 
        (hour, minute, seconds) items.
        -------------------------------------------------
        '''
        lower_bound = TimeTable.tuple_to_num(start, 60)
        upper_bound = TimeTable.tuple_to_num(end, 60)

        interval = (upper_bound - lower_bound) // n

        period_interval_list = []
        indiv_time_bounds = namedtuple("boundary", "start end")

        start_iter = start
        
        for m in range(n):
            """ Primarily, this part adds the time interval the start to get 
            the end, and then the start updates to the end, so the next period begins 
            at the end of the first!
            """
            add_interval_tup = TimeTable.add_sub_time(start_iter, interval)

            #---- Adds the "interval tuple" to the start time tuple which is given as
            # one of the parameters to the function. It returns a time tuple.

            period_interval = indiv_time_bounds(start_iter, add_interval_tup)
            period_interval_list.append(period_interval)

            # -- update the start_iter variable with the end of the previous period below
            start_iter = add_interval_tup

        return period_interval_list
        
        
    def _to_base(num, base):
        '''Converts a number "num" to base "base"
        and renders it as a tuple of place values according to
        said base '''
        valid, ans_list, number = True, [], num % 86400
        
        while valid:
            if number == 0:
                valid = False
            else:
                ans_list.append(number % base)
                number = number // base

        ans_list.reverse()
        return tuple(ans_list)


    remove_from_list = staticmethod(_remove_obj_from_list)
    split_into_periods = staticmethod(_boundary_split_into_periods)
    add_sub_time = staticmethod(_add_sub_time)
    tuple_to_num = staticmethod(_tuple_to_absolute)  # takes in Time tuple, (h,m,s) as arg to yield number.
    num_to_tuple = staticmethod(_to_base) # Also time tuples
