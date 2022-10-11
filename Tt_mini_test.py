# - ************************************************************************

# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.

# -- All rights (whichever they might be) reserved!

# **************************************************************************


from Tt_models import TimeTable
from Tt_algo import TimetableSorter
from Tt_algo_calc import XLXReflection, CenterCluster, LeapFrog, SortAlgorithms
import string, Tt_manager
from collections import namedtuple
import random

"""
    Setting up something similar to fego junior classes jss1-3
    -----------------------------------------------------------------
"""
W_PERIODS = 50
#-- Number of periods per week


DAYS = ["monday","Tuesday","wednesday","thursday","friday"]
    
CLASS_GROUPS = {'-JSS-', '-SSS-'}

FACULTIES = ["Math and ICT", 
                "Languages",
                "Sciences",
                "Commercials",
                "Arts"]

SUBJECTS = [
    ["Mathematics", "Further Maths", "ICT"],
    ["English","French", "Yoruba"],
    ["basic science","Basic Tech","Physics", "Chemistry"],
    ["business studies","Accounts"],
    ["crs", "Creative Arts", "History"]
]

CLASS_ARMS = string.ascii_letters[:9]

# instantiating a timetable object for experimentation
My_manager = Tt_manager.TimeTableManager()

# Store all models function in a variable, to be called repeatedly later
All_models = My_manager.get_model_items

# -----------------------------
# Create class groups
for name in CLASS_GROUPS:
    My_manager.create_school_class_group(name, description="Houses school classes of like properties")


# Create school class
for name in All_models("class_groups")[0]:
    for k in range(1,4):
        My_manager.create_school_class(str(k), name, update=False)

# Create class arm
for clss_fullname in All_models("school_classes")[0]:
    My_manager.generate_school_class_arms(clss_fullname, frequency=8, as_alpha=True, override=False)

# Create days
for day in DAYS:
    My_manager.create_day(day, rating=None, update=False)

# Create faculty (department)
for fac in FACULTIES:
    My_manager.create_faculty(fac, HOD="Esteemed HOD Sir/Ma'am", description="", update=False)

# Create dept (subjects)
for fac, subj_list in zip(All_models('faculties')[0], SUBJECTS):
    for deptname in subj_list:
        My_manager.create_department(deptname, hos=None, faculty=fac, A=1,T=1,P=1,G=1, update=False)

# Create periods
g_box_id = "by_duration"
selected_arms, selected_days = All_models("arms")[0], All_models("days")[0]
acad_dict = {"start":"00:07:30", "duration":"00:55:00", "freq":10, "interval":"00:1:30"}

# Pin days to class arms
My_manager.pin_day_generate_periods(g_box_id, selected_arms_list=selected_arms, selected_days_list=selected_days, 
    normal_periods_dict=acad_dict, nonacad_tuple_list=[])


# Create Teachers
# Make list with two depts chosen at random
rand_depts = [random.choices(All_models("courses")[0], k=2) for _ in range(4)]
rand_depts = All_models("courses")[0]
print(rand_depts)

# for depts in rand_depts:
My_manager.generate_teachers(frequency=12, teaching_days=All_models("days")[0], specialty="All", designation="Member of staff", course_list=rand_depts, update=False)


# Assign Teachers
# packet subjects into days
iter_list = []
iterable = namedtuple("dept_item", "dept frequency chunk")

for dept in All_models("depts")[0]:
    b = iterable(dept, random.randint(1,4), random.randint(1,2))
    print(b)
    iter_list.append(b)

My_manager.map_arms_to_chunkfreq_details(All_models("class_arms")[0], iter_list)
My_manager.auto_assign_teachers_to_arms()


for arm in All_models("class_arms")[1]:
    # print(arm, arm.depts_and_teachers)
    try:
        print(My_manager.TimetableSorter.set_deptpacket_into_day_per_class_arm(arm, iter_list))
    except Exception:
        pass

    # print(f"Arm subjs: {arm} --> {arm.temp_dept_holder_for_days}")
    # print(My_manager.TimetableSorter.set_deptpacket_into_day_per_class_arm(arm, iter_list))




#---------------------------------------




# def really_run():
#     for subj in my_tt.list_of_departments[:2]:
#         b = iterable(subj, random.randint(1,4), random.randint(1,2))
#         b = iterable(subj, 1, 1)
#         iter_list.append(b)

#     print(iter_list)
#     print()
#     print(sum([x.frequency for x in iter_list]))
#     print()

#     # -------------------------------------------------------------
#     for subj in my_tt.list_of_departments:
#         # map subjects to class arms
#         for arm in my_tt.list_of_school_class_arms:
#             my_tt.map_dept_to_arm(arm, subj)

#     # Assign subject teachers to arms
#     my_tt.auto_assign_teachers_to_all_arms(ascending=True)


#     print()
#     print("-"*60)
#     print("DEPT PACKETING HERE")
#     print()

#     for arm in my_tt.list_of_school_class_arms:
#         print(arm, my_sort.set_deptpacket_into_day_per_class_arm(arm, iter_list))

#         print("*"*70)
#         print()


#     print("-*"*30)
#     print(d.school_class_arms_today)

#     print("-"*90)
#     print("The algo sort")
#     print()
#     # Different day objects
#     ll, aa, bb, gg = my_tt.list_of_days[0], my_tt.list_of_days[1], my_tt.list_of_days[3], my_tt.list_of_days[4]

#     # for arm in my_tt.list_of_school_class_arms:
#     #     print(arm, arm.depts_and_teachers.keys())
#     print(my_sort.Sort_manager(SortAlgorithms.centercluster, reference_arm=m))
    
# really_run()
