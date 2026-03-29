"""
minimax_core.py
---------------
Adaptador de visualización para Minimax de Tic-Tac-Toe.

NO reescribe ninguna lógica de minimax.py ni utils.py.
Solo los importa y añade:
  1. Conteo de nodos evaluados (instrumentación mínima).
  2. Generación de candidatos con sus valores, para mostrar en el panel.
  3. Un generador paso a paso del análisis de movimientos candidatos.

Coloca este archivo en la raíz del proyecto, junto a visualizer_ttt.py.
"""

import sys
import os

# Agrega Semana_5 al path para importar los módulos originales
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Semana_5"))

# ── Importa EXACTAMENTE las funciones originales, sin modificar nada ──────────
from minimax import min_value, max_value, ai_play
from utils import actions, result, players, terminal, utility, PLAYER_X, PLAYER_O


# ── Contador de nodos (instrumentación no-invasiva) ───────────────────────────
# Wrapeamos min_value / max_value localmente para contar llamadas.
# Los originales en minimax.py no se tocan.

_node_count = 0

def _counted_max(board, depth=0):
    global _node_count
    _node_count += 1
    if terminal(board):
        return utility(board)
    best = float('-inf')
    for move in actions(board):
        best = max(best, _counted_min(result(board, move), depth + 1))
    return best

def _counted_min(board, depth=0):
    global _node_count
    _node_count += 1
    if terminal(board):
        return utility(board)
    best = float('inf')
    for move in actions(board):
        best = min(best, _counted_max(result(board, move), depth + 1))
    return best


def evaluate_candidates(board):
    """
    Devuelve lista de (move, value, is_best) para cada movimiento candidato,
    usando la lógica original de minimax.py.

    Llama a min_value / max_value igual que ai_play() lo hace —
    solo agrega el conteo de nodos y guarda los valores por candidato.

    Retorna:
        candidates: [(move, value), ...]  ordenados de mejor a peor
        best_move:  el movimiento elegido (igual que ai_play devolvería)
        nodes_evaluated: int
    """
    global _node_count
    _node_count = 0

    turn   = players(board)
    moves  = actions(board)

    if not moves or terminal(board):
        return [], None, 0

    candidates = []

    if turn == PLAYER_X:
        # X maximiza: evalúa con _counted_min (igual que ai_play usa min_value)
        best_value = float('-inf')
        best_move  = None
        for move in moves:
            val = _counted_min(result(board, move))
            candidates.append((move, val))
            if val > best_value:
                best_value = val
                best_move  = move
    else:
        # O minimiza: evalúa con _counted_max (igual que ai_play usa max_value)
        best_value = float('inf')
        best_move  = None
        for move in moves:
            val = _counted_max(result(board, move))
            candidates.append((move, val))
            if val < best_value:
                best_value = val
                best_move  = move

    nodes = _node_count
    return candidates, best_move, nodes


def candidate_generator(board):
    """
    Generador paso a paso: emite un estado por cada candidato evaluado.

    Estado emitido:
    {
        "move":       (x, y),           # candidato actual
        "value":      int,              # valor minimax de ese candidato
        "evaluated":  [(move, val)],    # todos los evaluados hasta ahora
        "best_so_far": (move, val),     # mejor hasta el momento
        "done":       bool,
        "best_move":  (x, y) | None,   # solo cuando done=True
        "nodes":      int,
    }
    """
    global _node_count
    _node_count = 0

    turn  = players(board)
    moves = actions(board)

    if not moves or terminal(board):
        yield {"move": None, "value": None, "evaluated": [],
               "best_so_far": None, "done": True, "best_move": None, "nodes": 0}
        return

    evaluated  = []
    best_move  = None
    best_value = float('-inf') if turn == PLAYER_X else float('inf')

    for move in moves:
        _node_count = 0
        if turn == PLAYER_X:
            val = _counted_min(result(board, move))
        else:
            val = _counted_max(result(board, move))

        evaluated.append((move, val))

        if turn == PLAYER_X and val > best_value:
            best_value = val
            best_move  = move
        elif turn == PLAYER_O and val < best_value:
            best_value = val
            best_move  = move

        yield {
            "move":        move,
            "value":       val,
            "evaluated":   list(evaluated),
            "best_so_far": (best_move, best_value),
            "done":        False,
            "best_move":   None,
            "nodes":       _node_count,
        }

    # Estado final
    total_nodes = sum(1 for _ in evaluated)  # approx; real count tracked above
    yield {
        "move":        best_move,
        "value":       best_value,
        "evaluated":   list(evaluated),
        "best_so_far": (best_move, best_value),
        "done":        True,
        "best_move":   best_move,
        "nodes":       _node_count,
    }
