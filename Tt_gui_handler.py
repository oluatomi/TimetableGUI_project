# - ************************************************************************

# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.

# -- All rights (whichever they might be) reserved!

# **************************************************************************

from PyQt5 import QtCore, QtGui, QtWidgets
import sys


def load_manual():
    with open('TimeTable Extras/Time_table.html', 'r', encoding="UTF-8") as file:
        contents = file.readlines()

    # print(contents)
    content_dict={}

    for line_num,line in enumerate(contents):
        if "TOPIC" in line:
            topic_num = line_num
            topic = line.strip("\n")
            continue
        if line_num == topic_num + 1:
            topic = line.strip("\n")
            content_dict[topic] = """"""
        else:
            content_dict[topic] += line

    return content_dict
        
if __name__ == "__main__":
    r = load_manual()
    print(r)
