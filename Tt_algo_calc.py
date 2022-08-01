import random, inspect, time

# Algoroithm for putting subjects into days.
# Each class here is prefixed with a 'D' representing Days

class DXLXReflection:
    """ This classes packets departments into days using the XLX-reflection method.
    However, no spaces between the days are required """


    @staticmethod
    def chunk(array):
        """ Chunks periods into the 'x,L-x' format with no spaces
        i.e. periods are assigned from both ends till the middle """

        ans = []

        for num in range(1, int((array+3)/2)):
            a,b = num, array+1-num
            if a!=b:
                d = [a,b]
            else:
                d = [b]
            ans.append(list(d))
        return ans


    @staticmethod
    def chunk_x_into_y(num, array):
        """ This function uses the chunk function defined above to chunk 
        values (less than the array value) into the array value.

        Works based on the 'x,L-x' reflection algorithm
        This is what is used to packet subjects into Days for the class arms
        
        """
        
        chunk_func = DXLXReflection.chunk(array)
        re_chunk = []
        for item in chunk_func:
            f = list(item)
            f.sort()
            re_chunk.append(f)

        if array % 2:
            if num % 2:
                chunk_num = re_chunk[-1]
                for x in range(int((num-1)/2)):
                    chunk_num.extend(re_chunk[x])
            else:
                chunk_num = []
                for x in range(int(num/2)):
                    chunk_num.extend(re_chunk[x])
        else:
            if num % 2:
                chunk_num = [re_chunk[-1][0]]
                for x in range(int((num-1)/2)):
                    chunk_num.extend(re_chunk[x])
            else:
                chunk_num = []
                for x in range(int(num/2)):
                    chunk_num.extend(re_chunk[x])

        return chunk_num


class DCenterCluster:
    """
    This is the center-cluster algorithm (no gaps in between) for chunking departments into days.
    Also prefixed with a "D" 
    """

    @staticmethod
    def chunk(array):
        """This function starts from the middle and then spreads out to the edges."""

        # The middle value
        start = int((array + 1)/2) if array % 2 else int(array/2)
    
        ans = []

        # the two operative variables
        a,b = start, start + 1
        run = True

        while run:
            if a >= 1:
                ans.append(a)
            if b <= array:
                ans.append(b)

            if a < 1 and b > array:
                run = False

            # Update a and b
            a -= 1
            b += 1

        return ans

    def chunk_x_into_y(num, array):
        """Relies on the method above to return a 'num' amount of chunked numbers"""

        all_chunk = DCenterCluster.chunk(array)

        return all_chunk[:num]


class DLeapFrog:
    """This handles packeting depts into days in the leapfrog ("This, skip one, that") way """

    @staticmethod
    def chunk(array):
        # All are singles. doubles are not required here
        # takes in the odd numbers, 1,3,5...

        ans = []
        item = 1
        
        while item <= array:
            ans.append(item)
            item += 2

        return ans


    @staticmethod
    def chunk_x_into_y(num, array):
        """Uses the above function to churn out numbers based on the chunk"""

        # The value of num beyond which the algo breaks and we have to begin to sort anew
        # The border value is the mathematical length of the chunk value
        border_val = (array + 1)/2 if array % 2 else array/2

        # 'num' should always be zero or positive and not more than the array value
        if num < 0:
            raise ValueError(f"Less than zero doesn't work")

        if num > array:
            raise ValueError(f"{num} does not go in {array}")

        if num <= border_val:
            return DLeapFrog.chunk(array)[:num]
        
        # in case of a fall-through
        ans = list(range(1, num + 1))

        # space out this ans list so it doesn't prove cumbersome to work with
        ans = space_out(ans, array)

        return ans


