# - ************************************************************************
# ------ WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.
# *************************************************************************
# -- All rights reserved!


# ------- This module is to manage the generation of classes, periods, 
# ------- depts and sort them accordingly
# ------------------------------------------------------
from collections import Counter, namedtuple, defaultdict
from .Tt_models import TimeTable
from . import Tt_algo_calc, Tt_exceptions
from .Tt_algo_calc import SortAlgorithms
import itertools, time, math



class TimetableSorter:
    """
    This is the class to MANAGE all the implementations of the sorting algorithms defined above. The timetable class,
    instantiated in the GUI controller (perhaps) is passed here for necessary operations
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

        # A dictionary containing the string name (key) and object (value) of the sort algorithms
        self.sort_algorithms = {
        "The Leapfrog Algorithm": SortAlgorithms.leap_frog,
        "The Reverse-leapfrog Algorithm": SortAlgorithms.r_leapfrog,
        "The Center-cluster Algorithm": SortAlgorithms.centercluster,
        "The Reverse-center-cluster Algorithm": SortAlgorithms.r_centercluster,
        "The XLX-Reflection Algorithm": SortAlgorithms.xlx_reflection,
        "The Reverse-XLX-Reflection Algorithm": SortAlgorithms.r_xlx_reflection
        }


    # ----------------------------------------------------------------------------------
    # -------------------------------- STATIC METHODS ----------------------------------
    @staticmethod
    def shredder(frequency, bit=1):
        """
            This function "shreds" or "chunks" the frequency of the subject upon which it is used into 
            packets that can be inserted into different days of the week. i.e. this function helps to 
            split the total frequency per week of a subject into the days within the week.

            the frequency, often chunked into 1s (single periods) can also be chunked into 2s (double periods)
            or "n"s. The "bit" parameter handles that. recurr is 1 for singles and so on.
        """
        a,b = divmod(frequency, bit)
        val = [bit for _ in range(a)] + [b] if b else [bit for _ in range(a)]

        # a+b (below) could also be written as len(val)    a+b is the total number of packets
        # val is the list containing all the chunk values to make up freq
        return val, a+b


    # ---------------------------------------------------------------------------------------
    class ArmPeriodsLeft:
        """Holds temporarily a numerical value for all the periods available in a class arm.
        This is a simple (relatively) helper class to help the 'chunking' process. """

        def __init__(self, class_arm, day_obj):
            self.class_arm = class_arm
            self.day = day_obj
            # list of arms periods today
            self.periodslist_today = [period for period in self.class_arm.periods[day_obj] if period.is_acad]
            # number of periods of arm today
            self.periodlength_today = len(self.periodslist_today)
            # returns the number of available periods today as a list of integers from 0 to len -1
            # self.periodsint_list = list(range(self.periodlength_today))

            self.periodsint_tuple = tuple(range(self.periodlength_today))
            self.todays_unique_depts = list(set(day_obj.get_all_depts_for_arm_today(class_arm)))

        @property
        def periodsint_list(self):
            return list(self.periodsint_tuple)
        

        def append_to_periodsleft(self, arg):
            """ adds 'arg' to its ordered position in the periodsintlist. 'arg' is a list of integers """
            periodsint_list = self.periodsint_list.copy()
            # Put it in a list anyway, whether, int or list object
            for item in Tt_algo_calc.strip_list_wrapper([arg]):
                # insert this new sorted list into its position in the periodsint_list
                periodsint_list.append(item)

            periodsint_list.sort()
            self.periodsint_tuple = tuple(periodsint_list)
    

        def pop_out_period_val(self, val):
            """Remove out a period number or a list value from the periodsint_list. 'val' is thus an int or a list"""
            periodsint_list = self.periodsint_list

            # If "val" is a list, remove all the items in turn
            for e_item in Tt_algo_calc.strip_list_wrapper([val]):
                try:
                    periodsint_list.remove(e_item)
                except ValueError:
                    raise ValueError(f"{e_item} cannot go in {periodsint_list}")

            # Cast to a tuple
            self.periodsint_tuple = tuple(periodsint_list)



        @property
        def list_after_pop(self):
            """ TUPLE? Returns the list, preferably after the popping has been done"""
            return self.periodsint_tuple


        def pop_out_dept(self, dept_obj):
            """Remove a dept from the list of depts today (after it has been chunked)"""
            self.todays_unique_depts.remove(dept_obj)


        def reset(self):
            """ Reset by running the init method all over again """
            self.__init__()
        # ------------------------------------------------------------------------------------------


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


    def packet_depts_into_arms_per_day(self, beam_max_value=50):
        """ Places the depts for each class arm into days of the week. This function is a more robust form of the "chunk_x_into_y" function 
        defined above. It tries to chunk x into y, but if it can't, because the day is already full, it just moves to the next day. This
        function is specifically for chunking packets into days, not sorting teachers into periods.
        "beam_max_value" is the maximum amount method will emit to the GUI to be displayed on the progressbar """


        def _packet_depts_into_one_arm(class_arm):
            """ packets subjects/depts into one arm on all of its days. """

            # 1. ---- The sorted list of the departments and their spreads (frequencies and all). ----
                # List of all the algorithms to be used to sort the classes (so all the classes do not get sorted the exact same way)

            # The 'arm_algo_index' is implemented so as to ensure that neighbouring arms do not use the same day 'packeting' algorithm. It does this
            # by picking out the index of the arm in the list of school class arms INDEX and finding INDEX % length of the list of algos. 
            # This way, the algorithms are applied in a cycle within this class.

            arm_algo_index = (self.tt_obj.list_of_school_class_arms.index(class_arm) + 1) % len(algorithms_list)
            
            # Every item here is an instance of the DeptEncase class
            # arm_chunk_array = self.prep_dept_freq(class_arm, class_arm.get_iterable_from_gui())
            arm_chunk_array = class_arm.get_dept_teacher_freq_chunk_list()
            
            # Sort the arm_chunk_array such that teachers with less teaching days come first
            arm_chunk_array.sort(key=lambda dept_tuple: len(dept_tuple[1].teaching_days) if dept_tuple[1] else 1000)
            displaced_depts = []
            arms_day_container = {day:[] for day in class_arm.get_class_arm_days}

            # 1. --- Loop through all the tuples in arm_chunk_array and packet them
            for dept,teacher,freq,chunk in arm_chunk_array:
                # Register this class arm with the teacher
                teacher.add_dept_arm_freq_to_teacher(dept, class_arm, frequency=freq)

                # Teacher might not be assigned yet, but if he has been, run the entire process...
                if teacher:
                    # Legal days are the teacher's teaching days that coincide with the arms' teaching days
                    legal_days = list(teacher.teaching_days_s & set(class_arm.get_class_arm_days))
                    legal_days.sort(key=lambda day: self.tt_obj.list_of_days.index(day))
                    chunk_limit = math.ceil(freq / len(legal_days))

                    # the chunk for spread (just in case the chunk from the user in the GUI is too small)
                    chunk_for_spread = max((chunk, chunk_limit))

                    # shredded: the list of packeted values e.g [2,2,2,1] and packets_num: the length of 'shredded'.
                    shredded, packets_num = self.shredder(freq, bit=chunk_for_spread)
                    # ---- Feed the packets into the algorithm
                    day_packet = algorithms_list[arm_algo_index](packets_num, len(legal_days))

                    for shred_num, packet_num in zip(shredded, day_packet):
                        # print(f"legal_days_length: {legal_days} ::len {len(legal_days)} -->>packets num {packets_num} --  {packet_num} --d-packet {day_packet}")
                        curr_day = legal_days[packet_num]
                        # Length of the periods for this arm today
                        width = class_arm.period_count_per_day(curr_day, include_nonacads=False)
                        for _ in range(shred_num):
                            if len(arms_day_container[curr_day]) < width:
                                # if there is room in the arms_day_container today, add this dept
                                arms_day_container[curr_day].append(dept)
                            else:
                                # If no room, add to the list of displaced_depts
                                displaced_depts.append((dept, teacher))

            # -----------------------------------------------------------------------------------------
            # -----------------------------------------------------------------------------------------
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

            return [dept_list for dept_list in class_arm.temp_dept_holder_for_days.values()], displaced_depts, algorithms_list[arm_algo_index].__name__, class_arm


        # ----------------------------------------------------------------------------------
        # ------------------- OUTSIDE THE ABOVE FUNCTION -----------------------------------
        algorithms_list = Tt_algo_calc.PacketAlgos.algorithms
        len_arms = len(self.tt_obj.list_of_school_class_arms)

        for count, arm in enumerate(self.tt_obj.list_of_school_class_arms, start=1):
            # Run the packeting inner function for each class arm
            # try:
            _packet_depts_into_one_arm(arm)
            # except IndexError:
                # pass
            # finally:
            beam_val = round(count*beam_max_value/len_arms)
            yield beam_val
            


    def repacket_teachers(self, beam_min_value=50, beam_max_value=100):
        """ Repackets all teacher, by repeatedly running the repacket_teacher function on all teachers """

        # ------------------------INNER FUNCTION TO REPACKET ONE TEACHER -----------------------------------
        def _repacket_teacher(teacher):
            """ Checks ëach teacher whose subjects run beyond array, and pushes the extras off to another day """
            
            # Check through all of his teaching days
            days_list = teacher.teaching_days.copy()
            days_list.extend([day for day in self.tt_obj.list_of_days if not day in teacher.teaching_days])
            
            for day in days_list:
                # list of (arm, dept) that teacher teaches today
                teachers_depts = day.teachers_depts_today(teacher)
                array = day.get_average_period_length_today()
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
                                # If the arm's temp_dept__holder is not full , simply add
                                else:
                                    # remove dept from the arm on the original day
                                    arm.temp_dept_holder_for_days[day].remove(dept)
                                    # Add dept to this new worthy day
                                    arm.temp_dept_holder_for_days[day_].append(dept)
                                    fixed_up = True
                                    break

                            if fixed_up:
                                break

                        else:
                            repacket_defaulters.add(dept)


        # WHAT TO DO IF FOR SOME REASON THIS DOES NOT WORK (TEACHER CAN'T JUST BE HELPED?). RAISE AN EXCEPTIONS FOR AS MANY TEACHERS AS CANNOT BE HELPED
        # ------------------------------------------------------------------------------------------------------
        # -------- OUTSIDE INNER FUNCTION
        # A set to hold a record of the subjects(depts) that fell through un-packeted
        repacket_defaulters = set()

        # The width of the "progressbar" representing this process
        beam_width = beam_max_value - beam_min_value
        len_teachers = len(self.tt_obj.list_of_all_teachers)

        # -------- TO BE REMOVED ------------        

        for count, teacher in enumerate(self.tt_obj.list_of_all_teachers, start=1):
            _repacket_teacher(teacher)
            beam_val = round((count * beam_width / len_teachers) + beam_min_value)
            yield beam_val


        for arm in self.tt_obj.list_of_school_class_arms:
            # copy the packeted depts into the arm permanently for use in the 'advanced' section
            for day, depts_list in arm.temp_dept_holder_for_days.items():
                arm.perm_dept_holder_for_days[day] = depts_list.copy()


        # After the packeting operation, if the set of repacket_defaulters is not empty, an exception is raised
        self.packet_repacket_defaulters = None
        if repacket_defaulters:
            # instance variable to be used outside this module
            self.packet_repacket_defaulters = repacket_defaulters
            raise Tt_exceptions.SomethingWentWrong(repacket_defaulters)


    def undo_packeting(self, beam_max_value=100):
        """ Handles removing all the subjects packeted(and repacketed) to all the days of the week """
        len_arms = len(self.tt_obj.list_of_school_class_arms)
        for count, arm in enumerate(self.tt_obj.list_of_school_class_arms, start=1):

            arm.temp_dept_holder_for_days.clear()
            arm.perm_dept_holder_for_days.clear()
            beam_val = round((count*beam_max_value/len_arms))
            yield beam_val


    # --------------------------------------------------------------------------------------------------
    # ---------------------------- THE SORTING PROPER BEGINS HERE ---------------------------------------
    def _nail_int_to_arms(self, day_obj):
        """Semi-private method. Makes (instantiates) ArmPeriodsLeft objects for all the class arms today. 
        This is to know which periods have already been nailed down to each teacher across the class arms during the chunking """

        # make instances of the ArmsPeriodsLeft or whatever class
        return {arm: self.ArmPeriodsLeft(arm, day_obj) for arm in day_obj.school_class_arms_today}


    def algosort_teachers_per_day(self, day_obj, algorithm, reference_arm=None,reference_arm_index=0):
        """ Does the Principal sorting of the teachers with the prescribed algorithm
        into periods such that the time-table parameters are met. """

        def T_A_Reconstruct(arm_obj=None,teacher_obj=None,teachers_replace_list_arg=None):
            """ INNER FUNCTION. Teacher_and _chunked_val[teacher] resonstruction.
            This is a helper function to handle the dismantling and reconstruction of this teacher's chunk values in
            the Teacher_and_chunk_val dictionary, as wella as the arm's chunk values. It replaces old with the new."""

            if teacher_obj:
                # Replace teacher with new chunk values and stuff
                for index, (details, repval) in enumerate(zip(Teachers_and_chunked_val[teacher_obj].copy(), teachers_replace_list_arg.copy())):
                    dept, arm = details.dept, details.arm
                    repval = repval.copy() if isinstance(repval, list) else repval
                    # This is (arm, new_chunk, dept)
                    replace_val = self.teacher_n_chunk(arm, repval, dept)
                    # Replace this teachers values at position 'index'
                    Teachers_and_chunked_val[teacher_obj][index] = replace_val
        # --------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------
        
        def arms_teachers_sort(ref_arm, array=10):
            """ INNER FUNCTION. Handles the bulk of the sorting for a class arm """
            
            # First, collect all the unique depts offered today by the reference arm sorted by the ATPG criterion
            base_dept_list = sorted(day_obj.get_depts_of_arm_today(ref_arm, duplicate=False), key=lambda dept:dept.dept_ATPG(), reverse=True)
            
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
                # The Count_with_order function is used instead of counter, to preserve the order of the items
                # -----------------------------------------------------------------------------------
                chunk_sequence = Tt_algo_calc.Count_with_order(list(Tt_algo_calc.Count_with_order(day_obj.teachers_depts_today(teacher)).values()))
                # -------------------------------------------------------------------------------------------------
                # --------------------------- FEED INTO THE CHUNKING ALGORITHM ------------------------------------
                # -------------------------------------------------------------------------------------------------
                # Shift with the int_values of the ArmsPeriodsLeft_objs of the arm so we can keep track of which ones have been poppwd when occupied2
                teacher_chunk_numbers = algorithm(array, chunk_list=chunk_sequence, shift_value=shift_val)
                teacher_depts_weight = Tt_algo_calc.weightlist(day_obj.teachers_depts_today(teacher))
                # print(f"Teacher depts weight: {teacher_depts_weight} -- chunk numers at first {teacher_chunk_numbers}")
                teacher_chunk_numbers = Tt_algo_calc.Moveover(teacher_chunk_numbers, array)
                teacher_chunk_numbers = Tt_algo_calc.align_chunklist_to_weightlist(teacher_depts_weight, teacher_chunk_numbers)

        
                ref_arm_details = []
                for (arm, dept), chunk in zip(Tt_algo_calc.Set_with_order(day_obj.teachers_depts_today(teacher)), teacher_chunk_numbers):

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
                shift_val = max(Tt_algo_calc.strip_list_wrapper(translate)) if translate else 0

                # ------------------------------------------------------------------------------------------------------------------
                # 1. Go through all the periods in the ref_arm and "Moveover" the periods chunk values for good measure

                # 1A. Now moveover_fixed the teachers chunk with the ref-arms chunks as constant
                # The armPeriodsLeft objs periods_int_list already provides the ref_arm list integers
                fixed = [elem.chunk for elem in ref_arm_details]
                # Now try move_over_fixed to see if its possible to keep this arm fixed
                clip_offs, all_chunk_list = 0, Teachers_and_chunked_val[teacher].copy()

                while True:
                    # In the event that the moveover_fixed fails because the fixed_chunk
                    # does not allow it, pop out the last item and Moveoever again
                    clipped_chunk = [elem.chunk for elem in all_chunk_list]
                    try:
                        teacher_fixed = Tt_algo_calc.Moveover_fixed(clipped_chunk, array, fixed_item=fixed)
                    except Exception:
                # Clip off the last item of all chunk. The chunk items in the 
                        clip_offs += 1
                        all_chunk_list.pop()
                    else:
                        break


                if clip_offs != 0:
                    carry_over = Teachers_and_chunked_val[teacher][-1*clip_offs:]

                    if teacher not in self.displaced_teachers:
                        self.displaced_teachers[teacher] = {}
                    if day_obj not in self.displaced_teachers[teacher]:
                        self.displaced_teachers[teacher][day_obj] = []
                    self.displaced_teachers[teacher][day_obj] += carry_over

                    for arm, _, dept in carry_over:
                        arm.remove_dept_from_arm_temp_holder_for_days(dept, day_obj)

                    Teachers_and_chunked_val[teacher][-1*clip_offs:] = []
                    # Remove these clipped_offs from the subject teacher teaches today and from Arm_and_chunked_val and Teacher_and_chunked_val
                    # --------------------------------------------------------------------------------------------
                            
                # 2A. Begin popping out teachers chunk (in its combination) numbers from the periodsint of the arms he is teaching
                combinations = Tt_algo_calc.Possible_combs_with_fixed(teacher_fixed, fixed, array)
                # A dictionary to record the number of times a fragment goes free before it crashes
                crash_counter = {index: 0 for index,_ in enumerate(combinations)}

                for index, combo in enumerate(combinations.copy()):
                    T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=combo.copy())
                    # The below is a list of (arm, chunk) tuples to help rebuild the arm's periodsint_list objects
                    frag_for_rebuild = []

                    for segment in Teachers_and_chunked_val[teacher].copy():
                        arm, chunk, dept = segment.arm, segment.chunk, segment.dept
                        try:
                            # Try popping out the chunk values from ArmPeriodsLeft
                            ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk)
                        except ValueError:
                            # If an error occurs because that chunk has already been cleaned off by a previous teacher
                            # Rebuild the arms_periodsleft object for another combination since this combination doesn't work.                            
                            for arm_, chunk_ in frag_for_rebuild:
                                ArmsPeriodsLeft_objs[arm_].append_to_periodsleft(chunk_)
                            break
                        
                        else:
                            # If the chunk value is popped out without any problems
                            crash_counter[index] += 1
                            frag_for_rebuild.append((arm, chunk))
                
                    else:
                        # ------- THE TEACHERS SEGMENT WORKED HERE! 
                        # Remove teachers subjects from the list of all the arms offering it. We are done with him
                        for class_arm, _, dept_ in Teachers_and_chunked_val[teacher]:
                            # Go to the dict bearing all the arms and remove him from there
                            class_arm.remove_dept_from_arm_temp_holder_for_days(dept_, day_obj)

                        break
                        # -------------------------------------------------------------------------------------
                
                # If despite all this, none of the combinations worked for the teacher's chunk
                else:
                    best_combo_index, best_fit_index = max(crash_counter.items(), key=lambda comb_index: comb_index[1])

                    choice = combinations[best_combo_index]
                    # print(f"choice: {choice} <==> {Teachers_and_chunked_val[teacher]}")
                    T_A_Reconstruct(teacher_obj=teacher, teachers_replace_list_arg=choice)

                    # # Remove everything after the index of best_fit from the teacher
                    carryover = Teachers_and_chunked_val[teacher][best_fit_index:]

                    for class_arm, _, dept in Teachers_and_chunked_val[teacher]:
                        # Remove teachers subjects from the list of all the individual arms offering it. We are done with him
                        # Go to the dict bearing all the arms and remove him from there
                        class_arm.remove_dept_from_arm_temp_holder_for_days(dept, day_obj)
                        
                    # Clear out this carryover from teachers and chunked val
                    Teachers_and_chunked_val[teacher][best_fit_index:] = []                    
                    # ------------------------------------
                    
                    # If the teacher and chunked val is not empty
                    if Teachers_and_chunked_val[teacher]:
                        for arm, chunk, _ in Teachers_and_chunked_val[teacher]:
                            ArmsPeriodsLeft_objs[arm].pop_out_period_val(chunk)
                        
                    else:
                        # If the Teacher_and_chunked_val list is empty, remove it completely
                        del Teachers_and_chunked_val[teacher]

                    # Add defaulting chunk fragments to the dictionary of displaced teachers
                    if not teacher in self.displaced_teachers:
                        self.displaced_teachers[teacher] = {}
                    if day_obj not in self.displaced_teachers[teacher]:
                        self.displaced_teachers[teacher][day_obj] = []
                    self.displaced_teachers[teacher][day_obj] += carryover

        # --------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------
        # OUTSIDE THE FUNCTION

        # the below returns a dictionary with the number of periods as value and the arm as the key
        all_armsperiods_today_dict = day_obj.all_classarm_periods_for_today()
        avg_period_len = day_obj.get_average_period_length_today()
        # A refence class arm is needed to help be the anchor for our chunking.
        ref_arm = reference_arm if reference_arm else day_obj.arms_today_list[reference_arm_index]

        # If this arm is present today rotate the list of arms according to it, else use the list that way.
        if ref_arm in day_obj.arms_today_list:
            self.list_from_reference_arm = TimetableSorter.rotate_list(day_obj.arms_today_list, item=ref_arm)
        else:
            self.list_from_reference_arm = day_obj.arms_today_list
        
        # The below is a dict with the arm:ArmPeriodsLeft()
        ArmsPeriodsLeft_objs = self._nail_int_to_arms(day_obj)

        # THIS SPECIAL DICTIONARY HOLDS ALL THE ARMS AND THEIR CHUNKED VALUES (WHEN THEY HAVE FINALLY BEEN CHUNKED)
        Teachers_and_chunked_val = {}

        # =========================================
         # Couple the new chunked value [a,b] and the arm into a dictionary {arm:[(dept,[a,b])]}
            # --------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------
        # Teachers already handled so we dont handle them
        touched_teachers = []
        # Below.. Stored in the variable self.sort_algorithm to be called from the details module
        self.sort_algorithm = algorithm
        for arm in self.list_from_reference_arm:
            arms_teachers_sort(arm, array=avg_period_len)

        # Also add all the teachers who have had no problems so far -- ready teachers
        self.All_Teachers_and_chunked_val[day_obj] = Teachers_and_chunked_val.copy()
        # Also add ArmsPeriodsLeft to the overall dictionary dictionary for today
        self.All_Armperiodsleft[day_obj] = ArmsPeriodsLeft_objs.copy()


    def initial_algosort(self, algorithm_text, reference_day=None, reference_arm=None, beam_max_value=40):
        """ Runs the sorting algorithm for all the days of the week (displaced_teachers are not yet considered).
        reference day and reference arm are the actual objects """

        # Get the working algorithm
        algorithm = self.sort_algorithms[algorithm_text]
        len_days = len(self.tt_obj.list_of_days)

        # Rotate this list with respect to the reference day
        days_list = self.tt_obj.list_of_days if not reference_day else self.rotate_list(self.tt_obj.list_of_days, item=reference_day)
        for count, day_obj in enumerate(days_list, start=1):
            # time.sleep(0.01)
            self.algosort_teachers_per_day(day_obj, algorithm, reference_arm=reference_arm, reference_arm_index=0)
            beam_val = round(count * beam_max_value / len_days)
            yield beam_val


    def handle_displaced_teachers(self, beam_max_value=20, prev_max_value=40):
        """ Handles the insertion of displaced teachers of a particular class arm into a new day since it cannot fit its home day.
        beam_max_value is the max width of each iteration, prev_max_value is the value from the algo_sort method and will translate
        the beam value in this method """

        # ---------------------------------------------------------------------------------------------
        def algo_teachers_teaching_days(teacher):
            """ returns the days in which a teacher teaches after his periods have been sorted by the algorithm """
            algo_teaching_days = []
            for day, teachers_dict in self.All_Teachers_and_chunked_val.items():
                if teacher in teachers_dict:
                    algo_teaching_days.append(day)
            return algo_teaching_days


        # ---------------------------------------------------------------------------------------------
        # Inner class to update Teacher_and_chunked_val as well as Arm_and_chunked_val
        def update_teacher_and_arm(day, dept, new_chunk, teacher=None, arm=None):
            """ Inner function to put new chunk values into the teacher_and _chunked_val and Arm_and_chunked_val
            on a particular day. new_chunk from the arg is cast into a list that encloses the new chunk value, even if it was a list before.
            Hence the next line... """

            new_chunk_val = new_chunk[0] if len(new_chunk) == 1 else tuple(new_chunk)
            
            if teacher:
                if teacher not in self.All_Teachers_and_chunked_val[day]:
                    # print(f"NN_OUTING: {self.All_Armperiodsleft[day][arm].periodsint_list} __ chunk_val: {new_chunk_val}")
                    self.All_Teachers_and_chunked_val[day][teacher] = [self.teacher_n_chunk(arm, new_chunk_val, dept)]
                else:
                    for index, (_arm_, _chunk_, _dept_) in enumerate(self.All_Teachers_and_chunked_val[day][teacher]):
                        # If the arm already exists in the dictionary today
                        if _arm_ == arm and _dept_ == dept:
                            new_list = [_chunk_] + [new_chunk_val]
                            # Replace the whole named_tuple at this position "index"
                            self.All_Teachers_and_chunked_val[day][teacher][index] = self.teacher_n_chunk(arm, new_list, dept)
                            break
                    else:
                        # If this arm does not already exist in the dictionary today
                        self.All_Teachers_and_chunked_val[day][teacher].append(self.teacher_n_chunk(arm, new_chunk_val, dept))
                    
                self.All_Armperiodsleft[day][arm].pop_out_period_val(new_chunk_val)
                # Tt_algo_calc.casual_removeall(arm.temp_dept_holder_for_days[day_], dept)


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
                            pre_chunk = [elem.chunk for elem in self.All_Teachers_and_chunked_val[day].setdefault(teacher, [])]
                            # get the unoccupied periods for arm today
                            un_occ = self.All_Armperiodsleft[day][arm].periodsint_list
                            # check which pieces of un_occ do not overlap for certified chunk pieces
                            cert = [piece for piece in un_occ if not Tt_algo_calc.check_for_overlap(pre_chunk + [piece])]
                        
                        else: 
                            # If teacher does not teach on this day
                            cert = self.All_Armperiodsleft[day][arm].periodsint_list

                    # If arm does not have class on this day, make room for it
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
                        update_teacher_and_arm(day, dept, cert.copy(), teacher=teacher, arm=arm)
                        self.len_chunk -= len(cert)

                    # ------------------------------------
                    if self.len_chunk <= 0:
                        self.handled = True
                        return

        # -----------------------------------------------------------------------------------------------
        # ------------------------ OUTSIDE BOTH INNER FUNCTIONS ------------------------------
        len_displaced_teachers = len(self.displaced_teachers.items())
        # Go to every teacher in the displaced teacher dict
        for count, (teacher, day_dict) in enumerate(self.displaced_teachers.items(), start=1):

            # Days among teacher's teaching days in which he actually teaches
            work_day= [day for day in teacher.teaching_days if day in algo_teachers_teaching_days(teacher)]
            # Days among teachers teaching days in which he does not teach
            free_day = [day for day in teacher.teaching_days if not day in algo_teachers_teaching_days(teacher)]
        

            for day_, chunk_list in day_dict.items():
                handled_list = chunk_list.copy()

                for details in chunk_list:
                    # print(f"Details here: {details}")                    
                    dept, arm, chunk = details.dept, details.arm, details.chunk
                    # length of the chunk
                    self.len_chunk = 1 if isinstance(chunk, int) else len(chunk)
                    
                    self.handled = False
                    patch_teachers(free_day, x_info="On free day.")
                    patch_teachers(work_day, x_info="On work days")
                    # patch_teachers(over_day, x_info="Overtime days")
                    
                    if self.handled:
                        handled_list.remove(details)
                    else:
                        # restore the self.displayed_teacher
                        # chunk_ = Tt_algo_calc.strip_list_wrapper([chunk])[-1*self.len_chunk:]
                        chunk_ = Tt_algo_calc.strip_list_wrapper([chunk])[-1*self.len_chunk:]
                        # print(f"Defaulting chunk: {chunk_}")
                        chunk_ = chunk_[0] if self.len_chunk == 1 else chunk_
                        # print(f"chunk that fell through: {chunk_, arm, dept} -- handled_list: {handled_list}")

                        # --- Remove replace this detail in handled_list
                        for index,(_arm_, _chunk_, _dept_) in enumerate(handled_list.copy()):
                            if _arm_ == arm and _chunk_ == chunk and _dept_ == dept:
                                handled_list[index] = self.teacher_n_chunk(arm, chunk_, dept)
                                break
                self.displaced_teachers[teacher][day_] = handled_list
                beam_val = round((count * beam_max_value / len_displaced_teachers) + prev_max_value)
                
                yield beam_val


    # ------------------- CLEAN UP THE SELF.DISPLACED_TEACHERS DICTIONARY ----------------------------
    def clean_out_displaced_teachers(self, beam_max_value=10, prev_max_value=60):
        """ Clean out the self.displaced_teachers dictionary stuff of teachers who already have been handlded """
        len_displaced_teachers = len(self.displaced_teachers)

        for count, (teacher_obj, day_dict) in enumerate(self.displaced_teachers.copy().items(), start=1):
            can_cancel = False if day_dict else True
            # for dict_item in chunk_list:
            for _day_, particulars_list in day_dict.copy().items():
                # If the list bearing all the teacher's items (particulars_list) is not empty break out this loop, CAN'T delete
                if particulars_list:
                    can_cancel = False
                    break
                del self.displaced_teachers[teacher_obj][_day_]
            else:
                can_cancel = True
            # If no break occurs that is all the particular_list items are empty
            if can_cancel:
                del self.displaced_teachers[teacher_obj]

            beam_val = round((count * beam_max_value / len_displaced_teachers) + prev_max_value)
            yield beam_val

        # ---- Defined below!!
        # Check if not all of the displaced teachers have been handled, raise an exception if so
        self.displaced_teachers_empty_or_no()


    def displaced_teachers_empty_or_no(self):
        """ This function checks whether the self.displaced_teachers dictionary is empty, if it is not, a certain type
        of exception is called """
        if self.displaced_teachers:
            raise Tt_exceptions.SomethingWentWrong(self.displaced_teachers)



    def map_chunk_to_arms_periods(self, beam_max_value=20, prev_max_value=80):
        """ Maps the already finished chunked values to the corresponding periods of the class arm """
        Arms_and_chunked_val = self.Arms_and_chunked_val()
        len_arms_and_chunked_val = len(Arms_and_chunked_val)

        for count, (day, arm_dict) in enumerate(Arms_and_chunked_val.items(), start=1):
            for arm, arm_detail_list in arm_dict.items():
                # filter out the academic periods from list of all the periods today
                acad_periods = [period for period in arm.periods[day] if period.is_acad]

                for dept, chunk, _ in arm_detail_list:
                    # map each chunk value to the period of this arm with the same index number
                    chunk_ = Tt_algo_calc.strip_list_wrapper([chunk])
                    for k in chunk_:
                        # Now map it to the period at position k on this day
                        acad_periods[k].add_details_to_period(dept)

            beam_val = round((count * beam_max_value / len_arms_and_chunked_val) + prev_max_value)
            yield beam_val

    

    def Arms_and_chunked_val(self):
        """ Make a dictionary of all the chunks per day based on the arm, and not the teacher this time """
        container = {}
        for day, t_dict_item in self.All_Teachers_and_chunked_val.items():
            container[day] = {}
            for teacher, t_details_list in t_dict_item.items():
                for arm, chunk, dept in t_details_list:
                    if arm not in container[day]:
                        container[day][arm] = []
                    container[day][arm].append(self.arm_n_chunk(dept, chunk, teacher))
        return container


    def map_finished_arm_chunk_dept_to_teacher(self, beam_max_value=10, prev_max_value=90):
        """ FINAL PROCESS OF THE SORTING OPERATION. As soon as the sorting is all done, add this arm_chunk_dept values from All_teachers_and_chunked_val
        to each of the teacher objects in the All_teachers_and_chunked_val dictionary """

        len_all_teachers_chunk_val = len(self.All_Teachers_and_chunked_val)
        for count, (day, teacher_dict) in enumerate(self.All_Teachers_and_chunked_val.items()):
            for teacher, chunk_list in teacher_dict.items():
                # teacher.add_finished_day_arm_chunk_dept_to_teacher(day, chunk_list)
                for arm, chunk, dept in chunk_list:
                    # Also add this details to the dept object at once
                    dept.add_finished_chunk_details_to_dept(arm, chunk, teacher, day)
                    teacher.add_dept_to_teacher(dept)
                    teacher.add_finished_day_arm_chunk_dept_to_teacher(day, (arm, chunk, dept))

                    
                    if dept.is_parallel:
                        for _teacher_ in dept.get_teacher_pair_given_teacher(teacher):
                            _teacher_.add_dept_to_teacher(dept)
                            _teacher_.add_finished_day_arm_chunk_dept_to_teacher(day, (arm, chunk, dept))

            beam_val = round((count * beam_max_value / len_all_teachers_chunk_val) + prev_max_value)
            yield beam_val


    def unsort_operation_gen(self, beam_max_value=100):
        """ A generator that totally cancels out the Sort operation """
        self.All_Teachers_and_chunked_val.clear()
        self.All_Armperiodsleft.clear()
        # Purge the the periods of the class arms
        len_arms, len_teachers = len(self.tt_obj.list_of_school_class_arms), len(self.tt_obj.list_of_all_teachers)
        # share
        arms_share, teachers_share = beam_max_value/2, beam_max_value/2

        for count, arm in enumerate(self.tt_obj.list_of_school_class_arms, start=1):
            arm.clean_out_dept_from_periods()
            beam_val = round(count * arms_share / len_arms)
            yield beam_val

        for count, teacher in enumerate(self.tt_obj.list_of_all_teachers.copy(), start=1):
            teacher.remove_all_finished_day_arm_chunk_dept_to_teacher()
            # if the teacher is an extra, space-filling teacher
            if teacher.space_filler:
                self.tt_obj.del_teacher(teacher)
            beam_val = round((count * teachers_share / len_teachers) + arms_share)
            yield beam_val
        yield beam_max_value


    def undo_sort_operation_func(self, beam_max_value=100):
        """ The function equivalent for the generator above """
        undo_gen = self.undo_sort_operation_gen(beam_max_value)
        loop = True
        while loop:
            try:
                next(undo_gen)
            except StopIteration:
                loop = False



    # ----------------------------------------------------------------------------------------------------------------------
    # -------------------------------- METHODS TO ESTIMATE HOW MANY MORE TEACHERS ------------------------------------------
    class ExtraTeacherHolder:
        """ class to handle the creation and assignment of arms to the extra teachers created """
        def __init__(self, tt_obj, dept):
            self.dept = dept
            self.timet_obj = tt_obj
            self.xtra_created_teachers = []

        def create_extra_teacher(self, freq=1):
            """ Creates a 'freq' number of teachers """
            self.timet_obj.create_teacher(frequency=freq, dept_objs_list=[self.dept], teaching_days=self.timet_obj.list_of_days,
                specialty=self.timet_obj.list_of_school_class_groups, designation="(Exclusive) Member of Staff")

            # Grab the teacher (the newly added teacher to the 'dept'; the last on the list)
            just_made_teachers = self.timet_obj.list_of_all_teachers[-self.dept.constituent_num():]
            self.xtra_created_teachers.extend(just_made_teachers)
            # indicate that these teachers are extra, space-filling teachers
            for teacher in self.xtra_created_teachers:
                teacher.space_filler = True
            # Smart! take the first teacher in the just made teachers as a pointer to the rest
            return just_made_teachers[0]

        def created_teachers_num(self):
            """ Returns the number of teachers created as a fix for self.dept """
            return len(self.xtra_created_teachers)


    # ------------------------------------------------------------------------------------------------
    def _undo_one_teacher_sort(self, _teacher_, _arm_, _dept_):
        """ Removes the details of 'teacher' where arm is 'arm' and dept is 'dept' from the 
        self.All_teachers_and_chunked_val dictionary"""
        for day, t_dict_item in self.All_Teachers_and_chunked_val.copy().items():
            for teacher, t_details_list in t_dict_item.items():
                if teacher == _teacher_:
                    for arm, chunk, dept in t_details_list:
                        if arm == _arm_ and dept == _dept_:
                            # Remove this particular detail named_tuple from the list
                            self.All_Teachers_and_chunked_val[day][_teacher_].remove((arm, chunk, dept))
                            # Add backs the chunk values to the All_periods_left objects
                            self.All_Armperiodsleft[day][arm].append_to_periodsleft(chunk)
                    


    def arms_and_periodsleft_for_dept(self, dept, day):
        """ DICT. {arm: arms_periods_left} for a particular day """

        dept_dict = defaultdict(list)
        for days_dict in self.displaced_teachers.values():
            if day in days_dict:
                for arm, chunk, dept_ in days_dict[day]:
                    if dept_ == dept:
                        try:
                            dept_dict[arm].append(self.All_Armperiodsleft[day][arm].list_after_pop)
                        except KeyError:
                            pass
        return dept_dict



    def xtra_teachers_for_balance(self):
        """ Estimates the extra number of teachers needed to plug the holes in the timetable """

        def distribute(arm, dept, teacher, distilled_periods_left):
            """ Packet (pre-arrange) this teachers periods into the arms days of the week """
            freq, chunk = arm.depts_and_freq_details[dept]
            # get all the period integers for every day
            periods_available = sum([len(self.All_Armperiodsleft[_day_][arm].list_after_pop) for _day_ in self.tt_obj.list_of_days
            if arm in self.All_Armperiodsleft[_day_]])

            print(f"Periods available: {periods_available} --- freq: {freq}")

            if freq <= periods_available:
                keep_cycling = True
                while keep_cycling:
                    for day in self.tt_obj.list_of_days:
                        arms_p_left_obj = self.All_Armperiodsleft[day].get(arm)

                        if arms_p_left_obj != None:
                            arms_list = arms_p_left_obj.list_after_pop
                            chop_off = min((len(arms_list), chunk)) if freq >= chunk else min((len(arms_list), freq))
                            # The periods that do not coincide at all with those of any other arm chosen today (for this teacher) in sorted format
                            viable_periods = sorted(list(set(arms_list) - distilled_periods_left[day]))
                            periods = viable_periods[0] if len(viable_periods) == 1 else viable_periods[:chop_off]
                            # Remove this amount from the periods_left object. It has been taken.
                            self.All_Armperiodsleft[day][arm].pop_out_period_val(periods)

                            # Add periods to the All_Teachers_and_chunked_val dictionary
                            if not teacher in self.All_Teachers_and_chunked_val.setdefault(day, {}):
                                self.All_Teachers_and_chunked_val[day][teacher] = [self.teacher_n_chunk(arm, periods, dept)]
                            else:
                                for index, (arm_, periods_, dept_) in enumerate(self.All_Teachers_and_chunked_val.copy()[day][teacher]):
                                    if arm_ == arm and dept_ == dept:
                                        self.All_Teachers_and_chunked_val[day][teacher][index] = self.teacher_n_chunk(arm, [periods_] + [periods], dept)
                                        break
                                else:
                                    # if this subject and arm were never there, add them
                                    self.All_Teachers_and_chunked_val[day][teacher].append(self.teacher_n_chunk(arm, periods, dept))

                            
                            # Add this periods to the distilled_periods_left set for today
                            for period in Tt_algo_calc.strip_list_wrapper([periods]):
                                distilled_periods_left[day].add(period)

                            # Reduce freq by chop_off
                            freq -= chop_off
                            if freq <= 0:
                                keep_cycling = False
                                break

        # Inner function
        def is_compatible(arm_x, dept_, distilled_periods_left):
            """ BOOL. Checks to see if there is any overlap between arm x and all the others today  for a particular dept """
            if not dept in arm.depts_and_freq_details:
                return None

            freq, _= arm.depts_and_freq_details[dept]
            unique_num = 0
            for day in self.tt_obj.list_of_days:
                arms_periods = set(self.All_Armperiodsleft[day][arm].list_after_pop)
                # check to see whether there are any periods not taken by any other arms today
                unique = arms_periods - distilled_periods_left.setdefault(day, set())
                unique_num += len(unique)
            return unique_num >= freq

        
        # Inner function, all the variables are in the scope of its container function
        def make_extra_teachers(dept):
            self.xtra_teachers_dict[dept] = self.ExtraTeacherHolder(self.tt_obj, dept)
            # extract all the free periods of all the defaulting arms offering dept to see if there are coincidences
            distilled_arms = []
            # A dictionary of {day: periods_left_list} for each dept
            distilled_periods_left = {_day_:set() for _day_ in self.tt_obj.list_of_days}

            for arm_dict in {_day_:self.arms_and_periodsleft_for_dept(dept, _day_) for _day_ in self.tt_obj.list_of_days}.values():
                for arm in arm_dict:
                    if not arm in distilled_arms:
                        distilled_arms.append(arm)
            
            # list of all the arms that would have the same teacher
            while distilled_arms:
                pairs_list = []
                for index, arm in enumerate(distilled_arms):
                    if index == 0:
                        pairs_list.append(arm)

                    # if it is not the first item in the distilled_arms list
                    else:
                        # if no coincidences, pair it together with the first_arm on the list
                        if is_compatible(arm, dept, distilled_periods_left):
                            pairs_list.append(arm)
                        
                # make a teacher for all the arms in pairs_list
                teacher = self.xtra_teachers_dict[dept].create_extra_teacher()
                for arm_ in pairs_list:
                    # map (assign) this arm to teacher and remove it from the list of distilled arms
                    self.tt_obj.map_teacher_from_dept_to_arm(dept, arm_, teacher_obj=teacher)
                    # distribute this arms frequency into the arm's periods left and return {day:periods_chosen_for_dept}
                    distribute(arm_, dept, teacher, distilled_periods_left)
                    distilled_arms.remove(arm_)
        
        # ---------------------------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------------------------
        if self.displaced_teachers:
            first_progress_width, second_progress_width = 20, 40

            self.xtra_teachers_dict, defaulting_depts_list = {}, []
            len_displaced_teachers = len(self.displaced_teachers)

            for count, (teacher, days_dict) in enumerate(self.displaced_teachers.items()):
                for day, arm_det_list in days_dict.items():
                    for arm, chunk, dept in arm_det_list:
                        # Undo all the sort and chunk operation for this teacher 
                        self._undo_one_teacher_sort(teacher, arm, dept)
                        # unmap (completely disengage) teacher from this arm and dept
                        self.tt_obj.unmap_teacher_from_dept_from_arm(dept, arm, teacher=teacher)
                        # add this dept to the list of defaulting_depts
                        print(f"{teacher} disengaged from {dept} for {arm} in fix")
                        if not dept in defaulting_depts_list:
                            defaulting_depts_list.append(dept)

                beam_val = round(count * first_progress_width / len_displaced_teachers)
                yield beam_val

            
            # ------ Now begin making extra (exclusive) teachers
            for count, dept in enumerate(defaulting_depts_list):
                make_extra_teachers(dept)
                beam_val = round(count * second_progress_width / len_displaced_teachers) + first_progress_width
                yield beam_val
    
    
    def clear_out_jobless_teachers(self):
        """ Goes through the timetable and deletes any 'jobless' teachers. i.e. teachers who, by reason
        of the sorting and the fixing, have had all the arms they teach stripped from them. """
        for teacher in self.tt_obj.list_of_all_teachers.copy():
            # if this teacher has en empty dictionary for the class arms they are teaching
            if not teacher.dept_and_arms:
                try:
                    self.tt_obj.del_teacher(teacher)
                except Exception as err:
                    print(f"{teacher} jobless, attempted delete: Error is {err}")
                else:
                    print(f"{teacher} (jobless) successfully cleared out")


    def track_model_item_thru_backend(self, model_item_str):
        """ Goes through the entire timetable and picks out all the occurrences of 'model_item_str' """

        track_dict = defaultdict(list)
        for arm in self.tt_obj.list_of_school_class_arms:
            for day, periods_list in arm.periods.items():
                for period in periods_list:
                    if model_item_str in period.contents_for_tracking():
                        # add the day, arm and period id (id is already 1-indexed, as opposed to 0-indexed)
                        track_dict[day.full_name].append((arm.full_name, period.id))
        return track_dict



    # ---------------------------------------------------------------------------------------------------------------
    # --------------------- METHODS TO HANDLE THE "ADVANCED SETTINGS" -----------------------------------

    # def calc_teachers_spacing_per_algorithm(self, reference_arm_obj=None, reference_day_obj=None):
        """ calculates the spacing of the teachers with all the algorithms in turn """

        # --------------------------------------------------------------------------------------
        def calc_spacing_function(space, denominator):
                """ Inner function to calculate the spacing of an item based on the sine curve """
                return round((4*efficiency_max*space*(1 - (space/denominator))/denominator) + efficiency_translation, 3)


        def calc_spacing(list_argument, periods_range_num):
            """ Handles the teaching efficiency calculation for the items in a list (list of integers).
            'periods_range_num' (INT) represents the total number of room available over which the spacing can be calculated. """
            list_arg = Tt_algo_calc.strip_list_wrapper(list_argument)
            list_arg_length = len(list_arg)
            if list_arg_length <= 1:
                return 0
         
            eff_list = []
            for k in range(list_arg_length):
                if k != 0:
                    eff_list.append(list_arg[k] - list_arg[k - 1] - 1)
            return sum([calc_spacing_function(m, periods_range_num) for m in eff_list])

        # -----------------------------------------------------------------------------------
        # The dictionary to hold the hold the key(alg_name_str) and ineer dictionaries of each teacher and its spacing values
        teacher_space_dict_by_algo = {}
        days_list = self.tt_obj.list_of_days if not reference_day_obj else self.rotate_list(self.tt_obj.list_of_days, item=reference_day_obj)

        # constants for the calculation of teachers' efficiency. The first is the maximum value of the parabolic curve, the second is
        # the 'extra' amount to translate by.
        efficiency_max, efficiency_translation = 0.85, 0.15
            
        # Now run all the algorithms in tow
        for algorithm in self.sort_algorithms.values():
            # Clear the dictionary to hold the contents of the teachers
            self.All_Teachers_and_chunked_val.clear()

            for arm in self.tt_obj.list_of_school_class_arms:
                # restore the packeted depts into temp_dept_holder_for_days
                arm.temp_dept_holder_for_days.clear()
                for day, depts_list in arm.perm_dept_holder_for_days.items():
                    arm.temp_dept_holder_for_days[day] = depts_list.copy()


            for day_obj in days_list:
                self.algosort_teachers_per_day(day_obj, algorithm, reference_arm=reference_arm_obj, reference_arm_index=0)
            
            handle_and_clean_out_teachers = self.handle_displaced_teachers(), self.clean_out_displaced_teachers()

            for operation in handle_and_clean_out_teachers:
                loop = True
                while loop:
                    try:
                        next(operation)
                    except Tt_exceptions.SomethingWentWrong:
                        print(f"Algorithm {algorithm.__name__} errored out!!")
                    except StopIteration:
                        loop = False
            
            # dict to hold teacher:[spacing value (number), amount_of days] for this algorithm
            teacher_spacing_dict = {}
            # Now check the teachers and chunked val dictionary for each of the algorithms
            for day, teachers_dict in self.All_Teachers_and_chunked_val.items():
                for teacher, chunk_details in teachers_dict.items():
                    # Get all the chunk values
                    chunk_list = map(lambda detail: detail.chunk, chunk_details)
                    chunk_list = sorted(Tt_algo_calc.strip_list_wrapper(chunk_list))
                    # get the average length of a period today
                    avg_period_length = day.get_average_period_length_today()
                    spacing = calc_spacing(chunk_list, avg_period_length)

                    if not teacher in teacher_spacing_dict:
                        teacher_spacing_dict[teacher] = [0,0]
                    teacher_spacing_dict[teacher][0] += spacing
                    teacher_spacing_dict[teacher][1] += 1

            # Now feed the details of the teacher_spacing_dict into the teacher_space_dict_by_algo
            # Morphe the details of the teacher_spacing_dict
            for teacher, (spacing, recurrence) in teacher_spacing_dict.copy().items():
                # Put the  spacing divided by the number of days to a deci,al place of 4
                teacher_spacing_dict[teacher] = round(spacing / recurrence, 4)

            # Add this dictionary into the teacher_space_dict_by_algo as the value to the algorithm_name (the key)
            teacher_space_dict_by_algo[algorithm.__name__] = teacher_spacing_dict


        # JUST TO TEST WITH
        print("--------    --------   ------- SPACING -------   --------   ---")
        print(teacher_space_dict_by_algo)
        return teacher_space_dict_by_algo



    # ------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------- METHODS SOLELY FOR TESTING -----------------------------
    def check_arms(self):
        """FOR TESTING."""
        for arm in self.tt_obj.list_of_school_class_arms:
            print("-"*40)
            for day, depts in arm.temp_dept_holder_for_days.items():
                print(f"{day} --> {len(depts)}")


    def sort_thru_days(self, algorithm, reference_arm=None):
        """ STRICTLY FOR TESTING. """
        for day_obj in self.tt_obj.list_of_days[:]:
            self.algosort_teachers_per_day(day_obj, algorithm, reference_arm=reference_arm, reference_arm_index=0)


    def print_displaced(self):
        """ STRICTLY FOR TESTING """
        print(self.displaced_teachers)
        print("----.....-----.....-----")
        print(len(self.displaced_teachers))


    def print_arms_periods(self):
        """ STRICTLY FOR TESTING. print out all the periods of each class arm  and how much less the empty ones are"""
        for arm in self.tt_obj.list_of_school_class_arms:
            for day, periods_list in arm.periods.items():
                print(f"--------------{day} ---------------")
                per = [period.dept for period in periods_list if period.dept]
                print(per, len(periods_list) - len(per))
            
            print()
            print(f".............. {arm} ...............")


    def check_arms_temp_dept_holder(self):
        """ FOR TESTING """
        for arm in self.tt_obj.list_of_school_class_arms:
            sum_ = sum([len(elem) for elem in arm.temp_dept_holder_for_days.values()])
            print(f"{arm} --===-- {sum_}")
            # for day, depts in arm.temp_dept_holder_for_days.items():


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
        """ FOR TESTING. Prints out all the period integers of each class arm every day """
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


    def render_all_arms_periods(self):
        """ FOR TESTING? This method renders all the arms with their periods after the chunking process has been carried out """
        for arm in self.tt_obj.list_of_school_class_arms:
            print(f"-------------- {arm} ----------------")
            for day, arm_dict in self.Arms_and_chunked_val().items():
                arm_list, chunk_list = [], []
                for arm_details in arm_dict.setdefault(arm, []):
                    dept, chunk, _ = arm_details
                    count = 1 if isinstance(chunk, int) else len(Tt_algo_calc.strip_list_wrapper(chunk))
                    chunk_list.append(chunk)
                    for _ in range(count):
                        arm_list.append(dept)
                print(f"{day} ===> == {chunk_list}")
            print()


    def inspect_arms_and_teachers(self):
        """ FOR TESTING. """
        for arm in self.tt_obj.list_of_school_class_arms:
            print()
            print("-"*30)
            print()
            for day, dict_item in self.Arms_and_chunked_val().items():
                if arm in dict_item:
                    print(f"{day}, {arm} --> {len(Tt_algo_calc.strip_list_wrapper([elem.chunk for elem in dict_item[arm]]))} -- {Tt_algo_calc.strip_list_wrapper([elem.chunk for elem in dict_item[arm]])} ")



    def inspect_timetable_thru(self):
        """ FOR TESTING. Inspects the entire timetable through to see if no subject frequencies are left stranded """
        for arm in self.tt_obj.list_of_school_class_arms:
            for dept in arm.depts_and_teachers:
                # Frequency of this dept for this arm
                ref_freq, _ = arm.depts_and_freq_details[dept]
                freq = 0
                for periods_list in arm.periods.values():
                    for period in periods_list:
                        if period.dept == dept:
                            freq += 1

                # Now compare
                if ref_freq != freq:
                    print(f"Overall: {dept} is stranded for {arm}")



    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    # STATIC METHODS BELOW
    rotate_list = staticmethod(Tt_algo_calc.Translate_list_items)
