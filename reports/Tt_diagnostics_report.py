from ..models.Tt_exceptions import SomethingWentWrong


class Diagnostics:
    """ SUPER CLASS of all the classes which will generate diagnostics. This class bears all the records which will be 
    common to all the child classes """
    def __init__(self, tt_sorter):
        self.tt_sorter = tt_sorter

    def diagnose(self):
        """ BOOLEAN. Returns true or false based on whether the tt_sorter's disolaced_teachers dictionary
        is empty or not. It will raise an EXCEPTION if sorting has not been done (no tt_sprter.displaced_teachers
        variable does not yet exist) """
        self.displaced_teachers_dict = self.tt_sorter.displaced_teachers
        return bool(self.displaced_teachers_dict)

    def extract_info(self):
        """ Extracts needed information from the timetable object (or the timetable sorter object) as the case may be"""
        self.all_teachers_created = [teacher.full_name for teacher in self.tt_sorter.tt_obj.list_of_all_teachers]
        self.all_days = [day.full_name for day in self.tt_sorter.tt_obj.list_of_days]
        self.all_classgroups = [classgroup.full_name for classgroup in self.tt_sorter.tt_obj.list_of_school_class_groups]
        self.all_classes = [clss.full_name for clss in self.tt_sorter.tt_obj.list_of_school_classes]
        self.all_arms = [clssarm.full_name for clssarm in self.tt_sorter.tt_obj.list_of_school_class_arms]
        # the faculties
        self.all_departments = [fac.full_name for fac in self.tt_sorter.tt_obj.list_of_faculties]
        self.all_subjects = [dept.full_name for dept in self.tt_sorter.tt_obj.list_of_departments]

    @property
    def all_teachers_created_set(self):
        return set(self._all_teachers_created)

    @property
    def teachers_who_got_to_teach_set(self):
        """"Returns a set of all the full_name attributes of all the teachers who, after the chunking and sorting processes got to teach
        at least one class """
        teachers = set()
        for teacher_dict in self.tt_sorter.All_Teachers_and_chunked_val.values():
            for  teacher in teacher_dict:
                teachers.add(teacher.full_name)
        return teachers

    @property
    def teachers_who_did_not_get_to_teach(self):
        """ Returns a set of teachers who through all the chunking and sorting did not get to teach, i.e. they were totally displaced """
        return self.all_teachers_created - self.teachers_who_got_to_teach_set


# ----------------------------------------------------------------------------------------------------
class DiagnosticsDocx(Diagnostics):
    def __init__(self, tt_sorter, template_filename="Timetable_Diagnostics.docx"):
        super().__init__(tt_sorter)
        self.template_filename = template_filename if template_filename.endswith((".docx",".doc")) else template_filename + ".docx"

