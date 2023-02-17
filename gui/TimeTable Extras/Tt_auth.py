import string, random


def generate_key(def_length=25):
    alphabet = [x  for x in string.ascii_letters]
    number_pool = [str(x) for x in range(10)]
    chunk_width = 5
    key = ""

    while len(key) <= def_length:
        if len(key) % chunk_width == 0 and len(key) != 0:
            key += "-"

        char = random.choice(alphabet + number_pool)
        key += char

    return key

def check():
    check = sum([ord(x) for x in "Olu'tomilayo"])

    return check

print(check())

for _ in range(500):
    print(generate_key(25))