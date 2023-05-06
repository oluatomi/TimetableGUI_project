import random, inspect, time

def unique_id_str(translate_by=97):
    """ Returns a unique string based on the number of seconds since the epoch """
    unique_num = str(time.time())
    # remove whatever decimal points are there
    unique_num = unique_num.replace(".", "")
    return "".join([chr(int(k) + translate_by) for k in unique_num])


def nth_suffix(num):
    """ Function to determine the appropriate english suffix to a number as in 1st, 2nd and so on.
    Floats will be converted to INT  """
    
    # Just to be super sure
    num = int(num)
    suffix_dict = {"0":"th", "1":"st", "2":"nd", "3":"rd"}
    suffix_dict.update({str(n):"th" for n in range(4, 14) if n != 10})

    num_str = str(num)

    if num_str[-2:] in suffix_dict:
        suffix_ = suffix_dict[num_str[-2:]]
    else:    
        suffix_ = suffix_dict[num_str[-1]]
    return num_str + suffix_



def Translate_list_items(list_arg, item=None, index=None, base_index=0):
    """ This function rotates the elements in a list by taking an 'item' or 'index' if provided 
    and moving to the position 'base_index' 
    item and index should not be provided at the same time. However, if done, the function defaults to 'item'
    """

    index_ = list_arg.index(item) if item else index

    if index_ is None:
        raise ValueError("Cannot rotate. No item selected")
    list_len = len(list_arg)
    list_arg_ = sorted(list_arg, key=lambda k: (list_arg.index(k) - (index_ - base_index)) % list_len)
    return list_arg_



# Algorithms for putting subjects into days.
class PacketAlgos:
    """ This classes packets departments into days using the XLX-reflection method.
    However, no spaces between the days are required """
    
    # @staticmethod
    def direct(num, array):
        """ returns nm number of days in the same order as that of counting numbers.
        Needs not be translated backwards """
        return list(range(num))

    # @staticmethod
    def rev_direct(num, array):
        """ Returns a list like direct above, but in reverse order.
        Needs not be translated """
        return list(range(array-1, -1, -1))[:num]


    # @staticmethod
    def leapfrog(num, array):
        """ Take a day, skip the next day, and so on... loop back and forth till array is full """

        ans =[]
        f_item, loop = 1, True
        sec_item = 2
        while loop:
            # GO over the odd numbers
            if f_item <= array:
                ans.append(f_item)
                f_item += 2
            else:
                # Go over even numbers
                
                if sec_item <= array:
                    ans.append(sec_item)
                    sec_item += 2
                else:
                    loop=False

        ans = PlainTranslate(ans, -1)
        return ans[:num]


    # @staticmethod
    def rev_leapfrog(num, array):
        """ Like leapfrog but in reverse """
        ans = []
        item, sec_item, loop = array, array -1, True

        while loop:
            # Go backwards from array    
            if array >= item > 0:
                ans.append(item)
                item -= 2
            else:
                # Go backwards from array - 1
                
                if array >= sec_item > 0:
                    ans.append(sec_item)
                    sec_item -= 2
                else:
                    loop = False

        ans = PlainTranslate(ans, -1)
        return ans[:num]

    # @staticmethod
    def xlxreflection(num, array):
        """ Grabs both ends before getting to the middle """
        ans =[]
        first, sec = 1, array
        loop = True

        while loop:

            if 1 <= first <= array:
                ans.append(first)
            if 1 <= sec <= array:
                ans.append(sec)

            first += 1
            sec -= 1
            
            if first > array and sec < 1:
                loop = False

        ans = PlainTranslate(ans, -1)
        return Set_with_order(ans)[:num]


    # @staticmethod
    def rev_xlxreflection(num, array):
        """ The xlx_reflection but in reverse """
        ans = []
        first, sec, loop = array, 1, True

        while loop:
            
            if 1 <= first <= array:
                ans.append(first)
            if 1 <= sec <= array:
                ans.append(sec)

            first -= 1
            sec += 1

            if first < 1 and sec > array:
                loop = False
        ans = PlainTranslate(ans, -1)
        return Set_with_order(ans)[:num]


    algorithms = [direct, rev_direct, leapfrog, rev_leapfrog, xlxreflection, rev_xlxreflection]


# ************************************************************************************************
# ************************************************************************************************

# -------------------------------------------------------------------------------------
# GENERAL HELPER FUNCTION. EVERYBODY PROBABLY USES THIS!
def space_out(list_arg, array_end):
    """
    This function is to help space out the items of a list at te middle in case the 
    chunking algorithms get broken (the whole arrangement collapses) and we have to begin afresh.

    The 'array_end' parameter represents the very last (highest, usually) term of the array. It is a number!
    
    """
    final1 = list_arg[:int(len(list_arg)/2)]
    try:
        last_of_chunk = list_arg[-1][-1]
    except Exception:
        last_of_chunk = list_arg[-1]


    # Stretch to the end of the array only if the spread is already over 70% of the array.
    # if last_of_chunk >= int(0.7*array) and last_of_chunk < array:
        
        # The remaining space till the end of the array
    diff = array_end - last_of_chunk

    final2 = list_arg[int(len(list_arg)/2):]

    # shift elements forward from the middle of the array with diff
    for index, item in enumerate(list_arg[int(len(list_arg)/2):]):

        if not isinstance(item, list):

            final2[index] += diff
        else:
            for y,z in enumerate(item):
                final2[index][y] += diff
                
    return final1 + final2
