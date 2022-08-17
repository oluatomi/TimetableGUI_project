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
    faculty = my_tt.create_faculty(subj)
    my_tt.create_department(subj, faculty=faculty)


for day in DAYS:
    my_tt.create_day(day)


for nick, name in CLASS_GROUPS.items():
    my_tt.create_school_class_group(name, abbrev=nick)


 # my_tt.create_department("Extra-curricular",is_special=True)


# # print()
print(my_tt.list_of_departments)
print("-"*80)
print(my_tt.list_of_school_class_groups)
print("-"*80)


for y in my_tt.list_of_school_class_groups:
    for x in range(1,4):
        my_tt.create_school_class(x, y)

print()
# print()



# Teachers are being created here
for dept in my_tt.list_of_departments:
    for _ in range(14):
        my_tt.create_teacher(dept_obj=dept, teaching_days=my_tt.list_of_days)

# Assign select teaching days for select teachers


                        # for teacher in my_tt.list_of_all_teachers:
                        #     # Every two teachers in a department
                        #     for e_day in my_tt.list_of_days:
                        #         teacher.add_day_to_teacher(e_day)

        # Add everyday to teachers except thursdays, corpmembers
    
for index, teacher in enumerate(my_tt.list_of_all_teachers):

    if not (index + 1) % 7:
        for day in teacher.teaching_days:
            if day.day == "Thursday":
                teacher.remove_day_from_teacher(day)



periods_ = my_tt.split_into_periods((8,0,0),(15,0,0),10)
print(periods_)


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

# r = Tt_manager.get_obj_from_param(m, "dept_name", "philosophy")
print()
print("_"*70)
print(m)
print()
# print(r)

print()
print("*"*84)
print(my_tt.list_of_school_classes)


for m in my_tt.list_of_school_classes:
    for _ in range(7):
        my_tt.create_school_class_arm(m, as_alpha=True)


# Add all the day objs to each arm
for arm in my_tt.list_of_school_class_arms:
    for day in my_tt.list_of_days:
        arm.add_day_to_arm(day)


print(my_tt.list_of_school_class_arms)


for arm in my_tt.list_of_school_class_arms:
    for dept, per, day in zip(my_tt.list_of_departments, periods_, my_tt.list_of_days):
        my_tt.create_period(per.start, day=day, end=per.end, sch_class_arm_obj=arm, dept_=None, 
            is_fav=False, title_of_fav=f"Special period for {arm.id}, on {day.day}")


print("_"*120)
print()

# print(my_tt.list_of_departments)
# my_tt.del_department(r)

print()
# print(my_tt.list_of_departments)
print()
print("*"*50)
print(my_tt.list_of_days) 

print()
# for day in my_tt.list_of_days:
#     print(day.sch_class_periods())

m = my_tt.list_of_school_class_arms[2]
d = my_tt.list_of_days[2]


# ----- A SECOND CONTAINER
my_sort = TimetableSorter()
my_sort.tt_obj = my_tt



print()

spec_dict = {}
for x in range(7,8):
    jo = my_tt.create_period(start=(8,0,0), day=d, end=None, sch_class_arm_obj=m, 
        dept_=None, is_fav=False, duration=(30,0),  spot=None, title_of_fav=None)
    jo.period_name = "Special_Me"

    spec_dict[jo] = x

# print(mom)
# print(len(mom))

                # mom = my_sort.generate_normal_n_special_in_time_bound(spec_dict, d, m, (8,0,0), (14,20,0), total=10, bound=0)


                # print()
                # for item in mom:
                #     print(item.start, item.end)

# -------------------------------------
# HOWEVER, CREATE REAL PERIODS FOR THE ARMS NOW
for arm in my_tt.list_of_school_class_arms:
    my_sort.generate_normal_n_special_in_time_bound(spec_dict, d, arm, (8,0,0), (14,20,0), total=10, bound=0)
    

print()
print(spec_dict)
    

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


def really_run():
    for subj in my_tt.list_of_departments:
        b = iterable(subj, random.randint(1,4), random.randint(1,2))
        b = iterable(subj, 4, 2)
        iter_list.append(b)

    print(iter_list)
    print()
    print(sum([x.frequency for x in iter_list]))
    print()

    # -------------------------------------------------------------
    for subj in my_tt.list_of_departments:
        # Assign (the already made) teachers to the class arms
        # by first adding them to the dept and then assigning teachers

        for arm in my_tt.list_of_school_class_arms:
            subj.add_arm_to_dept(arm)
            my_tt.dept_assigns_teacher_to_arm(subj, arm)

    print()
    print("-"*60)
    print("DEPT PACKETING HERE")
    print()

    for arm in my_tt.list_of_school_class_arms:
        print(arm, my_sort.set_deptpacket_into_day_per_class_arm(arm, iter_list))

        print("*"*70)
        print()


    print("-*"*30)
    print(d.school_class_arms_today)

    print("-"*90)
    print("The algo sort")
    print()

    # Different day objectsb
    ll, aa, bb, gg = my_tt.list_of_days[0], my_tt.list_of_days[1], my_tt.list_of_days[3], my_tt.list_of_days[4]

    # for arm in my_tt.list_of_school_class_arms:
    #     print(arm, arm.depts_and_teachers.keys())
    print(my_sort.Sort_manager(SortAlgorithms.centercluster, reference_arm=m))
    
really_run()

# count=0
# for _ in range(10):
#     count += 1
#     try:
#         really_run()
#         print()
#     except Exception as e:
#         print(f"Bailed on number: {count}")
#         print(e)
#         break
# else:
#     print("ABSOLUTE SUCCESS")

# print(my_sort.summon_all(d, CenterCluster))
