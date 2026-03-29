import math
from utils import utility, terminal, result, actions, players, PLAYER_X


# Rule of play
# X always plays first


def min_value(board):
    """
    Choose the action a in actions(s) that minimizes max - value(result(s, a))
    """
    if terminal(board):
        return utility(board)
    
    moves = actions(board)
    best_value = math.inf

    for move in moves:

        best_value = min(best_value, max_value(result(board, move)))
        
    return best_value

def max_value(board):
    """
    Choose the action a in actions(s) that maximizes min - value(result(s, a))
    """
    if terminal(board):
        return utility(board)
    
    moves = actions(board)
    best_value = -math.inf

    for move in moves:
        best_value = max(best_value, min_value(result(board, move)))
        
    return best_value

def ai_play(board):
    turn = players(board)
    moves = actions(board)

    if turn == PLAYER_X:
        best_value = -math.inf
        best_move = None

        for move in moves:
            value = min_value(result(board, move))
            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    else:
        best_value = math.inf
        best_move = None

        for move in moves:
            value = max_value(result(board, move))
            if value < best_value:
                best_value = value
                best_move = move

        return best_move