# ************************************************************************************************
# ************************************************************************************************
# Come back and finish up the class below
class XLXReflection:
    """ 
    Houses te x-L-x algorithm.
    The algoritms is defind as one which renders the reflection of an item (from the end) 
    based on how far it is from the start.

    """

    @staticmethod
    def chunk_singles(array):
        """ This algorithm obeys the XLX reflection algorithm for singles, but unlike the "chunk" below.
        It puts spaces in between its entries (as in, [1,n],[3, n-2])"""


        # Return an empty list if the array entered is zero or negative
        if array <= 0:
            return []

        first, last = 1, array
        ans = []

        # The two parameters that will be upgraded as we see fit
        a, b = first, last

        run = True
        # The loop runs only for when a (as it increases) is less than b (as it decreases)
        while run:
            if a - 2 < b:
                ans.append(a)

            if a > b:
                run = False

            if b > a:
                ans.append(b)

            a += 2
            b -= 2

        return ans


    @staticmethod
    def chunk_doubles(array):
        """ Uses XLX algo (with spaces) to chunk doubles """

        ans =[]
        a,b = 1,2
        c,d = array-1, array

        run = True

        while run:
            if b < c + 3:
                ans.append([a,b])

            if c > b:
                ans.append([c,d])
            
            else:
                run = False

            a += 3
            b += 3
            c -= 3
            d -= 3

        return ans


    @staticmethod
    def doubles_and_singles(num_singles, num_doubles, array, shift_value=0):
        """ This method combines both the "chunk singles" and "chunk doubles" methods 
        to make combinations of single and double periods """
        pass




    # ---- THE SECOND ALGORITHM
    def chunk2(array):
        """This chunking algorithm is for singles in the 1, 3, 2, 5, 4, 7, format"""

        ans = [1,3]
        for x in range(1, int(array/2)):
            a, b = 2*x, 2*x + 3
            if b > array:
                b = array
            ans.extend([a,b])
        return ans


    def chunk_x_into_y2(num, array):
        """Uses the algorithm defined above (for singles) 
        to chunk num into array"""

        chunk = chunk2(array)

        return chunk[:num]
    


# ---------------------------------------
# THE CENTER-CLUSTER ALGORITHM

