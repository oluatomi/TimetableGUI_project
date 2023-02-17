# THIS MODULE HANDLES THE GENERATION OF ALL THE TIMETABLE DETAILS


class TimetableDetails:
    """ This class mainly handles the generation of details concerning
    all the elements of a timetable object """
    def __init__(self, tt_sorter):
        # The TimetableSorter object
        self.tt_sorter = tt_sorter
        self.tt_obj = self.tt_sorter.tt_obj


    def packet_repacket_teachers(self):
        """ IF PACKETING-REPACKETING FAILS, it returns a tuple with first_item  as a dictionary with all the dept objects
        and the number of teachers more they should have to make packeting-repacketing feasible. IF PACKETING-REPACKETING SUCCEEDS, 
        JUST RETURN SOMETHING LIKE SUFFICIENT OR STUFF.
        
        APPLICABLE IF AND ONLY IF PACKETING-REPACKETING HAS BEEN DONE! """
        try:
            self.packet_defaulters = self.tt_sorter.packet_repacket_defaulters
        except AttributeError:
            # No defaulters were found, the self.tt_sorter.packet_repacket_defaulters variable was never made
            # Means the packet_repacket ran perfectly
            return [], []
        # Here be the drama
        return self.packet_defaulters, [dept.full_name for dept in self.packet_defaulters]


    def packet_repacket_teachers_percentage(self):
        """ Calculates the percentage of teachers who defaulted in their packeting, and the percentage of those who didn't """
        try:
            defaulting_teachers_percentage = round(len(self.packet_repacket_teachers()) * 100 / self.tt_obj.list_of_all_teachers, 2)
        except ZeroDivisionError:
            defaulting_teachers_percentage, non_defaulting_teachers_percentage = 0, 0
        else:
            non_defaulting_teachers_percentage = 100 - defaulting_teachers_percentage
        return defaulting_teachers_percentage, non_defaulting_teachers_percentage


    def how_many_more_teachers_for_depts_packeted(self):
        """ Returns a tuple, the (number of teachers each dept object needs to have repacketing work out,, total number of more teachers,, 
        percentage of the "more" teachers relative to the current number of teachers). the self.packet_repacket_teachers
        function should already have been run """
        defaulting_depts, _ = self.packet_repacket_teachers()
        all_days_num = len(self.tt_obj.list_of_days)
        more_teacher_dict = {dept: dept.how_many_more_teachers(all_days_len=all_days_num) for dept in defaulting_depts}
        num_more_teachers = sum(more_teacher_dict.values())
        try:
            more_teachers_percentage = round(num_more_teachers * 100 / self.tt_obj.list_of_all_teachers, 2)
        except ZeroDivisionError:
            more_teachers_percentage = "Incalculable, no teachers registered yet"

        return more_teacher_dict, num_more_teachers, more_teachers_percentage


    def calculate_teachers_efficiency(self):
        """ returns a tuple of (sort_algorithm,, dictionary of teacher: teacher_eff_value for all the teachers in the timetable) """
        return self.tt_sorter.sort_algorithm.__name__, {teacher: teacher.get_teaching_efficiency() for teacher in self.tt_obj.list_of_all_teachers}


