# ----- TESTING WITH FEGO STYLE -------------
# Simply populate all fields and save. Use the App to run the file
from . import Tt_manager, Tt_exceptions
from collections import namedtuple


def run_gen(gen_obj, *args, **kwargs):
    """ function to run a tuple of generators """
    
    print("."*40)
    print(f"GENERATOR RUNNING GENERATOR: {gen_obj.__name__}")

    for item in gen_obj(*args, **kwargs):
        run = True
        while run:
            try:
                val = next(item)
            except Tt_exceptions.SomethingWentWrong as err:
                print(err.comment)
                run = False
            except StopIteration:
                run = False


def run_gen_2(gen_obj, *args, **kwargs):
    """ function to run a generator of one object """
    gen_box = gen_obj(*args, **kwargs)
    run = True
    while run:
        try:
            val = next(gen_box)
        except Tt_exceptions.SomethingWentWrong as err:
            print(err.comment)
            run = False
        except StopIteration:
            run = False



filename = "FEGO_template.tmtb"
class_cat_det = namedtuple('class_cat_det', 'fullname abbrev description')
CLASS_GROUPS = [class_cat_det("Junior Secondary School", "JSS", "The first and junior class category of the Federal government college"),
class_cat_det("Senior Secondary School", "SSS", "The second and Senior class category of the Federal government college")]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

FACULTIES = ["Math and ICT", 
                "Languages",
                "Sciences",
                "Commercials",
                "Arts",
                "PHE"]

SUBJECTS = [
    ["Mathematics", "Further Mathematics", "Economics", "Home Econs", "Foods and nutrition"],
    ["English", "Lit-in-English", "French", "Yoruba", "Arabic", "History"],
    ["Basic science (BST3)", "Technical unit", "Physics", "Chemistry", "Biology", "Agricultural Science"],
    ["Business studies","Office Practice", "Commerce", "Marketing", "Salesmanship", "Book-keeping", "Fin. accounting","Insurance", "Store management"],
    ["CRS/IRS", "History", "Social studies", "Civic Edu (Junior)", "Civic Edu (Senior)", "Government", "CCAII (music)", "CCA1", "Visual Arts", "Dyeing & Bleaching"],
    ["BST1", "H/EDU", "P.E", "Economics", "ICT (Junior)", "ICT (senior)"]
]

NUM_ARMS_FOR_CLASSES = (7, 5, 7, 7, 8, 7)


Manager = Tt_manager.TimeTableManager()
All_models = Manager.get_model_items

# Create class categories/class groups
for detail in CLASS_GROUPS:
    Manager.create_school_class_group(detail.fullname, abbrev=detail.abbrev,description=detail.description)

# Create school class
for name in All_models("class_groups")[0]:
    for k in range(1,4):
        Manager.create_school_class(str(k), name, update=False)


# Create class arm
for arm_count, clss_fullname in zip(NUM_ARMS_FOR_CLASSES, All_models("school_classes")[0]):
    Manager.generate_school_class_arms(clss_fullname, frequency=arm_count, as_alpha=True, override=False)

# Create days
for day in DAYS:
    Manager.create_day(day, rating=None, update=False)


# Create faculty (Department in the GUI)
for fac in FACULTIES:
    Manager.create_faculty(fac, HOD="Esteemed HOD Sir/Ma'am", description="", update=False)

# Create dept (subjects)
for fac, subj_list in zip(All_models('faculties')[0], SUBJECTS):
    for deptname in subj_list:
        is_parallel = True if "CRS" in deptname else False
        Manager.create_department(deptname, hos=None, is_parallel=is_parallel, faculty=fac, A=1,T=1,P=1,G=1, update=False)


# Create NON-ACAD SUBJECTS
Manager.create_special_department("Short Break", update=False)
Manager.create_special_department("Long Break", update=False)

nonacad_tuple_list = [(nonacad_dept, "00:35:00", str(k + 6)) 
for k, nonacad_dept in enumerate(Manager.get_model_items("nonacads")[0])]


