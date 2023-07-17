# AUTHOR: OLUWATOMILAYO INIOLUWA OWOEYE


class StatsDiagDetails:
    """ Handles the generation of details from the timetable object for the statistics and diagnsotics report """
    def __init__(self, tt_sorter):
        # The TimetableSorter object
        self.tt_sorter = tt_sorter
        self.tt_obj = self.tt_sorter.tt_obj
        self.context_dict = {}

    