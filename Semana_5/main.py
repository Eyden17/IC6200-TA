# import math
from minimax import ai_play
from utils import result

board = [
    ["X", "X", None],
    ["O", "O", None],
    ["X", "X", None],
]


def play():
    print("Play tic-tac-toe")

    move = ai_play(board)
    new_board = result(board, move)

    print(move)
    print(new_board)


play()
