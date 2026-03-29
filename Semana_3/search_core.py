"""
search_core.py
--------------
Adaptadores de visualización para los algoritmos de búsqueda.

NO reimplementa ninguna lógica. Importa las funciones originales del
proyecto (Node, build_path, actions, is_in_frontier) y las envuelve en
generadores (yield) para exponer estados intermedios paso a paso.

Coloca este archivo en la raíz del proyecto, junto a matrix.csv.
"""

import sys
import os

# Agrega Semana_3 al path igual que lo hace a_star.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Semana_3"))

# Importa EXACTAMENTE las funciones que ya existen en el proyecto
from utils import Node, build_path, actions, is_in_frontier


# ── Helper: extrae posiciones de la frontera (lista de Nodes) ────────────────
def _frontier_pos(frontier):
    return [(n.x, n.y) for n in frontier]


# ── Formato de estado emitido en cada yield ───────────────────────────────────
# {
#   "current":  (x, y) | None,
#   "frontier": [(x, y), ...],
#   "visited":  [(x, y), ...],
#   "path":     [(x, y), ...] | None,   # solo cuando se encontró meta
#   "done":     bool,
#   "found":    bool,
# }


# ── DFS ───────────────────────────────────────────────────────────────────────
def dfs_generator(maze, start, goal):
    """
    Replica exacta del solve(..., algo="dfs") de search.py,
    convertida en generador para visualización paso a paso.
    """
    frontier = [Node(start)]
    visited  = []

    while frontier:
        current_node = frontier.pop(0)
        current_pos  = (current_node.x, current_node.y)

        if current_pos == goal:
            path = build_path(current_node)
            yield {"current": current_pos, "frontier": _frontier_pos(frontier),
                   "visited": list(visited), "path": path, "done": True, "found": True}
            return

        possible_moves = actions(maze, current_pos)
        visited.append(current_pos)

        # DFS: nuevos nodos al FRENTE (igual que search.py)
        frontier = [Node(m, current_node)
                    for m in possible_moves
                    if m not in visited and not is_in_frontier(m, frontier)] + frontier

        yield {"current": current_pos, "frontier": _frontier_pos(frontier),
               "visited": list(visited), "path": None, "done": False, "found": False}

    yield {"current": None, "frontier": [], "visited": list(visited),
           "path": None, "done": True, "found": False}


# ── BFS ───────────────────────────────────────────────────────────────────────
def bfs_generator(maze, start, goal):
    """
    Replica exacta del solve(..., algo="bfs") de search.py,
    convertida en generador para visualización paso a paso.
    """
    frontier = [Node(start)]
    visited  = []

    while frontier:
        current_node = frontier.pop(0)
        current_pos  = (current_node.x, current_node.y)

        if current_pos == goal:
            path = build_path(current_node)
            yield {"current": current_pos, "frontier": _frontier_pos(frontier),
                   "visited": list(visited), "path": path, "done": True, "found": True}
            return

        possible_moves = actions(maze, current_pos)
        visited.append(current_pos)

        # BFS: nuevos nodos al FINAL (igual que search.py)
        frontier += [Node(m, current_node)
                     for m in possible_moves
                     if m not in visited and not is_in_frontier(m, frontier)]

        yield {"current": current_pos, "frontier": _frontier_pos(frontier),
               "visited": list(visited), "path": None, "done": False, "found": False}

    yield {"current": None, "frontier": [], "visited": list(visited),
           "path": None, "done": True, "found": False}


# ── A* ────────────────────────────────────────────────────────────────────────
def astar_generator(maze, start, goal):
    """
    Replica exacta de a_star_search() de a_star.py,
    convertida en generador para visualización paso a paso.
    """
    def manhattan_distance(pos_1, pos_2):
        return abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1])

    frontier = [Node(start)]
    visited  = []

    frontier[0].cost               = 0
    frontier[0].manhattan_distance = manhattan_distance(start, goal)
    frontier[0].total_cost         = frontier[0].manhattan_distance + frontier[0].cost

    while frontier:
        frontier.sort(key=lambda x: x.total_cost)
        current_node = frontier.pop(0)
        current_pos  = (current_node.x, current_node.y)

        if current_pos == goal:
            path = build_path(current_node)
            yield {"current": current_pos, "frontier": _frontier_pos(frontier),
                   "visited": list(visited), "path": path, "done": True, "found": True}
            return

        possible_moves = actions(maze, current_pos)
        visited.append(current_pos)

        for move in possible_moves:
            if move in visited:
                continue

            cur_cost               = current_node.cost + 1
            cur_manhattan_distance = manhattan_distance(move, goal)
            cur_total_cost         = cur_cost + cur_manhattan_distance

            existing_node = is_in_frontier(move, frontier)
            if not existing_node:
                node = Node(move, current_node)
                node.cost               = cur_cost
                node.manhattan_distance = cur_manhattan_distance
                node.total_cost         = cur_total_cost
                frontier.append(node)
            else:
                if cur_total_cost < existing_node.total_cost:
                    existing_node.parent             = current_node
                    existing_node.cost               = cur_cost
                    existing_node.manhattan_distance = cur_manhattan_distance
                    existing_node.total_cost         = cur_total_cost

        yield {"current": current_pos, "frontier": _frontier_pos(frontier),
               "visited": list(visited), "path": None, "done": False, "found": False}

    yield {"current": None, "frontier": [], "visited": list(visited),
           "path": None, "done": True, "found": False}


# ── Greedy ────────────────────────────────────────────────────────────────────
def greedy_generator(maze, start, goal):
    """
    Replica exacta de greedy_search() de a_star.py,
    convertida en generador para visualización paso a paso.
    """
    def manhattan_distance(pos_1, pos_2):
        return abs(pos_1[0] - pos_2[0]) + abs(pos_1[1] - pos_2[1])

    frontier = [Node(start)]
    visited  = []

    while frontier:
        current_node = frontier.pop(0)
        current_pos  = (current_node.x, current_node.y)

        if current_pos == goal:
            path = build_path(current_node)
            yield {"current": current_pos, "frontier": _frontier_pos(frontier),
                   "visited": list(visited), "path": path, "done": True, "found": True}
            return

        possible_moves = actions(maze, current_pos)
        visited.append(current_pos)

        for move in possible_moves:
            if move not in visited and not is_in_frontier(move, frontier):
                node = Node(move, current_node)
                node.manhattan_distance = manhattan_distance(move, goal)
                frontier.append(node)
                frontier.sort(key=lambda x: x.manhattan_distance)

        yield {"current": current_pos, "frontier": _frontier_pos(frontier),
               "visited": list(visited), "path": None, "done": False, "found": False}

    yield {"current": None, "frontier": [], "visited": list(visited),
           "path": None, "done": True, "found": False}


# ── Registro de algoritmos disponibles ───────────────────────────────────────
ALGORITHMS = {
    "DFS":    dfs_generator,
    "BFS":    bfs_generator,
    "A*":     astar_generator,
    "Greedy": greedy_generator,
}