# ----------------------------------------------------------------------


# -----------------------------------------------------------------------------
# A SECOND HELPER FUNCTION TO SHIFT THE CHUNKED RESULTS BY 'x' SPACES FORWARD

def PlainTranslate(arg, shift):
    """Shifts an INTEGER or all the items of list "arg" by "shift". 
    It is not array-bounded. """

    if isinstance(arg, list):
        # If it's a list
        for index,item in enumerate(arg):
            if isinstance(item, list):
                PlainTranslate(item, shift)
            else:
                item = item + shift
                arg[index] = item
        return arg
        # if just an ordinary int
    arg += shift
    return arg



def Translatebyshift(list_arg, shift, array):
    """ Shifts every number item returned by the algortithm 
    by x (based on where the teacher resides in the list of periods for the day) within the module of "array" """


    for index, item in enumerate(list_arg):
        if isinstance(item, list):
            Translatebyshift(item, shift, array)

        # # If the item turns out to be empty list
        # elif isinstance(item, list) and not bool(item):
        #     list_arg[index] = item
        else:
            item = (item + shift) % array
            list_arg[index] = item

    return list_arg



def TotTranslate(elem, shift, array):
    """Container for TranslateByShift. This method translates both list objects and integer objects
    with modulo array. elem can be list (of integers) or a single integer in a list """

    if isinstance(elem, list):
        element = Translatebyshift(elem, shift, array)
        return element

    element = (elem + shift) % array
    return element


def spread_over(list_arg, skip_list=0):
    """This helper function is suitable for a situation like this:
    
    For teachers who only teach for say four days (like corp members), the chunking algorithm
    only uses four days as the 'array' value for them. But the problem is the chunking is from 1-4
    and not 1-5 (skipping 4) which actually is the case in real life

    'pos_list' is actually a list argument (or set) that contains the INDEX of all the items that have been removed
    (as in the days removed).

    "SPREADS THE LESS LIST OVER INTO THE BIGGER LIST WITHOUT INCREASING LEN()"

    list_arg always has to be a list of numbers
    """

    if skip_list  == []:
        return list_arg

    # max_pos = max(skip_list)
    min_pos = min(skip_list)
    len_list = len(list_arg)

    if min_pos < 0:
        raise ValueError("Less than zero is not acceptable")


    for sindex in sorted(skip_list):
        for ind,num in enumerate(list_arg):
            if num > sindex:
                list_arg[ind] += 1

    return list_arg


def refine_translate(list_arg, array):
    """After the chunked list has been translated, it is very possible for a double period to straddle
    the end and beginning of the array, e.g [9,0] (or more generically, [len(array)-1, 0]), which would be impossible
    in real life. This helper function checks if such occurs and shifts it by the necessary amount of places
    so that it no more does.
    This only affects doubles so its a list i'm checking for"""

    for item in list_arg:
        if isinstance(item, list) and 0 in item[1:]:
            list_arg = Translatebyshift(list_arg, item.index(0), array)

    return list_arg

# ===========================================================================================

# -------------------------------------------------------------------------------------------
def strip_list_wrapper(list_arg):
    """This functions nicely wraps the strip_list function, so fin_list can be initialised outside the strip_list function"""
    global fin_list

    def strip_list(list_arg):
        """This function goes through nested lists and strips them out as bare items in the list
        e,g ([1,2,3,[4,5]] to [1,2,3,4,5])"""
        for item in list_arg:
            # If it is not an iterator, that is a list, tuple or something
            if not hasattr(item, "__iter__"):
                fin_list.append(item)
            else:
                # Recursion here!
                strip_list(item)
        return fin_list

    fin_list = []
    return strip_list(list_arg) if bool(list_arg) else fin_list


# ________________________________________________________________________________________________
def check_for_overlap(list_arg):
    """ This inner function checks through a the fin_list to see if all the numbers are sorted
    such that there is no overlap, i.e when completely stripped, no number repeats, that is, when stripped, it
    is equal in length to its set"""
    return len(strip_list_wrapper(list_arg)) > len(set(strip_list_wrapper(list_arg)))


# ---------------------------------------------------------------------------------------------------
def check_match_get_container(list_arg, x):
    """Checks if a single x is in list_arg and returns the list container holding it, if it is a list"""

    for index,item in enumerate(list_arg):
        if isinstance(item, list):
            for inner in item:
                if inner == x:
                    return index, item
        if item == x:
            return index, item
    return ValueError(f"{x} does not occur in the list")

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
def f_check_for_overlap(list_arg, const=None, _list=None, const_index=0):
    """ This inner function checks through a the fin_list to see if all the numbers are sorted
    such that there is no overlap, i.e when completely stripped, no number repeats, that is, when stripped, it
    is equal in length to its set. with an item fixed """
    
    const_list = [const] if const else [_list[const_index]]
    if isinstance(const, list):
        # Morphe it into a set if it is a list
        const_set = set(strip_list_wrapper(const))
    else:
        # Just add it into a set if it is an int.
        const_set = {const}

        # Return True if there are still overlaps AND the numbers from the constant variable show up the chunking, wo we can re_moveover
    # return len(strip_list_wrapper(list_arg)) > len(set(strip_list_wrapper(list_arg))) and bool(set(strip_list_wrapper(list_arg)) & const_set)
    return len(strip_list_wrapper(list_arg + const_list)) > len(set(strip_list_wrapper(list_arg + const_list))) or bool(set(strip_list_wrapper(list_arg)) & const_set)



