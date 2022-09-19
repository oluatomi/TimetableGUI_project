# - ************************************************************************
# ------ WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.
# *************************************************************************
# -- All rights reserved!


# ------- This module is to manage the generation of classes, periods, 
# ------- depts and sort them accordingly
# ------------------------------------------------------
from collections import Counter, namedtuple
from Tt_models import TimeTable
import Tt_algo_calc, Tt_exceptions
from Tt_algo_calc import XLXReflection, SortAlgorithms
import itertools


class TimetableSorter:
    """
    This is the class to MANAGE all the implementations of the 
    sorting algorithms defined above. The timetable class, instantiated in the 
    GUI controller (perhaps) is passed here for necessary operations
    """
    
    def __init__(self):
        self.tt_obj = TimeTable()

        # A dictionary with {day:Arm_and_chunked_val dict}--- for that day
        self.All_Arms_and_chunked_val = {}
        # A dictionary with {day:Teacher_and_Chunked val}
        self.All_Teachers_and_chunked_val = {}

        # A dict of teacher:his particulars i.e. list of tuple(day_obj,namedtuple(dept, chunk, arm))
        self.displaced_teachers = {}

        # A dict to hold day: ArmPeriodsLeft dictionary for all the classes for that day
        self.All_Armperiodsleft = {}

        # declare namedtuples to hold values
        self.arm_n_chunk = namedtuple("particulars", "dept, chunk, teacher")
        self.teacher_n_chunk = namedtuple("t_particulars", "arm, chunk, dept")
    # ---------------------------------------------------------------------


    def department_shredder(frequency, recur=1):
        """
            This function "shreds" or "chunks" the frequency of the subject upon which it is used into 
            packets that can be inserted into different days of the week. i.e. this function helps to 
            split the total frequency per week of a subject into the days within the week.

            the frequency, often chunked into 1s (single periods) can also be chunked into 2s (double periods)
            or "n"s. The "recurr" parameter handles that. recurr is 1 for singles and so on.
        """
        a,b = divmod(frequency, recur)
        val = [recur for _ in range(a)] + [b] if b else [recur for _ in range(a)]

        return val, a+b



    def Translate_list_items(list_arg, item=None, index=None, base_index=0):
        """ This static function rotates the elements in a list by taking an 'item' or 'index' if provided 
        and moving to the position 'base_index' 
        
        item and index should not be provided at the same time. However, if done, the function defaults to 'item'
        """

        # The rotate_list static function!
        if item:
            item_index = list_arg.index(item)

        else:
            item_index = index
        
        # The difference between your index and the base index
        diff = item_index - base_index
        list_len = len(list_arg)

        # Shift everything aside by diff after getting the list of all the indices
        
        # Make a dictionary mapping each item to its index
        l_dict = {item: list_arg.index(item) for item in list_arg}

        for index in l_dict:
            # Shift everything aside by diff

            l_dict[index] = (l_dict[index] - diff) % list_len

        # Get the dictionary.items into a list so you can sort
        rot_list = list(l_dict.items())
        rot_list.sort(key=lambda key_val: key_val[-1])

        return [item for item, index in rot_list]


    class DeptPeriodEncase:
        """ A very simple class to hold each department, its frequency and its "chunk" value
        for ease of sorting """
        def __init__(self):
            self.dept_obj = None
    
        
        def get_spread(self):
            """Returns the number of packets the department's frequency has been chunked into"""
            spread = TimetableSorter.dept_shredder(self.frequency, self.chunk)
            return spread


        def teacher(self, arm):
            return self.dept_obj.teachers_for_client_class_arms[arm]

        @property
        def is_single(self):
            if self.chunk > 1:
                return False
            return True

        def __str__(self):
            return self.dept_obj

        def __repr__(self):
            return self.dept_obj.dept_name


    # ---------------------------------------------------------------------------------------
    class ArmPeriodsLeft:
        """Holds temporarily a numerical value for all the periods available in a class arm.
        This is a simple (relatively) helper class to help the 'chunking' process. """

        def __init__(self, class_arm, day_obj):
            self.class_arm = class_arm
            self.day = day_obj
            # list of arms periods today
            self.periodslist_today = self.class_arm.periods[day_obj]

            # number of periods of arm today
            self.periodlength_today = len(self.periodslist_today)

            # returns the number of available periods today as a list of integers from 0 to len -1
            self.periodsint_list = list(range(self.periodlength_today))

            self.todays_unique_depts = list(set(day_obj.get_all_depts_for_arm_today(class_arm)))
    

        def pop_out_period_val(self, val):
            """Remove out a period number or a list value from the periodsint_list"""

            if isinstance(val, list):
                # If "val" is a list, remove all the items in turn
                for e_item in Tt_algo_calc.strip_list_wrapper(val):
                    self.periodsint_list.remove(e_item)
            else:
                # If it is an integer
                self.periodsint_list.remove(val)


        def list_after_pop(self):
            """Returns the list, preferably after the popping has been done"""
            return self.periodsint_list


        def pop_out_dept(self, dept_obj):
            """Remove a dept from the list of depts today (after it has been chunked)"""

            self.todays_unique_depts.remove(dept_obj)

        def reconstitute(self):
            """ Run the init method all over again """
            self.__init__()

        
        # Onward, the self.periodintlist variable can be edited according to what is required of the chunking
    def prep_dept_freq(self, class_arm_obj, iterable_from_gui):
        """ This method accepts the 'dept', 'frequency' and 'chunk' values from the GUI controller
        amd makes each item an instance of the DeptPeriodEncase class

        The iterable_from_gui is a list of named tuples """

        container_list = []

        for item in iterable_from_gui:
            cont = self.DeptPeriodEncase()
            cont.dept_obj = item.dept
            cont.frequency = item.frequency
            cont.chunk = item.chunk
            container_list.append(cont)

        # --Sort the items in the container_list based on how many packets it has been chunked into

        container_list.sort(key=lambda item: item.frequency, reverse=True)
        return container_list


