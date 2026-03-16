
OBSTACLE = 1
PATH = 0

MOVE_UP = (0, -1)
MOVE_DOWN = (0, 1)
MOVE_LEFT = (-1, 0)
MOVE_RIGHT = (1, 0)

class Node:
    def __init__(self, pos, parent=None):
        self.x, self.y = pos
        self.parent = parent

        # For A* search
        self.manhattan_distance = 0
        self.cost = 0
        self.total_cost = 0


def build_path(node):
    path = []
    while node:
        path.append((node.x, node.y))
        node = node.parent
    return path[::-1]

def move(pos_1, pos_2):
    return tuple(x + y for x, y in zip(pos_1, pos_2))

def is_obstacle(maze, pos):
    x, y = pos
    return maze[y][x] == OBSTACLE

def is_valid_move(pos, width, height):
    x, y = pos
    return 0 <= x < width and 0 <= y < height

def is_in_frontier(pos, frontier):
    for node in frontier:
        if node.x == pos[0] and node.y == pos[1]:
            return node
    return False

def actions(maze, current_pos):
    width = len(maze[0])
    height = len(maze)

    up_move = move(current_pos, MOVE_UP)
    down_move = move(current_pos, MOVE_DOWN)
    left_move = move(current_pos, MOVE_LEFT)
    right_move = move(current_pos, MOVE_RIGHT)

    res = []

    for possible_move in [up_move, down_move, left_move, right_move]:
        if is_valid_move(possible_move, width, height) and not is_obstacle(maze, possible_move):
            res.append(possible_move)
    
    return res