def Moveover(listarg, array):
    # Spreads a list to ensure that no members overlap
    # ---------------------------------------------------------
    def slide_over_one(in_list, forward=True):
        # keep sliding over till there are no overlaps or at least till the cycle is exhausted

        bowl = []

        listarg = in_list.copy() if forward else list(reversed(in_list))
        trans = 1 if forward else -1
        
        for elem in listarg:
            # If there is a match (even just in one place), i.e the elem has featured before in 'bowl', translate it and append
            if abs_match_list_int(bowl, elem) or abs_match_list_int(list(range(array, array*3)), elem) or abs_match_list_int(list(range(-1, -3*array, -1)), elem):
                # print(f"Elem: {elem} features in bowl: {bowl} so we translate ")
                el = PlainTranslate(elem, trans)
                bowl.append(el)
            # If it hasnt featured before, add it anyway
            else:
                # print(f"{elem} freely added")
                bowl.append(elem)
        bowl = bowl if forward else list(reversed(bowl))
        # print(f"This is the bowl: {bowl}")

        return bowl
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # return listarg
    if len(strip_list_wrapper(listarg)) > array:
        return ValueError(f"Length of list_arg is greater than {array}")

    if not listarg:
        # If the list argument passed in is empty
        return []

    mark = listarg.copy()

    list_arg = list(enumerate(listarg.copy()))

    sorted_list = sorted(list_arg, key=lambda ind_item:max(strip_list_wrapper(ind_item[1])) if isinstance(ind_item[1], list) else ind_item[1])
    s_list = [item for index, item in sorted_list]
    w_list = s_list.copy()


    fin = w_list.copy()
    loop = True
    forward = True
    count = 0


    while loop:
        count += 1
        
        # time.sleep(1)
        # preserves the old value of fin in case it needs to retrace its steps with the var _keep
        # print(f"This is fin: {fin}")
        _keep = fin.copy() if max(strip_list_wrapper(fin)) < array else w_list.copy()

        # print(f"Fin uptop: {fin} and keep: {_keep}")

        fin = slide_over_one(fin, forward=forward)
        # print(f"Fin before criteria: {fin}")


        if max(strip_list_wrapper(fin)) < array and min(strip_list_wrapper(fin)) >= 0:
            if not check_for_overlap(fin):
                loop = False

        else:
        
            if max(strip_list_wrapper(fin)) >= array:
                # print("Going left")
                forward = False

            elif min(strip_list_wrapper(fin)) < 0:
                forward = True


        if count >= array*4:
            raise StopIteration(f"OVERLOADED!! {mark} did not work")
            

        # Reconstitute the list to its previous order
        # fin is one-one mapped to sorted_list

    fin = [(ind_item[0], fin_item) for ind_item, fin_item in zip(sorted_list, fin)]
    fin = sorted(fin, key=lambda ind_item:ind_item[0])
    fin = [elem for index,elem in fin]

    return fin

def Moveover_with_fixed(list_arg, array,fixed_item=None, fixed_index=0):
    """ Gives the moveover version of list_arg, with fixed item fixed. It does so by running all the combinations of the moved
    over function and giving the first value with fixed item in it. """

    fixed = fixed_item if fixed_item else list_arg[fixed_index]

    poss_with_fixed = Possible_combs_with_fixed(list_arg,fixed,array)
    return poss_with_fixed[0]


