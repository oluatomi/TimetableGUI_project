# Try to rotate a list (or an iterable)
import string

def rot(list_arg, item=None, index=None, r_index=0):
    """ Rotates list_arg by rotating 'item' or item at index 'index' to position r_index """
    index_ = list_arg.index(item) if item else index

    if index_ is None:
        raise ValueError("Nothing selected really")
    list_len = len(list_arg)
    list_arg_ = sorted(list_arg, key=lambda k: (list_arg.index(k) - (index_ - r_index)) % list_len)
    return list_arg_


test_list1 = [k for k in string.ascii_lowercase]
test_list2 = list(range(1, 30))

# print(rot(test_list1, item='j'))
print(rot(test_list2, index=0))
print(rot(test_list1, item='a', r_index=3))
