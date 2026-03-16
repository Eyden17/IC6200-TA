import sys
sys.path.append('./Semana_3')

from csv_reader import read_matrix_from_csv
from utils import actions, Node, build_path, is_in_frontier

maze = read_matrix_from_csv()

start = (0, 7)
goal = (10, 0)

final_path = []

def manhattan_distance(pos_1, pos_2):
    return (abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1]))

def a_star_search(maze, start, goal):
    frontier = [Node(start)]
    visited = []

    # valor inicial
    frontier[0].cost = 0
    frontier[0].manhattan_distance = manhattan_distance(start, goal)
    frontier[0].total_cost = frontier[0].manhattan_distance + frontier[0].cost

    while frontier:

        frontier.sort(key=lambda x: x.total_cost)

        current_node = frontier.pop(0)
        current_pos = (current_node.x, current_node.y)

        if current_pos == goal:
            return build_path(current_node)
        
        possible_moves = actions(maze, current_pos)
        visited.append(current_pos)

        for move in possible_moves:
            if move in visited:
                continue

            cur_cost = current_node.cost + 1
            cur_manhattan_distance = manhattan_distance(move, goal)
            cur_total_cost = cur_cost + cur_manhattan_distance

            existing_node = is_in_frontier(move, frontier)
            if not existing_node:
                node = Node(move, current_node)
                node.cost = cur_cost
                node.manhattan_distance = cur_manhattan_distance
                node.total_cost = cur_total_cost
                frontier.append(node)
            else:
                if cur_total_cost < existing_node.total_cost:
                    existing_node.parent = current_node
                    existing_node.cost = cur_cost
                    existing_node.manhattan_distance = cur_manhattan_distance
                    existing_node.total_cost = cur_total_cost
    return False

def greedy_search(maze, start, goal): 
    frontier = [Node(start)] 
    visited = [] 
    while frontier: 
        current_node = frontier.pop(0) 
        current_pos = (current_node.x, current_node.y) 
        
        if current_pos == goal: 
            return build_path(current_node) 
        possible_moves = actions(maze, current_pos) 
        visited.append(current_pos) 
        for move in possible_moves: 
            if move not in visited and not is_in_frontier(move, frontier): 
                node = Node(move, current_node) 
                node.manhattan_distance = manhattan_distance(move, goal) 
                frontier.append(node) 
                frontier.sort(key=lambda x: x.manhattan_distance) 
    return False

path = a_star_search(maze, start, goal)
print("A* Path found:", path)

path = greedy_search(maze, start, goal)
print("Greedy Path found:", path)