def Moveover_fixed(list_arg_, array,fixed_item=None, fixed_index=0):
    """ This function does the work of the moveover function except for the fact that it holds an item (if given), or it's 
    index (if given) fixed. It is done this way, we pop out the fixed item and moveover whats left. Then we concatenate what's left.
    Fixed_item is a list containing all the chunks (which could have lists within)
    """

    # --------------------------------------------------------------------------
    # def slide_right_left(list_arg,array, trans=1):
    def slide_right_left(in_list, rightward=True):
    # Stores the elements of list_arg ind its index in a tuple, so we can refer back to it
        # global pos, sorted_list_arg, fin_dict, test_li st

        test_list = []
        sorted_list_ = in_list.copy() if rightward else list(reversed(in_list))
        trans = 1 if rightward else -1
        for item in sorted_list_:
            # if item is already in testlist or greater than array, or lower than 0, then translate by trans
            if abs_match_list_int(test_list + strip_list_wrapper([const_list]), item) or abs_match_list_int(list(range(array, array*3)), item)\
             or abs_match_list_int(list(range(-1, -3*array, -1)), item):
                el = PlainTranslate(item, trans)
                test_list.append(el)
            else:
                test_list.append(item)

        test_list = test_list if rightward else list(reversed(test_list))
        return test_list
    # ----------------------------------------------------------------------------
    # -----------------------------------------------------------------------

    # In the event that list_arg is just one item and part_chunk is [] return list_arg back
    list_arg = list_arg_.copy()
    if len(list_arg) <= 1:
        return list_arg

    if len(list_arg) > array:
        return ValueError(f"Input {list_arg} longer than array")


    if fixed_item and abs_match_list_int(list_arg, fixed_item, strict=True):
        const_item = fixed_item
        # fixed_index = list_arg.index(fixed_item)

    # If fixed item is not none, but doesn't occur in the list, raise error
    elif fixed_item:
        raise ValueError(f"{fixed_item} does not occur in list_arg")

    else:
        const_item = list_arg[fixed_index]

    list_arg_copy = list_arg.copy()

    # Put the const item in the finished_list for now
    # const_item = const_item if isinstance(const_item, list) else [const_item]
    const_list = const_item.copy()
    # print(f"This is const item {const_item}")

    indices = [list_arg.index(k) for k in const_list]

    # Remove the indices of this const_list items from the listarg before moveover
    for kitem in const_list:
        list_arg.remove(kitem)

    # print(f"listarg here {list_arg}")

    # After the fixed items have been removed from list_arg, if list_arg is empty, (i.e. no other elemet apart from the fixed item),
    # return the old list_arg
    if not list_arg:
        return list_arg_copy

    # --------------------------------------------
    # Now start moving over
    # An empty dictionary to hold the indices and the new value to aid reconstitution
    fin_dict = {}
    test_list = []

    # -------------
    pos = [(index, item) for index, item in enumerate(list_arg)]
    # sorted_list_arg_index = sorted(pos, key=lambda ind_item:max(strip_list_wrapper(ind_item[1])) if isinstance(ind_item[1], list) else ind_item[1])
    # map a list of just the items to the sorted_list_arg_index
    # sorted_list_arg = [item for _,item in sorted_list_arg_index]

    sorted_list_arg = list_arg
    # --------------------------------
    final_val = sorted_list_arg
    count = 0
    loop = True
    forward = True
    
    # --------------------------------------------------------
    while loop:
        count +=1

        final_val = slide_right_left(final_val, rightward=forward)
        # print(f"Final_val: just checking: {final_val}")

        if max(strip_list_wrapper(final_val)) < array and min(strip_list_wrapper(final_val)) >= 0:
            if not check_for_overlap(final_val) and not abs_match_list_int(final_val, const_list):
                # print("Out with ye")
                loop = False

        else:
            if max(strip_list_wrapper(final_val)) >= array:
                # print("Going left")
                forward = False

            elif min(strip_list_wrapper(final_val)) < 0:
                forward = True

        if count == array*3:
            raise StopIteration(f"OVERLOADED!! moveover_fixed with listarg {list_arg_copy} with const {const_list} did not work")
            # print()
            # count = 0
            # print("FELL THROUGH")
            # loop = False
            # final_val = Moveover_fixed(strip_list_wrapper(list_arg_copy), array, fixed_item=fixed_item, fixed_index=fixed_index)
            # return final_val
            # print(f"List_arg is: {list_arg_copy}, fixed_item ; {fixed_item}")
            

    for ind, item in zip(indices,const_list):
        final_val.insert(ind, item)
    return final_val


def Possible_combs(listarg, array):
    """This function finds out all the possible legal spaces a chunked list can have when a piece is held constant
    Legal in the sense that it doesn't run past 0 or past the array and its items do not overlap

    The list_arg must have been "moved over", i.e no overlaps 

    """
    if not listarg:
        # If the list argument passed in empty
        return []
    # Move list_arg if it hasn't been moved before
    # --------------------------------------------------------
    list_arg = Moveover(listarg, array) 
    # ----------------------------------------------------------

    possible_list = []
    sec_list_arg = [(index,item) for index,item in enumerate(list_arg)]

    # Sort the sec_list_arg based on the max item in each list item if it is a list or the same number if it is an integer
    sorted_sec_list_arg = sorted(sec_list_arg, key=lambda ind_item:max(strip_list_wrapper(ind_item[1])) if isinstance(ind_item[1],list) else ind_item[1])

    # We hold a constant copy  of the sorted_sec_list_arg
    _sec_list_arg = [item for _,item in sorted_sec_list_arg]
    _const_sec_list_arg = _sec_list_arg.copy()


    count = 0

    for index in range(len(sorted_sec_list_arg)):

        # print(f"For index: {index}")
        # Translate backwards first
        loop = True
        left = True
        
        # item = _sec_list_arg[index]

        while loop:
            count += 1

            if not check_for_overlap(_sec_list_arg):
                if min(strip_list_wrapper(_sec_list_arg)) >= 0 and max(strip_list_wrapper(_sec_list_arg)) < array:
                    
                    ans = _sec_list_arg.copy()

                    # But before we append, we have to reconstitute the item to its previous order
                    # ans is one-one mapped to sorted_sec_list_arg, therefore

                    ans = [(index, sec_item) for index,sec_item in zip(sorted_sec_list_arg, ans)]
                    # Now sort according to index
                    ans = sorted(ans, key=lambda ind_secitem:ind_secitem[0])
                    ans = [sec_it for _,sec_it in ans]

                    possible_list.append(ans)

                else:
                    if left:
                        left = False
                        _sec_list_arg = _const_sec_list_arg.copy()
                    else:
                        loop = False
 
            else:
                if left:
                    left = False
                else:
                    loop = False


            # _sec_list_arg = _const_sec_list_arg.copy()
            item = _sec_list_arg[index].copy() if isinstance(_sec_list_arg[index], list) else _sec_list_arg[index]
            trans_num = -1 if left else 1
            item = PlainTranslate(item, trans_num)
            _sec_list_arg[index] = item

        _sec_list_arg = _const_sec_list_arg.copy()
    #---- A set cannot be used to weed out duplicates because of the nested lists, therefore a for-loop is used
    # ---Possible list is now populated
    final_list =[]
    for list_it in possible_list:
        if list_it not in final_list:
            final_list.append(list_it)

    return final_list


