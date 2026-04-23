import copy


PLAYER_X = "X"
PLAYER_O = "O"


def is_free_to_mark(board, movement):
    return board[movement[1]][movement[0]] is None

def players(board):
    count = 0
    for i in board:
        for j in i:
            if j != None:
                count += 1
    if count == 0 or count % 2 == 0:
        return PLAYER_X
    else:
        return PLAYER_O

def actions(board):
    possible_moves = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if is_free_to_mark(board, (j,i)):
                possible_moves.append((j,i))
    return possible_moves

def result(board, action):

    if not is_free_to_mark(board, action): 
        return

    next_player = players(board)

    new_board = copy.deepcopy(board)
    new_board[action[1]][action[0]] = next_player
    return new_board

def get_winner(board):
    diagonals = []
    anti_diagonals = []
    vertical_winners = list(zip(board[0], board[1], board[2]))

    for i in range(len(board)):
        diagonals.append(board[i][i])
        anti_diagonals.append(board[i][-i - 1])

        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != None:
            return board[i][0]
        if vertical_winners[i][0] == vertical_winners[i][1] == vertical_winners[i][2] and vertical_winners[i][0] != None:
            return vertical_winners[i][0]

    if diagonals.count(PLAYER_X) == 3 or anti_diagonals.count(PLAYER_X) == 3:
        return PLAYER_X
    if diagonals.count(PLAYER_O) == 3 or anti_diagonals.count(PLAYER_O) == 3:
        return PLAYER_O

    return None

def is_board_full(board):
    for i in board:
        if None in i:
            return False
    return True

def terminal(board):
    if get_winner(board):
        return True
    
    return is_board_full(board)

def utility(board):
    """
    Final numeric value for terminal state s
    """

    if (terminal(board)):
        winner = get_winner(board)
        if winner == PLAYER_X:
            return 1
        elif winner == PLAYER_O:
            return -1
    return 0