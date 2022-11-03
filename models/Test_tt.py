# Test generators
import itertools, string

# Dict to hold values
test_dict = {x:[str(100*x + 5*k) for k in range(10)] for x in range(1, 10)}

def yield_gen(key):
    yield from test_dict[key]

# y = yield_gen(1)

# print(next(y))
# print(next(y))

# v = yield_gen(6)
# print(next(v))
# print(next(v))


# for ID, k in enumerate(itertools.cycle(v)):
#     if ID > 1000:
#         break
#     print(k)


def check_yield(key):
    b = yield_gen(key)
    print(next(b))
    print(next(b))


# check_yield(1)
# print()
# check_yield(2)
# print()
# check_yield(3)
# print()
# check_yield(1)

# g = (x for x in range(200))
# print(g)
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))

def wrapper_function(original_function):
    def inner_function():
        print("Inner function says hi")
        original_function()
    return inner_function



# d = wrapper_function(test_func)
# print(d())

def big_wrapper(original_function):
    def inner():
        print("Outside wrapper says hi")
        original_function()
    return inner

@big_wrapper
@wrapper_function
def test_func():
    print("My test function!!!")

# print(test_func())


def base_up(num, base):

    ans = []
    while num > 0:
        num, rem = divmod(num, base)
        ans.insert(0, rem)
    return tuple(ans)


def stringify(num):
    in_tuple = base_up(num, 27)

    return "".join([string.ascii_uppercase[k-1] for k in in_tuple])



print(base_up(1000,2))

for k in range(1, 300):
    print(stringify(k))





