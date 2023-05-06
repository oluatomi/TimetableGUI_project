from jinja2 import Environment, FileSystemLoader
from ..models.Tt_algo_calc import nth_suffix


class ModelReportHTML:
    """ Super class for generating HTML reports. the details of institution and director etc
     """
    def __init__(self, template_name, output_filepath):
        self.template_name = template_name
        self.output_filepath = output_filepath if output_filepath.endswith("html") else output_filepath + ".html"
        self.stylesheet_filepath = "TIMETABLE/reports/report_templates/HTML_templates/shelva_stylesheet.css"
        self.context = {}
        self.institution=None
        self.director=None
        self.session=None
        self.acronym=None
        self.extra_info=None


    def populate_context(self):
        """ Populates the context dictioanry with some values that will be available to all the subclasses """
        self.context["institution"] = self.institution
        self.context["director"] = self.director
        self.context["session"] = self.session
        self.context["acronym"] = self.acronym
        self.context["extra_info"] = self.extra_info


    def load_template(self):
        """ This loads the template with the name 'template_name' and writes it into an HTML file """
        import os

        file_loader = FileSystemLoader("TIMETABLE/reports/report_templates/HTML_templates/")
        env = Environment(loader=file_loader)
        template = env.get_template("class_template.html")

        loaded_file = template.render(data=self.context)

        # write the contents of the loaded file into the outfile_name you specified
        with open(self.output_filepath, 'w') as file:
            file.write(loaded_file)
        
        # Copy out the contents of the stylesheet in the html templates folder
        with open(self.stylesheet_filepath, 'r') as file:
            stylesheet_ = file.read()

        # load into a stylesheet 
        stylesheet_filepath = os.path.join(os.path.dirname(self.output_filepath), "shelva_stylesheet.css")
        with open(stylesheet_filepath, 'w') as file:
            file.write(stylesheet_)




class HTMLReportByFaculties(ModelReportHTML):
    """ Facilitates the generation of reports on a faculty-by-faculty basis """
    def __init__(self, faculties_list, output_filepath, template_name="report_templates/HTML_templates/department_template.html"):
        super().__init__(template_name, output_filepath)
        # The faculty objects are handled at once in a list, the detail of each added into 
        # the self.context dictionary of the parent class
        self.faculties_list = faculties_list


    def populate_context(self):
        """ Populates the context dictionary that will be passed into the html document """
        super().populate_context()
        self.context["departments_and_details"] = []

        for faculty in self.faculties_list:
            context = {}
            context["department_name"] = faculty.name
            context["department_fullname_id"] = faculty.full_name
            context["department_description"] = faculty.description
            context["department_hod"] = faculty.HOD
            context["department_subjects"] = [
            {
                "name":dept.dept_name, "hos":dept.hos,
                "teachers":[{"fullname": teacher.full_name, "is_exclusive": teacher.is_exclusive(), "other_subjects":teacher.other_depts_taught_str(dept),
                "classarms_taught":teacher.classarms_taught_based_on_dept_str(dept), "specialization":teacher.specialization,
                "designation":teacher.designation, "regularity": "Full-time" if teacher.regularity else "Part-time"} for teacher in dept.teachers_list]
            } for dept in faculty.depts_list]

            # Add this faculties details to the self.context dictionary
            self.context["departments_and_details"].append(context)



class HTMLReportByClassGroups(ModelReportHTML):
    """ Facilitates the generation of reports on a classgroup basis """
    def __init__(self, classgroups_list, output_filepath, template_name=""):
        super().__init__(template_name, output_filepath)
        self.classgroups_list = classgroups_list


    def populate_context(self):
        """ Populates the context dictionary that will be passed into the html document """
        super().populate_context()
        self.context["classgroups_and_details"] = []

        for classgroup in self.classgroups_list:
            context = {}
            context["classgroup_name"] = classgroup.tag()
            context["classgroup_fullname_id"] = classgroup.full_name
            context["classgroup_position"] = nth_suffix(classgroup.id)
            context["sch_class_list"] = [{"sch_class_name":sch_class.sch_class_alias, "sch_class_fullname":sch_class.full_name,
                    "arms_list": [{"arm_name": arm.full_name, "arm_max_period_length":arm.max_period_length, 
                    "periods_per_day":[{"day":day.day, "periods": [{"period_name":period.period_name, "boundary":period.period_boundary_time_str} for period in periods_list]}
                    for day, periods_list in arm.periods.items()]} for arm in sch_class.school_class_arm_list]} 
                    for sch_class in classgroup.school_class_list]

            # Add this faculties details to the self.context dictionary
            self.context["classgroups_and_details"].append(context)



class HTMLReportByDays(ModelReportHTML):
    """ Facilitates the generation of reports on a day-day basis """
    def __init__(self, days_list, output_filepath, template_name="report_templates/HTML_templates/day_template.html"):
        super().__init__(template_name, output_filepath)
        self.days_list = days_list


    def populate_context(self):
        """ Populates the context dictionary that will be passed into the html document """
        super().populate_context()

        self.context["days_and_details"] = []

        for day in self.days_list:
            context = {}
            context["day_name"] = day.day
            context["day_position"] = nth_suffix(day.id)
            context["day_fullname_id"] = day.full_name
            context["class_groups"] = [{"classgroup_name":classgroup.full_name, "description":classgroup.description,
            "sch_classes_list":[{"name":sch_class.full_name,"arms_list":[{"name": arm.full_name, "periods": [{"period_name":period.period_name, "boundary":period.period_boundary_time_str}
                    for period in day.get_classarm_periods_for_today(arm)]} for arm in day.get_classarms_from_sch_classes(sch_class)]

                } for sch_class in day.get_sch_classes_from_class_group_today(classgroup)]
            } for classgroup in class_groups]

            # Add this faculties details to the self.context dictionary
            self.context["days_and_details"].append(context)



def HTMLReporter(tt_obj, basis, output_filepath):
    """ handles the generation of the HTML file for 'basis' (class_groups or by faculty or by day) """
    if "subject" in basis.lower():
        model_list = tt_obj.list_of_departments
        reporter = HTMLReportByFaculties(model_list, output_filepath)
    elif "class" in basis.lower():
        model_list = tt_obj.list_of_school_class_groups
        reporter = HTMLReportByClassGroups(model_list, output_filepath)
    else:
        model_list = tt_obj.list_of_days
        reporter = HTMLReportByDays(model_list, output_filepath)
    # ------ Instantiate with the proper arguments
    reporter.populate_context()
    reporter.load_template()