class CenterCluster:
    """ Houses the entire algorithm for te center cluster operation.
    
    The 'Center-cluster' algorithm is the algorithm that spaces the items (periods in this case) out
    first from the middle and then out to the edges on both sides. left before right!

     """
    
    @staticmethod
    def singles(array):
        """
        This defines the 'center-cluster' algorithm for single periods.
        It is referred to as 'center-cluster' because by design, unless it is contrained by some other factor,
        it clusters at the center before spreading out to the edges.

        """
        if array <=0:
            return []
        
        run = True

        # Calculating for even number of array
        if not array % 2:
            ans = []
            i = 0

            # Actually, on paper it was discovered that every consecutive odd-even part added up to k.
            # That is array + 2. This is a constank 'k' in the math.
            k = array + 2

            while run:
                a = int((array - 4*i)/2)
                b = k - a

                if a >= 1:
                    ans.append(a)
                    
                if b <= array:
                    ans.append(b)
                    i += 1
                
                else:
                   run = False


        # Calculating to odd number of array
        else:
            first = int((array + 1)/2)

            ans = [first]
            k = array + 1
            i = 1

            while run:
                a = first - 2*i
                b = first + 2*i

                if a >= 1:
                    ans.append(a)

                if b <= array:
                    ans.append(b)

                    i += 1

                else:
                    run = False

        return ans


    @staticmethod
    def doubles(array):
        """
        Uses the 'center-cluster' algorithm but for doubles this time
        """

        if array <= 0:
            return []

        run = True

        # The multiple number
        i = 1

        ans = []

        # If array is an odd number
        if array % 2:

            a = int((array + 1)/2)
            b = a + 1

            ans = [[a,b]]

            while run:
                c = [a - 3*i, b - 3*i]
                d = [a + 3*i, b + 3*i]

                # if the first item of the list to be appended to ans does not run past zero
                if c[0] >= 1:
                    ans.append(c)

                # If the very last item does not exceed the array number
                if d[-1] <= array:
                    ans.append(d)

                i += 1

                if c[0] < 1 and d[-1] > array:
                    run = False

        else:

            a = int(array/2)
            b = a + 1

            ans = [[a,b]]

            

            while run:
                c = [a - 3*i, b - 3*i]
                d = [a + 3*i, b + 3*i]

                if c[0] >= 1:
                    ans.append(c)

                if d[-1] <= array:
                    ans.append(d)

                i += 1

                if c[0] < 1 and d[-1] > array:
                    run = False

        return ans


    @staticmethod
    def doubles_and_singles(num_singles, num_doubles, array, shift_value=0):
        """ Handles both singles and doubles. This is the method exported out for the sorting algorithm """
        # the array is zero-indexed so even though its starting from 1 here, increase array by 1, so that it evens out

        span = num_singles + num_doubles*2
        length = num_singles + num_doubles

        if span > array:
            raise ValueError(f"{span} is more than {array}")

        if num_singles == num_doubles == 0:
            return []

        # As before, the singles come before the doubles, so
        
        doubles = CenterCluster.doubles(array)[:num_doubles]
        # The very last item of the last item of the doubles
        try:
            # In the event that the doubles is empty. the below gives an error
            end_item = doubles[-1][-1]
        except Exception:
            end_item = 0
        
        # Now to calculate the singles
        singl_ = []
        run = True

        # if no doubles are given, that is num_doubles = 0
        if num_doubles == 0:
            singl_ = CenterCluster.singles(array)
        

        # if the number of doubles is even
        elif not num_doubles % 2:

            # The last item of the second last item in the doubles list
            if len(doubles) == 1:
                last = doubles[0][-1]
                first = doubles[0][0]

            else:
                try:
                    # In the event that the doubles list is empty. This throws an error, hence the try-except block
                    last = doubles[-2][-1]

                    # The first item of the earliest item
                    first = doubles[-1][0]
                except Exception:
                    last, first = 0, 0


            while run:
                #New last-rightmost item 
                l_it = last + 2

                # New first-leftmost item
                f_it = first - 2

                if l_it <= array:
                    singl_.append(l_it)

                if f_it >= 1:
                    singl_.append(f_it)

                # Updating the last and first items to the new appended values
                last = l_it
                first = f_it

                if l_it > array and f_it < 1:
                    run = False


        # if the number of doubles is odd
        else:
            
            if len(doubles) == 1:
                last = doubles[0][-1]
                first = doubles[0][0]

            else:
                # The first item of the second last (earliest) item
                first = doubles[-2][0]

                # The last item of the latest item
                last = doubles[-1][-1]

            while run:
                f_it = first - 2
                l_it = last + 2

                if f_it >= 1:
                    singl_.append(f_it)

                if l_it <= array:
                    singl_.append(l_it)

                # Updating the last and first items to the new appended values
                last = l_it
                first = f_it

                if l_it > array and f_it < 1:
                    run = False


        singl_2 = singl_[:num_singles]


        # -----------------------------------------------------
        # If the input is greater than the chunked version, but not large enought to violate the array,
        # collapse the whole thing and reform

        tot = doubles + singl_

    
        # if total_chunk >= len(chunk_list) or chunk_list[-1] > array:
        if length > len(tot) or max(strip_list_wrapper(tot)) > array or num_doubles > (array + 1) // 3:
            # The last "or" condition in the statement above is for if num_doubles exceeds the maximum as allowed by the Centercluster algorithm

            doubles, singl_ = [], []
            a, b = 1, 2

            # Crating the doubles, however with no space in between. Contiguous!
            for doub in range(num_doubles):
                
                doubles.append([a,b])

                if doub != range(num_doubles).stop - 1:
                    a += 2
                    b += 2

            # Now creating singles
            for _ in range(num_singles):
                # the latest item is 'b'
            
                b += 1
                singl_.append(b)
                

            # Combine both singles and all the doubles
            rechunked = doubles + singl_

            # Slice to get the amount you want.
            # It really should be about the same size as rechunked
            # t_rechunked = rechunked[:length]

            # Now spread out the array nicely!
            final = space_out(rechunked, array)

            spit_out = Translatebyshift(space_out(final, array), shift_value, array)

            # NOW TRANSLATE EVERYTHING BACKWARDS, SO ITS ZERO INDEXED AND NOT FROM 1 AS IT CURRENTLY IS
            spit_out = Translatebyshift(spit_out, -1, array)

            # the below re-adjusts the output so you don't have e.g. [9,0]
            return refine_translate(spit_out, array)
            

        # If the above if-condition isnt met execute the below!
        final = doubles + singl_2

        # return Translatebyshift(final, shift_value, array)
        spit_out = Translatebyshift(final[:length], shift_value, array)

        spit_out = Translatebyshift(spit_out, -1, array)
        
        return refine_translate(spit_out, array)



