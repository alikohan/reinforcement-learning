import math
import parameters
import time

number_of_rows = parameters.number_of_rows
table_size = parameters.table_size


def distance_between(first, second):
    return math.sqrt(abs(first.index[0] - second.index[0]) ** 2 + abs(first.index[1] - second.index[1]) ** 2)

def get_position_with_index(index, mode='turtle'): # because coordinates in 'turtle' module is differente from coordinates in 'tkinter' module
    coordinates = [0, 0]
    center = number_of_rows // 2 + 1

    coordinates[0] = (index[0] - center) * table_size * 2 # x coordinate
    coordinates[1] = (index[1] - center) * table_size * 2 # y coordinate

    if mode == 'tkinter':
        coordinates[1] = - coordinates[1]

    return coordinates

def get_front_square_index(object):
    front_square_index = []
    if object.heading() == 0 : front_square_index = [object.index[0] + 1, object.index[1]]
    elif object.heading() == 90 : front_square_index = [object.index[0], object.index[1] + 1]
    elif object.heading() == 180 : front_square_index = [object.index[0] - 1, object.index[1]]
    elif object.heading() == 270 : front_square_index = [object.index[0], object.index[1] - 1]
    else : time.sleep(0.1)
    return front_square_index

def get_right_square_index(object):
    right_square_index = []
    if object.heading() == 0 : right_square_index = [object.index[0], object.index[1] - 1]
    elif object.heading() == 90 : right_square_index = [object.index[0] + 1, object.index[1]]
    elif object.heading() == 180 : right_square_index = [object.index[0], object.index[1] + 1]
    elif object.heading() == 270 : right_square_index = [object.index[0] - 1, object.index[1]]
    else : time.sleep(0.1)
    return right_square_index

def get_left_square_index(object):
    left_square_index = []
    if object.heading() == 0 : left_square_index = [object.index[0], object.index[1] + 1]
    elif object.heading() == 90 : left_square_index = [object.index[0] - 1, object.index[1]]
    elif object.heading() == 180 : left_square_index = [object.index[0], object.index[1] - 1]
    elif object.heading() == 270 : left_square_index = [object.index[0] + 1, object.index[1]]
    else : time.sleep(0.1)
    return left_square_index

def get_back_square_index(object):
    back_square_index = []
    if object.heading() == 0 : back_square_index = [object.index[0] - 1, object.index[1]]
    elif object.heading() == 90 : back_square_index = [object.index[0], object.index[1] - 1]
    elif object.heading() == 180 : back_square_index = [object.index[0] + 1, object.index[1]]
    elif object.heading() == 270 : back_square_index = [object.index[0], object.index[1] + 1]
    else : time.sleep(0.1)
    return back_square_index