def Possible_combs_with_fixed(list_arg, const, array):
    # Gets all the possible combinations with a fixed item inside. 
    # const is now an iterable holding all values. const is a list of constant(fixed) values. i.e. values that
    # should stay constant in the combination finding process
    
    all_ = Possible_combs(list_arg.copy(), array)

    if not bool(const):
        return all_
    # if len(const) == 1 or isinstance(const, int):
    #     return [lists for lists in all_ if const in lists]
    ans = []
    for item in all_:
        # For each item in all_, cycle through the const list
        for x in const:
            if x not in item:
                # Even if one isn't in that list, abandon it
                break
        else:
            # only add if all const are in the item list
            ans.append(item)
    return ans


def match_list_items(list_arg, match_list, strict=True):
    """ This function uses each of the items in match_list to match every item in list_arg.
    It returns true if and only if only all match. """
    if strict:
        for e_item in strip_list_wrapper(match_list):
            if e_item not in strip_list_wrapper(list_arg):
                return False
        return True
    # Strict implies every element in the nested match_list must match, no lenience
    # If not strict
    for e_item in strip_list_wrapper(match_list):
        if e_item in strip_list_wrapper(list_arg):
            return True
    return False


def abs_match_list_int(list_arg, match_val, strict=False):
    """Boolean. Matches all elements (lists and ints) in match_val with list_arg"""

    if isinstance(match_val, list):
        return match_list_items([list_arg], match_val, strict=strict)

    return match_val in strip_list_wrapper([list_arg])


def remove_all_sub_from_list(list_arg, sub_list):
    """ Returns a list where all elems in sub_list have been removed, list or int. 
    Removes all the elements of sub_list from list_arg or 'dies trying', i.e 
    raises a valueError sub_list is not a proper subset of list_arg.
    it really does not alter the original list_arg."""
    ans_list = strip_list_wrapper(list_arg)

    # cast into a list in the event that it an object or an int
    sub_list = [sub_list]
    for elem in strip_list_wrapper(sub_list):
        ans_list.remove(elem)
    return ans_list


def casual_removeall(list_arg, elem):
    """Removes all the occurences of elem in list_arg"""
    sec_list = list_arg.copy()
    for item in sec_list:
        if item == elem:
            list_arg.remove(elem)

    # Should it return list_arg?


def weightlist(listarg):
    """ Returns a list of int which indicate how many times an item occurs in listarg-- in order """

    # Make an ordered list of the unique items in the listarg
    s_list = Set_with_order(listarg)
    ans = []
    for k in s_list:
        ans.append(listarg.count(k))
    return ans
        


def align_chunklist_to_weightlist(weightlist, chunklist):
    """ The weightlist is the reference list here. the items in chunklist have the same len() as the integers
    in weightlist. This function merely makes sure that those values are one-one mapped. and realigns if not """

    ans = []
    for item in weightlist:
        chunklist_ = chunklist.copy()
        for index, item_ in enumerate(chunklist_):
            width = len(item_) if hasattr(item_, "__iter__") else 1
            if width == item:
                ans.append(item_)
                chunklist.remove(item_)
                break
    return ans


def Count_with_order(list_arg):
    """This is like the counter object except for the fact 
    that it prreserves the order of the items in the list"""

    ans = {}
    for item in list_arg:
        ans[item] = list_arg.count(item)
    return ans


def Set_with_order(list_arg):
    """Renders unique items like a Set, but preserves the order.
    Returns a list,"""
    ans = []
    for item in list_arg:
        if item not in ans:
            ans.append(item)
    return ans


