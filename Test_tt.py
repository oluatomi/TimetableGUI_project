from Tt_models import TimeTable
from Tt_algo import TimetableSorter
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
    

CLASS_GROUPS = {'jss': 'junior secondary school', 'sss': 'senior secondary school'}

SUBJECT_LIST = ["Mathematics", "English", "basic science", "french", "yoruba",
                     "business studies","basic technology", "home economics", "i c t",
                     "crs", "social studies", "civic education", "history",
                    "creative arts","music", "agric science", "philosophy"]
SUBJECT_NUM = len(SUBJECT_LIST)

CLASS_ARMS = string.ascii_letters[:9]

# instantiating a timetable object for experimentation
my_tt = TimeTable()

for subj in SUBJECT_LIST:
    my_tt.create_department(subj)

#                                        

for day in DAYS:
    my_tt.create_day(day)


for nick, name in CLASS_GROUPS.items():
    my_tt.create_school_class_group(name, abbrev=nick)


# -----------------------------------------------

print(my_tt.list_of_departments)
print("-"*80)
print(my_tt.list_of_school_class_groups)
print("-"*80)

for x in range(3):
    for y in my_tt.list_of_school_class_groups:
        my_tt.create_school_class(x, y)

print()
# print()



# Teachers already have been created
for dept in my_tt.list_of_departments:
    for _ in range(2):
        my_tt.create_teacher(dept_obj_=dept)



periods_ = my_tt.split_into_periods((8,0,0),(15,0,0),10)
print(periods_)
print("Hello tomi")


# for teacher in my_tt.list_of_all_teachers:
#     for dept in my_tt.list_of_departments:
#         teacher.add_dept_to_teacher(dept)

# for x in my_tt.list_of_school_class_groups:
#     print(x.school_class_list)
#     print("-"*80)

#     for v in x.school_class_list:
#         for m in range(8):
#             my_tt.create_school_class_arm(m, v)
#         # for s, per in zip(v.school_class_arm_list, periods_):
#         #     print(s, per)


print()

# days = my_tt.list_of_days

print(my_tt.list_of_all_teachers)
print()

print("-"*50)

m = my_tt.list_of_departments
u = my_tt.list_of_all_teachers[0]

# for dept in my_tt.list_of_departments[1:5]:
#     u.add_dept_to_teacher(dept)


# print(u.teachers_department_list)

r = Tt_manager.get_obj_from_param(m, "dept_name", "philosophy")
print()
print("_"*70)
print(m)
print()
print(r)

print()
print("*"*84)

print(my_tt.list_of_school_classes)



for m in my_tt.list_of_school_classes:
    for x in range(2):
        my_tt.create_school_class_arm(x, m, as_alpha=True)



day = my_tt.list_of_school_class_arms

print(day)
print()
# print(day.school_class_arms_toby)



my_sort = TimetableSorter()

# mom = my_sort.generate_normal_n_special_in_time_bound(spec_dict, d, m, (8,0,0), (14,20,0),total=11, bound=0)

print()
# print(mom)
# print(len(mom))

print()
# for item in mom:
#     print(item.start, item.end)

# g = my_tt.list_of_departments[4]

# for arm in my_tt.list_of_school_class_arms:
#     g.add_arm_to_dept(arm)

# l = my_tt.list_of_all_teachers[64]

# t_class = my_tt.list_of_school_class_arms[3]


# print(g.assign_teachers_to_all_arms())

# print(len(my_tt.list_of_school_class_arms))
print()
# print(l.classes_count)

# Trying to get all the teachers for a particular day from the timetable sorter object
# print(my_sort.teachers_today(my_tt.list_of_days[1]))

# print(len(my_sort.teachers_today(my_tt.list_of_days[1])))
print()

# ------------------------------------------------------------------------------

iterable = namedtuple("dept_item", "dept frequency chunk")

iter_list = []

for subj in my_tt.list_of_departments:
    b = iterable(subj, random.randint(1,4), random.randint(1,2))
    iter_list.append(b)

print(iter_list)
print()
print(sum([x.frequency for x in iter_list]))
print()

# -------------------------------------------------------------
for arm in my_tt.list_of_school_class_arms:
    my_sort.set_deptpacket_into_day_per_class_arm(arm, iter_list)



print("-*"*100)
print(d.school_class_arms_today)
print()

for subj in my_tt.list_of_departments:
    # Assign (the already made) teachers to the class arms
    # by first adding them to the dept and then assigning teachers

    for arm in my_tt.list_of_school_class_arms:
        subj.add_arm_to_dept(arm)
        subj.assign_teacher_to_arm(arm)


print()
print("-"*90)
print("The algo sort")
print()


print(my_sort.Algosort_teachers_per_day(d, "algo"))
print()
print(d.school_class_arms_today)
