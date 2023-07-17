# - ************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022
# -- All rights (whichever they might be) reserved!
# **************************************************************************
from ..models.Tt_models import TimeTable


def load_manual():
    with open('TIMETABLE/gui/TimeTable Extras/Time_table.html', 'r', encoding="UTF-8") as file:
        contents = file.readlines()

    content_dict = {}

    for line_num,line in enumerate(contents):
        if "TOPIC" in line:
            topic_num = line_num
            topic = line.strip("\n")
            continue
        if line_num == topic_num + 1:
            topic = line.strip("\n")
            content_dict[topic] = """"""
        else:
            content_dict[topic] += line
    return content_dict


def get_model_details_for_gui(model_object):
    """ 'model_object' is a faculty (Department in the GUI) or a dept object(the subject).
    This function makes details from the attributes of said object to be displayed on the GUI """
    if isinstance(model_object, Timetable.Faculty):
        detail_markup = f"""
            <p>Department name: {model_object.full_name}. </p>
            <p>Department headed by: {model_obj.HOD}. </p>
            <p>Child Subject Number: {len(model_object.depts_list)}.</p>
            <p>Description: {model_object.description}.</p>
          """
    
    elif isinstance(model_object, Timetable.Department):
        detail_markup = f"""
            <html>
            <p>Subject/course ID and full name: {model_object.full_name}.</p>
            <p>Headed by {model_object.hos}.
            <p>Mother Department: {model_object.faculty.full_name}.</p>
            <p>This course, based on the nature of its contents scores <strong>{model_object.dept_ATPG()}</strong> on the ATPG-
            course structure scale.
            <p>N.B: The ATPG scale is not by any means a measure of the importance of a subject/course. Such judgement is within the descretion
            of the school or Ministry of Education or the presiding institution(s) involved. This rating simply helps sort the courses.</p>
            <p>Number of resident teachers: {len(model_object.teachers_list)}</p>
            </html>
            """
    return detail_markup

        
if __name__ == "__main__":
    r = load_manual()
    print(r)
