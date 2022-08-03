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


    def generate_periods_classarms(self,day_obj,class_arm_obj, start, end, n):
        """This method generates the periods given a day, for a given class arm by chunking its 
        start and end times into 'n' amounts of equal periods."""

        gen_periods = self.tt_obj.split_into_periods(start, end, n)
        val = []

        for period in gen_periods:
            val.append(self.tt_obj.create_period(period.start, day=day_obj, end=period.end, sch_class_arm_obj=class_arm_obj, 
        dept_=None, is_fav=False, duration=0, spot=None, title_of_fav=None))

        return val


    def generate_periods_classarms_week(self, class_arm_obj, start_per_day, end_per_day, n):
        """Generates periods for every day of the week for a given class arm, by generating for 
        each day (in the method defined above) """

        week = []
        for each_day in self.tt_obj.list_of_days:
            week.append({each_day: generate_periods_classarms(each_day,class_arm_obj, start_per_day, end_per_day, n)})

        return week


    def special_period_insertion(self, class_arm, day_obj, period_obj, n):
        """This method is to help insert a period into a particular spot in the list of 
        periods for a day at the (n-1)th position"""

        pos = int(n) - 1
        class_arm.periods[day_obj].insert(pos, period_obj)


    def update_periods_after_insertion(self, period_list, boundary_thickness=(0,0,0)):
        """ This method updates all the start and end times of the list of periods for a classarm for a 
        single day in case some custom inserions were made that messed up the order. The boundary thickness 
        determines whether the periods are contiguous or have 
        some space in between.

        this doesn't need a day object or a class arm argument """

        for index in range(1, len(period_list)):
            # Convert the start of the second_period to the end of the first and 
            # updates the end times according to the duration till the end.
            period_list[index].start = TimeTable.add_sub_time(period_list[index - 1].end, boundary_thickness)
            period_list[index].end = TimeTable.add_sub_time(period_list[index].start, period_list[index].duration)


    def generate_normal_n_special_in_time_bound(self, spec_periods_dict, day_obj, class_arm, start, end, n=None, total = None, bound=(0,0)):
        """This method generates periods for a given day for a classarm if the absolute start
        and end times are given.
        The 'spec_periods_dict' is a dictionary that holds the special periods as keys and their
        position in the list as the value.

        'n' (if given) is the frequency of normal periods excluding the specials, so not an absolute boundary.
        'total' (if given) is the total number of periods for the day, including the special periods
        """

        # The span of the entire day
        span = TimeTable.tuple_to_num(TimeTable.add_sub_time(end, start, add=False), 60)
        # The above subtracts the end from the start

        dur = (0,0,0)

        # This sums up the durations of all the special periods
        for period in spec_periods_dict:
            dur = TimeTable.add_sub_time(dur, period.duration)

        abs_dur = TimeTable.tuple_to_num(dur, 60)

        # the sum of the durations of the special periods is subtracted from the span.
        # and made into the 'end' for the normal periods
        diff = span - abs_dur
        diffy = TimeTable.add_sub_time(start, diff)

        if total:
            n = total - len(spec_periods_dict)
        elif n:
            pass
        elif not total and not n:
            raise ValueError

        all_periods = self.generate_periods_classarms(day_obj,class_arm, start, diffy, n)



        # Inserting the special periods into the specified positions, whilst subtracting 1 to account for zero-based index
        for period in spec_periods_dict:
            all_periods.insert(spec_periods_dict[period] - 1, period)

        # -- At this point, the start and end of all these periods is messed up.
        # It needs to be updated. So we call the method defined earlier.

        self.update_periods_after_insertion(all_periods, boundary_thickness=bound)

        # Just to be certain

        # return all_periods


    def teachers_for_arms_today(self, day_obj):
        """ This method extracts all the teacher objects that feature on a particular day.
        But extracts also the classes they teach today, and not all the classes they teach as a whole """
        return day_obj.get_all_teachers_for_today()


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


        return all_days_contlist, falls_through
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
        arm_Armleft = {arm:self.ArmPeriodsLeft(arm, day_obj) for arm in all_arms}
        return arm_Armleft


    def Algosort_teachers_per_day(self, day_obj, algorithm, reference_arm=None,reference_arm_index=0):
        """
        Does the Principal sorting of the teachers with the prescribed algorithm
        into periods such that the time-table parameters are met 
        
        """

        # First, get all the teachers that teach on a particular day
        # But really return a dictionary of the teachers and the list of depts
        # The teachers can be extracted without a problem
        todays_teachers = day_obj.get_unique_teachers_depts_tday_assgn()

        # This is a dict of teacher:(arm,dept) for all depts offered today, naturally with all the duplicates
        todays_teachers_arm_depts_dupli = self.teachers_depts_today_for_chunk(day_obj)

        # print("-_-"*30)
        # print(f"These are all depts offered today in their arms: {todays_teachers_arm_depts_dupli}")


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

        # return

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


        # A quick single_double class to hold the values of singles and doubles for the approriate chunking
        class SingDoub:
            def __init__(self):
                self.teacher = None
                self.single = 0
                self.double = 0
                self.otherble = 0

        # singDoub_list = []
        
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
        # declare namedtuples to hold values
        arm_n_chunk = namedtuple("particulars", "dept, chunk, teacher")
        teacher_n_chunk = namedtuple("t_particulars", "arm, chunk, dept")
    # -----------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
        def arms_teachers_sort(ref_arm, array=avg_period_len):
            """ Handles the bulk of the sorting for a class arm """

            # print(f"THIS IS REF-ARM: {ref_arm}")
            
            # First, collect all the unique depts offered today by the reference arm sorted by the ATPG criterion
            base_dept_list = sorted(ArmsPeriodsLeft_objs[ref_arm].todays_unique_depts, key=lambda dept_: ATPG_sort(dept_obj=dept_))

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
                if teacher in [elem.teacher for elem in Arm_and_chunked_val[ref_arm]]:
                    continue
                # -----------------------------------------------------------------------
                # The inner Counter is for counting the occurences of depts in the teacher key-val pair
                # Then the values() are retrieved which are nums like 'dict_blah_blah [1,1,1] or [2,2,2] for the nums'
                # Then we make a counter object for that as well to know the frequency of the nums which returns the
                # value of the {single(or double): how many it is}

                # personal instance of the SingDoub class to record singles and doubles
                p_singDoub = SingDoub()
                # print(p_singDoub)
                chunk_for_arm = todays_teachers_arm_depts_dupli[teacher]
                # print()
                # print(f"This is chunk_for_arm: {chunk_for_arm}")

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

                # return f"This is this_teachers chunk: {this_teacher}"

                # print(f"This teachers chunk: {this_teacher}")
                # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}

                                    # # declare a namedtuple to hold values
                                    # arm_n_chunk = namedtuple("particulars", "dept, chunk, teacher")
                                    # teacher_n_chunk = namedtuple("t_particulars", "arm, chunk, dept")

                # define a quick class to hold the values in the namedtuple(which we may no longer need)


                for arm_dept, chunk in zip(Tt_algo_calc.Set_with_order(todays_teachers_arm_depts_dupli[teacher]), this_teacher):
                                            # dept, chunk, teacher
                    holder = arm_n_chunk(arm_dept[1], chunk,teacher)
                    t_holder = teacher_n_chunk(arm_dept[0], chunk, arm_dept[1])
                        # if it already exists, extend it by this much...
                        #   arm as key                         
                    Arm_and_chunked_val[arm_dept[0]] += [holder]
                        # Arm_and_chunked_val[arm_dept[0]] = [holder]

                # Register this teacher and his chunk vals and his arms (are his depts necessary?) in the dictionary defined up up above
                    Teachers_and_chunked_val[teacher] += [t_holder]
                
                # print()
                # print(Arm_and_chunked_val)
                # print("="*30)
                # print(Teachers_and_chunked_val)


                # shift_val is the value to shift by which is the length of all the previous chunk lists
                temp_ = []
                for detail in Arm_and_chunked_val[ref_arm]:
                    temp_.append(detail.chunk)
                
                # Get the absolute highest value in the list for the chunked values for this arm so we can shift by that
                shift_val = len(Tt_algo_calc.strip_list_wrapper(temp_))

                # print()
                # print(Arm_and_chunked_val[ref_arm])

                # Now moveover all the elements in the ref_arm (Because they might clash)

            ref_arm_list_in_prog = [elem.chunk for elem in Arm_and_chunked_val[ref_arm]]
            print()
            print(f"Old ref_arm_list in progress: {ref_arm_list_in_prog} for {ref_arm}")

            # NOW, "MOVEOVER" THE LIST ABOVE
            ref_arm_list_in_prog = Tt_algo_calc.Moveover(ref_arm_list_in_prog, array)
            print()
            print(f"New movedover: ref arm list in progress {ref_arm_list_in_prog}")
            print()
            # print(Arm_and_chunked_val[ref_arm])
            print()

            # MOVEOVER has been done, now replace this re_arms chunk value with the new movedover values
            try:
                for index,particular_new_chunk in enumerate(zip(Arm_and_chunked_val[ref_arm], ref_arm_list_in_prog)):
                    dept,teacher = particular_new_chunk[0].dept, particular_new_chunk[0].teacher

                    # Arm_and_... at position 'index'
                    Arm_and_chunked_val[ref_arm][index] = arm_n_chunk(dept, particular_new_chunk[1], teacher)
            except Exception:
                print("JUST TO KNOW WHAT IS GOING ON! where the error happened")
                print(Arm_and_chunked_val[ref_arm], ref_arm_list_in_prog)

            print()
            # print(f"Again :{Arm_and_chunked_val[ref_arm]}")

            # Also correct the Teacher_n_chunk with the new 'movedover' values

            # For all the teachers for this Arm today
            
            for elem in Arm_and_chunked_val[ref_arm]:
                teacher, dept,chunk = elem.teacher, elem.dept, elem.chunk

                for index,teacher_2 in enumerate(Teachers_and_chunked_val[teacher]):
                    if ref_arm == teacher_2.arm:
                        det = teacher_n_chunk(ref_arm,chunk, dept)

                        # Replace the old value with the new
                        # print()
                        # print("HERE BOYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                        
                        Teachers_and_chunked_val[teacher][index] = det


            # MOVEOVER each of the teachers in the ref_arm and update them in the Arms_chunk_val and in Teachers_chunk_val
            for elem in Arm_and_chunked_val[ref_arm]:
                teacher, dept,chunk = elem.teacher, elem.dept, elem.chunk
                
                # Grab this teacher in the Teachers_and_chunked_val
                full_chunk = [item.chunk for item in Teachers_and_chunked_val[teacher]]

                # grab the chunk for this ref_arm so we can use it as the const value for our moveover function
                part_chunk = [item.chunk for item in Teachers_and_chunked_val[teacher] if item.arm == ref_arm]
                # print(f"This is the part chunk:{part_chunk}, and full: {full_chunk}")

                # Now moveover_fixed with part_chunk as the const item
                print(f"This is part chunk: {part_chunk}")
                adjusted_chunk = Tt_algo_calc.moveover_fixed(full_chunk, array,fixed_item=part_chunk)
                # print(f"THIS IS THE MOVEDOVER_ADJ FIXED: {adjusted_chunk}")



                # Replace with these values in the Teacher_and_chunk_val dictionary
                replace_for_teacher = [teacher_n_chunk(arm, adj, dept) for arm, adj, dept in zip(
                    [teacher.arm for teacher in Teachers_and_chunked_val[teacher]],adjusted_chunk,
                    [teacher.dept for teacher in Teachers_and_chunked_val[teacher]])]

                # Replace the Teachers_and_chunk and Arm_and_chunk with these new and imporoved values
                # print()
                # print(f"Replace_for teacher: {replace_for_teacher}")
                Teachers_and_chunked_val[teacher] = replace_for_teacher

            # -----------------------------------------------------------------------------------------------
                
            # Also do the replacement for the Arm_and_chunk_val dictionary (for every teacher in the arm)
            arm_chunk = [tt.chunk for tt in Teachers_and_chunked_val[teacher] if tt.arm == ref_arm]

            # print(f"This is arm_chunk: {arm_chunk}")

            # Replace each item in Arm_chunk_val[ref_arm] with its old dept, new chunk (in arm_chunk), and old teacher
            list_from_armdict = Arm_and_chunked_val[ref_arm]

            for index,elem_chunk in enumerate(zip(list_from_armdict, arm_chunk)):
                dept, teacher = elem_chunk[0].dept, elem_chunk[0].teacher

                replace_val = arm_n_chunk(dept, elem_chunk[1], teacher)

                # Add in the replacement at position index
                Arm_and_chunked_val[ref_arm][index] = replace_val


            # print()
            # print(f"Arm_and_chunked[ref_arm] is very really this:")
            # print()
            # print(Arm_and_chunked_val[ref_arm])
            # print()

            # print("="*50)
            
            # print(f"NEW AND IMPROVED Arms_and_chunk_val")
            # print(Arm_and_chunked_val)
            # print()
            # print(f"NEW AND IMPROVED Teachers_and_chunked_val")
            # print(Teachers_and_chunked_val)
            # print()

            

            def Teacher_and_chunk_reconstruct(teacher_obj,replace_list_arg):
                """ This is a helper function to handle the dismantling and reconstruction of this teacher's chunk values in
                the Teacher_and_chunk_val dictionary. It replaces old with the new."""

                # For each teacher's details and the replacement value
                for index, details_repval in enumerate(zip(Teachers_and_chunked_val[teacher_obj], replace_list_arg)):
                    dept, arm = details_repval[0].dept, details_repval[0].arm

                    # This is (arm, new_chunk, dept)
                    replace_val = teacher_n_chunk(arm, details_repval[1], dept)
                    # Replace this teachers values at position 'index'
                    Teachers_and_chunked_val[teacher_obj][index] = replace_val
            # ------------------------------------------------------------------------------------------
            
            # --------------------------------------------------------------------------------------
            # OUTSIDE THE FUNCTION...

            # Go through all the teachers for this class arm (which are now perfect!?) and 
            # TRY removing all the chunked values, OR any COMBINATION that favours it and also remove the dept
            # from the list of arms. We are done with said teacher
            settled_teachers = []

            for index, elem in enumerate(Arm_and_chunked_val[ref_arm]):
                # print(f"This is elem: {elem}")
                teacher = elem.teacher

                # if index != 0:
                #     # If this teacher has already been treated before, skip them
                #     if teacher == Arm_and_chunked_val[ref_arm][index - 1].teacher:
                #         continue

                if teacher in settled_teachers:
                    continue

                # Add this teacher to the list of teachers that already have been touched
                settled_teachers.append(teacher)


                # The t_particulars of the teacher of interest, i.e. (arm, chunk and dept)
                # First gather all his chunk values
                all_teachers_chunk = [teacher_details.chunk for teacher_details in Teachers_and_chunked_val[teacher]]
                # The fixed part of the chunk, that is, all the chunks already settled for the reference arm
                fixed_var = [teacher_details.chunk for teacher_details in Teachers_and_chunked_val[teacher] if teacher_details.arm == ref_arm]

                # Returns all the possible arrangements including the original chunk values as the first item
                possible_arrangement = Tt_algo_calc.possible_combs_with_fixed(all_teachers_chunk, fixed_var, array)

                # length of the possible_arrangement variable
                poss_arr_length = len(possible_arrangement)
                count,loop = 0, True


                # dictionary with segment_number(value) and index (count) of teachers combination (key).
                teacher_crash_record = {x:0 for x in range(len(possible_arrangement))}

                while loop:
                    # Reconstitute up-top, first with the original value, or it it doesnt work, all the possible arrangements of the teacher's chunk

                    # The old ArmsPeriods_left values remaining before this teacher
                    # Doing this so that if a teacher crashes through despite all the combinations the ArmsPeriods_left is reconstituted
                    
                    # ----------------------------------
                    # periods_left_for_arm = ArmsPeriodsLeft_objs
                    # ---------------------------------------------

                    # If count does not exceed the length of the possible_arrangement variable
                    if count < poss_arr_length:     
                        Teacher_and_chunk_reconstruct(teacher,possible_arrangement[count])

                        # ----------------------------------
                        # The teacher crash record is only needed when none of the possible combinations fit, and so
                        # we choose the one that best fits (i.e. with hte most working segments) and record it up to the point where it breaks and go with that
                        # pushing the defaulting part to another day.

                        
                        segment_number = 0

                        # count for each segment
                        inner_count = 0

                        for teacher_particulars in Teachers_and_chunked_val[teacher]:
                            arm, chunk_val = teacher_particulars.arm, teacher_particulars.chunk


                            # Go to the arm in Armsleft... and Try removing chunk
                            try:
                                ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk_val)
                            except ValueError:
                                # Break out of the for-loop

                                # Let's see where this arrangement broke
                                print(teacher_crash_record[count])

                                print("NOPE! CRASHED! CHECKING FOR ANOTHER POSSIBLE ARRANGEMENT")
                                break

                            else:
                                # If it works fine, increase the segment number by 1
                                segment_number += 1
                                teacher_crash_record[count] = segment_number
                                print(f"WORKING COUNT: {teacher_crash_record[count]}")

                        
                        else:
                            # Satisfied! Outside the for loop and end the while loop ends!
                            # Teacher's combination works, then
            
                            # worked = True
                            print("--"*50)
                            print("WORKED! IT (FINALLY) WORKED")
                            loop = False

                            for details in Teachers_and_chunked_val[teacher]:
                                arm, dept = details.arm, details.dept

                                # POP out the department from the dictionary ArmPeriodsLeft_objs?

                                # ArmsPeriodsLeft_objs[arm].pop_out_dept(dept)

                                # todays_teachers_dupli is the list (is it?) of all the subjects taken by all teachers today ([math, math, eng,eng...])
                                # So we remove this dept from that list, since we've settled tit already
                                Tt_algo_calc.remove_all_sub_from_list(todays_teachers_dupli[teacher], dept)

                        count += 1
                    else:
                        # If the teachers combination does not fit and count has run past the number of possible arrangements for the teacher,
                        # that means it did not work, so break out of the loop
                        print("COULDN'T BE HELPED EVEN WITH COMBINATION. FIND ANOTHER SOLUTION!")
                        loop = False
                        print()
                        print(f"All the crashes: {teacher_crash_record}")

                        # Of all the elements choose which one  best fits that is the first one with the greatest value
                        best_fit = sorted(teacher_crash_record.items(), key=lambda item:item[1], reverse=True)[0]

                        # slice the Teachers_and_chu... list(at the teacher) at the index directly next to best_fit (i.e. where the error began)
                        best_fit = best_fit[1]

                        carryover = Teachers_and_chunked_val[teacher][best_fit:]

                        # del Teachers_and_chunked_val[teacher][best_fit:]
                        print()
                        print(f"Teachers carryover: {carryover}. Teacher's chunk left after pull out: {Teachers_and_chunked_val[teacher]}")


            print()
            # print(f"ArmsPeriodsLeft_objs: {[periods.periodsint_list for arms,periods in ArmsPeriodsLeft_objs.items()]}")
            for arm,period in ArmsPeriodsLeft_objs.items():
                print(f"Arms: {arm} --> Periods left: {period.periodsint_list}")


                # Sniff out this teacher from Teachers_and_chunk_val


    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
        all_classes = [arms_teachers_sort(arm) for arm in self.list_from_reference_arm[:]]
        # all_classes = arms_teachers_sort(ref_arm)
        return all_classes


    def summon_all(self,day_obj, algorithm, reference_arm=None,reference_arm_index=0):
        """Makes a dictionary of every class arm and its corresponding periods"""

        all_dict = {arm:[] for arm in self.list_from_reference_arm}
        chunk_in_mid_process = self.Algosort_teachers_per_day(day_obj, algorithm,reference_arm=reference_arm,reference_arm_index=reference_arm_index)

        for list_item in chunk_in_mid_process:
            for dict_item in list_item:
                for arm, chunk_vals in dict_item.items():
                    if not chunk_vals in all_dict[arm]:
                        all_dict[arm].append((chunk_vals))

        return all_dict
        # Now start collating
        

    def render_on_print():
        """Renders all the classes periods'chunk numbers so I can see them well"""
        pass


    # ------------------------------------------------------------------------------------------
    # STATIC METHODS BELOW
    dept_shredder = staticmethod(department_shredder)
    rotate_list = staticmethod(Translate_list_items)



if __name__ == "__main__":
    print(TimetableSorter.rotate_list(list(range(1,16)), item=9, base_index=0))