import common_instructions as comins
import tile_world_instructions as tileins
import parameters
import turtle
import tkinter as tk
import threading
import time
import copy
import random
import queue

# --- UI ---
number_of_rows = parameters.number_of_rows
table_size = parameters.table_size
table_color = parameters.table_color
table_outside_color = parameters.table_outside_color
movement_speed = parameters.movement_speed
interval_between_each_step_in_run_best_policy = parameters.interval_between_each_step_in_run_best_policy
should_display_state_labels = parameters.should_display_state_labels

obstacles_index = parameters.obstacles_index
initial_tiles_index = parameters.initial_tiles_index
initial_holes_index = parameters.initial_holes_index
initial_agents_index = parameters.initial_agents_index

# --- RL ---
gamma = parameters.gamma
noise = parameters.noise # noise = 0 means environment is deterministic
iteration = parameters.iteration
arrow_length = parameters.arrow_length # for display policy
arrow_width = parameters.arrow_width
iteration_interval = parameters.iteration_interval # interval between each iteration (in seconds)
rewards = parameters.rewards
should_run_test = parameters.should_run_test

# variables
value_functions = parameters.initial_value_functions
directions = copy.deepcopy(value_functions) # best action for of each state
not_free_spaces_index = obstacles_index + initial_tiles_index + initial_holes_index # spaces that not need to calculate value functions

# ---------------------------------- table display functions ----------------------------------

def drawTable(canvas, size, number_of_rows):
    canvas.create_line(-size, -size, size, -size)
    canvas.create_line(-size, -size, -size, size)
    canvas.create_line(size, size, size, -size)
    canvas.create_line(size, size, -size, size)

    for number_of_rows in range(3, number_of_rows+1, 2):
        canvas.create_line(-size, -size, -size*number_of_rows, -size)
        canvas.create_line(-size, -size, -size, -size*number_of_rows)
        
        canvas.create_line(size, -size, size*number_of_rows, -size)
        canvas.create_line(size, -size, size, -size*number_of_rows)
        
        canvas.create_line(size, size, size*number_of_rows, size)
        canvas.create_line(size, size, size, size*number_of_rows)

        canvas.create_line(-size, size, -size*number_of_rows, size)
        canvas.create_line(-size, size, -size, size*number_of_rows)

        canvas.create_line(-size*number_of_rows*10, -size*number_of_rows, size*number_of_rows*10, -size*number_of_rows)
        canvas.create_line(-size*number_of_rows, -size*number_of_rows*10, -size*number_of_rows, size*number_of_rows*10)
        canvas.create_line(size*number_of_rows, size*number_of_rows*10, size*number_of_rows, -size*number_of_rows*10)
        canvas.create_line(size*number_of_rows*10, size*number_of_rows, -size*number_of_rows*10, size*number_of_rows)
    # clear outside lines
    canvas.create_rectangle(-size*number_of_rows*10 , -size*number_of_rows*10, size*number_of_rows*10, -size*number_of_rows-1, fill=table_outside_color, outline=table_outside_color)
    canvas.create_rectangle(-size*number_of_rows*10 , -size*number_of_rows*10, -size*number_of_rows-1, size*number_of_rows*10, fill=table_outside_color, outline=table_outside_color)
    canvas.create_rectangle(size*number_of_rows*10 , size*number_of_rows*10, size*number_of_rows+1, -size*number_of_rows*10, fill=table_outside_color, outline=table_outside_color)
    canvas.create_rectangle(size*number_of_rows*10 , size*number_of_rows*10, -size*number_of_rows*10, size*number_of_rows+1, fill=table_outside_color, outline=table_outside_color)


def fillTable(obstacles_index, tiles_index, holes_index, agents_index):
    tiles = []
    holes = []
    agents = []
    for obstacleIndex in obstacles_index:
        obstacle = turtle.Turtle(shape='square')
        obstacle.speed(movement_speed)
        obstacle.penup()
        obstacle.turtlesize(table_size / 10)
        position = comins.get_position_with_index(obstacleIndex)
        obstacle.goto(position[0], position[1])
    for tileIndex in tiles_index:
        tile = turtle.Turtle(shape='square')
        tile.speed(movement_speed)
        tile.penup()
        tile.turtlesize(table_size / 15)
        tile.color('orange')
        position = comins.get_position_with_index(tileIndex)
        tile.goto(position[0], position[1])
        tile.index = tileIndex
        tiles.append(tile)
    for holeIndex in holes_index:
        hole = turtle.Turtle(shape='square')
        hole.speed(movement_speed)
        hole.penup()
        hole.turtlesize(table_size / 15)
        hole.color('yellow')
        position = comins.get_position_with_index(holeIndex)
        hole.goto(position[0], position[1])
        hole.index = holeIndex
        holes.append(hole)
    for agentIndex in agents_index:
        agent = turtle.Turtle(shape='turtle')
        agent.speed(movement_speed)
        agent.penup()
        agent.turtlesize(table_size / 15)
        agent.color('red')
        position = comins.get_position_with_index(agentIndex)
        agent.goto(position[0], position[1])
        agent.index = agentIndex
        agents.append(agent)
    return tiles, holes, agents