class SortAlgorithms:
    """ This class handles ALL the chunking algorithms, the Leapfrog,xlx and the
    centercluster algorithms, for a length of periods per class "array" """

    # sort_algorithms_list = [leap_frog, xlx_reflection, centercluster, r_leapfrog, r_xlx_reflection, r_centercluster]

    @staticmethod
    def leap_frog(array, chunk_list={2:2, 1:2}, shift_value=0):
        """ Revised leapfrog algorithm. """

        # sort the chunk_list items by the chunk_number from largest to smallest
        c = chunk_list.items()
        # Dummy list with order preserved
        order_preserved_dummy = [list(range(1, chunk+1)) for chunk, freq in c for _ in range(freq)]

        chunk_list_itz = sorted(list(enumerate(order_preserved_dummy)), key=lambda item:len(item[1]), reverse=True)
        # The below is only to check if the chunklist can squish or collapse or is not compatible
        chunk_list_for_check = sorted(list(enumerate(c)), key=lambda item:len(item[1]), reverse=True)
        # Elem contains is the tuple of the kev-val pair from chunk_list.items()
        chunk_list_items = [elem for _, elem in chunk_list_itz]
        chunk_check = [elem for _, elem in chunk_list_for_check]
        # the length of the sequences, 3 if (triples, singles and doubles) or 2 (doubles, and singles) so we can see if we can space them
        chunk_sequence = len(chunk_list)
        # print(f"Chunk list items: {chunk_list_items}")
        # The variable checks whther we can add one space after each chunk sequence, else it "compromises" and contracts without collapsing just yet!
        compromise = False
        check = sum([chunk + (freq - 1)*(chunk + 1) for chunk, freq in chunk_check]) + chunk_sequence - 1
        # The total sum of the frequencies of all the chunks must also not exceed array, otherwise there is no way to chunk!
        chunks_squished = sum([chunk*freq for chunk, freq in chunk_check])


        if chunks_squished > array:
            # If all the chunks in their freqiencies side-by-side exceed array, break out
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")

        if check > array:
            # Contract but do not collapse
            check -= (chunk_sequence - 1)
            if check > array:
                # If after contracting, it still spills beyond array
            
                # IMPLEMENT HERE -- COLLAPSE THE WHOLE THING AND REBUILD!
                SortAlgorithms.collapse(array, chunk_list, shift_value=shift_value)
            else:
                compromise = True
        
        ans, count = [], 0

        for chunk in chunk_list_items:
            if count > 0:
                last_item = strip_list_wrapper(ans)[-1] + 1 if not compromise else strip_list_wrapper(ans)[-1]
            else:
                last_item = 0

            # for x in range(1, len(chunk)+1):

            item = list(range(1,len(chunk) + 1))
            item = PlainTranslate(item, last_item)
            ans.append(item)

            count += 1
        # Translate everthing back by 1.
        semi_ans = PlainTranslate(SortAlgorithms._semi_strip_list(ans), -1)

        # In case it is shifted by shift_val, refine afterward
        spit_out = Translatebyshift(semi_ans, shift_value, array)
        final_ans = refine_translate(spit_out, array)
        final_ans = Moveover(final_ans, array)

        # Reconstitute, the final answer to its initial order
        # Putting the original index of the chunk_list_sort...
        final_ans = [(index_chunk[0],elem) for index_chunk, elem in zip(chunk_list_itz, final_ans)]
        final_ans = sorted(final_ans, key=lambda item:item[0])
        final_ans = [elem for _, elem in final_ans]

        return final_ans


    @staticmethod
    def xlx_reflection(array, chunk_list={2:1, 1:1}, shift_value=0):
        """ The xlx chunking algorithm (revised). """
        ans = []

        # The 'elem' below is the Key,value tuple in chunk_list.items()
        old_chunklist_elem_only = [elem for elem in chunk_list.items()]

        items_unsorted = list(enumerate(old_chunklist_elem_only))

        items_unsorted_list = [elem for _, elem in items_unsorted]   

        items_ind = sorted(list(enumerate(old_chunklist_elem_only)), key=lambda item: item[1][0], reverse=True)
        # Elem contains is the tuple of the kev-val pair from chunk_list.items()
        items_list = [elem for _, elem in items_ind]
        # make the first two items of the list
        # first item (the first item of the first item which is a tuple (chunkval, freq))
        chunks_squished = sum([chunk*freq for chunk, freq in items_list])

        # FIRST CHECK, IF THE CHUNKLIST IS IN ITS SPECS LARGER THAN THE ARRAY, BAIL!!!
        if chunks_squished > array:
            # If the number of singles and doubles all put together exceeds the array
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")

        # Second check needs to be raised to we can determine the moment of collapse

        init_items_freqlist = []

        for chunk,freq in items_unsorted_list:
            # Make a list that represents the chunk
            m = list(range(1, chunk+1))

            for _ in range(freq):
                # append to the items_freqlist freq number of times
                init_items_freqlist.append(m)

        # print(f"This is init_item_freqlist {init_items_freqlist}")

        # Get the generic list and its indices and sort it according to the length of its chunk
        items_freqlist_ind = sorted(list(enumerate(init_items_freqlist)), key=lambda item:len(item[1]), reverse=True)
        items_freqlist = [elem for _, elem in items_freqlist_ind]


        focal = items_freqlist[0]

        if len(items_unsorted) == 1:
            ans = init_items_freqlist
            

        else:
            # second_in the items_list, which will be the last in our algorithm
            lfocal = PlainTranslate(items_freqlist[1].copy(), array - len(items_freqlist[1]))

            # print(f"This is focal {focal}; and lfocal: {lfocal}")

            ans += [focal, lfocal]

            for index, item in enumerate(items_freqlist[2:]):

                    # As long as tgere are no overlaps in the ans, add to it
                if not index % 2:
                    # If is even, add forward
                    added = PlainTranslate(focal.copy()[:len(item)], len(focal) + 1)
                    ans.append(added.copy())
                    # Update the leftward focal point
                    focal = added

                else:
                    # if odd, subtract backwards
                    added = PlainTranslate(lfocal.copy()[:len(item)], -1*(len(item) + 1))
                    ans.append(added.copy())
                    # update lfocal variable the rightward focal point
                    lfocal = added

        # REconstitute this ans in its particular order

        # Reconstitute, the final answer to its initial order
        # Putting the original index of the chunk_list_sort...
        ans = [(index_chunk[0],elem) for index_chunk, elem in zip(items_freqlist_ind, ans)]
        ans.sort(key=lambda item:item[0])
        ans = [elem for _, elem in ans]

        if not check_for_overlap(ans):
            # Translate everything back by 1 and then "refine"
            semi_ans = PlainTranslate(SortAlgorithms._semi_strip_list(ans), -1)

            # In case it is shifted by shift_val, refine afterward
            spit_out = Translatebyshift(semi_ans, shift_value, array)
            return refine_translate(spit_out, array)


        return SortAlgorithms.collapse(array, chunk_list, shift_value=shift_value)


    @staticmethod
    def centercluster(array, chunk_list={2:3}, shift_value=0):
        """The center cluster algorithm"""

        ans = []
        # we take into account the indices that is the particular order the chunk_list takes

        # The 'elem' below is the Key,value tuple in chunk_list.items()
        old_chunklist_elem_only = [elem for elem in chunk_list.items()]

        chunk_list_sorted = sorted(chunk_list.items(), key=lambda item:item[0], reverse=True)
        # The 'elem' below is the Key,value tuple in chunk_list.items()
        # ---chunk_list_sorted = [elem for _, elem in chunk_list_sort] 
        # The check part
        chunks_squished = sum([chunk*freq for chunk,freq in chunk_list_sorted])

        # FIRST CHECK, IF IT THE CHUNKLIST IS IN ITS SPECS LARGER THAN THE ARRAY, BAIL!!!
        if chunks_squished > array:
            # If the number of singles and doubles all put together exceeds the array
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")


        # the initial chunklist with no translations yet e.g. [[1,2],[1,2],[1], [1]]
        # The one without the sorting into doubles first then singles or so
        order_preserved_dummy = [list(range(1, chunk+1)) for chunk, freq in old_chunklist_elem_only for _ in range(freq)]

        dummy_chunk_ = sorted(list(enumerate(order_preserved_dummy)), key=lambda item:len(item))
        dummy_chunk_list = [item for _, item in dummy_chunk_]


        # The list of integers up to the first item of the first item of the chunk_list_sorted list.
        focal = PlainTranslate(dummy_chunk_list[0], (array - 1)//2)     #This is also the min point of the array
        ans.append(focal)

        forwardable, backwardable = True, True

        for index,chunk in enumerate(dummy_chunk_list[1:]):

            if not index % 2 and forwardable:
                # At even index, add forwards
                # The max value in the ans that we have started writing our answers to.
                max_b4 = max(strip_list_wrapper(ans)) + 1
                item = PlainTranslate(chunk.copy(), max_b4)

                if max(item) <= array:
                    ans.append(item)
                
                else:
                    forwardable = False
                    min_b4 = min(strip_list_wrapper(ans)) - (len(chunk) + 1)
                    item_ = PlainTranslate(chunk, min_b4 -1)
                    # print(f"This is minb4: {min_b4}, chunk: {chunk}, items: {item_}")

                    if min(item_) >= 1:
                        ans.append(item_)
                    else:
                    # If it hits sthe ground but still has not run out
                        backwardable = False
                        return SortAlgorithms.collapse(array, chunk_list)
                    # Break
                    # return collapse(array, chunk_list)

            elif index % 2 and backwardable:
                # Choose the minimum value of the ans array, and translate item beyond that such that there is still one period of space 
                min_b4 = min(strip_list_wrapper(ans)) - (len(chunk) + 1)
                item = PlainTranslate(chunk.copy(), min_b4 -1)

                if min(item) >= 1:
                    ans.append(item)
                else:
                    # If it hits sthe ground but still has not run out
                    backwardable = False
                    return SortAlgorithms.collapse(array, chunk_list, shift_value=shift_value)



        # The raw for 'ans is shifted cack by 1, as the chunking is zero-based'
        semi_ans = PlainTranslate(SortAlgorithms._semi_strip_list(ans), -1)
        
        # In case it is shifted by shift_val, refine afterward
        spit_out = Translatebyshift(semi_ans, shift_value, array)
        final_ans = refine_translate(spit_out, array)

        # Reconstitute, the final answer to its initial order
        # Putting the original index of the chunk_list_sort...
        final_ans = [(index_chunk[0],elem) for index_chunk, elem in zip(dummy_chunk_, final_ans)]
        final_ans.sort(key=lambda item:item[0])
        final_ans = [elem for _, elem in final_ans]

        return final_ans

        # ----------------------------------------------------------------------------------------------
    @staticmethod
    def r_leapfrog(array, chunk_list={1:1, 2:2}, shift_value=0):
        """ The leap_frog algorithm, but in reverse. """
        leapfrog = SortAlgorithms.leap_frog(array, chunk_list=chunk_list, shift_value=shift_value)
        # Reverse the whole thing
        r_leapfrog = SortAlgorithms.Add_list_to_x(leapfrog, array)
        return r_leapfrog
    
    @staticmethod        
    def r_xlx_reflection(array, chunk_list={1:1, 2:2}, shift_value=0):
        """ The xlx_reflection algorithm, but in reverse """
        xlx = SortAlgorithms.xlx_reflection(array, chunk_list=chunk_list, shift_value=shift_value)
        r_xlx = SortAlgorithms.Add_list_to_x(xlx, array)
        return r_xlx

    @staticmethod
    def r_centercluster(array, chunk_list={1:1, 2:2}, shift_value=0):
        """ The xlx_reflection algorithm, but in reverse """
        cen_cl = SortAlgorithms.centercluster(array, chunk_list=chunk_list, shift_value=shift_value)

        cen_cl = SortAlgorithms.Add_list_to_x(cen_cl, array)
        return cen_cl


    @staticmethod
    def collapse(array, chunk_list={2:2, 1:2}, shift_value=0):
        """Spacing out chunk values that somehow collapsed during chunking with the selected algorithm"""

        # The 'elem' below is the Key,value tuple in chunk_list
        old_chunklist_elem_only = [elem for elem in chunk_list.items()]

        chunk_list_sorted = sorted(chunk_list.items(), key=lambda item:item[0], reverse=True)
        # the initial chunklist with no translations yet e.g. [[1,2],[1,2],[1], [1]]

        order_preserved_dummy = [list(range(1, chunk+1)) for chunk, freq in old_chunklist_elem_only for _ in range(freq)]
        dummy_chunk_ = sorted(list(enumerate(order_preserved_dummy)), key=lambda item:len(item))

        init_chunk_list = [item for _, item in dummy_chunk_]
        # init_chunk_list = [list(range(1, chunk+1))for chunk, freq in chunk_list_sorted for _ in range(freq)]
        
        w_chunk_list = []

        for index, item in enumerate(init_chunk_list):
            if index == 0:
                # Append the first item freely
                w_chunk_list.append(item)
            else:
                trans = max(strip_list_wrapper(w_chunk_list))

                added = PlainTranslate(item.copy(), trans)
                w_chunk_list.append(added)


        # print(f"This is w_chunk_list: {w_chunk_list}")

        # Number of items in the init chunk list
        len_init  = len(init_chunk_list)
        # This is the range (The very end of all our chunklists put side by side) the edge of the chunk
        chunk_range = len(strip_list_wrapper(init_chunk_list))
        # calculate the difference between the array, and the egde of the chunk
        diff = array - chunk_range

        # The working diff, (i.e. the diff we would actually use to space stuff out)
        w_diff = len_init - 1 if diff >= (len_init -1) else diff

        for x in range(1,w_diff+1):
            slice_point = ((x*len_init))//(w_diff+1)
            
            # Take out the chunk from the end where we are about to split
            slice_items = w_chunk_list[slice_point:]
            # split! That is translate by 1
            slice_items = PlainTranslate(slice_items, 1)

            # Place it back into the init_chunk_list
            w_chunk_list[slice_point:] = slice_items

        # The process is done at this point. Translate everything back by 1  and then "refine"
        semi_ans = PlainTranslate(SortAlgorithms._semi_strip_list(w_chunk_list), -1)
        
        # In case it is shifted by shift_val, refine afterward
        spit_out = Translatebyshift(semi_ans, shift_value, array)
        final_ans = refine_translate(spit_out, array)

        # Handles the reconstitution into the original order in which it came
        final_ans = [(index_chunk[0],elem) for index_chunk, elem in zip(dummy_chunk_, final_ans)]
        final_ans.sort(key=lambda item:item[0])
        final_ans = [elem for _, elem in final_ans]

        return final_ans



    @staticmethod
    def _semi_strip_list(list_arg):
        """Private method used to strip elements in a list if its length is one. This method strips the abouve chunked values into values
        usable by the rest of the software, i.e. from [[1,2], [3]] to [[1,2], 3]"""

        ans = []
        for elem in list_arg:
            # If it is a list...
            if isinstance(elem, list):
                # ... and has a length of more than 1
                if len(elem) != 1:
                    ans.append(elem)
                else:
                    ans.append(elem[0])
            # If it is not a even a list to begin with
            else:
                ans.append(elem)
        return ans


    # --------------------------------------------
    @staticmethod
    def Add_list_to_x(elemlist, array):
        """Adds an element (dependent on the element) to the elem_list.
        Specifically for the reverse algorithms"""
        ans = elemlist.copy()
    
        for index, elem in enumerate(elemlist):
            if isinstance(elem, list):
                for index_,x in enumerate(elem):
                    upd = array - 1 - x
                    elem[index_] = upd
                elem.sort()
            else:
                elem = array - 1 - elem
            ans[index] = elem
        return ans



if __name__ == "__main__":
    chunk_test = {2:2, 1:2}
    test_liste = [[0,1],[7,8],[8,9]]
    me_test = [4, 5, 6, 7, 8, [0, 1], 3]
    again = [4, [5, 6], 7, 8, 9, [0, 1], [3, 4]]
    yet = [[0, 1], [7, 8], [8, 9], 0, [1, 2], 3]

    tt = [[0,1],[8,9],[8,9], [1,2]]
    
    # # ----------------------------
    # print(f"|| {Moveover_fixed([[0,1], [0,1]], 10, fixed_item=[[0,1]])}")
    # cast = [1,2,2,3,4,4,4,6,7,8,4,4,4,4,4,8,9,0]

    # casual_removeall(cast, 4)
    # print(cast)

    # print(PacketAlgos.direct(10,15))
    # print(PacketAlgos.rev_direct(10,15))
    # print(PacketAlgos.leapfrog(10,15))
    # print(PacketAlgos.rev_leapfrog(10,15))
    # print(PacketAlgos.xlxreflection(25,30))
    # print(PacketAlgos.rev_xlxreflection(10,15))

    # ---------------------------------------------------------
    # movedover_fixed error handled
    # print(Moveover_fixed([7, 8, [0, 1], [2, 3], [4, 5], [6, 7]], 10, fixed_item=[7,8]))

    # print(SortAlgorithms.xlx_reflection(10, chunk_list={2:5}, shift_value=5))

    for k in range(101):
        print(nth_suffix(k))
    
