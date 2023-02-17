from Tt_algo_calc import Possible_combs_with_fixed,Moveover,\
                            SortAlgorithms, align_chunklist_to_weightlist, weightlist
import random, string, math


ff = [[6, 7, 8, 9], [1, 2, 3, 4]]
rr = [[1,2], [3,4], 8]

def ran_dict():
    keys, values = [], []
    b = random.randint(1,4)
    for _ in range(b):
        keys.append(random.randint(1,4))
        values.append(random.randint(1,4))

    return {a:b for a,b in zip(keys, values)}



def shredder(num, base):
    """
        This function "shreds" or "chunks" the frequency of the subject upon which it is used into 
        packets that can be inserted into different days of the week. i.e. this function helps to 
        split the total frequency per week of a subject into the days within the week.

        the frequency, often chunked into 1s (single periods) can also be chunked into 2s (double periods)
        or "n"s. The "recurr" parameter handles that. recurr is 1 for singles and so on.
    """
    a,b = divmod(num, base)
    val = [base for _ in range(a)] + [b] if b else [base for _ in range(a)]
    return val, a+b


def to_base(num, base=60):
        '''Converts a number "num" to base "base" and renders it as a tuple of place values according to
        said base. Returns the time tuple '''
        
        # valid, ans_list, number = True, [], num % 86400
        ans = []
        while num > 0:
            num, rem = divmod(num, base)
            ans.insert(0, rem)

        return tuple(ans)


def stringer(num):
    alph_list = [k for k in string.ascii_uppercase]
    width = len(alph_list)

    if num >= width:
        w_num = num - width
        if w_num == 0:
            w_num_tuple = (0,)
        else:
            w_num_tuple = to_base(w_num, width)
        
        if len(w_num_tuple) <= 1:
            w_num_tuple = [0] + list(w_num_tuple)
            w_num_tuple = tuple(w_num_tuple)
    else:
        if num == 0:
            w_num_tuple = (0,)
        else:
            w_num_tuple = to_base(num, width)

    ans = ""
    for k in w_num_tuple:
        ans += alph_list[k]

    return ans



# combos = Possible_combs_with_fixed(rr, rr[:1], 10)
combos = SortAlgorithms.leap_frog(10, chunk_list={1:2, 3:1}, shift_value=0)
# print(combos)

weightlist_, chunklist = [3,1], [[7,8,9], 5]

print(align_chunklist_to_weightlist(weightlist_, chunklist))
# print(weightlist([1,1,1,2,2,6,7,8,9,9,9]))
# combos = Moveover(combos, 10)
# print(ran_dict())

# for _ in range(1000):
#     rand = ran_dict()
#     try:
#         chunks = SortAlgorithms.leap_frog(10, chunk_list=rand, shift_value=0)
#     except Exception:
#         print(f"Error occured in {rand}")
#     else:
        # print(f"{rand} -- gave rise to -- {chunks}")

# print(shredder(7,1))
# print(to_base(0,6))

# for k in range(100000):
#     print(stringer(k))



def dial_value_to_index(dial_value, model_length, min_=1, max_=100):
    """ This function converts the value passed in from the QDial into the index (int) of the model_object """
    index = math.ceil(dial_value * model_length/(max_ - min_ + 1)) - 1
    return index

def index_to_dial_value(index, model_length, min_=1, max_=100):
    """ Converts the value of the index to its QDial value on the GUI. Returns the QDial value """
    dial_value = math.floor((index + 1)*(max_ - min_ + 1)/model_length)
    return dial_value

model_length = 800

print("DIAL TO MODEL INDEX")
for k in range(1,101):
    print(f"{k}, to index value => {dial_value_to_index(k, model_length)}")

print()
print("MODEL INDEX TO DIAL")
for k in range(model_length):
    print(f"{k}, to dial value => {index_to_dial_value(k, model_length)}")

