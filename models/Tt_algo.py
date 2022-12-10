# - ************************************************************************
# ------ WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.
# *************************************************************************
# -- All rights reserved!


# ------- This module is to manage the generation of classes, periods, 
# ------- depts and sort them accordingly
# ------------------------------------------------------
from collections import Counter, namedtuple
from .Tt_models import TimeTable
from . import Tt_algo_calc, Tt_exceptions
from .Tt_algo_calc import SortAlgorithms
import itertools


class TimetableSorter:
    """
    This is the class to MANAGE all the implementations of the 
    sorting algorithms defined above. The timetable class, instantiated in the 
    GUI controller (perhaps) is passed here for necessary operations
    """
    
    def __init__(self, tt_obj=None):
        self.tt_obj = tt_obj if tt_obj else TimeTable()

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


    # ----------------------------------------------------------------------------------
    # -------------------------------- STATIC METHODS ----------------------------------
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

        # a+b (below) could also be written as len(val)
        # a+b is the total number of packets
        # val is the list containing all the chunk values to make up freq
        return val, a+b



    def Translate_list_items(list_arg, item=None, index=None, base_index=0):
        """ This static function rotates the elements in a list by taking an 'item' or 'index' if provided 
        and moving to the position 'base_index' 
        item and index should not be provided at the same time. However, if done, the function defaults to 'item'
        """

        index_ = list_arg.index(item) if item else index

        if index_ is None:
            raise ValueError("Cannot rotate. Nothing selected really")
        list_len = len(list_arg)
        list_arg_ = sorted(list_arg, key=lambda k: (list_arg.index(k) - (index_ - base_index)) % list_len)
        return list_arg_


    class DeptPeriodEncase:
        """ A very simple class to hold each class arm, department, its frequency and its "chunk" value
        for ease of sorting """
        def __init__(self, class_arm, dept, frequency, chunk):
            self.dept_obj = dept
            self.frequency = frequency
            self.class_arm = class_arm
            self.chunk = chunk
    
        
        def get_spread(self, chunk=1):
            """Returns the number of packets the department's frequency has been chunked into"""
            spread = TimetableSorter.dept_shredder(self.frequency, chunk)
            return spread


        def teacher(self):
            return self.dept_obj.teachers_for_client_class_arms[self.class_arm]

        @property
        def is_single(self):
            return self.chunk == 1

        def reg_with_teacher(self):
         # register the freq, dept, arm to the teacher
            self.teacher().add_dept_arm_freq_to_teacher(self.dept_obj, self.class_arm, frequency=self.frequency)
            
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
            # self.periodsint_list = list(range(self.periodlength_today))

            self.periodsint_tuple = tuple(list(range(self.periodlength_today)))
            self.todays_unique_depts = list(set(day_obj.get_all_depts_for_arm_today(class_arm)))

        @property
        def periodsint_list(self):
            return list(self.periodsint_tuple)
        

        def append_to_periodsleft(self, arg):
            """ adds 'arg' to its ordered position in the periodsintlist. 'arg' is a list of integers """

            periodsint_list = self.periodsint_list
            # Put it in a list anyway, whther, int or list object
            arg_list = sorted([arg].copy())
            for item in Tt_algo_calc.strip_list_wrapper(arg_list):
                # insert this new sorted list into its position in the periodsint_list
                periodsint_list.insert(item, item)

            self.periodsint_tuple = tuple(periodsint_list)
    

        def pop_out_period_val(self, val):
            """Remove out a period number or a list value from the periodsint_list"""
            val_arg = [val]
            periodsint_list = self.periodsint_list

            # If "val" is a list, remove all the items in turn
            for e_item in Tt_algo_calc.strip_list_wrapper(val_arg):
                try:
                    periodsint_list.remove(e_item)
                except ValueError:
                    raise ValueError(f"{e_item} cannot go in {periodsint_list}")

            # Cast to a tuple
            self.periodsint_tuple = tuple(periodsint_list)


        @property
        def list_after_pop(self):
            """Returns the list, preferably after the popping has been done"""
            return self.periodsint_tuple


        def pop_out_dept(self, dept_obj):
            """Remove a dept from the list of depts today (after it has been chunked)"""
            self.todays_unique_depts.remove(dept_obj)


        def reconstitute(self):
            """ Run the init method all over again """
            self.__init__()

        # Onward, the self.periodintlist variable can be edited according to what is required of the chunking


    def prep_dept_freq(self, class_arm_obj, iterable_from_gui):
        """ This method accepts the 'dept', 'frequency' and 'chunk' values from the GUI controller and makes each item an instance
        of the DeptPeriodEncase class. The iterable_from_gui is a list of named tuples. """

        container_list = []

        for item in iterable_from_gui: 
            cont = self.DeptPeriodEncase(class_arm_obj, item.dept, item.frequency, item.chunk)
            container_list.append(cont)

        # --Sort the items in the container_list based on how many packets it has been chunked into
        return container_list