# -------------------------------------------------------------------
# ---- THE LEAPFROG ALGORITHM FOR SINGLES
class LeapFrog:
    """ Houses the Leap-frog algorithm.

    The Leap-frog algoritm is operates by skipping the
    adjacent period to te period chosen

    """

    @staticmethod
    def chunk_singles(array):
        # -- The Leap-Frog algorithm
        #- for singles not doubles with one free period in between

        num, count = 1, 0
        ans = [num]
        while True:
            num += 2
            count += 1
            if num <= array:
                ans.append(num)
            else:break
        
        return ans

        
    @staticmethod
    def chunk_x_into_y3(num, array):
        chunk = chunk_singles(array)

        if num <= len(chunk):
            return chunk[:num]
        return [x for x in range(1, num + 1)]


    @staticmethod
    def chunk_doubles(array):
        # --Handles the spacing of double periods with one period in between
        # -- the leap-frog way
        if array <= 0:
            return []

        a,b = 1,2
        ans = [[a,b]]

        while True:
            a += 3
            b += 3
            if b <= array:
                ans.append([a,b])
            else:
                break
        return ans


    @staticmethod
    def chunk_x_into_y4(num, array):
        # -- Handles the chunking of double periods
        chunk = chunk_doubles(array)

        if num <= len(chunk):
            return chunk[:num]

        a,b = 1,2
        ans = [[a,b]]

        while True:
            a += 2
            b += 2
            if b <= num:
                ans.append([a,b])
            else:break

        return ans


    @staticmethod
    def doubles_and_singles(num_single, num_double,array, shift_value=0):
        # -- To help chunk singles and doubles side by side, with doubles coming first

        # This is the complete stretch of all the numbers of singles and doubles in the array
        # Uses the LEAP-FROG ALGORITHM?


        total_chunks_doub = num_single + num_double*2

        # the total number of sinles and doubles in the array
        total_chunk = num_single + num_double

        if total_chunks_doub > array:
            raise ValueError(f"ERROR: cannot work, {total_chunks_doub} is greater than {array}")

        chunk_double = LeapFrog.chunk_doubles(num_double*3 - 1)

        # chunk_double returns nested lists. The below is to pick the absolute last item 
        try:
            # in the event that zero is passed as the array to the chunk double function. 
            # Trying the below to index it would yield an error

            end_double = chunk_double[-1][-1]
        except Exception:
            end_double = 0

        chunk_single = LeapFrog.chunk_singles(array - end_double)

        # Shift all the elements in chunk_single forwards by end_double
        chunk_single_shifted = [x + end_double for x in chunk_single]

        chunk_list =  chunk_double + chunk_single_shifted


        # total chunk sometimes might be greater than the value in chunk_list

        # --If the number of insertions are more than the regular chunking with spaces,
        # --collapse the whole thing and reform

        # --Also the "or chunk_list[-1] > array" is for when the last item in the chunk_list spills past array.
        #  We don't want that, so we collapse it and begin anew

        if total_chunk >= len(chunk_list) or chunk_list[-1] > array:
            a,b = 1,2
            ans = [a,b]

            while True:
                a += 2
                b += 2
                if b <= num_double*2:
                    ans.extend([a,b])
                else:
                    break

            # break up array into a nested list of two items for the doubles
            ans2 = []

            for i in range(0, num_double*2, 2):
                ans2.append([ans[i], ans[i + 1]])

            try:
                # since the sinlges begin after the doubles, we must get the last item of the doubles.
                # if the array is zero, the below yields an error, hence the try-except clause.
                # We either want it to give the last item in the doubles or zero if it can't find it
                double_end = ans[-1]
            except Exception:
                double_end = 0

            # The extra singles is for whatever singles are left over when the doubles have been taken
            # From below, it starts where the doubles stop
            # extra_singles = list(range(double_end+1, array+1))


            # The if statement below checks to see if there is still space in what is left of the array
            if num_single < (total_chunk - num_double):

                extra_singles = chunk_singles(array - double_end)

                # Shift all the entries forward by double_end+1
                extra_singles = [x + double_end for x in extra_singles]
            else:
                extra_singles = list(range(double_end+1, array+1))

            tot = ans2 + extra_singles

            # last minute clean up!
            # if there is still space at the end, the below takes that space and wedges it at the middle of the tot[:total_chunk]
            # list and shifts every number to the right by the same  amount

            # Finding the absolute last item of the list
            final = tot[:total_chunk]



            # the first half of the final, i.e. the chunked list that we want to space out in the middle
            spit_out = Translatebyshift(space_out(final, array), shift_value, array)
            return refine_translate(spit_out, array)
            
        spit_out = Translatebyshift(chunk_list[:total_chunk], shift_value, array)
        return refine_translate(spit_out, array)


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
    """Shifts an INTEGER or all the items of a list by "shift". 
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
    """Container for TranslateByShift. This method translates both list objects and integer objects"""

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
    the end and beginning of the array, e.g [9,0] (or more generically, [len(array), 0]), which would be impossible
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

        global fin_list

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
    is equal in length to its set"""
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



