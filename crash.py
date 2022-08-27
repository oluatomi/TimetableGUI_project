import Tt_algo_calc
import random


moved = Tt_algo_calc.Moveover([[0, 1], [0, 1]], 10)

def gen_chunks():

    m = random.randint(0,9)

    a = [[m+i for i in range(random.randint(1, 4))] for _ in range(random.randint(1, 5))]

    ans = []
    for x in a:
        if len(x) == 1:
            ans.append(x[0])
        else:
            ans.append(x)

    return ans


for _ in range(100):
    b = gen_chunks()
    print("-"*40)
    # print(b)
    b = [[[1, 2], 3, [1, 2]]]
    try:
        print(Tt_algo_calc.Moveover(b, 10))
    except ValueError as e:
        print(e)
    except StopIteration as f:
        print(f"Gen_chunks:{b} ---- {f}")