# ---------------------------------- test functions ----------------------------------

def run_test(agent): # for test
    time.sleep(5)
    tileins.turn_left(agent, agents, tiles, holes)
    tileins.turn_left(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.turn_right(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.turn_right(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.turn_left(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.turn_right(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)
    tileins.move_forward(agent, agents, tiles, holes)


# ---------------------------------- RL ----------------------------------

def is_wall(x, y):
    if x >= number_of_rows or y >= number_of_rows or x < 0 or y < 0:
        return True
    else:
        return False


def get_action_value(value_functions, rewards, x, y):
    right, up, left, down = None, None, None, None
    right = rewards[x][y] + gamma * (value_functions[x + 1][y] if (not is_wall(x + 1, y) and [x + 2, y + 1] not in obstacles_index) else value_functions[x][y])
    up = rewards[x][y] + gamma * (value_functions[x][y + 1] if (not is_wall(x + 1, y + 1) and [x + 1, y + 2] not in obstacles_index) else value_functions[x][y])
    left = rewards[x][y] + gamma * (value_functions[x - 1][y] if (not is_wall(x - 1, y) and [x, y + 1] not in obstacles_index)else value_functions[x][y])
    down = rewards[x][y] + gamma * (value_functions[x][y - 1] if (not is_wall(x, y - 1) and [x + 1, y] not in obstacles_index) else value_functions[x][y])
    return right, up, left, down


def update_each_value_function(value_functions, value_functions_new, rewards, x, y):
    right, up, left, down = get_action_value(value_functions, rewards, x, y)
    value_functions_new[x][y] = (1 - noise) * max([i for i in [right, up, left, down] if i is not None])


def update_value_functions(value_functions, rewards):
        value_functions_new = copy.deepcopy(value_functions)
        for x in range(number_of_rows):
            for y in range(number_of_rows):
                if [x + 1, y + 1] not in not_free_spaces_index: # obstacles_index or not_free_spaces_index
                        update_each_value_function(value_functions, value_functions_new, rewards, x, y)
        value_functions = copy.deepcopy(value_functions_new)
        return value_functions
    

def get_highest_value_function(value_functions, rewards, x, y):
    right, up, left, down = get_action_value(value_functions, rewards, x, y)
    not_None_values = [i for i in [right, up, left, down] if i is not None]
    return [i for i, j in enumerate([right, up, left, down]) if j == max(not_None_values)]


def greedy_policy(value_functions, directions, queue_ui):
    value_functions = queue_ui.get()
    directions_passive = copy.deepcopy(directions)
    for x in range(number_of_rows):
        for y in range(number_of_rows):
            if [x + 1, y + 1] not in not_free_spaces_index:
                directions_passive[x][y] = get_highest_value_function(value_functions, rewards, x, y)
                directions[x][y] = directions_passive[x][y][0]
                position = comins.get_position_with_index((x + 1, y + 1), 'tkinter')
                if 0 in directions_passive[x][y]: # right
                    canvas.create_line(position[0], position[1], position[0] + arrow_length, position[1], arrow=tk.LAST, fill='green', width=arrow_width)
                if 1 in directions_passive[x][y]: # up
                    canvas.create_line(position[0], position[1], position[0], position[1] - arrow_length, arrow=tk.LAST, fill='red', width=arrow_width)
                if 2 in directions_passive[x][y]: # left
                    canvas.create_line(position[0], position[1], position[0] - arrow_length, position[1], arrow=tk.LAST, fill='blue', width=arrow_width)
                if 3 in directions_passive[x][y]: # down
                    canvas.create_line(position[0], position[1], position[0], position[1] + arrow_length, arrow=tk.LAST, fill='black', width=arrow_width)
                time.sleep(0.1)
    return directions


def implement_noise(directions):
    direction = directions[agents[0].index[0] - 1][agents[0].index[1] - 1]
    if random.random() >= noise: # always True in determinstic environments
    # right -> 0 * 90 = 0 | up -> 1 * 90 = 90 | left -> 2 * 90 = 180 | down -> 3 * 90 = 270
        agents[0].setheading(direction * 90)
    else:
        possible_actions = [0, 1, 2, 3]
        possible_actions.remove(direction)
        agents[0].setheading(random.choice(possible_actions) * 90)


def run_best_policy(directions):
    target_index = tiles[0].index
    while comins.get_position_with_index(agents[0].index, 'tkinter') != comins.get_position_with_index(target_index, 'tkinter'):
        implement_noise(directions)
        time.sleep(interval_between_each_step_in_run_best_policy)
        tileins.move_forward(agents[0], agents, tiles, holes)
    tiles[0].hideturtle()
    agents[0].color('green')


def display_value_functions(value_functions, label_values):
    for i in range(number_of_rows):
        for j in range(number_of_rows):
            label_values[i][j].config(text=round(value_functions[i][j], 2))



def update_and_display_value_functions(value_functions, rewards, label_values, queue_ui, label_iteration):
    for i in range(iteration):
        time.sleep(iteration_interval)
        value_functions = update_value_functions(value_functions, rewards)
        if should_display_state_labels:
            display_value_functions(value_functions, label_values)
        label_iteration.config(text=i + 1)
    queue_ui.put(value_functions)


def onClick_update_value_functions(value_functions, rewards, label_values, queue_ui, label_iteration):
    threading.Thread(target=update_and_display_value_functions, args=(value_functions, rewards, label_values, queue_ui, label_iteration, )).start()

def onClick_display_policy(value_functions, directions, queue_ui):
    threading.Thread(target=greedy_policy, args=(value_functions, directions, queue_ui)).start()

def onClick_run_policy(directions):
    threading.Thread(target=run_best_policy, args=(directions, )).start()


# ---------------------------------- user interface ----------------------------------
def create_buttons(canvas, queue_ui):
    button = tk.Button(canvas.master, text='update value functions', command=lambda: onClick_update_value_functions(value_functions, rewards, label_values, queue_ui, label_iteration))
    canvas.create_window(parameters.button_position_width, parameters.button_position_height, window=button)

    button = tk.Button(canvas.master, text='display policy', command=lambda: onClick_display_policy(value_functions, directions, queue_ui))
    canvas.create_window(parameters.button_position_width, parameters.button_position_height + 50, window=button)

    button = tk.Button(canvas.master, text='run policy', command=lambda: onClick_run_policy(directions))
    canvas.create_window(parameters.button_position_width, parameters.button_position_height + 100, window=button)

def create_information_labels(canvas):
    label_iteration = tk.Label(canvas.master, text='', font=('Times', 15), bg=table_outside_color) # display iteration number
    canvas.create_window(parameters.label_position_width, parameters.label_position_height, window=label_iteration)
    return label_iteration

def create_state_labels(canvas):
    label_values = copy.deepcopy(value_functions)
    for i in range(number_of_rows):
        for j in range(number_of_rows):
            coordinates = comins.get_position_with_index([i + 1, j + 1], mode='tkinter')
            label_values[i][j] = tk.Label(canvas.master, text=round(value_functions[i][j], 2), font=('Times', table_size // 3), bg=table_color)
            canvas.create_window(coordinates[0], coordinates[1], window=label_values[i][j])
    return label_values

def create_canvas():
    screen = turtle.Screen()
    screen.bgcolor(table_color)
    screen.setup(width=0.6, height=0.8) # window size at launch time
    canvas = screen.getcanvas()
    return canvas

# ---------------------------------- Main ----------------------------------
if __name__ == '__main__':
    canvas = create_canvas()
    drawTable(canvas, table_size, number_of_rows)
    tiles, holes, agents = fillTable(obstacles_index, initial_tiles_index, initial_holes_index, initial_agents_index)
    label_iteration = create_information_labels(canvas)
    if should_display_state_labels:
        label_values = create_state_labels(canvas)
    queue_ui = queue.Queue()
    create_buttons(canvas, queue_ui)
    if should_run_test:
        threading.Thread(target=run_test, args=(agents[0], )).start()
    turtle.done()