# Create periods
g_box_id = "by_duration"
selected_arms, selected_days = All_models("arms")[0], All_models("days")[0]
acad_dict = {"start":"00:05:30", "duration":"00:55:00", "freq":10, "interval":"00:1:30"}

# Pin days to class arms and generate periods
Manager.pin_day_generate_periods(g_box_id, selected_arms_list=selected_arms, selected_days_list=selected_days, 
    normal_periods_dict=acad_dict, nonacad_tuple_list=nonacad_tuple_list)

# --------------------------------------------------------------------
# --------------------------------------------------------------------

arms_by_classgroup_dict = {"All": All_models("arms")[1]}
arms_by_classgroup_dict.update({clssgr: [arm for arm in All_models("arms")[1] if arm.school_class.school_class_group.full_name == clssgr]
    for clssgr in All_models("class_groups")[0]})


junior_key, senior_key = All_models("class_groups")[0]

# define helper functions
def arm_names_range(range_str, key="All"):
    global arms_by_classgroup_dict
    lower, upper = range_str.split("-")

    return_list = []
    begin = False
    for arm in arms_by_classgroup_dict[key]:
        if arm.local_id.lower() >= lower.lower():
            begin = True
        else:
            begin = False

        if upper:
            if arm.local_id.lower() > upper.lower():
                begin = False

        if begin:
            return_list.append(arm.full_name)
        
    return return_list


def get_dept_fullname(name):
    """ Returns the fullname of the object which has the word 'name' in it """
    for dept_fullname in All_models("depts")[0]:
        if name.lower() in dept_fullname.lower():
            return dept_fullname
    return f"Void for {name}"



# GENERATE TEACHERS
def make_teacher(freq, course_list):
    # Find the subjects with fullnames
    course_list_ = [get_dept_fullname(rough_name) for rough_name in course_list]
    Manager.generate_teachers(frequency=freq, teaching_days=All_models("days")[0], specialty="All",
designation="Member of staff", course_list=course_list_, update=False)


make_teacher(5, ["Agricultural Science"])
make_teacher(5, ["Biology"])
make_teacher(7, ["Chemistry"])
make_teacher(3, ["Physics"])
make_teacher(5, ["BST1", "H/EDU", "P.E"])
make_teacher(5, ["BST3"])
make_teacher(12, ["English", "Lit-in-English"])
make_teacher(10, ["Yoruba"])
make_teacher(3, ["French"])
make_teacher(1, ["Arabic"])
make_teacher(4, ["Technical unit"])
make_teacher(4, ["Home Econs", "Foods and nutrition"])
make_teacher(4, ["CCAII"])
make_teacher(2, ["CCA1", "Visual Arts", "Dyeing & bleaching"])
make_teacher(16, ["Business studies","Office Practice", "Commerce", "Marketing", "Salesmanship", "Book-keeping", "Fin. accounting","Insurance", "Store management"])
make_teacher(3, ["Government"])
make_teacher(5, ["Economics"])
make_teacher(6, ["Social studies"])
make_teacher(3, ["History"])
make_teacher(4, ["CRS/IRS"])
# make_teacher(2, ["IRS"])
make_teacher(4, ["Civic Edu (Junior)"])
make_teacher(4, ["Civic Edu (Senior)"])
make_teacher(3, ["ICT (Senior)"])
make_teacher(3, ["ICT (Junior)"])
make_teacher(13, ["Mathematics", "Further Mathematics"])

