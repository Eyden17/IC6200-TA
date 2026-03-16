from csv_reader import read_matrix_from_csv
from utils import actions, Node, build_path, is_in_frontier

maze = read_matrix_from_csv()

start = (0, 1)
goal = (1, 0)

final_path = []

def solve(maze, start, goal, algo="dfs"):
    frontier = [Node(start)]
    visited = []

    while frontier:
        current_node = frontier.pop(0)
        current_pos = (current_node.x, current_node.y)
        
        if current_pos == goal:
            return build_path(current_node)
        
        possible_moves = actions(maze, current_pos)

        visited.append(current_pos)

        if algo.lower() == "dfs":
            frontier = [Node(move, current_node) for move in possible_moves if move not in visited and not is_in_frontier(move, frontier)] + frontier
        elif algo.lower() == "bfs":
            frontier += [Node(move, current_node) for move in possible_moves if move not in visited and not is_in_frontier(move, frontier)]

    return False

path = solve(maze, start, goal, algo="bfs")
print("Path found:", path)