# - ************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA. APRIL, 2022.
# -- All rights (whichever apply) reserved!
# --- OLUTOMI'S SHELVA
# **************************************************************************


# Main module for class definition of classes(school)
# ------------------------------------------

from collections import namedtuple
from . import Tt_exceptions, Tt_algo_calc
import string, datetime, itertools, math, pickle, time

#-----------------------------------------------------------------------------------
# --------------------------- THE TIMETABLE OBJECT ITSELF ----------------------------
#-----------------------------------------------------------------------------------
AUTHOR = "Oluwatomilayo Inioluwa OWOEYE"

class TimeTable:
    '''The universal set for all operations 
    with regard to the time-table operation code'''

    # Timetable_list = Queue(maxsize=30)
    Timetable_list = []

    def __init__(self):
        # TimeTable.Timetable_list.put(self)
        TimeTable.Timetable_list.append(self)

        # ----------- Information variables --------------------------
        self.institution = "None provided"
        self.director = "None provided"
        self.session_or_year = None
        self.acronym = None
        self.extra_info = ""
        self.logo_path = None
        # ------------------------------------------------------------

        # Lists of Depts , classes and periods to help keep score
        # List of subjects
        self.list_of_departments = []
        # list of non-academic departments e.g break
        self.list_of_nonacad_depts = []
        self.list_of_all_teachers = []

        self.list_of_school_class_groups = []
        self.list_of_school_classes = []
        self.list_of_school_class_arms = []
        self.list_of_faculties = []
        self.list_of_days = []

        self.fac_id, self.dept_id, self.nonacad_id, self.teacher_id = 0,0,0,0
        self.clsgroup_id, self.cls_id, self.self = 0,0,0
        self.clsarm_id, self.day_id = 0, 0
        
        # --- initialize the file path to which this timetable file will be saved
        self.project_file_path = ""

        # the actual file name of the project
        self.project_file_name = "Timetable_file (UNSAVED)"