# ----------------------------------------------------------------------------
chunk_freq_dict = {
    "junior":[
    (get_dept_fullname("Agric"), 3, 2),
    (get_dept_fullname("BST1"), 3, 1),
    (get_dept_fullname("BST3"), 3, 2),
    (get_dept_fullname("English"), 4, 2),
    (get_dept_fullname("Yoruba"), 2, 1),
    (get_dept_fullname("French"), 2, 2),
    (get_dept_fullname("Arabic"), 1, 1),
    (get_dept_fullname("Technical unit"), 3, 2),
    (get_dept_fullname("Home Econs"), 3, 2),
    (get_dept_fullname("CCAII"), 2, 2),
    (get_dept_fullname("CCA1"), 2, 2),
    (get_dept_fullname("Business studies"), 3, 1),
    (get_dept_fullname("Social studies"), 2, 2),
    (get_dept_fullname("History"), 2, 2),
    (get_dept_fullname("CRS"), 2, 2),
    (get_dept_fullname("IRS"), 2, 2),
    (get_dept_fullname("Civic Edu (Junior)"), 3, 2),
    (get_dept_fullname("ICT"), 3, 2),
    (get_dept_fullname("Mathematics"), 4, 2),
    ],
    "senior":[
    (get_dept_fullname("Agric"), 4, 2),
    (get_dept_fullname("Biology"), 4, 2),
    (get_dept_fullname("Chemistry"), 4, 2),
    (get_dept_fullname("Physics"), 4, 2),
    (get_dept_fullname("H/EDU"), 3, 1),
    (get_dept_fullname("P.E"), 3, 1),
    (get_dept_fullname("English"), 4, 2),
    (get_dept_fullname("Lit-in-English"), 3, 2),
    (get_dept_fullname("Yoruba"), 3, 1),
    (get_dept_fullname("French"), 3, 2),
    (get_dept_fullname("Technical unit"), 4, 2),
    (get_dept_fullname("Foods and nutrition"), 4, 2),
    (get_dept_fullname("Visual Arts"), 2, 1),
    (get_dept_fullname("Dyeing & bleaching"), 2, 2),
    (get_dept_fullname("Office Practice"), 3, 2),
    (get_dept_fullname("Commerce"), 4, 2),
    (get_dept_fullname("Marketing"), 3, 1),
    (get_dept_fullname("Salesmanship"), 2, 2),
    (get_dept_fullname("Book-keeping"), 4, 2),
    (get_dept_fullname("Fin. accounting"), 4, 2),
    (get_dept_fullname("Insurance"), 4, 2),
    (get_dept_fullname("Store management"), 3, 2),
    (get_dept_fullname("Government"), 4, 2),
    (get_dept_fullname("Economics"), 4, 2),
    (get_dept_fullname("CRS/IRS"), 3, 2),
    (get_dept_fullname("Civic Edu"), 4, 2),
    (get_dept_fullname("ICT"), 4, 2),
    (get_dept_fullname("Mathematics"), 4, 2),
    (get_dept_fullname("Further Mathematics"), 4, 2)
    ]
}
# (get_dept_fullname("IRS"), 3, 2)
print("Total sum: ",sum([det[1] for det in chunk_freq_dict["junior"]]))


def condense(*args):
    """ returns the (arm, freq, chunk) tuple for each of the args """
    ans = []
    for name in args:
        for det in chunk_freq_dict["senior"]:
            if name.lower() in det[0].lower():
                ans.append(det)
                break
    return ans



# Now map all subjects  to arms for junior classes
Manager.map_arms_to_chunkfreq_details(arm_names_range("A-", key=junior_key), chunk_freq_dict["junior"])

# Now do the more complicated senior classes
Manager.map_arms_to_chunkfreq_details(arm_names_range("D-", key=senior_key), condense("agric", "biology","chemistry", "physics", "P.E","further Mathematics"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("A-B", key=senior_key), condense("H/EDU", "Lit-in-English", "visual arts", "dyeing and bleaching", "CRS", "IRS"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("A-", key=senior_key), condense("english", "yoruba", "French","foods and nutrition", "civic edu (senior)", "ICT (senior)", "Mathematics", "Economics"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("F-", key=senior_key), condense("Technical unit"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("C-C", key=senior_key)[:-1], condense("office Practice", "Salesmanship"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("C-C", key=senior_key), condense("commerce", "Book-keeping", "Fin. accounting", "insurance", "store management"))
Manager.map_arms_to_chunkfreq_details([arm.full_name for arm in arms_by_classgroup_dict[senior_key][:7]], condense("marketing"))
Manager.map_arms_to_chunkfreq_details(arm_names_range("D-", key=senior_key), condense("government"))

# Assign teachers to arms
run_gen(Manager.auto_assign_teachers_to_arms)
print(arm_names_range("C-C", key=senior_key))

def run():
    print(Manager)
    Manager.save(filename)
    