def Moveover(list_arg, array):
    # Spreads a list to ensure that no members overlap

    if len(strip_list_wrapper(list_arg)) > array:
        return ValueError(f"Length of list_arg is greater than {array}")


    list_arg = list(enumerate(list_arg.copy()))

    sorted_list = sorted(list_arg, key=lambda ind_item:max(ind_item[1]) if isinstance(ind_item[1], list) else ind_item[1])
    s_list = [item for index, item in sorted_list]
    w_list = s_list.copy()


    # ---------------------------------------------------------
    def slide_over_one(in_list, forward=True):
        # keep sliding over till there are no overlaps or at least till the cycle is exhausted

        bowl = []
        print()
        # print(f"List before switching: {in_list}")

        listarg = in_list.copy() if forward else list(reversed(in_list))

        print()
        # print(f"The working list_arg in function: {listarg}")
        print()

        trans = 1 if forward else -1
        
        for elem in listarg:
            # If there is a match, i.e the elem has featured before in 'bowl', translate it and add
            if abs_match_list_int(bowl, elem) or abs_match_list_int([array], elem):
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
    fin = w_list.copy()
    loop = True
    forward = True
    count = 0


    while loop:
        count += 1
        
        # time.sleep(1)
        # preserves the old value of fin in case it needs to retrace its steps with the var _keep
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
                fin = _keep

            elif min(strip_list_wrapper(fin)) < 0:
                # print("Going right again")
                forward = True

                # print(f"This is fin going backwards: {fin}")
                # print("-"*30)

            fin = _keep.copy()
            # else:
            #     if min(strip_list_wrapper(fin)) < 0:
            #         loop = False
            #         print("Bailed out!")

        
  
        if count >= array*5:
            raise StopIteration(f"OVERLOADED!! {fin} did not work")  

        # Reconstitute the list to its previous order
        # fin is one-one mapped to sorted_list

    fin = [(ind_item[0], fin_item) for ind_item, fin_item in zip(sorted_list, fin)]
    fin = sorted(fin, key=lambda ind_item:ind_item[0])
    fin = [elem for index,elem in fin]

    return fin



