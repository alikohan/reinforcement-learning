import common_instructions as comins
import parameters

number_of_rows = parameters.number_of_rows
table_size = parameters.table_size
movement_speed = parameters.movement_speed

obstacles_index = parameters.obstacles_index
initial_tiles_index = parameters.initial_tiles_index
initial_holes_index = parameters.initial_holes_index


# ------------- JUDGEMENT -------------

def what_exists_front(agent, agents, tiles, holes): # CF
    front_square_index = comins.get_front_square_index(agent)
    for age in agents:
        if front_square_index == age.index:
            return 0 # agent
    for tile in tiles:
        if front_square_index == tile.index:
            return 1 # tile
    for hole in holes:
        if front_square_index == hole.index:
            return 2 # hole
    return 3 # if nothing exist

def what_exists_right(agent, agents, tiles, holes): # CR
    right_square_index = comins.get_right_square_index(agent)
    for age in agents:
        if right_square_index == age.index:
            return 0 # agent
    for tile in tiles:
        if right_square_index == tile.index:
            return 1 # tile
    for hole in holes:
        if right_square_index == hole.index:
            return 2 # hole
    return 3 # if nothing exist

def what_exists_left(agent, agents, tiles, holes): # CL
    left_square_index = comins.get_left_square_index(agent)
    for age in agents:
        if left_square_index == age.index:
            return 0 # agent
    for tile in tiles:
        if left_square_index == tile.index:
            return 1 # tile
    for hole in holes:
        if left_square_index == hole.index:
            return 2 # hole
    return 3 # if nothing exist

def what_exists_back(agent, agents, tiles, holes): # CB
    back_square_index = comins.get_back_square_index(agent)
    for age in agents:
        if back_square_index == age.index:
            return 0 # agent
    for tile in tiles:
        if back_square_index == tile.index:
            return 1 # tile
    for hole in holes:
        if back_square_index == hole.index:
            return 2 # hole
    return 3 # if nothing exist
    

# return values :
# forward = 0
# right = 1
# left = 2
# backward = 3
def find_direction(agent, obj): # calculate position of object than agent and return which direction should agent choose to arrive to object
    x_distance = obj.index[0] - agent.index[0]
    y_distance = obj.index[1] - agent.index[1]
    if agent.heading() == 0:
        if abs(x_distance) >= abs(y_distance):
            if x_distance > 0:
                return 0 # forward
            if x_distance < 0:
                return 3 # backward    
        else:
            if y_distance > 0:
                return 2 # left
            if y_distance < 0:
                return 1 # right
    if agent.heading() == 90:
        if abs(x_distance) > abs(y_distance):
            if x_distance > 0:
                return 1 # right
            if x_distance < 0:
                return 2 # left    
        else:
            if y_distance > 0:
                return 0 # forward
            if y_distance < 0:
                return 3 # backward
    if agent.heading() == 180:
        if abs(x_distance) >= abs(y_distance):
            if x_distance > 0:
                return 3 # backward
            if x_distance < 0:
                return 1 #forward
        else:
            if y_distance > 0:
                return 1 #right
            if y_distance < 0:
                return 2 # left
    if agent.heading() == 270:
        if abs(x_distance) > abs(y_distance):
            if x_distance > 0:
                return 2 # left
            if x_distance < 0:
                return 1 # right
        else:
            if y_distance > 0:
                return 3 # backward
            if y_distance < 0:
                return 0 # forward


def nearest_tile_direction(agent, not_use1, tiles, not_use2): # NTD
    distances = []
    for tile in tiles:
        distances.append(comins.distance_between(agent, tile))
    return find_direction(agent, tiles[distances.index(min(distances))])

def second_nearest_tile_direction(agent, not_use1, tiles, not_use2): # SNT
    distances = []
    for tile in tiles:
        distances.append(comins.distance_between(agent, tile))
    distances_forsort = distances.copy()
    distances_forsort.sort()
    return find_direction(agent, tiles[distances.index(distances_forsort[1])])

def nearest_hole_direction(agent, not_use1, not_use2, holes): # NHD
    distances = []
    for hole in holes:
        distances.append(comins.distance_between(agent, hole))
    return find_direction(agent, holes[distances.index(min(distances))])


# ------------- PROCESSING -------------

def check_outting(index):
    """for check agent or tile doesn't outting from table"""
    if index[0] > number_of_rows or index[0] < 1 or index[1] > number_of_rows or index[1] < 1:
        return True
    return False

def check_overlapping(agent, agents, tiles, holes):
    """check elements don't be overlapping (except overlapping between tiles and holes)"""
    front_square_index = comins.get_front_square_index(agent)
    for obstacle_index in obstacles_index:
        if obstacle_index == front_square_index:
            return True
    for age in agents:
        if age.index == front_square_index:
            return True
    for hole in holes:
        if hole.index == front_square_index:
            return True
    for tile in tiles:
        if tile.index == front_square_index:
            tile.setheading(agent.heading())
            while tile.heading() != agent.heading(): # because it takes time
                tile.setheading(agent.heading())

            # -----------------------------------------------------------------------------------------------------------
            # if check_outting(comins.get_front_square_index(tile)) == True:
            #     return True

            for t in tiles:
                if comins.get_front_square_index(tile) == t.index:
                    t.setheading(tile.heading())
                    while t.heading() != tile.heading(): # because it takes time
                        t.setheading(tile.heading())
                    return tile, t, True
            for hole in holes:
                if comins.get_front_square_index(tile) == hole.index:
                    return tile, hole, False
            for agent in agents:
                if comins.get_front_square_index(tile) == agent.index:
                    return True
            for obstacle_index in obstacles_index:
                if comins.get_front_square_index(tile) == obstacle_index:
                    return True
            return tile
    return False

def move_forward(agent, agents, tiles, holes): # MF
    candidate_index = comins.get_front_square_index(agent)
    if check_outting(candidate_index):
        return
    elif check_overlapping(agent, agents, tiles, holes) == False:
        agent.index = candidate_index
        agent.goto(comins.get_position_with_index(agent.index))
    elif type(check_overlapping(agent, agents, tiles, holes)) == type(()) and not check_overlapping(agent, agents, tiles, holes)[2]: # return tile and hole as tuple
        tile, hole, not_use = check_overlapping(agent, agents, tiles, holes)
        tile.index = comins.get_front_square_index(tile)
        tile.goto(comins.get_position_with_index(tile.index))
        tile.color("green")
        agent.index = candidate_index
        agent.goto(comins.get_position_with_index(agent.index))
    elif type(check_overlapping(agent, agents, tiles, holes)) == type(()) and check_overlapping(agent, agents, tiles, holes)[2]: # return two tile as tuple
        tile, tile2, not_use = check_overlapping(agent, agents, tiles, holes)
        if not check_overlapping(tile, agents, tiles, holes) == True:
            move_forward(tile, agents, tiles, holes)
            # tile.index = comins.get_front_square_index(tile)
            agent.index = candidate_index
            agent.goto(comins.get_position_with_index(agent.index))
    elif type(check_overlapping(agent, agents, tiles, holes)) == type(agent):
        tile = check_overlapping(agent, agents, tiles, holes)
        tile.index = comins.get_front_square_index(tile)
        tile.goto(comins.get_position_with_index(tile.index))
        agent.index = candidate_index
        agent.goto(comins.get_position_with_index(agent.index))


def turn_right(agent, not_use1, not_use2, not_use3): # TR
    agent.right(90)

def turn_left(agent, not_use1, not_use2, not_use3): # TL
    agent.left(90)

def stay(not_use1, not_use2, not_use3, not_use4): # ST
    pass
