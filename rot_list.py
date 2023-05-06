# Try to rotate a list (or an iterable)
import string, random
from matplotlib import pyplot as plt

def calc_spacing_function(space, denominator):
    """ Inner function to calculate the spacing of an item based on the sine curve """
    return round(space*(denominator - space)/4, 2)


def calc_spacing(list_argument, periods_range_num):
    """ Handles the teaching efficiency calculation for the items in a list (list of integers).
    'periods_range_num' (INT) represents the total number of room available over which the spacing can be calculated. """
    list_arg = list_argument
    list_arg_length = len(list_arg)
    if list_arg_length <= 1:
        return 0
    # Rank-order (in reverse) list_arg and hold that new rank-ordered list in the variable below
    eff_list = []
    for k in range(list_arg_length):
        if k != 0:
            eff_list.append(list_arg[k] - list_arg[k - 1] - 1)

    print([calc_spacing_function(m, periods_range_num) for m in eff_list])
    return sum([calc_spacing_function(m, periods_range_num) for m in eff_list])



# print(calc_spacing([1,5,7,8,9], 10))
x = [random.randint(3,25) for _ in range(20)]
y = [random.randint(3,25) for _ in range(20)]

print(f"x: {x} ... y: {y}")
plt.plot(x,y)
plt.show()