def moveover_fixed(list_arg, array,fixed_item=None, fixed_index=0):
    """This function does the work of the moveover function except for the fact that it holds an item (if given), or it's 
    index (if given) fixed.
    It is done this way, we pop out the fixed item and moveover whats left. Then we concatenate what's left"""

    # --------------------------------------------------------------------------
    # def slide_right_left(list_arg,array, trans=1):
    def slide_right_left(sorted_list_arg, trans=1):
    # Stores the elements of list_arg ind its index in a tuple, so we can refer back to it
        # global pos, sorted_list_arg, fin_dict, test_li st

        test_list = []
    
        for item in sorted_list_arg:
            if isinstance(item, list):
                # check if any item in this list has already featured in test_list
                for x in item:
                    if x in strip_list_wrapper(test_list + const_list):
                        print()
                        new = Translatebyshift(item, trans, array)
                        # print(f"Translating first item: {item} forwards!:{x}, to: {new} ")
                        # Translate it forward by 1 (By default)
                        test_list.append(new)
                        break 

                else:
                    print()
                    # print("List appended")
                    test_list.append(item)
                    
    
            # If it is an integer
            else:
                if item in strip_list_wrapper(test_list + const_list):
                    val = (item + trans) % array
                    test_list.append(val)
                    # print()
                    # print("Translating int forwards!")
                    
                else:
                    test_list.append(item)
                    # print("int appended")
                    

        # print("-"*70)
        # print(f"This is test_list in the function: {test_list}")
        # print("-"*70)
        # print()

        return test_list

    # ----------------------------------------------------------------------------
# -----------------------------------------------------------------------

    # global fin_dict, pos, sorted_list_arg
    # Get the fixed (const) item either from the item itself of from its index in the list_arg
    if fixed_item and abs_match_list_int(list_arg, fixed_item, strict=True):
        const_item = fixed_item
        # fixed_index = list_arg.index(fixed_item)

    # If fixed item is not none, but doesn't occur in the list, raise error
    elif fixed_item:
        raise ValueError(f"{fixed_item} does not occur in list_arg")

    else:
        const_item = list_arg[fixed_index]

    # Now remove the const_item from the list_arg, so it can be moveover'ed without it
    list_arg = remove_all_sub_from_list(list_arg, const_item)

    # The length of the newly popped upon list_arg
    list_len = len(list_arg)

    # Put the const item in the finished_list for now
    const_list = const_item
    # print(f"This is const item {const_item}")

    # Now start moving over
    # An empty dictionary to hold the indices and the new value to aid reconstitution
    fin_dict = {}
    test_list = []

    # -------------
    pos = [(index, item) for index, item in enumerate(list_arg)]
    sorted_list_arg_index = sorted(pos, key=lambda ind_item:max(ind_item[1]) if isinstance(ind_item[1], list) else ind_item[1])
    # map a list of just the items to the sorted_list_arg_index
    sorted_list_arg = [item for _,item in sorted_list_arg_index]
    # ---------------


    final_val = sorted_list_arg

    count = 0
    loop = True
    right = True
    
    # --------------------------------------------------------
    while loop:
        if f_check_for_overlap(final_val, const_item):
            
            final_val = slide_right_left(final_val)
            # print(f"This is f_val forwards: {final_val}")

            if count >= array*2:
                loop=False
                # print(f"Stranded! loop ran out")

            count += 1
        else:
            loop = False
        # -------------------------------------------------


    count, loop = 0, True
    # Now check if final_val spills past the edge of the array

    while loop:
        if 0 in strip_list_wrapper(final_val)[1:]:
            final_val = slide_right_left(final_val, trans=-1)
            print(f"This is final val in the second loop: {final_val}")

            if count >= array*5:
                print("Ran out in the second loop!")
                loop = False
            count += 1
        else:
            loop = False
            

    # Note that test_list (final_val) is one-one-mapped to sorted_list_arg
    # Therefore to reconstitute the list...

    # Map final_val to its index
    final_val = [(ind_item[0], f_val) for f_val, ind_item in zip(final_val, sorted_list_arg_index)]
    
    # Now sort this final_val based on its index
    final_val = sorted(final_val, key=lambda ind_val:ind_val[0])
    # Now wring out the list of just the items from final_val
    final_val = [item for _,item in final_val]
    # Now return it

    # Now add back the const_item into the final list

    # final_val.insert(fixed_index, const_item)
    final_val = final_val[:fixed_index] + const_item + final_val[fixed_index + 1:]
    return final_val