# ----------------------------------------------------------------------------------------------
# ------------ METHODS FOR CREATING AND DELETING THE MODEL CONTAINERS
# ----------------------------------------------------------------------------------------------
    def commit_general_info(self, info_dict):
        """ Registers general information, i.e. name of institution, name of director, project acronym and whatnot
        the info_dict has the same keys as the attributes of this timetable. """

        for info, val in info_dict.items():
            setattr(self, info, val)


    def get_general_info(self):
        """ Retrieves the value of the general info attributes and sends them out to the manager """
        return {
        'institution':self.institution,
        'director':self.director,
        'session_or_year':self.session_or_year,
        'acronym':self.acronym,
        'extra_info':self.extra_info,
        'logo_path':self.logo_path
        }


    def create_faculty(self, faculty_name, HOD="Esteemed HOD Sir/Ma'am", description="", update=False, preexisting_obj=None):
        """Creates a faculty to hold departments"""
        if not update:
            faculty = self.Faculty(faculty_name, HOD=HOD, description=description)
            self.list_of_faculties.append(faculty)
            # Give the faculty id
            self.fac_id += 1
            faculty.id = self.fac_id
            # Just for testing
            return faculty
        preexisting_obj.name = faculty_name
        preexisting_obj.HOD = HOD
        preexisting_obj.description = description


    def del_faculty(self, faculty_obj):
        """ Remove this faculty from the list of all this timetable's faculties """

        self.list_of_faculties.remove(faculty_obj)
        # go through every dept object in its courselist and delete them too
        for dept in faculty_obj.course_list:
            self.del_department(dept)


    def create_department(self, name, faculty=None, hos=None, is_special=False, A=1, T=1, P=1, G=1, 
        update=False,is_parallel=False, preexisting_obj=None):
        '''A method to instantiate the department object'''
        if not update:
            if not is_special:
                department = self.Department(name,faculty=faculty, hos=hos, is_special=is_special, A=A,P=P,T=T,G=G, is_parallel=is_parallel)
                self.list_of_departments.append(department)
                # Set this department's id
                self.dept_id += 1
                department.id = self.dept_id
                return department
            
            else:
                # Creating the "special" non-academic period
                department = self.Department(name, is_special=is_special)
                self.list_of_nonacad_depts.append(department)
                self.nonacad_id += 1
                department.id = self.nonacad_id

        else:
            # To UPDATE pre_existing obj
            preexisting_obj.dept_name = name
            if not preexisting_obj.is_special:
                preexisting_obj.dept_name = name
                preexisting_obj.hos = hos
                preexisting_obj.arithmetic = A
                preexisting_obj.thoeretical = T
                preexisting_obj.practical = P
                preexisting_obj.grammatical = G


    def del_department(self, dept_obj):
        """ Handles the deletion of a dept (the course/subject) """
        self.list_of_departments.remove(dept_obj)
        
        for arm in dept_obj.teachers_for_client_class_arms:
            arm.remove_dept_from_class_arm(dept_obj)


    def del_nonacad_department(self, nonacad_obj):
        """ Handles deletion of a non-academic department e.g. break """
        self.list_of_nonacad_depts.remove(nonacad_obj)


    def create_school_class_group(self, class_group_name, description='', abbrev=None, update=False, preexisting_obj=None):
        """ This function instantiates the school_class_group, i.e. maybe Junior school 
            or Senior school or updates the fields of a preexisting class group object. """
        if not update:
            class_group = self.SchoolClassGroup(class_group_name, class_group_description=description, abbrev=abbrev)
            self.list_of_school_class_groups.append(class_group)

            self.clsgroup_id += 1
            class_group.id = self.clsgroup_id
            return class_group

        preexisting_obj.class_group_name = class_group_name
        preexisting_obj.description = description
        preexisting_obj.abbreviation = abbrev


    def del_school_class_group(self, clssgroup_obj):
        """ Handles the deletion of a class category (class group) """
        self.list_of_school_class_groups.remove(clssgroup_obj)

        # Delete all the school classes under it
        for sch_clss in clssgroup_obj.school_class_list:
            self.del_school_class(sch_clss)


    def create_school_class(self, name, class_group_obj, update=False, preexisting_obj=None):
        """ This function creates a school class considering the school class group 
        whether 'Junior' or 'Senior' school """

        if not update:
            school_class = self.SchoolClass(name, class_group_obj)
            self.list_of_school_classes.append(school_class)
            # Update class id counter
            self.cls_id += 1
            school_class.id = self.cls_id
            return school_class
        # Else
        preexisting_obj.level = name



    def del_school_class(self, sch_class_obj):
        """ Deletion of school classes """
        self.list_of_school_classes.remove(sch_class_obj)
        clss_group = sch_class_obj.school_class_group

        # Remove this class from its mother school class group
        clss_group.remove_clss_from_clss_group(sch_class_obj)

        # Delete every school class arm under it
        for arm in sch_class_obj.school_class_arm_list:
            self.del_school_class_arm(arm)



    def create_school_class_arm(self, school_class_obj, as_alpha=True):
        """ This function creates the arm for the school class passed in. The 'num_id'
        parameter is kinda like the '1' behind 'Jss 1'. Helps to identify the class
         """
        class_arm = self.SchoolClassArm(school_class_obj, as_alpha=as_alpha)
        self.clsarm_id += 1
        class_arm.id = self.clsarm_id
        self.list_of_school_class_arms.append(class_arm)
        return class_arm
    

    def del_school_class_arm(self, arm):
        # Removes a school class from the list todays list of class arms
        self.list_of_school_class_arms.remove(arm)

        # Delete this arm from the depts it offers which hold it in teachers_for_client_class_arms dict.
        for dept in arm.depts_and_teachers:
            del dept.teachers_for_client_class_arms[arm]

            # Also clear this arm from the list of arms taught by the teacher
            teacher = dept.teachers_for_client_class_arms[arm]
            teacher.classes_taught.remove(arm)



    def create_teacher(self, frequency=0, dept_objs_list=None, teaching_days=None, specialty=None, designation=None, update=False, preexisting_obj=None):
        """Hangles the creation of a teacher object under a department dept_obj (Under a course, not faculty)"""
        # -------------------------------------------------------------------------
        def _create_single_teacher():
            teacher = self.Teacher()   
            #-- Add teacher to the list of all teachers
            self.list_of_all_teachers.append(teacher)
            # -- create a personal id attr for teacher. It is their index on the list of all teachers + 1
            self.teacher_id += 1
            teacher.id = self.teacher_id

            # Add teachers days to  the teacher
            for day_obj in teaching_days:
                teacher.add_day_to_teacher(day_obj)

            teacher.specialty = specialty
            teacher.designation = designation
            return teacher
        # -----------------------------------------------------------------------------
        # -------------- OUTSIDE THE INNER FUNCTION ----------------------
        #--- WHEN CREATING TEACHER

        if not update:
            # dept_objs (in the args) is now a list of all the depts(subjects) the teacher teaches
            
            teachers_by_freq = [_create_single_teacher() for _ in range(frequency)]
            for dept in dept_objs_list:
                # Add this departments to the teacher if this
                if not dept.is_parallel:
                    # for _ in range(frequency):
                    for teacher_obj in teachers_by_freq:
                        # teacher = _create_single_teacher()
                        self.map_teacher_to_dept(teacher_obj, dept)

                else:
                    # if dept.is_parallel is set to True
                    for split_name in dept.parallel_names:
                        parallel_teachers_tuple = [_create_single_teacher() for _ in range(frequency)]
                        dept.add_teachers_tuple_to_parallel_dept(split_name, parallel_teachers_tuple)
                        for _teacher_ in parallel_teachers_tuple:
                            self.map_teacher_to_dept(_teacher_, dept)

                    # Reset the dept.teachers_list based on the teachers generated for the parallel dept
                    dept.adapt_teachers_list_for_parallel()
            return

        # -------- TO UPDATE TEACHER ----------
        # The preexisting teacher object ---
        preexisting_obj.teachers_depts_list = []
        preexisting_obj.teaching_days = []

        for course in dept_objs_list:
            preexisting_obj.add_dept_to_teacher(course)

        for tday in teaching_days:
            preexisting_obj.add_day_to_teacher(tday)

        preexisting_obj.specialty = specialty
        preexisting_obj.designation = designation
    # --------------------------------------------------------------------------------------

    def del_teacher(self, teacher_obj):
        """ Deletes a teacher object """
        self.list_of_all_teachers.remove(teacher_obj)

        for dept in teacher_obj.teachers_depts_list:
            dept.teachers_list.remove(teacher_obj)


    def create_day(self, day_name, rating=None, update=False, preexisting_obj=None):
        """ This is the function to create the day instance, with day_id being a unique identifier 
        in case two or more days share the same name (in the case where the time-table spans more 
        than a week) """

        if not update:
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
            return
        preexisting_obj.day = day_name


    def del_day(self, day_obj):
        """ Handles the deletion of day objects """
        self.list_of_days.remove(day_obj)

        # Clear out this day objects from the containers of all the arm that feature in it
        for arm in day_obj.school_class_arms_today:
            del arm.periods[day_obj]


    def create_period(self, start=None, day=None, end=None, duration=None, sch_class_arm_obj=None, is_acad=True, title_of_fav=None):
        '''This creates the periods, both the usual and the special period
        dept_, sch_class_ represent the department object and the 
        school class object respectively, if none is specified, an object is expected.
        if your dept doesn't exist yet, you should call the function to make it first
        title_of_fav is the nonacademic OBJECT'''
        return self.Period(day, sch_class_arm_obj, start, end=end, duration=duration, is_acad=is_acad, title_of_nonacad=title_of_fav)


    def del_period(self, day_obj, class_arm, index):
        """deeltes the period of a school class arm on a particular day"""
        period_list = class_arm.periods[day_obj]
        del period_list[index]


    def save(self, project_file_path):
        """ This big-boy function will handle storing all the important info to a file.
        More on that later. Maybe a pickle file, really.
        """
        import os

        self.project_file_path = project_file_path + ".tmtb" if not project_file_path.endswith(".tmtb") else project_file_path
        self.todays_date = datetime.date.today()

        with open(self.project_file_path, "wb") as file:
            # dump this timetable object into the file
            pickle.dump(self, file)

        self.project_file_name = os.path.basename(self.project_file_path)
    


    # --------------------------------------------------------------------------------------------------
    # ----------- METHODs TO CARRY OUT OPERATIONS BETWEEN THE AFOREMENTIONED CONTAINERS -----------------
    # --------------------------------------------------------------------------------------------------
    def set_ATPG_parameters(self, analytic_tuple, theoretical_tuple, practical_tuple, grammatical_tuple):
        """ Sets the ATPG values to the new user-specified values. tuple contains (int_val, parameter_name) """
        for dept in self.list_of_departments:
            dept.analytic_parameter = analytic_tuple
            dept.theoretical_parameter = theoretical_tuple
            dept.practical_parameter = practical_tuple
            dept.grammatical_parameter = grammatical_tuple


    def map_dept_to_arm(self, classarm, dept, freq, chunk):
        """ This method adds a  dept to a class arm and does all the registration and stuff """
        classarm.add_dept_to_class_arm(dept)
        # Also record the chunk and freq values at once
        classarm.add_dept_details_to_class_arm(dept, freq, chunk)
        dept.add_arm_to_dept(classarm)


    def unmap_dept_from_arm(self, classarm, dept):
        """ Removes dept from arm and arm from dept """
        classarm.remove_dept_from_class_arm(dept)
        # Remove any chunk, or frequency records from this class arm
        classarm.remove_dept_details_from_class_arm(dept)
        dept.remove_arm_from_dept(classarm)


    def unmap_all_depts_from_arm(self, classarm):
        """ removes all the depts from classarm and removes class_arm from the records of each dept """
        for dept in classarm.depts_and_teachers.copy():
            self.unmap_dept_from_arm(classarm, dept)


    def map_day_to_arm(self, classarm, day_obj):
        """ Adds day_obj to class arm and also adds class_arm to the day_obj """
        classarm.add_day_to_arm(day_obj)
        day_obj.add_arm_to_day(classarm)


    def unmap_day_from_arm(self, classarm, day_obj):
        """ Removes day from arm, and arm from day. """
        classarm.remove_day_hence_periods_from_arm(day_obj)
        day_obj.remove_arm_from_day(classarm)


    def unmap_all_arms_from_day(self, day_obj):
        """ Removes all arm objects from the day object and every other attatchment"""
        for arm in day_obj.school_class_arms_today:
            self.unmap_day_from_arm(arm, day_obj)


    def map_teacher_to_dept(self, teacher, dept):
        """ Adds dept to teacher, teacher to dept """
        teacher.add_dept_to_teacher(dept)
        # To add this teacher to the list of teachers of the department that was added
        dept.add_ready_made_teacher(teacher)
        # in case dept has is_parallel set to True


    def unmap_teacher_from_dept(self, teacher, dept):
        """ Completely disengages teacher from dept, dept from teacher """
        teacher.remove_dept_from_teacher(dept)
        dept.remove_teacher_from_dept(teacher)


    def map_teacher_from_dept_to_arm(self, dept_obj, class_arm, ascending=True, teacher_obj=None):
        """This method does all the labour of assigning a teacher to a class arm.
        It notifies the teacher, dept and class arm objects of this and satisfies all of them
        accordingly, no trouble."""

        if class_arm in dept_obj.teachers_for_client_class_arms:
            # The generated teacher
            gen_teacher = dept_obj.assign_teacher(class_arm, teacher=teacher_obj)

            if gen_teacher:
                # Add this class and the teacher to the department's records
                dept_obj.teachers_for_client_class_arms[class_arm] = gen_teacher
                # Add the department and teacher to the class' records
                class_arm.add_teacher_to_class_arm_for_dept(gen_teacher, dept_obj)
                # Add the class arm to the teacher's list of class arms they are teaching
                # gen_teacher.classes_taught.add(class_arm)
                # Add this dept and arm to teacher's dept_and_arms dictionary, with chunk set to None (not assigned any chunk yet)
                gen_teacher.add_dept_to_teacher(dept_obj)

                # Also add the class arm's frequency details (BUT NOT THE CHUNK) to the teacher object
                freq, _ = class_arm.depts_and_freq_details[dept_obj]
                gen_teacher.add_dept_arm_freq_to_teacher(dept_obj, class_arm, frequency=freq)
        else:
            raise ProjectExceptions.SomethingWentWrong("Teachers could not be assigned to class arm")


    def unmap_teacher_from_dept_from_arm(self, dept_obj, class_arm):
        """ Removes assigned teacher from class arm and all the other stuff that goes with it """

        teacher = class_arm.depts_and_teachers[dept_obj]
        # teacher could be None, but in the event that it isn't
        if teacher:
            dept_obj.teachers_for_client_class_arms[class_arm] = None
            # remove this class from the teacher's record
            teacher.remove_dept_arm_freq_from_teacher(dept_obj, class_arm)
            # Also remove this teachers details from class arm
            class_arm.remove_teacher_from_class_arm_for_dept(teacher, dept_obj)


    def load_teachers_from_all_depts(self, ascending=True):
        """ TO BE CALLED ONLY ONCE!! 
        Makes the internal operations that yield teachers for assignment to class arms FOR ALL DEPTS (SUBJECTS) """
        for dept in self.list_of_departments:
            # load all the generators to help yield teacher
            try:
                # Catch error if this "dept" has not had any teachers assigned to it. so doesn't error out and impede the others
                dept.sort_teachers_by_weight()
                dept.load_teachers_for_classgroup(ascending=ascending)
            except Exception:
                pass


    def auto_assign_teachers_to_all_arms(self, ascending=True, beam_val_max=100):
        """ Assigns teachers to to every department offered by every class arm. AUTOMATED """

        # initialize the count variable that will be yielded upon run
        len_arms = len(self.list_of_school_class_arms)

        for count, arm in enumerate(self.list_of_school_class_arms, start=1):
            # time.sleep(0.01)
            for dept, teacher in arm.depts_and_teachers.items():
                # only do  this mapping if teacher had not been previously assigned
                if teacher is None:
                # map teacher to each dept of each arm
                    try:
                        # If the below errors out because no teachers have been made for dept
                        self.map_teacher_from_dept_to_arm(dept, arm, ascending=ascending)
                    except Exception:
                        pass
            # Only yield if it is intended as a generator
            beamed_val = round(count * beam_val_max / len_arms)
            yield beamed_val



    def undo_assign_teachers_to_arms(self, beam_val_max=100):
        """ Strips each arm of its subject teacher """
        len_arms = len(self.list_of_school_class_arms)

        for count, arm in enumerate(self.list_of_school_class_arms, start=1):
            # time.sleep(0.01)
            for dept in arm.depts_and_teachers:
                self.unmap_teacher_from_dept_from_arm(dept, arm)
            beamed_val = round(count * beam_val_max / len_arms)
            yield beamed_val
            
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
            # the list of depts (subjects)
            self.depts_list = []

        def add_dept_to_course_list(self, dept_obj):
            self.depts_list.append(dept_obj)

        def remove_dept_from_course_list(self, dept_obj):
            self.depts_list.remove(dept_obj)

        @property
        def full_name(self):
            """The full name of the faculty as will be shown in the app"""
            return f"DEPT. ID:{self.id}  {self.name}"

        @property
        def detailed_info(self):
            return f"""
            <p>Department name: {self.full_name}. </p>
            <p>Department headed by: {self.HOD}. </p>
            <p>Child Subject Number: {len(self.depts_list)}.</p>
            <p>Description: {self.description} </p>
            """
        

    class Department:
        '''This is the Course/Subject class, where teachers come from
        This is referenced as "SUBJECT/COURSE" in the GUI
        '''  
    
        def __init__(self, name, faculty=None, hos=None, is_special=False, A=None, T=None, P=None,G=None, 
            is_parallel=False, delimiter_if_parallel="/"):
            """This is the department class. It is the SCHOOL SUBJECT to be 
            handled. However, it might not be an academic_class. It just 
            could be recess or what we call a special class.

            The 'is_special' argument helps to identify if the class is non-academic or academic. is_special == True
            means it is a non-academic dept """

            self.dept_name = name
            self.is_special = is_special
            self.id = 0

            # Rating on how critical, mathematical or otherwise this department is
            # This numerical value will help sort the department in the list of other departments

            self.info = f"Special subject: {self.dept_name}"

            if not self.is_special:
                # Works if this department is academic and NOT "Special" as in recess or extracurriculars

                # self.HOD = HOD
                self.faculty = faculty
                self.hos = hos

                # Add this department to the course_list of its faculty since it is not a special period
                self.faculty.add_dept_to_course_list(self)
                self.info = f"Name of subject: {self.dept_name}"

                # Very important list, DONT TOUCH!
                self.teachers_list=[]

                # A dictionary holding class_group:[teachers who can teach it]
                self.teachers_for_classgroup  = {}

                # A dictionary to store teachers (key) and a [counter, day_weight] -- (values)
                self.teachers_count = {}

                # This is a dictionary of each class arm object (the key) and the teacher (the value) from this department handling it
                self.teachers_for_client_class_arms = {}

                # --- Dictionary to store the finished arm, chunk, teacher namedtuple (from Teachers_and_chunked_val in the Tt_algo module)
                # as values() and day as the key()
                self.finished_arm_chunk_teacher_day_dict = {}
                
                # ---------------------------------------------------------------------
                # The descriptive attributes of the department (on how analytic, theoretical and such)
                # Numerical values are added to help sort the departments or the teachers that teach 
                # this course as the case may be
                self.analytic_parameter = 3, "Analytic"
                self.theoretical_parameter = 2, "Theoretical"
                self.practical_parameter = 3, "Practical"
                self.grammatical_parameter = 2, "Grammatical"

                self.analytic = A
                self.theoretical = T
                self.practical = P
                self.grammatical = G

                # A tuple of seven prime numbers
                self.ATPG_primes = (2,3,5,7,11,13,17)
                # --------------------------------------------------------------------------------------------------
                # -- This is_para attr is to test whether this department should always feature in the timetable alongside another
                # department during the same period.
                self.is_parallel = is_parallel
                if self.is_parallel:
                    # A dictionary of "arm":list of teachers, these teachers are the remaining teachers for when first teacher has been chosen
                    # to be represented in the up-top self.teacher_for_client_class_arms
                    self.parallel_names = self.dept_name.split(delimiter_if_parallel)
                    self.parallel_names = [name.strip() for name in self.parallel_names]
                    # receives tuples of teacher objects before assignment into key=split_name, value=tuple of teachers
                    self.parallel_teachers_dict = {}
                    
                    # THE LOGIC IS QUITE SIMPLE:
                    # EVEN IF IS_PARALLEL == True, self.teachers_for_client_class_arms still yields a teacher object... the first teacher
                    # the remaining teachers for the parallel are mapped to that first teacher in a tuple. that first teacher serves as our marker and goes through
                    # all the chunk process for us. we only record values for the other teachers as soon as the chunking process is done


        # ...................................................................................................................................
        # ----------------------------- PARALLEL METHODS ()METHODS WHEN THE DEPT HAS IS_PARALLEL SET TO TRUE -----------------------------
        def add_teachers_tuple_to_parallel_dept(self, split_name, teacher_list):
            """ this adds a teacher_tuple to the self.parallel_teachers_list if of course, is_parallel is true """
            if self.is_parallel:
                if not split_name in self.parallel_teachers_dict:
                    self.parallel_teachers_dict[split_name] = []

                self.parallel_teachers_dict[split_name] += teacher_list
                

        def remove_teachers_tuple_from_parallel_dept(self, split_name):
            """ this adds a teacher_tuple to the self.parallel_teachers_list if of course, is_parallel is true """
            if self.is_parallel and split_name in self.parallel_teachers_dict:
                del self.parallel_teachers_dict[split_name]


        def adapt_teachers_list_for_parallel(self):
            """ SHOULD BE RUN ONLY WHEN ALL THE PARALLEL TEACHER TUPLES HAVE BEEN ADDED (OR REMOVED).
            This method repopulates the self.teachers_list list with a single teacher chosen specially to represent
            all the parallel teachers. Order important! """

            if self.is_parallel:
                # Overrides self.teachers_list with thises new values
                self.teachers_list = list(self.parallel_teachers_dict.values())[0]


        def return_teacher_pairs_for_parallel(self):
            """ This method returns a list of tuples of all the teacher objects (teaching each different split name) but taking the same class arm
            Would probably be useful for mapping periods back to teachers """
            if self.is_parallel:
                overall_list = []
                for index, teacher in enumerate(self.teachers_list):
                    sub_list = []
                    for teacher_tuple in self.parallel_teachers_dict.values():
                        teacher = teacher_tuple[index]
                        if not teacher in sub_list:
                            sub_list.append(teacher)
                    overall_list.append(tuple(sub_list))
                return overall_list


        def remove_teacher_pair_for_parallel(self, teacher_pair):
            """ This method removes this pair of teachers from the parallel_teachers_dict."""
            if self.is_parallel:
                for teacher, teacher_list in zip(teacher_pair, self.parallel_teachers_dict.values()):
                    if teacher in teacher_list:
                        teacher_list.remove(teacher)


        def get_parallel_dept_given_teacher(self, teacher):
            """ Returns the para-dept name that a teacher object is allowed to teach, given the teacher, e.g. for
            Yoruba/Igbo teacher teaches Yoruba """
            for para_split_name, teacher_list in self.parallel_teachers_dict.items():
                if teacher in teacher_list:
                    return para_split_name, f"C-ID {self.id}: {para_split_name}{' -P' if self.is_parallel else ''}"


        def get_teacher_pair_given_teacher(self, teacher):
            """ Returns a teacher_pair if 'teacher' object is found there """
            for teacher_pair_tuple in self.return_teacher_pairs_for_parallel():
                if teacher in teacher_pair_tuple:
                    return teacher_pair_tuple

        # ----------------------------------------------------------------------------------------------------------------------------------
        # ......................................................................................................................................

        @property
        def class_group_span(self):
            """ IMPORTANT! This method retrieves all the classgroups across which all the school classes taking this 
            dept are. This function is to help place teachers who are only specialized to a certain class group (category).
            Only works for academic courses. """
            if not self.is_special:
                return {arm.school_class.school_class_group for arm in self.teachers_for_client_class_arms}


        def dept_ATPG(self):
            """ sThis method handles the calculation of assigning a weight to the course by the elements in the course description.
            ATPG is merely an acronym for analytic, theoretical... """

            return (self.analytic * self.analytic_parameter[0]) + (self.theoretical * self.theoretical_parameter[0])\
             + (self.practical * self.practical_parameter[0]) + (self.grammatical * self.grammatical_parameter[0])
                

        def teachers_rating_list(self, arg_list, desc=False):
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


        def remove_teacher_from_dept(self, teacher_obj):
            """Removes a teacher object from the department!"""
            if teacher_obj in self.teachers_list:
                self.teachers_list.remove(teacher_obj)

            # Completely remove teacher's posse if this dept is parallel
            if self.is_parallel:
                for teacher_tuple in self.return_teacher_pairs_for_parallel():
                    if teacher_obj in teacher_tuple:
                        self.remove_teacher_pair_for_parallel(teacher_tuple)


        def add_ready_made_teacher(self, teacher_obj):
            """This methods adds an ALREADY-MADE teacher object to the teachers_list.
            This really is adding a teacher from another department, e.g a further maths teacher to teach math"""
            if teacher_obj not in self.teachers_list:
                self.teachers_list.append(teacher_obj)


        def __repr__(self):
            return f"{self.dept_name}, ID:{self.id}"


        def teachers_plenty_enough(self):
            """ BOOLEAN. checks whether each of the teachers of this dept have not been overworked.
            overworked as in teaching every period throughout the day...or more. """
            return all([
                teacher.total_frequency_okay(compare_val=None) for teacher in self.teachers_list
                ])


        def how_many_more_teachers(self, all_days_len=5):
            """ Returns al tuple (minimun amount of teachers needed, how many more teachers needed based on what you have)
            Does all the calculation on how many more teachers need to be generated for this department,
            using the pattern of the number of subjects handled by the previous teachers. Using a mathematical equation I drafted out """
            # ---------------------------------------------------------
            def _each_teacher(teacher):
                """ Does all the necessary operation on one teacher """

                # As an aside, spillover must not be less than 0
                # we want to trim off the number of arms allocated to teacher so that the overworking problem doesn't exist anymore
                trim = 0
                spill = True
                container_count = 0
                spillover = teacher.total_frequency_spillover
                for (dept, arm), frequency in teacher.dept_and_arms.items():
                    if dept == self:
                        container_count += 1

                        while spill:
                            # print("CALCULATION DEFAULTING")
                            trim += 1
                            spillover -= frequency
                            # print(f"spillover {spillover}, frequency {frequency}")
                            if spillover <= 0:
                                spill = False

                ideal = container_count - trim
                return ideal
            # -------------------------------------------------------------

            summation_ideal = sum([_each_teacher(teacher) for teacher in self.teachers_list])
            summation_teaching_days = sum([len(teacher.teaching_days) for teacher in self.teachers_list])
            num_arms = len(self.teachers_for_client_class_arms)

            # For the number of extra teachers to be idealy added "K"
            K = math.ceil(summation_teaching_days * (num_arms - summation_ideal)/(all_days_len * num_arms))
            total_min_teachers = len(self.teachers_list) + K
            return total_min_teachers, K


        def teachers_plenty_enough_report(self, all_days_len=5):
            """ Report on whether the resident teachers are enough """
            if self.teachers_plenty_enough():
                return "#004a00", "Teachers sufficient."

            total, more = self.how_many_more_teachers(all_days_len=all_days_len)
            return "#9b0000", f"Insufficient. Needs at least {total} teachers in total ({more} regular teachers more)."


        def teachers_regularity_ratio(self):
            """ DICTIONARY_OF_FLOATS. FOR REPORT (MOST_LIKELY) Returns the ratio of teachers who are not 
            regular to teachers who are regular (to 2 decimal places) """
            num_teachers = len(self.teachers_list)
            num_reg_teachers = len([teacher for teacher in self.teachers_list if teacher.regularity])
            num_nonreg = num_teachers - num_reg_teachers

            reg_ratio = 0 if num_teachers == 0 else round(num_reg_teachers / num_teachers, 2)
            non_reg_ratio = 1 - reg_ratio
            nonreg_to_reg_ratio_str = f"{num_nonreg}:{num_reg_teachers}"
            return {"reg_ratio": reg_ratio, "non_reg_ratio":non_reg_ratio, "nonreg_to_reg_ratio_str": nonreg_to_reg_ratio_str}


        @property
        def full_name(self):
            return f"C-ID {self.id}: {self.dept_name}{' -P' if self.is_parallel else ''}"
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


        def sort_teachers_by_weight(self):
            """ Sorts all the teacher objects by the number of his teaching days """

            def _sort_teacher_by_weight(teacher):
                """ Sorts a teacher by weight """
                weight = round(len(teacher.teaching_days)*len(self.teachers_for_client_class_arms)/teachers_days_sum)
                # Add this weight and the counter to the apprpriate dictionary
                self.teachers_count[teacher] = [0, weight]
                # ------------------------------------------------------------------------

            teachers_days_sum = sum([len(teacher.teaching_days) for teacher in self.teachers_list])
            # sort every teacher by weight
            for teacher in self.teachers_list:
                _sort_teacher_by_weight(teacher)


        def load_teachers_for_classgroup(self, ascending=True):
            """ Populates the self.teacher_for_classgroup dictionary with the classgroup(key) and
             the list of teachers who can teach it (value) """

            self.teachers_for_classgroup.clear()

            for classgroup in self.class_group_span:
                for teacher in self.teachers_list:
                    if classgroup in teacher.specialty:
                        if classgroup not in self.teachers_for_classgroup:
                            self.teachers_for_classgroup[classgroup] = []
                        self.teachers_for_classgroup[classgroup].append(teacher)

                # Sort the teachers in the list according to the how many class groups
                # they can teach across. Least to greatest (if ascending is true)

            # A dict to keep track of the count of each classgroup, so we know which teacher to yield
            self.classgroups_with_count = {classgroup:0 for classgroup in self.class_group_span}

            for classgroup in self.class_group_span:
                # In the event that teachers have NOT been generated to teach the course, which in turn affects the self.teachers_for_classgroup dict
                
                sorted_list = sorted(self.teachers_for_classgroup[classgroup], key=lambda teacher: len(teacher.specialty), reverse=not(ascending))
                sorted_list_gen = [teacher for teacher in sorted_list if self.teachers_count[teacher][0] <= self.teachers_count[teacher][1]]

                self.teachers_for_classgroup[classgroup] = sorted_list_gen

                # except KeyError:
                #     # self.teachers_for_classgroup[classgroup] = (elem for elem in itertools.cycle([None]))
                #     self.teachers_for_classgroup[classgroup] = [None]


        def assign_teacher(self, class_arm, teacher=None):
            '''This function assigns a teacher already in the list to a class. It simply gives the teacher with the lowest class rating'''

            # Only works if this is not a nonacad (special) department
            if not self.is_special:
                classgroup = class_arm.school_class.school_class_group

                # If a teacher has been manually assigned
                if teacher:
                    if classgroup in teacher.specialty:
                        self.teachers_for_client_class_arms[class_arm] = teacher
                        return teacher
                    raise Tt_exceptions.SomethingWentWrong(f"""Teacher: {teacher.full_name} does not teach {class_arm.full_name}'s
                         class category and so does not qualify to handle {self.full_name} for this class arm.""")

                # When teacher is programmatically assigned
                # yield the teacher from the self.teacher_for_classgroup dict which houses classgroup:teacher_generator
                teacher = self.teachers_for_classgroup[classgroup][self.classgroups_with_count[classgroup]]
                # increment the classgroups_with_count so we begin from the next teacher on the list
                self.classgroups_with_count[classgroup] = (self.classgroups_with_count[classgroup] + 1) % len(self.teachers_for_classgroup[classgroup])
                
                # updates the teachers count (a record of the max number of arms a teacher can take, based on his days)
                if teacher:
                    self.teachers_count[teacher][0] += 1
                return teacher


        def add_finished_chunk_details_to_dept(self, arm, chunk, teacher, day):
            """ AFTER SORTING. Adds the finished arm, chunk, teacher (as a tuple) and day (as the key to the dictionary) objects to this dept object """
            if day not in self.finished_arm_chunk_teacher_day_dict:
                self.finished_arm_chunk_teacher_day_dict[day] = []
            self.finished_arm_chunk_teacher_day_dict[day].append((arm, chunk, teacher))



        @property
        def detailed_info(self):
        
            return f"""
            <html>
            <p>Subject/course ID and full name: {self.full_name}.</p>
            <p>Headed by {self.hos}.
            <p>Mother Department: {self.faculty.full_name}.</p>
            <p>This course, based on the nature of its contents scores <strong>{self.dept_ATPG()}</strong> on the ATPG-
            course structure scale.
            <p>N.B: The ATPG scale is not by any means a measure of the importance of a subject/course. Such judgement is within the descretion
            of the school or Ministry of Education or the presiding institution(s) involved. This rating simply helps sort the courses.</p>
            <p>Number of resident teachers: {len(self.teachers_list)}</p>
            </html>
            """

        # def __getstate__(self):
        #     new_state = self.__dict__.copy()
        #     if "load_teachers_for_classgroup" in new_state:
        #         del new_state["load_teachers_for_classgroup"]
        #     if "assign_teacher" in new_state:
        #         del new_state["assign_teacher"]
        #     return new_states


    class Teacher:
        '''The teacher object which is in composition with the department object, i.e, "teacher has a department"
        he teaches'''
        def __init__(self):

            self.id = 0
            self.teachers_depts_list = [] 

            # The set containing the days in which the teacher can teach
            self.teaching_days = []
            # Specialty refers to the LIST of class groups across which teacher can teach
            self.specialty = None

            self.designation = "Staff member"
            # A dictionary that stores (dept, arm) as key and frequency as value
            self.dept_and_arms = {}
            # --- WILL BE CANCELED LATER. A dictionary that of day_obj:[arms_taught]
            self.days_and_arms_taught = {}

            # A dictionary of tuples of day:[(arm1, chunk_val, dept)] Recieves the Teacher_and_chunked_val namedtuple
            self.day_arm_chunk_dept = {}

            # instance variable to initailize whether teacher is regular or not (So as to make it easy to call this variable
            # from outside the class without calling the self.regular_or_no function)
            self.regularity = None


        @property
        def teaching_days_s(self):
            # Returns the SET form if the teaching day attr, so as to eradicate duplicates
            return set(self.teaching_days)

        @property
        def str_teacher_depts(self):
            """For GUI. This property method renders all the depts offered by the teacher as a comma-delimited
            string (for the GUI or for report)"""
            return ", ".join([dept.full_name if not dept.is_parallel else dept.get_parallel_dept_given_teacher(self)[1] for dept in self.teachers_depts_list])


        @property
        def record_teachers_parallel_depts(self):
            """ If any of the depts taught by the teacher has is_parallel as True, record which of nthe parallel depts
            exactly that this teacher teaches """

            # dictionary to hold dept_obj: dept_para_split_name
            parallel_depts_dict = {}
            for dept in self.teachers_depts_list:
                if dept.is_parallel:
                    # dept.get_parallel_dept_given_teacher(self) returns a tuple of the (dept_para_split_name
                    # and, the dept_para_split_name with ID and stuff).
                    parallel_depts_dict[dept] = dept.get_parallel_dept_given_teacher(self)

            return parallel_depts_dict if parallel_depts_dict else None


        def str_teaching_days(self, tt_obj):
            """For GUI. This function checks if teacher teaches on all the registered days"""
            day_diff = set(tt_obj.list_of_days) - self.teaching_days_s
            if not day_diff:
                self.regularity = True
                return "All"
            day_diff_list = [day.day for day in day_diff]
            return "All Except " + ", ".join(day_diff_list)

        
        @property
        def specialization(self):
            """ MANAGER_GUI method. Returns a STRING of the list of the full_names for all the classgroups in teachers specialty """
            return ", ".join([item.full_name for item in self.specialty])


        def regular_or_no(self, tt_obj):
            """Returns 'Regular' or 'Special' based on how many days taught."""
            reg_or_no = self.str_teaching_days(tt_obj)
            return "Full-time" if reg_or_no == "All" else "Part-time"


        @property
        def classes_count(self):
            return len(self.classes_taught)


        @property
        def all_teacher_depts_id(self):
            # Get all the unique ids for the departments this oga is teaching as values 
            # and depts as keys
            self.teachers_dept_id = {dept: dept.id for dept in self.teachers_depts_list}
            return self.teachers_dept_id


        def __repr__(self):
            return f"Teacher id: {self.id}"


        def add_dept_to_teacher(self, dept_obj):
            """Apparently, a teacher can teach more than one subject (e.g. math and further maths).
            This function adds a new unique department object to the list of departments owned by the teacher"""

            # -- To check to make sure no duplicates exist
            if not dept_obj in self.teachers_depts_list:
                self.teachers_depts_list.append(dept_obj)


        def add_dept_arm_freq_to_teacher(self, dept, class_arm, frequency=0):
            """ Registers the dept (WHICH MUST ALREADY BE IN THIS TEACHER'S DEPT LIST!!!), the arm offering it, and the frequency
            in a dictionary """

            if dept in self.teachers_depts_list:
                self.dept_and_arms[(dept, class_arm)] = frequency


        def remove_dept_arm_freq_from_teacher(self, dept, class_arm):
            """ This removes the classarm (given dept) from the teacher's dept_and_arm dictionary.
            would be used in the function to unmap teachers from class arms given dept """
            if (dept, class_arm) in self.dept_and_arms:
                del self.dept_and_arms[(dept, class_arm)]
            
            
        def remove_dept_from_teacher(self, dept_obj):
            """Removes a department object from the list of depts taught by the teacher"""

            # Remove dept from teachers list
            self.teachers_depts_list.remove(dept_obj)
            del self.dept_and_arms[dept_obj]
            # Remove teacher from the list of teachers of the department
            dept_obj.remove_teacher_from_dept(self)


        def add_day_to_teacher(self, day_obj):
            """ Adds a day object to the list of days in which the teacher can teach """
            
            # is needed. sets do not preserve the order, so sets are no longer used
            if day_obj not in self.teaching_days:
                self.teaching_days.append(day_obj)


        def add_finished_day_arm_chunk_dept_to_teacher(self, day, arm_chunk_dept_tuple):
            """ Adds the arm, chunk and dept to the self.day_arm_chunk_and_dept dictionary.
            arm_chunk_dept is a tuple culled from the namedtuple from Teachers_and_chunked_val after the sorting is all done """
            if day not in self.day_arm_chunk_dept:
                self.day_arm_chunk_dept[day] = []
            self.day_arm_chunk_dept[day].append(arm_chunk_dept_tuple)


        def remove_day_from_teacher(self, day_obj):
            """Removes the day_obj from the self.teaching_days set"""
            self.teaching_days.remove(day_obj)


        def teachers_sequence(self):
            """ Returns a list of tuples (dept, arm) that the teacher teaches """
            return tuple(self.dept_and_arms.keys())


        @property
        def classarms_taught(self):
            """ Returns a set of the class arms ALONE that teacher teaches """
            return {arm for _, arm in self.teachers_sequence()}


        def is_exclusive(self):
            """ BOOL. Returns True if teacher only teaches from one subject, and false if not """
            return len(self.teachers_depts_list) <= 1


        def other_depts_taught(self, dept):
            """ Returns any other dept(subject) this teacher teaches apart from the "dept" """
            return [dept_ for dept_ in self.teachers_depts_list if dept_ == dept]


        def other_depts_taught_str(self, dept):
            """ FOR THE REPORT. Returns the list of strings of other depts taught aside dept """
            return ", ".join([dept_.dept_name for dept_ in self.other_depts_taught(dept)])


        @property
        def classarms_taught_str(self):
            """ FOR REPORT. Returns teacher's class arms taught in string format """
            return ", ".join([arm.full_name for arm in self.classarms_taught])

    
        def classarms_taught_based_on_dept(self, dept):
            """ Returns all the class arms for which a teacher teaches a particular
            subject (dept). """
            return [arm for dept_,arm in self.teachers_sequence() if dept_ == dept]
        

        def classarms_taught_based_on_dept_str(self, dept):
            """ FOR REPORT. Renders all the arms teacher takes a particular subject "dept" in string form """
            return ", ".join([arm.arm_and_id for arm in self.classarms_taught_based_on_dept(dept)])


        @property
        def teachers_total_frequency(self):
            """ The sum total of all the periods for all depts in all the arms in which teacher teaches.
            It is equal to the total number of periods he teaches all through """
            return sum(self.dept_and_arms.values())


        @property
        def total_frequency_spillover(self):
            """ Returns the amount with which teachers total frequency exceeds the legal amount  """
            return self.teachers_total_frequency - (min([len(periods)
                for arm in self.classarms_taught
                for periods in arm.periods.values()])*len(self.teaching_days))
        

        def total_frequency_okay(self, compare_val=None):
            """ Function that checks whether the sum of teacher's frequency does not spill past the max
            number of periods he can teach in for the whole week. Returns True if less and False if not. """
            if compare_val:
                return self.teachers_total_frequency <= compare_val
            
            return self.teachers_total_frequency <= min([len(periods)
                for arm in self.classarms_taught
                for periods in arm.periods.values()])*len(self.teaching_days)


        def teachers_arms_taught_per_day(self):
            """ Populates the dictionary containing the arms (in its duplicate) that teacher teachers on a GIVEN DAY """
            for day in self.teaching_days:
                self.days_and_arms_taught[day] = day.teachers_depts_today(self)

        @property
        def teachers_freq_average(self):
            """ Returns the average frequency of the teacher per day """
            return math.ceil(self.teachers_total_frequency/len(self.teaching_days))

        @property
        def full_name(self):
            return f"ID: {self.id}. {self.designation}"


        def get_teaching_efficiency(self):
            """ This method calculates the teaching efficiency of said teacher (a measure of how much space is between each of his lessons)
            in all of the different arms in which he teaches """

            def calc_efficiency(list_argument):
                """ Handles the teaching efficiency calculation for the items in a list (list of integers) """
                list_arg = Tt_algo_calc.strip_list_wrapper(list_argument)
                list_arg_length = len(list_arg)
                if list_arg_length <= 1:
                    return 0
                # Rank-order list_arg and hold that new rank-ordered list in the variable below
                list_arg_ = sorted(list_arg, reverse=True)
                eff = 0
                for k in range(1, list_arg_length):
                    eff += list_arg_[k] - list_arg_[k - 1]
                return round(eff/(list_arg_length - 1), 3)
            # ----------------------------------------------------------------------------
            # ----------------------------------------------------------------------------

            # 1. Get all of his chunk values per day (in a list)
            eff_cummulative = 0
            for arm_chunk_dept_list in self.day_arm_chunk_dept.values():
                chunk_numbers = [elem.chunk for elem in arm_chunk_dept_list]
                # 2. Use the efficiency funcion/equation to calculate efficiency "E" for said day
                E = calc_efficiency(chunk_numbers)
                eff_cummulative += E
            # 4. Find the average of E across all the days in which he teaches
            
            return round(eff_cummulative/len(self.day_arm_chunk_dept), 2)


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

        def tag(self):
            """ Name tag to prefix child school classes """
            return self.abbreviation if self.abbreviation else self.class_group_name

        @property
        def full_name(self):
            return f"ID: {self.id}. {self.class_group_name}"

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
        def sch_class_alias(self):
            return f"{self.school_class_group.tag()} - {self.level}"


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
            return f"Class ID:{self.id}. {self.school_class_group.tag()} - {self.level}"
        

    class SchoolClassArm:
        """ This class models every arm that a school class has. It can represent the arms 
        with letters or numbers.
        The 'as_alpha' parameter controls this. short for 'is_a_letter_of_the_alphabet' """

        def __init__(self,school_class_obj, as_alpha=True):

            self.school_class = school_class_obj
            self.id = 0
            self.days_list = []

            # --A dictionary of all the periods for every day (the dict has a key-value pair of the day_obj: list of periods)
            self.periods = {}
            self.period_id_counter = {}
            self.school_class.school_class_arm_list.append(self)

            self.local_identifier = self.school_class.school_class_arm_list.index(self)

            if as_alpha:
                self.local_id = TimeTable.stringify(self.local_identifier)
            else:
                self.local_id = self.local_identifier + 1

            # -- Dictionary to hold... dept(key) and teacher(value)
            self.depts_and_teachers = {}

            # --- Dictionary of dept: (frequency, chunk)
            self.depts_and_freq_details = {}

            # below is a variable to store the iterable_from_gui list of tuples
            self.iterable_from_gui = None

            # Variable to store this arms properties for the arms_feasible_periods
            self.arms_feasible_table_data = [None, None, False, "#df0000"]

            # --- Tentative dictionary (below) to hold the list of subjects offered per day
            #  'day' is the key and the list of subjects is the value. It is first put as None for ease
            self.temp_dept_holder_for_days = {}
            # 
            #-------------------------------------------------------- 
            # container for when a dept has been actively assigned 
            self.depts_assigned_by_algo_per_day = {}


        @property
        def get_class_arm_days(self):
            """Returns a list of every school day for which the class runs"""
            return self.days_list


        def add_day_to_arm(self, day_obj):
            """ Adds a day object to the days_list for this classarm. """
            if day_obj not in self.days_list:
                self.days_list.append(day_obj)
                self.temp_dept_holder_for_days[day_obj] = []


        def remove_day_hence_periods_from_arm(self, day_obj):
            """Removes a day object from the list of days of this class arm and empties out all 
            the periods for that day for the class arm too"""
            if day_obj in self.days_list:
                self.days_list.remove(day_obj)
                # Remove this arm from the list of arms in the day_obj
                day_obj.school_class_arms_today.remove(self)
                # Remove the day from the dictionary that holds the days packeted dept objects
                del self.temp_dept_holder_for_days[day_obj]

            # Also remove this day from this class arm's periods dictionary
            if day_obj in self.periods:
                del self.periods[day_obj]


        def store_iterable_from_gui(self, iterable):
            """ Stores the iterable_from_gui into the iterable_from_gui variable """
            self.iterable_from_gui = iterable


        def store_arms_feasible_table_data(self, data):
            """ method stores the properties of the arms_feasible_table """
            self.arms_feasible_table_data = data


        def get_arms_feasible_table_data(self):
            """ retrieves the arms_feasible _table_data """
            # the arm's full_name is added
            return tuple([self.full_name] + self.arms_feasible_table_data)

        # -------------------------------------------------------------------------------------------------------------
        def add_dept_to_class_arm(self, dept_obj, descent=False, auto=True, teacher_index=None):
            """ Adds to the dictionary a tuple of as the key and the teacher object as the value. The teacher is first set None. 
            The 'get_teacher_for_department_in_arm method' is called to assign the teacher given by the department to this subject for this class.

            This adds a new subject for learning to the class arm """
            if dept_obj not in self.depts_and_teachers:
                self.depts_and_teachers[dept_obj] = None


        def remove_dept_from_class_arm(self, dept_obj):
            """ Removes a subject from the offered subjects stored by the class arm """
            if dept_obj in self.depts_and_teachers:
                del self.depts_and_teachers[dept_obj]

            # Remove whatever chunk, freq, details might have already been recorded for this dept_obj
            self.remove_dept_details_from_class_arm(dept_obj)
        # ------------------------------------------------------------------------------------------------------
        
        def add_dept_details_to_class_arm(self, dept_obj, freq, chunk):
            """ Adds a tuple of (frequency and chunk) as value to the dept (key) """
            self.depts_and_freq_details[dept_obj] = (freq, chunk)


        def remove_dept_details_from_class_arm(self, dept_obj):
            """ Removes the chunk, frequency and dept details from the self.depts_and_freq_details  dictionary """
            if dept_obj in self.depts_and_freq_details:
                del self.depts_and_freq_details[dept_obj]

        # ---------------------------------------------------------------------------------------------------------

        def add_teacher_to_class_arm_for_dept(self, teacher, dept):
            """ Adds the teacher for a certain dept to this class arm """
            if dept in self.depts_and_teachers:
                self.depts_and_teachers[dept] = teacher


        def remove_teacher_from_class_arm_for_dept(self, teacher, dept):
            """ Removes the teacher assigned to this class arm for the given dept """
            if dept in self.depts_and_teachers:
                self.depts_and_teachers[dept] = None


        def remove_dept_from_arm_temp_holder_for_days(self, dept_obj, day_obj):
            """ Remove all the instances of 'dept' from the dictionary holding the temporarily assigned
            dept to this arm on a daily basis """

            if dept_obj not in self.temp_dept_holder_for_days[day_obj]:
                raise ValueError(f"{dept} not in {self} subjects for today")
                
            for dept in self.temp_dept_holder_for_days[day_obj].copy():
                if dept == dept_obj:
                    self.temp_dept_holder_for_days[day_obj].remove(dept_obj)


        def get_teacher_for_department_in_arm(self, dept_obj):
            """ The dept_obj is called to assign a teacher for the class_arm """
            dept_obj.add_arm_to_dept(self)
            # use the dept obj to assign a teacher to this class arm
            dept_obj.assign_teacher_to_arm(self, descent=False, auto=True, teacher_index=None)

            teacher = dept_obj.teachers_for_client_class_arms[self]
            self.add_teacher_to_class_arm_for_dept(teacher, dept_obj)


        def all_teachers_for_class_arm(self):
            """ Returns a set of all the teachers teaching this particular arm
            from the self.depts_and_teachers attribute, just in case some teachers repeat """
            return {teacher for teacher in self.depts_and_teachers.values()}


        def period_count_per_day(self, day_obj, include_nonacads=False):
            """ INT. Returns the number of periods for this class arm today """
            if day_obj in self.periods:
                if include_nonacads:
                    return len(self.periods[day_obj])
                return len([period for period in self.periods[day_obj] if period.is_acad])
            return 0

        def period_count_total(self, include_nonacads=False):
            """ INT. Returns the total number of all the periods for all the days available for this arm """
            return sum([self.period_count_per_day(day, include_nonacads=include_nonacads) for day in self.periods])


        def total_period_contains_freq(self, freq):
            """ BOOL. checks whether 'num' is greater than the total number of periods or not. in other words, checks if
            num can be contained in the total number of periods. """
            return self.period_count_total() > freq
            

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


        @property
        def arm_and_id(self):
            return f"{self.school_class.sch_class_alias} {self.local_id}"


        def __repr__(self):
            return self.arm_and_id


        @property
        def full_name(self):
            return f"Arm ID:{self.id}. {self.arm_and_id}"
        

    class Period:
        '''Model for every class period.
        it is owned by a school class ARM and has a teacher
        from a department (or not, if it is a special (favourite) period)'''
        def __init__(self, day, class_arm, start, end=None, duration=None, is_acad=True, title_of_nonacad=None):
            self.is_acad = is_acad
            self.dept = None
            self.day = day
            self.class_arm = class_arm
            self.start = start
            self.nonacad_title = title_of_nonacad if not self.is_acad else None
            self.teacher = None 
            self.end = end
            self.duration = self.get_duration() if self.end else duration

            self.add_period_to_arm()


        def get_duration(self):
            return TimeTable.add_sub_time(self.end, self.start, add=False)


        def add_period_to_arm(self):
            """ Method to add this period object to the dictionary of the school_class_arm
            adds a period one at a time """

            if self.day in self.class_arm.days_list:
                # ---- To update the list of periods
                if not self.day in self.class_arm.periods:
                    self.class_arm.periods[self.day] = []
                self.class_arm.periods[self.day].append(self)

                # ---------- To update the period counter of this periods's arm ----------
                if not self.day in self.class_arm.period_id_counter:
                    self.class_arm.period_id_counter[self.day] = 0
                self.class_arm.period_id_counter[self.day] += 1
            else:
                raise ProjectExceptions.SomethingWentWrong(f"{self.day} is not in the days_list of {self.school_class_arm}")


        def add_details_to_period(self, dept, teacher):
            """ Adds a dept object to this period """
            if self.is_acad:
                self.teacher = teacher
            self.dept = dept


        @property
        def id_barebones(self):
            """ Returns the actual position of this period in its arm's list of periods today. 
            Useful for inputting dept objects after chunking is done, as it is zero-indexed """
            return self.class_arm.periods[self.day].index(self)

        @property
        def id(self):
            """ Returns the formal (formal as in to be displayed on the GUI) ID of this period. """
            return self.id_barebones + 1
        

        @property
        def period_title(self):
            if self.is_acad:
                return f"Acad {self.id}"
            return f"Non-acad"

        @property
        def dept_content(self):
            return self.dept.full_name if self.dept else "UNOCCUPIED"

        @property
        def period_name(self):
            """ TENTATIVE """
            return f"{self.period_title} - {self.dept_content}"
        

        def __repr__(self):
            return self.period_title


    class Day:
        """
            This class represents all the days for which the timetable runs. This could be 5 days (the standard for schools) or other. 
            The 'rating' parameter in the init method is to help rank the objects of this class
        """
        
        def __init__(self, day_name="Monday", rating=None):
            self.day = day_name.capitalize()
            # dummy value for id (has been changed in run-time)
            self.id = 0
            # This var below helps to sort the day in the list of days especially when rating is not None
            self.sort_id = rating
            self.school_class_arms_today = []


        def add_arm_to_day(self, class_arm):
            """ Adds class_arm to the days list containing class arms """
            if class_arm not in self.school_class_arms_today:
                self.school_class_arms_today.append(class_arm)


        def remove_arm_from_day(self, class_arm):
            """ Remove class_arm from this day object """
            self.school_class_arms_today.remove(class_arm)


        @property
        def arms_today_list(self):
            # Attribute to return the set of arms today in a list
            return self.school_class_arms_today


        def get_classgroups_today(self):
            """ Returns the classgroup objects of all the arms featuring today """
            classgroups = []
            for classarm in self.school_class_arms_today:
                if not classarm.school_class.school_class_group in classgroups:
                    classgroups.append(classarm.school_class.school_class_group)
            return classgroups


        def get_sch_classes_today(self):
            """ Returns a list of all the school classes of all the arms featuring today """
            sch_classes = []
            for classarm in self.school_class_arms_today:
                if not classarm.school_class in sch_classes:
                    sch_classes.append(classarm.school_class)
            return sch_classes


        def get_sch_classes_from_class_group_today(self, classgroup):
            """ Returns all the school classes a that have "classgroup" as their classgroup """
            return [clss for clss in self.get_sch_classes_today() if clss.school_class_group == classgroup]


        def get_classarms_from_sch_classes(self, sch_class):
            """ Returns the arms that have their school_class as "sch_class" """
            return [arm for arm in self.school_class_arms_today if arm.school_class == sch_class]
        

        def get_classarm_periods_for_today(self, class_arm):
            """This function squeezes out all the periods for a particular class arm today """
            return class_arm.periods[self]


        def all_classarm_periods_for_today(self):
            '''This function squeezes out every period for every school class arm that has been instantiated.
            by going through the school class list and finding out every period associated with 
            that school class (that has already been instantiated) for that day and putting it into a dictionary
            with the key as the class_arm and the value as the list of periods today.
            '''
            classes_period_dict = {classarm: self.get_classarm_periods_for_today(classarm) for classarm in self.school_class_arms_today}
            return classes_period_dict


        def periods_per_class_arm(self, class_arm_obj):
            """ This method gets all the periods associated with a particular class arm """
            return {class_arm_obj: class_arm_obj.periods[self]}


        def get_depts_of_arm_today(self, class_arm, duplicate=True):
            """ Gets all the depts for today for a class arm
            if duplicate is False, it returns a list of a set of a list of the depts today"""
            if duplicate:
                return class_arm.temp_dept_holder_for_days[self] 
            
            unique_depts = []
            for dept in class_arm.temp_dept_holder_for_days[self]:
                if not dept in unique_depts:
                    unique_depts.append(dept)
            return unique_depts


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
            This method extracts all the teachers that teach those depts today in the class arm.
            RETURNS A DICT!!! """


            # returns all the teacher_objs associated with all the depts for a class arm

            # Maybe i should return a dictionary of teachers depts
            # Teacher is the key with depts (list) is the value
            # Yup! I did.
            teach_assgn_today = {}

            # the items in the below (a set, by the way) are intances of the DeptEncase class
            depts_today = self.get_all_depts_for_arm_today(clss_arm)

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
            """gets all the assigned teachers (from the algorithm) from all the class_arms.
                it does so by calling the 'self.get_arm_teachers_today_from_depts_assgn' method (which happens on
                a class arm) on all the class arms. """

            # A set is used here to avoid duplicates
            all_teachers = []

            for arm in self.school_class_arms_today:
            # get teacher for each arm
                for teacher in self.get_arm_teachers_today_from_depts_assgn(arm):
                    if teacher not in all_teachers:
                        all_teachers.append(teacher)

            # Returns just a set of all the teachers today
            return all_teachers


        def teachers_n_depts_today_dupli(self):
            """ This method gets into a DICT all the teachers(keys) and all the (depts they teach and the arm)(values)
                considering all the duplicates. """
            teach_dept_dupli = {}

            for arm in self.school_class_arms_today:
                # For each dept in the container (dict) of the departments that were assigned to today by the packeting algorithm
                for dept in arm.temp_dept_holder_for_days[self]:
                    teacher = dept.teachers_for_client_class_arms[arm]
                    # Now add teacher into the dictionary, but first check if it already exists
                    if teacher not in teach_dept_dupli:
                        teach_dept_dupli[teacher] = []
                    teach_dept_dupli[teacher].append((arm, dept))

            return teach_dept_dupli


        def teachers_depts_today(self, teacher):
            """ Returns a list of tuples of (arm, dept) for teacher object today """
            return self.teachers_n_depts_today_dupli().setdefault(teacher, [])


        def get_unique_teachers_depts_tday_assgn(self):
            """ Returns a dictionary Gets all the teachers who teach today (key) and the depts they teach(values)
            Does not allow for duplicates. """


            # First get the teacher-deptlist dictionary from the first class arm today and update with the rest
            all_teachers_tday = {}

            for teacher, depts_list in self.teachers_n_depts_today_dupli().items():
                all_teachers_tday[teacher] = set(depts_list)
                                                                                    
            # finally return the dictionary with teachers (as keys) and the list of depts and arms[as values]
            # for every class arm that features today

            return all_teachers_tday


        # IMPORTANT!!!!!
        def get_all_teachers_today(self):
            """ Returns a set of all teachers teaching today. dept or arm taught disregarded """
            return {teacher for teacher in self.get_unique_teachers_depts_tday_assgn()}

            

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

        def get_average_period_length_today(self):
            """ INT. returns the average length of all the periods of all the arms today """
            all_widths = [len(arm.periods.setdefault(self, [])) for arm in self.school_class_arms_today]

            return round(sum(all_widths)/len(all_widths))



        def __repr__(self):
            return self.day

        @property
        def full_name(self):
            return f"Day ID:{self.id}. {self.day}"


#------------------------------------------------------------------------------------------
# --------- Below are the static class methods and special methods, that help make some
# -- calculation or the other.
# -----------------------------------------------------------------------------------------

    def _remove_obj_from_list(list_obj, obj=None, id=None):
        """This function removes an object from the list given"""
        if obj:
            list_obj.remove(obj)
        else:
            del list_obj[int(id)]


    def _tuple_to_absolute(tuple, base=60):
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


    def _add_sub_time(time_tuple1, time_tuple2, add=True, base=60):
        '''
        Adds or subtracts two (hour, minute, seconds) tuples. time_tuple1 always is a tuple, 
        However, time_tuple2 couldbe an integer or a tuple, depending on if it is an actual time
        (rendered as a tuple) or duration.

        WORKS FOR BOTH TIME DIFFERENCE (BETWEEN TWO TIME TUPLES) AND TIME AND DURATION (TIME TUPLE AND AN INTEGER)!

        time_tuple2 is the duration for the period.
        '''

        if isinstance(time_tuple2, tuple):
            time2 = TimeTable.tuple_to_num(time_tuple2, base)
        else:
            time2 = time_tuple2
        # the above unpacks the tuple arguments.
        time1 = TimeTable.tuple_to_num(time_tuple1, base)
        
        # The above converts the time to absolute time in 
        # seconds
        if add:
            time3 = time1 + time2
        else:
            time3 = time1 - time2
        # Adds or subtracts the time depending on the add argument
        return TimeTable.num_to_tuple(time3, base)


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
             # Primarily, this part adds the time interval the start to get the end, and then the start updates to the end, so the next period begins 
            # at the end of the first!
            
            add_interval_tup = TimeTable.add_sub_time(start_iter, interval)

            #---- Adds the "interval tuple" to the start time tuple which is given as
            # one of the parameters to the function. It returns a time tuple.

            period_interval = indiv_time_bounds(start_iter, add_interval_tup)
            period_interval_list.append(period_interval)

            # -- update the start_iter variable with the end of the previous period below
            start_iter = add_interval_tup

        return period_interval_list
        
        
    def _to_base(num, base=60):
        '''Converts a number "num" to base "base" and renders it as a tuple of place values according to
        said base. Returns the time tuple '''
        
        # valid, ans_list, number = True, [], num % 86400
        ans = []
        while num > 0:
            num, rem = divmod(num, base)
            ans.insert(0, rem)

        return tuple(ans)


    def _stringify(num):
        """ static function to assign letters of the alphabet to class arms based on the class arm local_identifier """
        alph_list = [k for k in string.ascii_uppercase]
        width = len(alph_list)

        if num >= width:
            w_num = num - width
            if w_num == 0:
                w_num_tuple = (0,)
            else:
                w_num_tuple = TimeTable.num_to_tuple(w_num, width)
            
            if len(w_num_tuple) <= 1:
                w_num_tuple = [0] + list(w_num_tuple)
                w_num_tuple = tuple(w_num_tuple)
        else:
            if num == 0:
                w_num_tuple = (0,)
            else:
                w_num_tuple = TimeTable.num_to_tuple(num, width)
        ans = ""
        for k in w_num_tuple:
            ans += alph_list[k]
        return ans



    @staticmethod
    def to_time_str(t_tuple):
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


    stringify = staticmethod(_stringify)
    remove_from_list = staticmethod(_remove_obj_from_list)
    split_into_periods = staticmethod(_boundary_split_into_periods)
    add_sub_time = staticmethod(_add_sub_time)
    tuple_to_num = staticmethod(_tuple_to_absolute)  # takes in Time tuple, (h,m,s) as arg to yield number.
    num_to_tuple = staticmethod(_to_base) # Also time tuples