# ------------------- GENERATED PERIODS ----------------------------------------
    def generate_periods_classarms(self,day_obj,class_arm_obj, start, end, n):
        """This method generates the periods given a day, for a given class arm by chunking its 
        start and end times into 'n' amounts of equal periods."""

        gen_periods = self.tt_obj.split_into_periods(start, end, n)
        val = []

        for period in gen_periods:
            val.append(self.tt_obj.create_period(period.start, day=day_obj, end=period.end, sch_class_arm_obj=class_arm_obj, 
        dept_=None, is_fav=False, duration=0, spot=None, title_of_fav=None))
        return val



    def generate_periods_classarms_weekdays(self, class_arm_obj, start_per_day, end_per_day, n, days_list):
        """Generates periods for every day of the week for a given class arm, by generating for 
        each day (in the method defined above) """

        if days_list:
            week = []
            for each_day in days_list:
                week.append({each_day: generate_periods_classarms(each_day,class_arm_obj, start_per_day, end_per_day, n)})
            return week



    def update_periods_after_insertion(self, period_list, boundary_thickness=(0,0,0)):
        """ This method updates all the start and end times of the list of periods for a classarm for a 
        single day in case some custom insertions were made that messed up the order. The boundary thickness 
        determines whether the periods are contiguous or have some space (interval) in between.

        this doesn't need a day object or a class arm argument """

        for index in range(1, len(period_list)):
            # Convert the start of the second_period to the end of the first and 
            # updates the end times according to the duration till the end.
            period_list[index].start = TimeTable.add_sub_time(period_list[index - 1].end, boundary_thickness)
            period_list[index].end = TimeTable.add_sub_time(period_list[index].start, period_list[index].duration)



    def generate_periods_given_duration(self, class_arm, day,start, duration,freq, nonacad_tuple=None, boundary_interval=(0,0)):
        """ Generates periods along with nonacademic periods given start and duration. freq denotes the frequency of the normal periods.
         """
        # stretch out all the durations of the frequencies into one thin strip (i.e. duration in frequency places)
        total_duration = TimeTable._tuple_to_absolute(duration) * freq
        end = TimeTable.add_sub_time(start, TimeTable._to_base(total_duration, 60))

        academic_periods = self.generate_periods_classarms(day,class_arm, start, end, freq)
        # now insert the special (non-acad periods)

        all_periods = self._insert_nonacad(academic_periods, nonacad_tuple)
        # Just to help print it out
        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)
        return all_periods



    def generate_periods_given_acadspan(self, class_arm, day, start, limit, freq, nonacad_tuple, boundary_interval=(0,0)):
        """ Generates academic periods between start and limit. That is before fixing the special (nonacad) periods Duration
         is calculated implicitly """
        academic_periods = self.generate_periods_classarms(day,class_arm, start, limit, freq)
        # insert non-acad (special) periods
        all_periods = self._insert_nonacad(academic_periods, nonacad_tuple)

        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)
        return all_periods



    def generate_periods_given_abs_constraints(self, class_arm, day, abs_start, abs_end, freq, nonacad_tuple, boundary_interval=(0,0)):
        """ Generates periods with the non-acads and all, with end point fixed """

        # Get sum the non-academic periods durations first
        sum_dur = (0,0)

        for _, positions, duration in nonacad_tuple:
            for _ in positions:
                sum_dur = TimeTable.add_sub_time(sum_dur, duration)

        # Subtract this sum of durations time from the span, i.e. end - start
        span = TimeTable.add_sub_time(abs_end, abs_start, add=False)
        # What is left of the span when non-acads durations have been removed
        sub_span = TimeTable.add_sub_time(span, sum_dur, add=False)
        # Add this sub_span to abs_start to get the limit of the academic periods
        limit = TimeTable.add_sub_time(abs_start, sub_span)
        # Now generate periods
        academic_periods = self.generate_periods_classarms(day, class_arm, abs_start, limit, freq)
        # insert non-acad (special) periods
        all_periods = self._insert_nonacad(academic_periods, nonacad_tuple)

        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)
        return all_periods



    # ----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    def _insert_nonacad(self, academic_periods, nonacad_tuple):
        """ Inserts the non-academic periods into the already generated normal (academic) periods.
        The nonacad_dict is a a tuple with of form:  (nonacad_name(str), [positions (int)], duration_nonacad(time tuple)).
        THE duration_nonacad IS A TIME-TUPLE
        """
        academic_periods = academic
        nonacads = []

        for non_acad, poslist, duration_nonacad in nonacad_tuple:
            for position in poslist:
                # Create the non-academic period
                nonacad_period = self.tt_obj.create_period(start=(8,0,0), day=day, end=None, sch_class_arm_obj=class_arm, dept_=None, is_fav=True,
                    duration=duration_nonacad,spot=None, title_of_fav=non_acad)
                nonacads.append((position, nonacad_period))

        # Now insert all of these nonacads contents into the main list
        for position, nonacad_period in nonacads:
            academic_periods.insert(position - 1, nonacad_period)

        return academic_periods
        # --------------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------

                                                                                    # def generate_normal_n_special_in_time_bound(self, spec_periods_dict, day_obj, class_arm, start, end, n=None, total=None, bound=(0,0)):
                                                                                    #     """This method generates periods for a given day for a classarm if the absolute start
                                                                                    #     and end times are given.
                                                                                    #     The 'spec_periods_dict' is a dictionary that holds the special periods as keys and their
                                                                                    #     position in the list as the value.

                                                                                    #     'n' (if given) is the frequency of normal periods excluding the specials, so not an absolute boundary.
                                                                                    #     'total' (if given) is the total number of periods for the day, including the special periods
                                                                                    #     """

                                                                                    #     periods_list = []
                                                                                    #     # make first period with "start", the rest with duration






                                                                                    #     # The span of the entire day
                                                                                    #     span = TimeTable.tuple_to_num(TimeTable.add_sub_time(end, start, add=False), 60)
                                                                                    #     # The above subtracts the end from the start

                                                                                    #     dur = (0,0,0)

                                                                                    #     # This sums up the durations of all the special periods
                                                                                    #     for period, pos in spec_periods_dict.items():
                                                                                    #         for _ in range(len(pos)):
                                                                                    #             dur = TimeTable.add_sub_time(dur, period.duration)


                                                                                    #     abs_dur = TimeTable.tuple_to_num(dur, 60)
                                                                                    #     # the sum of the durations of the special periods is subtracted from the span.
                                                                                    #     # and made into the 'end' for the normal periods. so we can start splitting
                                                                                    #     diff = span - abs_dur
                                                                                    #     diffy = TimeTable.add_sub_time(start, diff)

                                                                                    #     if total:
                                                                                    #         n_ = total - len(spec_periods_dict)
                                                                                    #     elif n:
                                                                                    #         n_=n
                                                                                    #     elif not total and not n:
                                                                                    #         raise ValueError

                                                                                    #     all_periods = self.generate_periods_classarms(day_obj,class_arm, start, diffy, n_)



                                                                                    #     # Inserting the special periods into the specified positions, whilst subtracting 1 to account for zero-based index
                                                                                    #     for period in spec_periods_dict:
                                                                                    #         all_periods.insert(spec_periods_dict[period] - 1, period)

                                                                                    #     # -- At this point, the start and end of all these periods is messed up.
                                                                                    #     # It needs to be updated. So we call the method defined earlier.
                                                                                    #     self.update_periods_after_insertion(all_periods, boundary_thickness=bound)
                                                                                    #     # Just to be certain

                                                                                    #     # return all_periods


    def set_deptpacket_into_day_per_class_arm(self, class_arm, iterable_from_gui):
        """ Places the depts for each class arm into days of the week.
            This function is a more robust form of the "chunk_x_into_y" function 
            defined above. It tries to chunk x into y, but if it can't, because the day is already full,
            it just moves to the next day.
            This function is specifically for chunking packets into days, not sorting teachers into periods 
        """


        # ---------------------------------------------------------------------------------------------------
        # ---- The sorted list of the departments and their spreads (frequencies and all). ----

        # List of all the algorithms to be used to sort the classes (so all the classes do not get sorted the exact same way)

        self.algor_list = [Tt_algo_calc.DXLXReflection, Tt_algo_calc.DCenterCluster, Tt_algo_calc.DLeapFrog]

        # The 'arm_algo_index' is implemented so as to ensure that neighbouring arms do not use the same
        # day 'packeting' algorithm. It does this by picking out the index of the arm in the list of school
        # class arms INDEX and finding INDEX % length of the list of algos
        # This way, the algroithms are applied in a cycle within this class and not from some for loop outside
        # in the 'Tt_mini_test' module


        arm_algo_index = self.tt_obj.list_of_school_class_arms.index(class_arm) % len(self.algor_list)


        # Every item here is an instance of the DeptEncase class
        arm_chunk_array = self.prep_dept_freq(class_arm, iterable_from_gui)
        
        # list to accept all the dept objects that end up put in a day
        day_objs_list = class_arm.get_class_arm_days

        days_int = len(day_objs_list)

        all_days_contlist = [list() for _ in range(len(day_objs_list))]

        # The depts that do not get fixed into a day because everywhere is filled or previously occupied hy itself
        falls_through = []

        
        for dept in arm_chunk_array:

            # Retrieves the index postions that the chunking function yields (that is, the days to put stuff in)
            positions = self.algor_list[arm_algo_index].chunk_x_into_y(dept.get_spread()[1], 
                len(dept.teacher(class_arm).teaching_days_s))

            # Shifts everything backwards by 1 so it can be zero-indexed!
            positions = [x-1 for x in positions]

            # Determine the very day in which the teacher does not teach by the subtracting the set of all days
            # from the set of teachers's days
            free_day = set(self.tt_obj.list_of_days) - dept.teacher(class_arm).teaching_days_s
            #-------------------------------
            # create a list of all the indices of all the items from the free day container (set in this case)
            f_days_index = [self.tt_obj.list_of_days.index(f_day) for f_day in free_day]


            # Apply the "spreadover" function to situate positions considering the index of the day_item
            # in which the teacher does not teach
            positions = Tt_algo_calc.spread_over(positions, f_days_index)

            # Adds a dept to the list in the position of "index" in the all_days_contlist
            for index, item in enumerate(positions):

                # index stands for the index of the day in the list of positions
                # item is the actual number in the position list (which also happens to be the index of the all_days_contlist)
                # Adds in the dept for the amount of the packet size

                try:
                    for _ in range(dept.get_spread()[0][index]):
                    
                        # Keep adding the depts till the list reaches the size of 10 (for testing)

                        if len(all_days_contlist[item]) < 10:
                            all_days_contlist[item].append(dept.dept_obj)

                        else:
                            # Loop through the list to find any day with available space which doesn't already have it.

                            for z in range(1, days_int):

                                curr_index = (item + z) % days_int

                                if not dept in all_days_contlist[curr_index] and len(all_days_contlist[curr_index]) < 10:
                                    all_days_contlist[curr_index].append(dept.dept_obj)
                                    break
                            else:
                                # Notes any department that falls through (gets no free space to be)
                                falls_through.append(dept)

                                # Assigns the department to a day anyway!
                                if len(falls_through) != 0:
                                    for day_item in all_days_contlist:
                                        if len(day_item) < 10:
                                            day_item.append(dept.dept_obj)
                                            break
                                    else:
                                        # If after all has been done, the department still falls through
                                        print(f"Can't help {dept.dept_obj.dept_name}")


                except Exception as e:
                    print(e)
                    print()
                    print(f"Problem with {dept.dept_obj.dept_name}: {dept.get_spread()} chunk: {dept.chunk}")


        # Put the contents of the all_days_contlist into the tentative

        for day_index, dept_list in enumerate(all_days_contlist):
            # Add each list of days into the classarm's tentative... attr (a dictionary)
            class_arm.temp_dept_holder_for_days[day_objs_list[day_index]] = dept_list


        return all_days_contlist, falls_through, class_arm
        # return class_arm.temp_dept_holder_for_days

    # ------------------------------------------------------------
    def teachers_depts_today_for_chunk(self, day_obj):
        """Gets all the teachers today from all the depts offered 
        today and puts them in a teacher:[arm,dept] dictionary. That is the depts they teach
        in the arms they teach them.

        This naturally includes all the duplicates."""

        # gets all the arms that feature today
        all_arms_today = day_obj.arms_today_list

        # instantiates the dictionary that will at last be returned
        teacher_depts_dict = {}

        for arm in all_arms_today:
            # get all the depts that feature today from each arm
            for dept in arm.temp_dept_holder_for_days[day_obj]:
                teacher = dept.teachers_for_client_class_arms[arm]

                # If its already in the dict, simply append
                if teacher in teacher_depts_dict:
                    teacher_depts_dict[teacher].append((arm, dept))
                
                # if it isnt, then make a new [dept]
                else:
                    teacher_depts_dict[teacher] = [(arm, dept)]


        return teacher_depts_dict


    def _nail_int_to_arms(self, day_obj):
        """Semi-private method. Makes (instantiates) ArmPeriodsLeft objects for all the class arms today. 
        This is to know which periods have already been nailed down to each teacher across the class arms during the chunking"""

        # All the class arms today
        all_arms = day_obj.arms_today_list

        # make instances of the ArmsPeriodsLeft or whatever class
        return {arm:self.ArmPeriodsLeft(arm, day_obj) for arm in all_arms}


    def Algosort_teachers_per_day(self, day_obj, algorithm, reference_arm=None,reference_arm_index=0):
        """
        Does the Principal sorting of the teachers with the prescribed algorithm
        into periods such that the time-table parameters are met 
        
        """

        # First, get all the teachers that teach on a particular day
        # But really returns a dictionary of the teachers and the list of depts
        # The teachers can be extracted without a problem
        # A dict of teacher: arms and departments they teach

        def T_A_Reconstruct(arm_obj=None,teacher_obj=None,teachers_replace_list_arg=None, arms_replace_list_arg=None):
            """ Teeacher and Arm and chunked value dictionary reconstruction.
            This is a helper function to handle the dismantling and reconstruction of this teacher's chunk values in
            the Teacher_and_chunk_val dictionary, as wella as the arm's chunk values. It replaces old with the new."""

            # For each teacher's details and the replacement value

            if arm_obj:
                for index, details_repval in enumerate(zip(Arm_and_chunked_val[arm_obj], arms_replace_list_arg)):
                    dept, teacher = details_repval[0].dept, details_repval[0].teacher

                    replace_val = self.arm_n_chunk(dept, details_repval[1],teacher)

                    # Now update with the replaced value at position index
                    Arm_and_chunked_val[arm_obj][index] = replace_val


            if teacher_obj:
                # Replace teacher with new chunk values and stuff
                for index, details_repval in enumerate(zip(Teachers_and_chunked_val[teacher_obj], teachers_replace_list_arg)):
                    dept, arm = details_repval[0].dept, details_repval[0].arm

                    # This is (arm, new_chunk, dept)
                    replace_val = self.teacher_n_chunk(arm, details_repval[1], dept)
                    # Replace this teachers values at position 'index'
                    Teachers_and_chunked_val[teacher_obj][index] = replace_val
        # -------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------
            # OUTSIDE THE FUNCTION


        todays_teachers = day_obj.get_unique_teachers_depts_tday_assgn()
        # This is a dict of teacher:(arm,dept) for all depts offered today, naturally with all the duplicates
        todays_teachers_arm_depts_dupli = day_obj.teachers_n_depts_today_dupli()

        print("-_-"*30)
        # print(f"These are all depts offered today in their arms: {todays_teachers_arm_depts_dupli}, with length: {len(todays_teachers_arm_depts_dupli)}")
        # return


        # todays teachers(keys) with the duplicates of depts (value) (a dictionary)
        todays_teachers_dupli = {}

        # populate "todays_teachers_dupli" by adding only depts and its duplicates
        for teacher, arm_dept_list in todays_teachers_arm_depts_dupli.items():
            # print(f"in question: {todays_teachers_arm_depts_dupli.items}")

            for arm_dept in arm_dept_list:
                if teacher in todays_teachers_dupli:
                    # Adds dept only to the todays_teachers_dupli dictionary
                    todays_teachers_dupli[teacher].append(arm_dept[1])
                else:
                    todays_teachers_dupli[teacher] = [arm_dept[1]]

        print()
        # print(f"This todays_teachers_dupli: {todays_teachers_dupli}")

        # The all_depts_today variable is messy but True.
        # it comes with all the duplicates (repeated depts during the chunking per day, for all the days)
        all_depts_today = day_obj.get_all_depts_today()


        todays_teachersonly_list = [person for person in todays_teachers]
        # the below returns a dictionary with the number of periods as value and the arm as the key
        all_armsperiods_today_dict = day_obj.all_sch_class_periods_for_today()

        # Find the average of the length of the periods of all the classes for today
         # to get the average period length for chunking
        avg_period_len = sum([len(all_armsperiods_today_dict[arm]) for arm in all_armsperiods_today_dict]) // len(all_armsperiods_today_dict)
        

        # --------------------------------------------------
        # BEGIN THE SORT FOR ALL TEACHERS TODAY!!!

        # create a dictionary housing the teacher object and the list holding their count (how much 
        # they occur) for the day so we can start chunking based on that
        count_dict = {}
        
        # ------------------------------------------------------------------------------------

        def ATPG_sort(teacher=None, dept_obj=None):
            # The function used to sort the teachers based on how 'critical their courses are'

            if teacher:
                # gets all the 'dept_ATPG' values of the depts that feature today that the teacher teaches
                sort_depts=[dept.dept_ATPG() for dept in teacher.teachers_department_list if dept in all_depts_today]

                # Find the average of all the items in the list and return that
                return sum(sort_depts) // len(sort_depts) if bool(sort_depts) else 0

            # if the dept_obj instead is given, sort by the ATPG value of the dept_obj
            return dept_obj.dept_ATPG()
            
        # ------------------    teachers_chunked.sort(key=lambda teacher_tup: ATPG_teachersort(teacher_tup[0]))

        # A refence class arm is needed to help be the anchor for our chunking. jss1_A by default (position 0)
        # The below is a list generated by rotating around the list of all arms today till the reference class comes to position zero
        if reference_arm:
            ref_arm = reference_arm
        else:
            ref_arm = day_obj.arms_today_list[reference_arm_index]


        self.list_from_reference_arm = TimetableSorter.rotate_list(day_obj.arms_today_list, item=ref_arm)
        
        # the below is a dict with the arm:ArmPeriodsLeft()
        ArmsPeriodsLeft_objs = self._nail_int_to_arms(day_obj)


        # THIS SPECIAL DICTIONARY HOLDS ALL THE ARMS AND THEIR CHUNKED VALUES (WHEN THEY HAVE FINALLY BEEN CHUNKED)
        # IT IS {arm:[(dept,chunked_vals)]}
        Arm_and_chunked_val = {arm:[] for arm in self.list_from_reference_arm}

        # Also, this is {teacher:arm,dept, chunk}
        Teachers_and_chunked_val = {teacher:[] for teacher in todays_teachers}

        # =========================================
         # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}
            # --------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------
        # Teachers already handled so we dont handle them
        touched_teachers = []
        # visited = []
        # visited_ = []

        def arms_teachers_sort(ref_arm, array=avg_period_len):
            """ Handles the bulk of the sorting for a class arm """

            # print(f"THIS IS REF-ARM: {ref_arm}")
            
            # First, collect all the unique depts offered today by the reference arm sorted by the ATPG criterion
            
            # base_dept_list = sorted(ArmsPeriodsLeft_objs[ref_arm].todays_unique_depts, key=lambda dept_: ATPG_sort(dept_obj=dept_))
            base_dept_list = sorted(day_obj.get_depts_of_arm_today(ref_arm, duplicate=False), key=lambda dept:dept.dept_ATPG(), reverse=True)
            print(f"Base_dept_list:{base_dept_list}, Length of base_dept_list : {len(base_dept_list)}")
            print(f"With all the duplicates: {ref_arm.temp_dept_holder_for_days[day_obj]} for {ref_arm}")

            # ----------------------------------------------------------------------------------
            # create a list of dictionaries of the teachers in the base class and the classes they teach and their chunk number
            ref_arm_teachers = []
            teachers_chunked = {}

            # ==========================================
            # The variable below serves as a counter for the space by which the chunk values should be shifted
            # It records how much it has shifted over the past teachers and increments by the length of the previous item (teacher) in the for-loop below
            # ---------------------------
            # Note that the real shift_values contained in the ArmPeriodsLeft_objs dictionary for this arm are being changed the moment it
            # has been occupied by a teacher

            shift_val = 0
            # ALso, the ArmsPeriodsLeft objects for all the class arms, so that when a teacher is chunked into the base class, every other
            # class arm he teaches is also noted as occupied in its particular period

            
            for index, dept in enumerate(base_dept_list):
                # Find the teachers of these courses
                teacher = dept.teachers_for_client_class_arms[ref_arm]

                # It teacher has already been chunked with all the arms he's teaching, kindly exclude him
                # if teacher in [elem.teacher for elem in Arm_and_chunked_val[ref_arm]]:
                if teacher in touched_teachers:
                    continue

                touched_teachers.append(teacher)
                # -----------------------------------------------------------------------
                # The inner Counter is for counting the occurences of depts in the teacher key-val pair
                # Then the values() are retrieved which are nums like 'dict_blah_blah [1,1,1] or [2,2,2] for the nums'
                # Then we make a counter object for that as well to know the frequency of the nums which returns the
                # value of the {single(or double): how many it is}

                # print(p_singDoub)
                chunk_for_arm = todays_teachers_arm_depts_dupli[teacher]
                # print(f"This is teachers chunk for arm: {chunk_for_arm} for Teacher: {teacher}")

                # count_dict is a dict object!!!
                # The Count_with_order function is used instead of counter, to preserve the order of the items
                count_dict[teacher] = Tt_algo_calc.Count_with_order(list((Tt_algo_calc.Count_with_order(todays_teachers_arm_depts_dupli[teacher])).values()))
            
                print(f"This is the count_dict for chunking: {count_dict[teacher]} for Teacher: {teacher}")                
                
            # -------------------------------------------------------------------------------------------------
            # --------------------------- FEED INTO THE CHUNKING ALGORITHM ------------------------------------
            # -------------------------------------------------------------------------------------------------
                # Shift with the int_values of the ArmsPeriodsLeft_objs of the arm so we can keep track of which ones have been poppwd when occupied2
                
                # this_teacher = algorithm.doubles_and_singles(p_singDoub.single, p_singDoub.double, array, 
                #     shift_value=ArmsPeriodsLeft_objs[ref_arm].periodsint_list[shift_val])

                this_teacher = algorithm(array,chunk_list=count_dict[teacher], shift_value=shift_val)
                print(f"This is this_teachers chunk: {this_teacher}")


                print(f"Depts set: {len(todays_teachers_arm_depts_dupli[teacher])} .This teachers chunk: {this_teacher}")
                print("-"*40)
                # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}

            
                for arm_dept, chunk in zip(Tt_algo_calc.Set_with_order(todays_teachers_arm_depts_dupli[teacher]), this_teacher):
                                            # dept, chunk, teacher
                    holder = self.arm_n_chunk(arm_dept[1], chunk, teacher)
                    t_holder = self.teacher_n_chunk(arm_dept[0], chunk, arm_dept[1])
                        # if it already exists, extend it by this much...
                        #   arm as key

                    Arm_and_chunked_val[arm_dept[0]].append(holder)
                    # Arm_and_chunked_val[arm_dept[0]] = [holder]
                        # Register this teacher and his chunk vals and his arms (are his depts necessary?) in the dictionary defined up up above
                    Teachers_and_chunked_val[teacher].append(t_holder)
                
                
                # print("_-"*30)
                # print(f"Check length of teacher against his chunk: {len(Teachers_and_chunked_val[teacher])} and {len(this_teacher)}")

                # print(f"Comparing: {Arm_and_chunked_val[ref_arm]} and {[elem.chunk for elem in Teachers_and_chunked_val[teacher] if elem.arm == ref_arm]}")



                # shift_val is the value to shift by which is the length of all the previous chunk lists
                temp_ = []
                for detail in Arm_and_chunked_val[ref_arm]:
                    temp_.append(detail.chunk)
                
                # Get the absolute highest value in the list for the chunked values for this arm so we can shift by that
                shift_val = len(Tt_algo_calc.strip_list_wrapper(temp_))
           
            # =---------------------------------------
            # print("Length of Arms_and_chunked_val for ref arm today")
            # print(len(Arm_and_chunked_val[ref_arm]), [elem.chunk for elem in Arm_and_chunked_val[ref_arm]],
                # len(Tt_algo_calc.strip_list_wrapper([elem.chunk for elem in Arm_and_chunked_val[ref_arm]])))

            # ------------------------------------------------------------------------------------------------------------------

            # 1. Go through all the periods in the ref_arm and "Moveover" the periods chunk values for good measure
            refarm_periods = Tt_algo_calc.Set_with_order([elem.chunk for elem in Arm_and_chunked_val[ref_arm]])

            print()
            print(f"Ref_arm periods: {refarm_periods} for arm: {ref_arm}")
            print()

            # Now move them over to avoid  any overlaps
            refarm_periods = Tt_algo_calc.Moveover(refarm_periods, array)
            print(f"Updated ref_armPeriods: {refarm_periods}")
            print(f"Day is: {day_obj}")
            print()

            # Moveover is now done! Reconstitute the Arm_and_chunked val dictionary with this
            T_A_Reconstruct(arm_obj=ref_arm, arms_replace_list_arg=refarm_periods)
            # print(f"Updated Arms_and_chunk for refarm: {Arm_and_chunked_val[ref_arm]}")


            # 2. Reconstruct Teacher_and" at teacher... with the new value of the listarg in the ref_arm
            for elem in Arm_and_chunked_val[ref_arm]:
                # Pick the teacher for the ref_arm
                teacher = elem.teacher
                chunk = elem.chunk

                # Look for that teacher in this dict
                for index,elem2 in enumerate(Teachers_and_chunked_val[teacher]):
                    if elem2.arm == ref_arm:
                        # Replace the Teacher_andChunked_val at position index at the refarm
                        Teachers_and_chunked_val[teacher][index] = self.teacher_n_chunk(ref_arm, chunk, elem.dept)

                print(f"SEMI-DONE: {Teachers_and_chunked_val[teacher]}")


            # 3. Moveover each teacher in the ref_arm so no overlaps in a teacher's full sequence. but with its ref_arm periods fixed
            visited_ = []
            for elem in Arm_and_chunked_val[ref_arm]:

                teacher = elem.teacher
                if teacher in visited_:
                    continue

                visited_.append(teacher)

                # ----------------------------------
                fixed_chunk = []
                for elem in Teachers_and_chunked_val[teacher]:
                    if elem.arm == ref_arm:
                        if isinstance(elem.chunk, list):
                            fixed_chunk.append(elem.chunk.copy())
                        else:
                            fixed_chunk.append(elem.chunk)

                # --------------------------------
                all_chunk = []
                for elem in Teachers_and_chunked_val[teacher]:
                    if isinstance(elem, list):
                        all_chunk.append(elem.chunk.copy())
                    else:
                        all_chunk.append(elem.chunk)
                # ---------------------------------

                print(f"This is all_chunk: {all_chunk} and fixed: {fixed_chunk}")
                teacher_fixed = Tt_algo_calc.Moveover_fixed(all_chunk, array, fixed_item=fixed_chunk)
                print(f"Newly movedover: {teacher_fixed}")
                # Reconstitute this almost "perfect" teachers chunk list in Teachers_and_chunked_val
                T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=teacher_fixed)

            # 4. Try fixing each of these teachers chunks into periods of the class arm, and checking for possibilities if it breaks
            visited = []
            for elem in Arm_and_chunked_val[ref_arm]:
                teacher = elem.teacher

                if teacher in visited:
                    continue
                visited.append(teacher)

                t_chunk = [elem.chunk for elem in Teachers_and_chunked_val[teacher]]
                # ----------------------------------------
                teachers_chunk = []
                for elem in t_chunk:
                    if isinstance(elem, list):
                        teachers_chunk.append(elem.copy())
                    else:
                        teachers_chunk.append(elem)
                # ---------------------------------------------

                # The teachers stationary chunk. that is the chunk for this ref_arm
                teachers_fixed = [elem.chunk for elem in Teachers_and_chunked_val[teacher] if elem.arm is ref_arm]
                print(f"TEACHERS CHUNK FOR POSS COMBS: {teachers_chunk}, fixed: {teachers_fixed}, array: {array}")


                combinations = Tt_algo_calc.Possible_combs_with_fixed(teachers_chunk, teachers_fixed, array)
                print(f"Combinations with fixed: {combinations}")

                # A dictionary to record the number of times a segment goes free before it crashes
                crash_counter = {index: 0 for index,_ in enumerate(combinations)}
                worked = False

                for index, combo in enumerate(combinations):
                    T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=combo)
                    for segment in Teachers_and_chunked_val[teacher]:
                        arm = segment.arm
                        chunk = segment.chunk

                        try:
                            ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk)
                        except:
                            worked = False
                            print("SOMETHING CAME UP!")
                            break
                        else:
                            worked = True
                            crash_counter[index] += 1

                            print("Worked")
                    else:
                        # THE TEACHERS SEGMENT WORKED HERE! 
                        print(f"This combination worked: {combo}. This is worked: {worked}")
                        print(f"Crash combination FOR WORKED: {crash_counter}")

                        # Remove teachers subjects from the list of all the arms offering it. We are done with him
                        # for class_arm, chunk,dept in Teachers_and_chunked_val[teacher]:
                        #     # Go to the dict bearing all the arms and remove him from there
                        #     Tt_algo_calc.casual_removeall(class_arm.temp_dept_holder_for_days[day_obj], dept)

                        break

                # If despite all this, none of the combinations worked for the teacher's chunk
                else:
                    if not worked:
                        print(f"Crash combination: {crash_counter}")
                        # Get the least objectionable combination, i.e the combination with the highest segment count before it crashed
                        # Sort based on highest to lowest, grab the first item, and the second item of the first item which is the seg_count
                        best_fit_index = sorted(crash_counter.items(), key=lambda item: item[1], reverse=True)[0][1] if crash_counter else 0 

                        # Remove everything after the index of best_fit from the teacher
                        carryover = Teachers_and_chunked_val[teacher][best_fit_index:]

                        # Remove this teacher from the arms he is teaching in Arms_and_chunked_val
                        for detail in carryover:
                            arm, dept, chunk = detail.arm, detail.dept, detail.chunk

                            for elem in Arm_and_chunked_val[arm]:
                                if elem.teacher is teacher and elem.dept is dept:
                                    Arm_and_chunked_val[arm].remove(elem)

                        

                        Teachers_and_chunked_val[teacher][best_fit_index:] = []
                        # -------------------------------------------------------
                        # Remove teachers subjects from the list of all the individual arms offering it. We are done with him
                        for class_arm, chunk, dept in carryover:
                            # Go to the dict bearing all the arms and remove him from there
                                # print()
                            for _ in range(4):
                                print("*")
                            print(f"Before removeall: {class_arm.temp_dept_holder_for_days[day_obj]}")
                            Tt_algo_calc.casual_removeall(class_arm.temp_dept_holder_for_days[day_obj], dept)
                            print(f"After removeall: {class_arm.temp_dept_holder_for_days[day_obj]}")
                        # ---------------------------------------

                        # If the Teacher_and_chunked_val list is empty, remove it completely
                        if not Teachers_and_chunked_val[teacher]:
                            del Teachers_and_chunked_val[teacher]


                        # Add this carryover namedtuples to the dictionary of displaced teachers
                        if teacher in self.displaced_teachers:
                            self.displaced_teachers[teacher].append({day_obj:carryover})
                        else:
                            self.displaced_teachers[teacher] = [{day_obj:carryover}]

                        
                        break

    # -------------------------------------------------------------------------------------
            # Add the Arm_and_chunked_val to the overall dictionary for today
            self.All_Arms_and_chunked_val[day_obj] = Arm_and_chunked_val
            # Also add all the teachers who have had no problems so far -- ready teachers
            self.All_Teachers_and_chunked_val[day_obj] = Teachers_and_chunked_val
            # Also add ArmsPeriodsLeft to the overall dictionary dictionary for today
            self.All_Armperiodsleft[day_obj] = ArmsPeriodsLeft_objs
            
            for arm,period in ArmsPeriodsLeft_objs.items():
                print(f"Arms: {arm} --> Periods left: {period.periodsint_list}")

            print()
            print(f"Displaced teachers num: {len(self.displaced_teachers)}")
            print()

    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
    # OUTSIDE THE ABOVE FUNCTION
        for arm in self.list_from_reference_arm[:]:
            arms_teachers_sort(arm, array=10)


    def Sort_manager(self, algorithm, reference_arm=None):
        """This method handles the operation of the algo_sort for every day and handles displaced teachers by seeking to reassign them """

        for day_obj in self.tt_obj.list_of_days[:]:
            self.Algosort_teachers_per_day(day_obj, algorithm, reference_arm=reference_arm, reference_arm_index=0)
            
        for day_obj in self.tt_obj.list_of_days[:]:
            print()
            print("^"*40)
            for clist in self.All_Teachers_and_chunked_val[day_obj].values():
                print([elem.chunk for elem in clist])



        print(self.displaced_teachers)

        before = len(self.displaced_teachers)
        self.handle_displaced_teachers()

        # for arm,period in self.All_Armperiodsleft[self.tt_obj.list_of_days[0]].items():
        #     print(f"Arms: {arm} --> Periods left: {period.periodsint_list}")

        print()
        print("DISPLACED TEACHERS")
        print(self.displaced_teachers)
        print()
        print(before, len(self.displaced_teachers))


    def handle_displaced_teachers(self):
        """Handles the insertion of displced teachers of a particular
        class arm into a new day since it cannot fit its home day."""

        # ---------------------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------------------
        # Inner class to update Teacher_and_chunked_val as well as Arm_and_chunked_val

        def update_teacher_and_arm(day, dept, new_chunk, teacher=None, arm=None):
            """ Inner function to put new chunk values into the teacher_and _chunked_val and Arm_and_chunked_val
            on a particular day. new_chunk from the arg is cast into a list that encloses the new chunk value, even if it was a list before.
            Hence the next line... """

            new_chunk_val = new_chunk[0] if len(new_chunk) == 1 else new_chunk
            if teacher:
                if teacher in self.All_Teachers_and_chunked_val[day]:
                    self.All_Teachers_and_chunked_val[day][teacher].append(self.teacher_n_chunk(arm, new_chunk_val, dept))
                else:
                    self.All_Teachers_and_chunked_val[day][teacher] = [self.teacher_n_chunk(arm, new_chunk_val, dept)]

            if arm:
                if arm in self.All_Arms_and_chunked_val[day]:
                    self.All_Arms_and_chunked_val[day][arm].append(self.arm_n_chunk(dept, new_chunk_val, teacher))
                else:
                    self.All_Arms_and_chunked_val[arm][teacher] = [self.arm_n_chunk(dept, new_chunk_val, teacher)]


        # -----------------------------------------------------------------------------------------------
        def patch_teachers(days_list, x_info=None):
            """ The function that finds an empty, non-overlapping spot to put teachers in """

            # ------------------------------------------------------------------
            if not self.handled:
                print()
                print(f"Yee-haw {x_info}")
                print()

                for day in days_list:
                    # check if arm has class on this day, (you know to be robust)
                    if arm in day.school_class_arms_today:
                        # check if teacher already teaches today
                        if teacher in self.All_Teachers_and_chunked_val[day] and self.All_Armperiodsleft[day][arm].periodsint_list:
                            # Since he does, get all of his pre-existing chunk values
                            pre_chunk = [elem.chunk for elem in self.All_Teachers_and_chunked_val[day][teacher]]
                            # get the unoccupied periods for arm today
                            un_occ = self.All_Armperiodsleft[day][arm].periodsint_list
                            # check which pices of un_occ do not overlap for certified chunk pieces
                            cert = [piece for piece in un_occ if not Tt_algo_calc.check_for_overlap(pre_chunk + [piece])]
                            print(f"No overlaps...: {cert}")
                        
                        # If teacher does not teach on this day
                        else:
                            cert = self.All_Armperiodsleft[day][arm].periodsint_list


                        if cert and len(cert) >= self.len_chunk:
                            # Add this len(cert)'s worth of chunk values into the teacher's credentials
                            update_teacher_and_arm(day, dept, cert[:self.len_chunk], teacher=teacher, arm=arm)
                            # ...and subbtract it from len_chunk
                            self.len_chunk = 0


                        elif cert and len(cert) < self.len_chunk:
                            # empty cert and put it into the teachers credentials
                            update_teacher_and_arm(day, dept, cert, teacher=teacher, arm=arm)
                            self.len_chunk -= len(cert)

                        # ------------------------------------
                        if self.len_chunk == 0:
                            self.handled = True
                            # Delete this teachers details from the record of displaced teachers
                            # ------------------------------------------------------------------
                            for elem in second_displaced[teacher][index][day_]:
                                if elem.arm == arm and elem.dept == dept:
                                    # print()
                                    # print(f"Disp teachers info: {self.displaced_teachers[teacher][index][day_]}")
                                    # print()
                                    self.displaced_teachers[teacher][index][day_].remove(elem)


            else:
                print("Begin again!!")
                print()
            # ------------------------------------------------------------
            # Delete teacher's details from displaced teachers if teacher has already been handled
            try:
                if not second_displaced[teacher][index][day_]:
                    self.displaced_teachers[teacher].remove(item)

                # If the day_chunk list (the big list right next to teacher is empty, remove the teacher)
                if not second_displaced[teacher]:
                    del self.displaced_teachers[teacher]
                    print()
                    print(f"Teacher: {teacher} safely removed")
            except Exception:
                pass
        # -----------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        

        second_displaced = self.displaced_teachers.copy()

        # Go to every teacher in the displaced teacher dict
        for teacher, day_chunk in second_displaced.items():
            # Note the day in which they were displaced

            # Days among teacher's teaching days in which he actually teaches
            work_day= [day for day in teacher.teaching_days if teacher in day.get_all_teachers_today_from_depts_assgn()]
            # Days among teachers teaching days in which he does not teach
            free_day = [day for day in teacher.teaching_days if teacher not in day.get_all_teachers_today_from_depts_assgn()]
            # days in which teacher may not come to work. He (ideally) shouldnt teach on this days
            over_day = [day for day in self.tt_obj.list_of_days]


            for index,item in enumerate(day_chunk):
                day_ = list(item.keys())[0]
                chunk_list = item.values()

                # print(f"This is day_ down: {day_}")

                for det in chunk_list:
                    # print()
                    # print(f"This is det {det, chunk_list}")
                    
                    for index_2,details in enumerate(det):
                        dept, arm, chunk = details.dept, details.arm, details.chunk
                        # length of the chunk
                        self.len_chunk = 1 if isinstance(chunk, int) else len(chunk)

                        # The teachers (arm, dept) tuple to search with in the teacher_dept_dupli blah blah variable
                        day_dupli_tuple = (arm, dept)
                        
                        # COMING BACK HERE!!!!
                        self.handled = False
                        patch_teachers(free_day, x_info="When I actually can.")
                        patch_teachers(work_day, x_info="Now on my works days")
                        patch_teachers(over_day, x_info="OVERTIME DAY")
                        if self.handled:
                            break

                    # In the event that the teachers details could not be reassigned to another day
                    else:
                        print()
                        print("TEACHER COULD NOT BE HANDLED!")

        # ---------------------------------------------------------------
        # Start deleting teachers who laready have been handled
        # Go to every teacher in the displaced teacher dict
        

                        


    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    # STATIC METHODS BELOW
    dept_shredder = staticmethod(department_shredder)
    rotate_list = staticmethod(Translate_list_items)



if __name__ == "__main__":
    print(TimetableSorter.rotate_list(list(range(1,16)), item=9, base_index=0))