def possible_combs(list_arg, array):
    """This function finds out all the possible legal spaces a chunked list can have when a piece is held constant
    Legal in the sense that it doesn't run past 0 or past the array and its items do not overlap

    The list_arg must have been "moved over", i.e no overlaps 

    """

    # Move list_arg if it hasn't been moved before
    # --------------------------------------------------------
    list_arg = Moveover(list_arg, array)
    # ----------------------------------------------------------

    possible_list = []
    sec_list_arg = [(index,item) for index,item in enumerate(list_arg)]

    # Sort the sec_list_arg based on the max item in each list item if it is a list or the same number if it is an integer
    sorted_sec_list_arg = sorted(sec_list_arg, key=lambda ind_item:max(ind_item[1]) if isinstance(ind_item[1],list) else ind_item[1])

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
                if min(strip_list_wrapper(_sec_list_arg)) >= 0 and max(strip_list_wrapper(_sec_list_arg)) <= array:
                    
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


def possible_combs_with_fixed(list_arg,const,array):
    # Gets all the possible combinations with a fixed item inside. 
    # const is now an iterable holding all values
    
    all_ = possible_combs(list_arg, array)

    if not bool(const):
        return all_

    # if len(const) == 1 or isinstance(const, int):
    #     return [lists for lists in all_ if const in lists]

    ans = []
    
    for item in all_:
        # For each item in all_, cycle through the const list
        for x in const:
            if x not in item:
                # Even if one isn't in that list abandon it
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
    """Removes all the elements of sub_list from list_arg or 'dies trying', i.e 
    raises a valueerror sub_list is not a proper subset of list_arg"""
    ans_list = strip_list_wrapper(list_arg.copy())

    # cast into a list in the event that it an object or an int
    sub_list = [sub_list]
    for elem in strip_list_wrapper(sub_list):
        ans_list.remove(elem)
    return ans_list


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

    @staticmethod
    def leap_frog(array, chunk_list={2:2, 1:2}):
        """ Revised leapfrog algorithm """

        # sort the chunk_list itms by the chunk_number from largest to smallest
        chunk_list_items = sorted(chunk_list.items(), key=lambda item:item[0], reverse=True)
        # the length of the sequences, 3 if (triples, singles and doubles) or 2 (doubles, and singles) so we can see if we can space them
        chunk_sequence = len(chunk_list)
        # The variable checks whther we can add one space after each chunk sequejnce, else it "compromises" and contracts without collapsing just yet!
        compromise = False
        
        check = sum([chunk + (freq - 1)*(chunk + 1) for chunk, freq in chunk_list_items]) + chunk_sequence - 1

        # The total sum of the frequencies of all the chunks must also not exceed array, otherwise there is no way to help!
        chunks_squished = sum([chunk*freq for chunk, freq in chunk_list_items])


        if chunks_squished > array:
            # If all the chunks in their freqiencies side-by-side exceed array, break out
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")

        if check > array:
            # Contract but do not collapse
            check -= (chunk_sequence - 1)
            if check > array:
                # If after contracting, it still spills beyond array
                # raise ValueError(f"Can't be helped! {check} is more than {array}")
                # IMPLEMENT HERE -- COLLAPSE THE WHOLE THING AND REBUILD!
                SortAlgorithms.collapse(array, chunk_list)
            else:
                compromise = True
        
        ans, count = [], 0

        for chunk, freq in chunk_list_items:
            if count > 0:
                last_item = strip_list_wrapper(ans)[-1] + 1 if not compromise else strip_list_wrapper(ans)[-1]
            else:
                last_item = 0

            for x in range(freq):
                item = list(range(1,chunk + 1))
                item = PlainTranslate(item, last_item + (x*(chunk + 1)))

                ans.append(item)

            count += 1
        return ans

    @staticmethod
    def xlx_reflection(array, chunk_list={2:1, 1:1}):
        """The xlx chunking algorithm (revised)"""
        ans = []
        items_list = sorted(chunk_list.items(), key=lambda item: item[0], reverse=True)
        # make the first two items of the list
        # first item (the first item of the first item which is a tuple (chunkval, freq))
        chunks_squished = sum([chunk*freq for chunk, freq in items_list])

        # FIRST CHECK, IF IT THE CHUNKLIST IS IN ITS SPECS LARGER THAN THE ARRAY, BAIL!!!
        if chunks_squished > array:
            # If the number of singles and doubles all put together exceeds the array
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")


        # Second check needs to be raised to we can determine the moment of collapse


        items_freqlist = []

        for chunk,freq in items_list:
            # Make a list that represents the chunk
            m = list(range(1, chunk+1))

            for _ in range(freq):
                # append to the items_freqlist freq number of times
                items_freqlist.append(m)

        # print(f"This is item_freqlist {items_freqlist}")


        focal = items_freqlist[0]
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

        if not check_for_overlap(ans):
            return ans

        return SortAlgorithms.collapse(array, chunk_list)


    @staticmethod
    def centercluster(array, chunk_list={2:3}):
        """The center cluster algorithm"""

        ans = []
        chunk_list_sorted = sorted(chunk_list.items(), key=lambda item:item[0], reverse=True)

        # The check part
        chunks_squished = sum([chunk*freq for chunk, freq in chunk_list_sorted])

        # FIRST CHECK, IF IT THE CHUNKLIST IS IN ITS SPECS LARGER THAN THE ARRAY, BAIL!!!
        if chunks_squished > array:
            # If the number of singles and doubles all put together exceeds the array
            raise ValueError(f"Not compatible. {chunks_squished} greater than {array}")


        # the initial chunklist with no translations yet e.g. [[1,2],[1,2],[1], [1]]
        dummy_chunk_list = [list(range(1, chunk+1)) for chunk, freq in chunk_list_sorted for _ in range(freq)]

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
                    return SortAlgorithms.collapse(array, chunk_list)

        return ans




    def collapse(array, chunk_list={2:2, 1:2}):
        """Spacing out chunk values that somehow collapsed during chunking with the selected algorithm"""

        chunk_list_sorted = sorted(chunk_list.items(), key=lambda item:item[0], reverse=True)
        # the initial chunklist with no translations yet e.g. [[1,2],[1,2],[1], [1]]
        init_chunk_list = [list(range(1, chunk+1))for chunk, freq in chunk_list_sorted for _ in range(freq)]
            
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


        return w_chunk_list
    


if __name__ == "__main__":
    chunk_test = {4:2, 2:1}
    test_liste = [[0,1],[7,8],[8,9]]
    me_test = [4, 5, 6, 7, 8, [0, 1], 3]
    again = [4, [5, 6], 7, 8, 9, [0, 1], [3, 4]]
    yet = [[0, 1], [7, 8], [8, 9], 0, [1, 2], 3]

    tt = [[0,1],[8,9],[8,9], [1,2]]
    
    # my = Moveover(test_liste, 10)
    # print()
    # print(my)
    # print(moveover_fixed(me_test, 10, fixed_item=[[0,1]]))

    # print(possible_combs(my,10))

    # print("Hello")
    # print(possible_combs_with_fixed(test_liste,[[0,1]], 10))

    print(SortAlgorithms.centercluster(12, chunk_test))
    # print(collapse(10, chunk_test))
