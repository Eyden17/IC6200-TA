from utils import actions, is_free_to_mark, players, result, terminal, utility


def test_actions_empty_board():
    """Test: empty board - all 9 positions are valid movements"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    result = actions(board)

    assert len(result) == 9

    assert (0, 0) in result
    assert (0, 1) in result
    assert (0, 2) in result
    assert (1, 0) in result
    assert (1, 1) in result
    assert (1, 2) in result
    assert (2, 0) in result
    assert (2, 1) in result
    assert (2, 2) in result


def test_actions_no_possible_movements():
    """Test: full board - no available movements"""
    board = [
        ["X", "O", "X"],
        ["O", "X", "O"],
        ["X", "O", "X"],
    ]
    result = actions(board)

    assert len(result) == 0
    assert result == []


def test_actions_multiple_possible_movements():
    """Test: partial board - multiple available movements"""
    board = [
        ["X", None, "O"],
        [None, "X", None],
        ["O", None, "X"],
    ]
    result = actions(board)

    assert len(result) == 4
    assert (1, 0) in result
    assert (0, 1) in result
    assert (2, 1) in result
    assert (1, 2) in result


def test_is_free_to_mark_empty():
    """Test: position is free (None) - returns True"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]

    assert is_free_to_mark(board, (0, 0)) is True
    assert is_free_to_mark(board, (1, 1)) is True
    assert is_free_to_mark(board, (2, 2)) is True


def test_is_free_to_mark_occupied_x():
    """Test: position occupied by X - returns False"""
    board = [
        ["X", None, None],
        [None, "X", None],
        [None, None, "X"],
    ]

    assert is_free_to_mark(board, (0, 0)) is False
    assert is_free_to_mark(board, (1, 1)) is False
    assert is_free_to_mark(board, (2, 2)) is False


def test_is_free_to_mark_occupied_o():
    """Test: position occupied by O - returns False"""
    board = [
        ["O", None, None],
        [None, "O", None],
        [None, None, "O"],
    ]

    assert is_free_to_mark(board, (0, 0)) is False
    assert is_free_to_mark(board, (1, 1)) is False
    assert is_free_to_mark(board, (2, 2)) is False


def test_players_x_to_move():
    """Test: X has equal marks as O - X plays next"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]

    assert players(board) == "X"


def test_players_o_to_move():
    """Test: O has one less mark than X - O plays next"""
    board = [
        ["X", "O", "X"],
        [None, "X", None],
        [None, None, "O"],
    ]

    assert players(board) == "O"


def test_result_places_x():
    """Test: place X at position (0, 0)"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    new_board = result(board, (0, 0))

    assert new_board[0][0] == "X"


def test_result_places_o():
    """Test: place O at position (2, 2) - after X plays first"""
    board = [["X", None, None], [None, None, None], [None, None, None]]
    new_board = result(board, (2, 2))

    assert new_board[2][2] == "O"


def test_result_x_moves_first():
    """Test: on empty board, X moves first"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    new_board = result(board, (1, 1))

    assert new_board[1][1] == "X"


def test_result_o_moves_after_x():
    """Test: after X plays, O moves next"""
    board = [
        ["X", None, None],
        [None, None, None],
        [None, None, None],
    ]
    new_board = result(board, (1, 1))

    assert new_board[1][1] == "O"


def test_result_immutability():
    """Test: original board is not mutated"""
    board = [
        ["X", None, None],
        [None, "O", None],
        [None, None, None],
    ]
    new_board = result(board, (2, 2))

    assert board[2][2] is None
    assert new_board[2][2] == "X"


def test_result_various_positions():
    """Test: placing marks at different positions"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]

    new_board = result(board, (0, 0))
    assert new_board[0][0] == "X"

    new_board = result(new_board, (1, 1))
    assert new_board[1][1] == "O"

    new_board = result(new_board, (2, 2))
    assert new_board[2][2] == "X"


def test_result_partial_board():
    """Test: result on a board with existing marks"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]
    new_board = result(board, (2, 0))

    assert new_board[0][2] == "X"
    assert new_board[1][0] is None
    assert new_board[0][0] == "X"


def test_terminal_row_win_x():
    """Test: X wins in first row - returns True"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]

    assert terminal(board) is True


def test_terminal_row_win_o():
    """Test: O wins in second row - returns True"""
    board = [
        ["X", "X", None],
        ["O", "O", "O"],
        ["X", None, None],
    ]

    assert terminal(board) is True


def test_terminal_col_win():
    """Test: O wins in first column - returns True"""
    board = [
        ["O", "X", None],
        ["O", "X", None],
        ["O", None, "X"],
    ]

    assert terminal(board) is True


def test_terminal_diagonal_win():
    """Test: X wins on main diagonal - returns True"""
    board = [
        ["X", "O", None],
        ["O", "X", None],
        [None, None, "X"],
    ]

    assert terminal(board) is True


def test_terminal_anti_diagonal_win():
    """Test: O wins on anti-diagonal - returns True"""
    board = [
        ["X", "X", "O"],
        ["X", "O", None],
        ["O", None, None],
    ]

    assert terminal(board) is True


def test_terminal_not_terminal():
    """Test: game in progress - returns False"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]

    assert terminal(board) is False


def test_terminal_draw():
    """Test: board full with no winner - returns True (terminal state)"""
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    assert terminal(board) is True


def test_terminal_tie_is_final_state():
    """Test: tie board is a final state - both terminal and utility work together"""
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    assert terminal(board) is True
    assert utility(board) == 0


def test_utility_x_wins_row():
    """Test: X wins in row, player is X - returns 1"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]

    assert utility(board) == 1


def test_utility_o_wins_row():
    """Test: O wins in row - returns -1"""
    board = [
        ["X", "X", None],
        ["O", "O", "O"],
        ["X", None, None],
    ]

    assert utility(board) == -1


def test_utility_x_wins_col():
    """Test: X wins in column, player is X - returns 1"""
    board = [
        ["X", "O", None],
        ["X", "X", None],
        ["X", None, "O"],
    ]

    assert utility(board) == 1


def test_utility_x_wins_diagonal():
    """Test: X wins on main diagonal, player is X - returns 1"""
    board = [
        ["X", "O", None],
        ["O", "X", None],
        [None, None, "X"],
    ]

    assert utility(board) == 1


def test_utility_o_wins_anti_diagonal():
    """Test: O wins on anti-diagonal - returns -1"""
    board = [
        ["X", "X", "O"],
        ["X", "O", None],
        ["O", None, None],
    ]

    assert utility(board) == -1


def test_utility_x_loses_row():
    """Test: O wins in row, player is X - returns -1"""
    board = [
        ["X", "X", None],
        ["O", "O", "O"],
        ["X", None, None],
    ]

    assert utility(board) == -1


def test_utility_o_loses_row():
    """Test: X wins in row - O loses, returns 1"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]

    assert utility(board) == 1


def test_utility_draw():
    """Test: board full with no winner - returns 0"""
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    assert utility(board) == 0


def test_utility_game_in_progress():
    """Test: game in progress - returns 0"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]

    assert utility(board) == 0
