import jinja2


class ModelReportHTML:
    """ Super class for generating HTML reports. the details of institution and director etc
     """
    def __init__(self, template_name, output_filename):
        self.template_name = template_name
        self.output_filename = output_filename if output_filename.endswith((".docx",".doc")) else output_filename + ".docx"
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



class HTMLreportByDepartment(ModelReportHTML):
    def __init__(self, facutly, template_name, output_filename):
        super().__init__(template_name, output_filename)