# ------------------- GENERATED PERIODS ----------------------------------------
    def generate_periods_classarms(self,day_obj,class_arm_obj, start, end, n):
        """This method generates the periods given a day, for a given class arm by chunking its 
        start and end times into 'n' amounts of equal periods."""

        gen_periods = self.tt_obj.split_into_periods(start, end, n)
        val = []

        for period in gen_periods:
            val.append(self.tt_obj.create_period(period.start, day=day_obj, end=period.end, sch_class_arm_obj=class_arm_obj,
                is_acad=True, title_of_fav=None))
        
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



    def generate_periods_given_duration(self, class_arm, day, acad_periods_dict=None, nonacad_tuple_list=None):
        """ Generates periods along with nonacademic periods given start and duration. freq denotes the frequency of the normal periods.
         """
        # stretch out all the durations of the frequencies into one thin strip (i.e. duration in frequency places)
        start = acad_periods_dict["start"]
        duration = acad_periods_dict["duration"]
        freq = acad_periods_dict["freq"]
        boundary_interval = acad_periods_dict["interval"]


        total_duration = TimeTable.tuple_to_num(duration) * freq
        end = TimeTable.add_sub_time(start, TimeTable.num_to_tuple(total_duration))
        academic_periods = self.generate_periods_classarms(day,class_arm, start, end, freq)
        # now insert the special (non-acad periods)
        all_periods = self._insert_nonacad(class_arm, day, academic_periods, nonacad_tuple_list)
        # Just to help print it out
        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)

        class_arm.periods[day] = all_periods
        return all_periods


    def generate_periods_given_acadspan(self, class_arm, day, acad_periods_dict=None, nonacad_tuple_list=None):
        """ Generates academic periods between start and limit. That is before fixing the special (nonacad) periods Duration
        is calculated implicitly. """
        start = acad_periods_dict["start"]
        limit = acad_periods_dict["limit"]
        freq = acad_periods_dict["freq"]
        boundary_interval = acad_periods_dict["interval"]


        academic_periods = self.generate_periods_classarms(day,class_arm, start, limit, freq)
        # insert non-acad (special) periods
        all_periods = self._insert_nonacad(class_arm, day, academic_periods, nonacad_tuple_list)

        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)

        class_arm.periods[day] = all_periods
        return all_periods


    def generate_periods_given_abs_constraints(self, class_arm, day, acad_periods_dict=None, nonacad_tuple_list=None):
        """ Generates periods with the non-acads and all, with end point fixed """

        abs_start = acad_periods_dict["start"]
        abs_end = acad_periods_dict["end"]
        freq = acad_periods_dict["freq"]
        boundary_interval = acad_periods_dict["interval"]

        # Get sum the non-academic periods durations first
        sum_dur_nonacad = (0,0)

        for _, duration, positions in nonacad_tuple_list:
            for _ in positions:
                sum_dur_nonacad = TimeTable.add_sub_time(sum_dur_nonacad, duration)


        # length of positions for the nonacad periods
        len_pos = len(nonacad_tuple_list[-1]) if nonacad_tuple_list else 0
        # total length of all periods the academic periods and the nonacads
        tot_length = freq + len_pos

        # Subtract this sum of durations time from the span, i.e. end - start
        span = TimeTable.add_sub_time(abs_end, abs_start, add=False)
        # The span of the intervals tot_length - 1 long
        interval_span = TimeTable.tuple_to_num(boundary_interval)*(tot_length - 1)
        cut_out = TimeTable.add_sub_time(sum_dur_nonacad, interval_span)
        # What is left of the span when non-acads durations have been removed
        sub_span = TimeTable.add_sub_time(span, cut_out, add=False)
        # Add this sub_span to abs_start to get the limit of the academic periods
        limit = TimeTable.add_sub_time(abs_start, sub_span)
        # Now generate periods
        academic_periods = self.generate_periods_classarms(day, class_arm, abs_start, limit, freq)
        # insert non-acad (special) periods
        all_periods = self._insert_nonacad(class_arm, day, academic_periods, nonacad_tuple_list)

        # Mesh the periods with one another
        self.update_periods_after_insertion(all_periods, boundary_thickness=boundary_interval)

        class_arm.periods[day] = all_periods
        return all_periods


    # ----------------------------------------------------------------------------------------------
    # --------------------------- PERIOD GENERATION AND ADDING SUBJECT AND DAY TO A CLASS ARM -------------------------
    def _insert_nonacad(self, class_arm, day, academic_periods, nonacad_tuple):
        """ Inserts the non-academic periods into the already generated normal (academic) periods.
        The nonacad_dict is a a tuple with of form:  (nonacad_name(str), [positions (int)], duration_nonacad(time tuple)).
        THE duration_nonacad IS A TIME-TUPLE.
        """
        academic_periods = academic_periods
        nonacads = []

        for non_acad, duration_nonacad, positions_list in nonacad_tuple:
            # Fetch the nonacad dept object for non_acad

            for position in positions_list:
                # Create the non-academic period
                nonacad_period = self.tt_obj.create_period(start=(8,0,0), day=day, end=None, duration=duration_nonacad, is_acad=False, sch_class_arm_obj=class_arm, title_of_fav=non_acad)
                nonacads.append((position, nonacad_period))

        # Now insert all of these nonacads contents into the main list
        for position, nonacad_period in nonacads:
            academic_periods.insert(position - 1, nonacad_period)
        return academic_periods


    def packet_depts_into_arms_per_day(self, iterable_from_gui):
        """ Places the depts for each class arm into days of the week. This function is a more robust form of the "chunk_x_into_y" function 
        defined above. It tries to chunk x into y, but if it can't, because the day is already full, it just moves to the next day. This
        function is specifically for chunking packets into days, not sorting teachers into periods """


        def _packet_depts_into_one_arm(class_arm, iterable_from_gui):
            """ packets subjects/depts into one arm on all of its days. """

            # 1. ---- The sorted list of the departments and their spreads (frequencies and all). ----
                # List of all the algorithms to be used to sort the classes (so all the classes do not get sorted the exact same way)

            # The 'arm_algo_index' is implemented so as to ensure that neighbouring arms do not use the same day 'packeting' algorithm. It does this
            # by picking out the index of the arm in the list of school class arms INDEX and finding INDEX % length of the list of algos. This way, the algorithms are applied in a cycle within this class.

            arm_algo_index = self.tt_obj.list_of_school_class_arms.index(class_arm) % len(algorithms_list)

            # Every item here is an instance of the DeptEncase class
            arm_chunk_array = self.prep_dept_freq(class_arm, iterable_from_gui)
            
            # Sort the arm_chunk_array such that teachers with less teaching days (e.g NYSC corps members) come first
            arm_chunk_array.sort(key=lambda deptEncaseItem: len(deptEncaseItem.teacher().teaching_days_s) if deptEncaseItem.teacher() else 0)
            displaced_depts = []
            arms_day_container = {day:[] for day in class_arm.get_class_arm_days}


            # 1. --- Loop through all the DeptEncase objects in arm_chunk_array and packet them
            for encase_item in arm_chunk_array:
                dept, teacher = encase_item.dept_obj, encase_item.teacher()
                encase_item.reg_with_teacher()

                # Legal days are the teacher's teaching days that coincide with the arms' teaching days
                legal_days = list(teacher.teaching_days_s & set(class_arm.get_class_arm_days))
                legal_days.sort(key=lambda day: self.tt_obj.list_of_days.index(day))

                chunk_for_spread = encase_item.chunk if encase_item.chunk < len(legal_days) else len(legal_days)
                shredded, packets_num = encase_item.get_spread(chunk=chunk_for_spread)

                # Feed the packets into the algorithm
                day_packet = algorithms_list[arm_algo_index](packets_num, len(legal_days))

        
                for shred_num, packet_num in zip(shredded, day_packet):
                    curr_day = legal_days[packet_num]
                    # Length of the periods for this arm today
                    width = len(class_arm.periods[curr_day])
                    for _ in range(shred_num):
                        if len(arms_day_container[curr_day]) < width:
                            # if there is room in the arms_day_container today, add this dept
                            arms_day_container[curr_day].append(dept)
                        else:
                            # If no room, add to the list of displaced_depts
                            displaced_depts.append((dept, teacher))


            # 2. --- Now handle the displaced_depts list
            displaced_depts_length = len(displaced_depts)

            for _ in range(displaced_depts_length):
                dept, teacher = displaced_depts.pop()
                # Make a list of class_arms_days but with teachers teaching days preceeding
                days_list = teacher.teaching_days.copy()
                days_list.extend([day for day in class_arm.get_class_arm_days if not day in teacher.teaching_days])

                for day in days_list:
                    width = len(class_arm.periods[day])
                    if len(arms_day_container[day]) < width:
                        arms_day_container[day].append(dept)
                        break
                # If it loops through without finding room, add it back to the list of displaced_depts
                else:
                    displaced_depts.append((dept, teacher))


            # 3. --- Add this arms_day_container as the class_arm's temp_dept_holder
            for day, depts_list in arms_day_container.items():
                class_arm.temp_dept_holder_for_days[day] = depts_list.copy()

            print()
            return [dept_list for dept_list in class_arm.temp_dept_holder_for_days.values()], displaced_depts, algorithms_list[arm_algo_index].__name__, class_arm

        # ----------------------------------------------------------------------------------
        # ------------------- OUTSIDE THE ABOVE FUNCTION -----------------------------------

        algorithms_list = Tt_algo_calc.PacketAlgos.algorithms
        for arm in self.tt_obj.list_of_school_class_arms:
            # Run the packeting inner function for each class arm
            print(_packet_depts_into_one_arm(arm, iterable_from_gui))



    # ------------------------------------------------------------
    def _nail_int_to_arms(self, day_obj):
        """Semi-private method. Makes (instantiates) ArmPeriodsLeft objects for all the class arms today. 
        This is to know which periods have already been nailed down to each teacher across the class arms during the chunking"""

        # make instances of the ArmsPeriodsLeft or whatever class
        return {arm:self.ArmPeriodsLeft(arm, day_obj) for arm in day_obj.arms_today_list}


    def repacket_teachers(self, array=10):
        """ Repackets all teacher, by repeatedly running the repacket_teacher function on all teachers """

        # -------------------------------------------------------------------------------------------------------------
        def _repacket_teacher(teacher, array=10):
            """ Checks ëach teacher whose subjects run beyond array, and pushes the extras off to another day """
            
            # Check through all of his teaching days
            days_list = teacher.teaching_days.copy()
            days_list.extend([day for day in self.tt_obj.list_of_days if not day in teacher.teaching_days])
            
            for day in days_list:
                # list of (arm, dept) that teacher teaches today
                teachers_depts = day.teachers_depts_today(teacher)
                if len(teachers_depts) > array:

                    # diff is a negative number, useful for the list slicing from the right 
                    diff = array - len(teachers_depts)
                    # the extra (arm, dept) items
                    extra = teachers_depts[diff:]
                    # teachers_depts[diff:] = []
                    
                    # Remove the extras
                    for arm, dept in extra:
                        # days that coincide with teacher's teaching days, but not today
                        w_days = teacher.teaching_days_s & set(arm.days_list) - {day}
                        w_days = list(w_days)
                        w_days.sort(key=lambda day_:self.tt_obj.list_of_days.index(day_))
                        # print(f"w_days: {w_days}")

                        fixed_up = False
                        for day_ in w_days:
                            # Check if the day is not jam-packed for teacher
                            # print(f"Non-choice day: {day_}")

                            if len(day_.teachers_depts_today(teacher)) < array:
                                # print(f"Choice day: {day_}")

                                # ------------------------------------------------------
                                # If the arm's temp_dept_holder is already full, simply substitute
                                if len(arm.temp_dept_holder_for_days[day_]) >= array:

                                    for dept_ in reversed(arm.temp_dept_holder_for_days[day_]):
                                        _teacher = dept_.teachers_for_client_class_arms[arm]
                                        # If it is a different teacher, and one that has not been re_packeted before
                                        if  _teacher != teacher and len(day.teachers_depts_today(_teacher)) < array:
                                            # Remove worthy dept_ from this class arms depts list
                                            arm.temp_dept_holder_for_days[day_].remove(dept_)
                                            # Add the dept from the extras
                                            arm.temp_dept_holder_for_days[day_].append(dept)
                                            # Remove this dept from the arm on the original day
                                            arm.temp_dept_holder_for_days[day].remove(dept)
                                            # Add the dept of the arm (on the other day) to this arm on this day
                                            arm.temp_dept_holder_for_days[day].append(dept_)
                                            fixed_up = True
                                            break
                                
                                else:
                                    # If the arm's temp_dept_holder still has room, i.e. not up to array, add the dept from the exras

                                    # remove dept from the arm on the original day
                                    arm.temp_dept_holder_for_days[day].remove(dept)
                                    # Add dept to this new worthy day
                                    arm.temp_dept_holder_for_days[day_].append(dept)
                                    fixed_up = True
                                    break

                            if fixed_up:
                                break

                        else:
                            print(f"REPACKETING ERROR, COULDN'T REPACKET {arm, dept, teacher}.")

            # return teacher, [len(day.teachers_depts_today(teacher)) for day in teacher.teaching_days]


        # WHAT TO DO IF FOR SOME REASON THIS DOES NOT WORK (TEACHER CAN'T JUST BE HELPED?)?
        # ------------------------------------------------------------------------------------------------------
        # -------- OUTSIDE INNER FUNCTION
        for teacher in self.tt_obj.list_of_all_teachers:
            _repacket_teacher(teacher, array=array)


        for teacher in self.tt_obj.list_of_all_teachers:
            print(teacher, [len(day.teachers_depts_today(teacher)) for day in self.tt_obj.list_of_days], 
                teacher.teachers_freq_average, teacher.str_teacher_depts)


    def check_arms(self):
        armz = [arm for arm in self.tt_obj.list_of_school_class_arms if arm.id in list(range(8,15)) + [42]]
            
        for arm in armz:
            print("-"*40)
            for day, depts in arm.temp_dept_holder_for_days.items():
                print(f"{day} --> {len(depts)}")



    def Algosort_teachers_per_day(self, day_obj, algorithm, reference_arm=None,reference_arm_index=0):
        """
        Does the Principal sorting of the teachers with the prescribed algorithm
        into periods such that the time-table parameters are met 
        
        """

        # First, get all the teachers that teach on a particular day

        def T_A_Reconstruct(arm_obj=None,teacher_obj=None,teachers_replace_list_arg=None, arms_replace_list_arg=None):
            """ Teeacher and Arm and chunked value dictionary reconstruction.
            This is a helper function to handle the dismantling and reconstruction of this teacher's chunk values in
            the Teacher_and_chunk_val dictionary, as wella as the arm's chunk values. It replaces old with the new."""

            # For each teacher's details and the replacement value

            if arm_obj:
                for index, (details, repval) in enumerate(zip(Arm_and_chunked_val[arm_obj].copy(), arms_replace_list_arg)):
                    dept, teacher = details.dept, details.teacher
                    repval = repval.copy() if isinstance(repval, list) else repval
                    replace_val = self.arm_n_chunk(dept, repval, teacher)

                    # Now update with the replaced value at position index
                    Arm_and_chunked_val[arm_obj][index] = replace_val


            if teacher_obj:
                # Replace teacher with new chunk values and stuff
                for index, (details, repval) in enumerate(zip(Teachers_and_chunked_val[teacher_obj].copy(), teachers_replace_list_arg.copy())):
                    dept, arm = details.dept, details.arm
                    repval = repval.copy() if isinstance(repval, list) else repval
                    # This is (arm, new_chunk, dept)
                    replace_val = self.teacher_n_chunk(arm, repval, dept)
                    # Replace this teachers values at position 'index'
                    Teachers_and_chunked_val[teacher_obj][index] = replace_val

            # -------------------------------------------------------------------------------------------------------
            # -----------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------------
                # OUTSIDE THE FUNCTION

        todays_teachers = day_obj.get_unique_teachers_depts_tday_assgn()

        # print(f"These are all depts offered today in their arms: {todays_teachers_arm_depts_dupli}, with length: {len(todays_teachers_arm_depts_dupli)}")
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
        
        # ------------------------------------------------------------------------------------
    
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
    
        # Also, this is {teacher:arm,dept, chunk}
        Teachers_and_chunked_val = {}

        # =========================================
         # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}
            # --------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------
        # Teachers already handled so we dont handle them
        touched_teachers = []


        def arms_teachers_sort(ref_arm, array=avg_period_len):
            """ Handles the bulk of the sorting for a class arm """
            
            # First, collect all the unique depts offered today by the reference arm sorted by the ATPG criterion
            base_dept_list = sorted(day_obj.get_depts_of_arm_today(ref_arm, duplicate=False), key=lambda dept:dept.dept_ATPG(), reverse=True)
            
            if ref_arm in [arm for arm in self.tt_obj.list_of_school_class_arms if arm.id in list(range(8,15)) + [42]]:
                print(f"{day_obj}, {ref_arm}, Base depts today: {base_dept_list}")

            # Get the list of periods from the ArmsPeriodsLeft obj dictionary
            periods_intlist = ArmsPeriodsLeft_objs.get(ref_arm).periodsint_list

            # ==========================================
            # The variable below serves as a counter for the space by which the chunk values should be shifted
            # It records how much it has shifted over the past teachers and increments by the length of the previous item (teacher) in the for-loop below
            # ---------------------------
            # Note that the real shift_values contained in the ArmPeriodsLeft_objs dictionary for this arm are being changed the moment it
            # has been occupied by a teacher

            shift_val = min(periods_intlist) if periods_intlist else 0
            # ALso, the ArmsPeriodsLeft objects for all the class arms, so that when a teacher is chunked into the base class, every other
            # class arm he teaches is also noted as occupied in its particular period

            
            for index, dept in enumerate(base_dept_list):
                # Find the teachers of these courses
                teacher = dept.teachers_for_client_class_arms[ref_arm]

                # It teacher has already been chunked with all the arms he's teaching, kindly exclude him
                if teacher in touched_teachers:
                    continue

                touched_teachers.append(teacher)
                # -----------------------------------------------------------------------
                # The inner Counter is for counting the occurences of depts in the teacher key-val pair
                # Then the values() are retrieved which are nums like 'dict_blah_blah [1,1,1] or [2,2,2] for the nums'
                # Then we make a counter object for that as well to know the frequency of the nums which returns the
                # value of the {single(or double): how many it is}
                
                # ----------------------------------------------------------------------------------------------------
                # count_dict is a dict object!!!
                # The Count_with_order function is used instead of counter, to preserve the order of the items
                chunk_sequence = Tt_algo_calc.Count_with_order(list((Tt_algo_calc.Count_with_order(day_obj.teachers_depts_today(teacher)).values())))
                
                if ref_arm in [arm for arm in self.tt_obj.list_of_school_class_arms if arm.id in list(range(8,15)) + [42]]:
                    print(f"    {teacher}'s chunk sequence {chunk_sequence}, --> {day_obj}")
                    print(day_obj.get_depts_of_arm_today(ref_arm))
                # -------------------------------------------------------------------------------------------------
                # --------------------------- FEED INTO THE CHUNKING ALGORITHM ------------------------------------
                # -------------------------------------------------------------------------------------------------
                # Shift with the int_values of the ArmsPeriodsLeft_objs of the arm so we can keep track of which ones have been poppwd when occupied2
                teacher_chunk_numbers = algorithm(array, chunk_list=chunk_sequence, shift_value=shift_val)
                # print(f"This is this_teachers chunk: {this_teacher}")
                # print("-"*40)
                # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}

                ref_arm_details = []
                for (arm,dept), chunk in zip(Tt_algo_calc.Set_with_order(day_obj.teachers_depts_today(teacher)), teacher_chunk_numbers):

                    if arm == ref_arm:
                        holder = self.arm_n_chunk(dept, chunk, teacher)
                        ref_arm_details.append(holder)

                    t_holder = self.teacher_n_chunk(arm, chunk, dept)

                    if not teacher in Teachers_and_chunked_val:
                        Teachers_and_chunked_val[teacher] = []
                    Teachers_and_chunked_val[teacher].append(t_holder)
                
                # shift_val is the value to shift by which is the length of all the previous chunk lists
                translate = [detail.chunk for detail in ref_arm_details]
                
                # Get the absolute highest value in the list for the chunked values for this arm so we can shift by that
                shift_val = max(Tt_algo_calc.strip_list_wrapper(translate))

            # ------------------------------------------------------------------------------------------------------------------
            # 1. Go through all the periods in the ref_arm and "Moveover" the periods chunk values for good measure

            # 1A. Now moveover_fixed the teachers chunk with the ref-arms chunks as constant
            # The armPeriodsLeft objs periods_int_list already provides the ref_arm list integers
                fixed = [elem.chunk for elem in ref_arm_details]
                # Now try move_over_fixed to see if its possible to keep this arm fixed
                clip_offs, all_chunk_list = 0, Teachers_and_chunked_val[teacher].copy()

                while True:
                    # In the event that the moveover_fixed fails because the fixed_chunk does not allow it
                    clipped_chunk = [elem.chunk for elem in all_chunk_list]
                    try:
                        teacher_fixed = Tt_algo_calc.Moveover_fixed(clipped_chunk, array, fixed_item=fixed)
                    except Exception:
                        # Clip off the last item of all chunk. The chunk items in the 
                        clip_offs += 1
                        all_chunk_list.pop()
                    else:
                        break


                 # Remove these clipped_offs from the subject teacher teaches today and from Arm_and_chunked_val and Teacher_and_chunked_val
                # --------------------------------------------------------------------------------------------
                for count in range(clip_offs):
                    # The negative index of val in order to locate the dept and arm that maps to it
                    pos = index - clip_offs
                    arm_chunk_dept = Teachers_and_chunked_val[teacher].pop()
                    arm, chunk, dept = arm_chunk_dept

                    # remove this dept from the arm's temp_dept_holder for today
                    Tt_algo_calc.casual_removeall(arm.temp_dept_holder_for_days[day_obj], dept)

                    # -----------------------------------------------
                    # ADD THIS ARM_CHUNK_DEPT ITEM TO SELF.DISPLACED TEACHERS
                    if teacher not in self.displaced_teachers:
                        self.displaced_teachers[teacher] = []

                    for dict_item in self.displaced_teachers[teacher]:
                        for day in dict_item:
                            if day == day_obj:
                                # Append this arm_chunk_dept info to the dict_item's list whose day is today
                                dict_item[day_obj].append(arm_chunk_dept)
                                break
                        # If after all, no such day exits for teacher in self.display_teachers today, create a new one
                        else:
                            dict_item[day_obj] = [arm_chunk_dept]


            # 2A. Begin popping out teachers chunk (in its combination) numbers from the periodsint of the arms he is teaching
                combinations = Tt_algo_calc.Possible_combs_with_fixed(teacher_fixed, fixed, array)
                # print(f"Combinations with fixed: {combinations} and teacher: {teacher}, fixed is: {fixed}")
                print()
                # A dictionary to record the number of times a fragment goes free before it crashes
                crash_counter = {index: 0 for index,_ in enumerate(combinations)}


                for index, combo in enumerate(combinations):
                    T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=combo)
                    # The below is a list of (arm, chunk) tuples to help rebuild the arm's periodsint_list objects
                    frag_for_rebuild = []
                    worked = False

                    for segment in Teachers_and_chunked_val[teacher]:
                        arm, chunk, dept = segment.arm, segment.chunk, segment.dept

                        preserve = ArmsPeriodsLeft_objs[arm].list_after_pop

                        try:
                            # Try popping out the chunk values from ArmPeriodsLeft
                            ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk)
                        except:
                            # If an error occurs becuase that chunk has already been cleaned off by a previous teacher
                            
                            # Rebuild the arms_periodsleft object for another combination since this combination doesn't work.
                            for arm_, chunk_ in frag_for_rebuild:
                                ArmsPeriodsLeft_objs[arm_].append_to_periodsleft(chunk_)
                            break
                        
                        else:
                            # If the chunk value is popped out without any problems
                            crash_counter[index] += 1
                            # print(f"chunk: {chunk} IN list_after_pop: {preserve} for {arm} dept: {dept}")
                            frag_for_rebuild.append((arm, chunk))
                
                    else:
                        # ----THE TEACHERS SEGMENT WORKED HERE! 
                        # Clear the list to keep track of fragments since teacher works now
                        frag_for_rebuild.clear()
                        worked = True
                        # print(f"{teacher} ABSOLUTELY WORKED, before: {preserve}, now: {ArmsPeriodsLeft_objs[arm].periodsint_list}")

                        # Remove teachers subjects from the list of all the arms offering it. We are done with him
                        for class_arm, _, dept in Teachers_and_chunked_val[teacher]:
                            # Go to the dict bearing all the arms and remove him from there
                            Tt_algo_calc.casual_removeall(class_arm.temp_dept_holder_for_days[day_obj], dept)

                        break
                        # -------------------------------------------------------------------------------------
                
                # If despite all this, none of the combinations worked for the teacher's chunk
                else:
                    best_combo_index, best_fit_index = max(crash_counter.items(), key=lambda comb_index: comb_index[1])
                    # best_combo_index, best_fit_index = sorted(list(crash_counter.items()), key=lambda comb_index: comb_index[1], reverse=True)[0]
                    # print()
                    # print(f"Bestest: {best_combo_index} and best fit: {best_fit_index}")
                    # print()

                    # # Remove everything after the index of best_fit from the teacher
                    carryover = Teachers_and_chunked_val[teacher][best_fit_index:]

                    # # Clear out this carryover from teachers and chunked val
                    Teachers_and_chunked_val[teacher][best_fit_index:] = []

                    choice = combinations[best_combo_index][:best_fit_index]
                    # print(f"{teacher} DIDN'T WORK, HAS TO BE RE-ADJUSTED")

                    T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=choice)
                    
                    # If the teacher and chunked val is not empty
                    if Teachers_and_chunked_val[teacher]:
                        for detail in Teachers_and_chunked_val[teacher]:
                            arm, chunk = detail.arm, detail.chunk
                            ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk)

                        for class_arm, _, dept in Teachers_and_chunked_val[teacher]:
                            # Remove teachers subjects from the list of all the individual arms offering it. We are done with him
                            # Go to the dict bearing all the arms and remove him from there
                            Tt_algo_calc.casual_removeall(class_arm.temp_dept_holder_for_days[day_obj], dept)

                        
                    else:
                        # If the Teacher_and_chunked_val list is empty, remove it completely
                        del Teachers_and_chunked_val[teacher]
                        # touched_teachers.remove(teacher)

            

                    # Add this carryover namedtuples to the dictionary of displaced teachers
                    if teacher not in self.displaced_teachers:
                        self.displaced_teachers[teacher] = []
                    self.displaced_teachers[teacher].append({day_obj:carryover})
                                  

        # ------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------
        # OUTSIDE THE ABOVE FUNCTION
        for arm in self.list_from_reference_arm[:]:
        # armz = [arm for arm in self.tt_obj.list_of_school_class_arms if arm.id in list(range(8,15)) + [42]]
        # for arm in armz:
            arms_teachers_sort(arm)

        # Also add all the teachers who have had no problems so far -- ready teachers
        self.All_Teachers_and_chunked_val[day_obj] = Teachers_and_chunked_val
        # Also add ArmsPeriodsLeft to the overall dictionary dictionary for today
        self.All_Armperiodsleft[day_obj] = ArmsPeriodsLeft_objs


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
                if teacher not in self.All_Teachers_and_chunked_val[day]:
                    self.All_Teachers_and_chunked_val[day][teacher] = [self.teacher_n_chunk(arm, new_chunk_val, dept)]
                # self.All_Teachers_and_chunked_val[day][teacher].append(self.teacher_n_chunk(arm, new_chunk_val, dept))
                else:
                    for index, (_arm_, chunk, dept) in enumerate(self.All_Teachers_and_chunked_val[day][teacher].copy()):
                        # If the arm already exists in the dictionary today
                        if _arm_ == arm:
                            new_list = [chunk, new_chunk_val]
                            # Replace the whole named_tuple at this position "index"
                            self.All_Teachers_and_chunked_val[day][teacher][index] = self.teacher_n_chunk(arm, new_list, dept)
                            break
                    else:
                        # If this arm does not already exist in the dictionary today
                        self.All_Teachers_and_chunked_val[day][teacher].append(self.teacher_n_chunk(arm, new_chunk_val, dept))

                                            
                self.All_Armperiodsleft[day][arm].pop_out_period_val(new_chunk_val)
                Tt_algo_calc.casual_removeall(arm.temp_dept_holder_for_days[day_], dept)


        # -----------------------------------------------------------------------------------------------
        def patch_teachers(days_list, x_info=None):
            """ The function that finds an empty, non-overlapping spots to put teachers in """

            # ------------------------------------------------------------------
            if not self.handled:

                for day in days_list:
                    # check if arm has class on this day, (you know to be robust)
                    if arm in day.arms_today_list:
                        # check if teacher already teaches today
                        if teacher in self.All_Teachers_and_chunked_val[day] and self.All_Armperiodsleft[day][arm].periodsint_list:
                            # Since he does, get all of his pre-existing chunk values
                            pre_chunk = [elem.chunk for elem in self.All_Teachers_and_chunked_val[day][teacher]]
                            # get the unoccupied periods for arm today
                            un_occ = self.All_Armperiodsleft[day][arm].periodsint_list
                            # check which pieces of un_occ do not overlap for certified chunk pieces
                            cert = [piece for piece in un_occ if not Tt_algo_calc.check_for_overlap(pre_chunk + [piece])]
                            # print(f"No overlaps...: {cert}")
                        
                        else: 
                            # If teacher does not teach on this day
                            cert = self.All_Armperiodsleft[day][arm].periodsint_list

                    # If arm does not have class on this day
                    else:
                        cert = self.All_Armperiodsleft[day][arm].periodsint_list
                        

                    # If the certified periods (in which teacher can teach) exceeds the length of the chunk
                    if cert and len(cert) >= self.len_chunk:
                        # Add this len(cert)'s worth of chunk values into the teacher's credentials
                        update_teacher_and_arm(day, dept, cert[:self.len_chunk], teacher=teacher, arm=arm)
                        # ...and subtract it from len_chunk
                        self.len_chunk = 0

                    elif cert and len(cert) < self.len_chunk:
                        # empty cert and put it into the teachers credentials
                        update_teacher_and_arm(day, dept, cert, teacher=teacher, arm=arm)
                        self.len_chunk -= len(cert)

                    # ------------------------------------
                    if self.len_chunk == 0:
                        self.handled = True
                        return

        # -----------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------
        second_displaced = self.displaced_teachers.copy()

        # Go to every teacher in the displaced teacher dict
        for teacher, teacher_chunk in second_displaced.items():
            # Note the day in which they were displaced
            # List to determine whether all details in chunk_list are have been handled
            details_in_chunk_list = []

            # Days among teacher's teaching days in which he actually teaches
            work_day= [day for day in teacher.teaching_days if teacher in day.get_all_teachers_today_from_depts_assgn()]
            # Days among teachers teaching days in which he does not teach
            free_day = [day for day in teacher.teaching_days if teacher not in day.get_all_teachers_today_from_depts_assgn()]
            # days in which teacher may not come to work. He (ideally) shouldnt teach on this days
            over_day = [day for day in self.tt_obj.list_of_days if day not in teacher.teaching_days]


            for index, dict_item in enumerate(teacher_chunk):
                # print(f"This is day_chunk: {day_chunk}")

                for day_, chunk_list in dict_item.items():
                    # print()
                    handled_list = chunk_list.copy()
                    # print(f"This is inner day and chunk_list:Teacher: {teacher}, -- {day_},-- {chunk_list}")

                    for index_2, details in enumerate(chunk_list):
                        # print(f"Details here: {details}")                    
                        dept, arm, chunk = details.dept, details.arm, details.chunk
                        # length of the chunk
                        self.len_chunk = 1 if isinstance(chunk, int) else len(chunk)

                        # The teachers (arm, dept) tuple to search with in the teacher_dept_dupli blah blah variable
                        # day_dupli_tuple = (arm, dept)
                        
                        # COMING BACK HERE!!!!
                        self.handled = False
                        patch_teachers(free_day, x_info="On free day.")
                        patch_teachers(work_day, x_info="On my works days")
                        patch_teachers(over_day, x_info="Overtime days")
                        details_in_chunk_list.append(self.handled)
                        
                        if self.handled:
                            handled_list.remove(details)
                            
                    self.displaced_teachers[teacher][index][day_] = handled_list

        # ------------------- CLEAN UP THE SELF.DISPLACED_TEACHERS DICTIONARY ----------------------------
        # Clean out the self.displaced_teachers dictionary stuff of teachers who already have been handlded
        for teacher_obj, chunk_list in self.displaced_teachers.copy().items():
            cancelable = False if chunk_list else True

            for dict_item in chunk_list:
                for _day_, particulars_list in dict_item.items():
                    # If the list bearing all the teacher's items (particulars_list) is not empty break out this loop, CAN'T delete
                    if particulars_list:
                        cancelable = False
                        break
                    else:
                        if dict_item in self.displaced_teachers[teacher_obj]:
                            self.displaced_teachers[teacher_obj].remove(dict_item)
                else:
                    cancelable = True

            # If no break occurs that is all the particular_list items are empty
            if cancelable:
                del self.displaced_teachers[teacher_obj]

        # ---------------------------------------------------------------
        # Start deleting teachers who laready have been handled
        # Go to every teacher in the displaced teacher dict


    def Sort_manager(self, algorithm, reference_arm=None):
        """This method handles the operation of the algo_sort for every day and handles displaced teachers by seeking to reassign them """

        for day_obj in self.tt_obj.list_of_days[:]:
            self.Algosort_teachers_per_day(day_obj, algorithm, reference_arm=reference_arm, reference_arm_index=0)
            
        print(self.displaced_teachers)
        before = len(self.displaced_teachers)
        # Just for testing
        self.before_dict = self.displaced_teachers.copy()
        # self.print_all_arms()
        self.handle_displaced_teachers()

        print()
        print("DISPLACED TEACHERS")
        print(self.displaced_teachers)
        print()
        print(before, len(self.displaced_teachers))


    def print_all_teachers(self):
        """ FOR TESTING. Prints out the chunk of all teachers so we can inspect """
        for day, teacher_dict in self.All_Teachers_and_chunked_val.items():
            print("-"*40)
            print(f"Today is {day}")
            print()
            for teacher, details in teacher_dict.items():
                print(f"{teacher} -- chunk_details: {[elem.chunk for elem in details]} -- {teacher in self.before_dict}")


    def print_all_arms(self):
        """ FOR TESTING. Prints out all the arms' chunks """
        for day, arm_dict in self.All_Arms_and_chunked_val.items():
            print("-_"*30)
            print(f"Today is {day}")
            print()
            for arm, details in arm_dict.items():
                print(f"{arm} -- chunk_details: {[elem.chunk for elem in details]} --")


    def print_all_periods(self):
        """ FPR TESTING. Prints out all the period integers of each class arm every day """
        for day in self.tt_obj.list_of_days:
            print()
            print(f"{'-'*35} {day} Done {'-'*35}")
            for arm,period in self.All_Armperiodsleft[day].items():
                print(f"Arms: {arm} --> Periods left: {period.periodsint_list}")


    def check_armperiods_left(self):
        """FOR TESTING. returns the number of periods left for every class arm for every day """

        for arm in self.tt_obj.list_of_school_class_arms:
            sum_ = 0
            for day, left_dict in self.All_Armperiodsleft.items():
                sum_ += len(left_dict[arm].periodsint_list)

            print(f"{arm.full_name} ---> {sum_}")


    def populate_arms_and_chunked_val(self):
        """ FOR TESTING??? """
        for day, t_dict_item in self.All_Teachers_and_chunked_val.items():
            arm_cont = {}
            # Rebuild Arm_and_chunked_val from eachers_and_chunked_val...
            for teacher, t_details in t_dict_item.items():
                for arm,chunk,dept in t_details:
                    if arm not in arm_cont:
                        arm_cont[arm] = []
                    arm_cont[arm].append(self.arm_n_chunk(dept, chunk, teacher))
            self.All_Arms_and_chunked_val[day] = arm_cont


    def inspect_arms_and_teachers(self):
        """ FOR TESTING. """
        # armz = [arm for arm in self.tt_obj.list_of_school_class_arms if arm.id in list(range(8,15)) + [42]]
        # print(armz)

        for arm in self.tt_obj.list_of_school_class_arms:
            print()
            print("-"*30)
            print()
            for day, dict_item in self.All_Arms_and_chunked_val.items():
                if arm in dict_item:
                    print(f"{day}, {arm} --> {len(Tt_algo_calc.strip_list_wrapper([elem.chunk for elem in dict_item[arm]]))} ")
    

    def map_chunk_to_arms_periods(self):
        """ Maps the already finished chunked values to the corresponding periods """

        # CALL populate_arms_and_chunked_val before
        
        for day, arm_dict in self.All_Arms_and_chunked_val.items():
            for arm, arm_detail_list in arm_dict.items():
                # filter out the academic periods from list of all the periods today
                acad_periods = [period for period in arm.periods[day] if period.is_acad]

                for dept, chunk, teacher in arm_detail_list:
                    # map each chunk value to the period of this arm with the same index number
                    chunk_ = Tt_algo_calc.strip_list_wrapper([chunk])
                    for k in chunk_:
                        # Now map it to the period at position k on this day
                        # arm.periods[day][k].add_details_to_period(dept, teacher)
                        # pick out the academic periods
                        acad_periods[k].add_details_to_period(dept, teacher)



    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    # STATIC METHODS BELOW
    dept_shredder = staticmethod(department_shredder)
    rotate_list = staticmethod(Translate_list_items)



if __name__ == "__main__":
    print(TimetableSorter.rotate_list(list(range(1,16)), item=9, base_index=0))