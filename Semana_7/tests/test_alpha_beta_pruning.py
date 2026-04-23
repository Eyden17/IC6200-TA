import math

from alpha_beta_pruning import ai_play, max_value, min_value
from minimax import ai_play as minimax_ai_play
from minimax import max_value as minimax_max_value
from minimax import min_value as minimax_min_value
from utils import actions, result, terminal, utility


def test_min_value_terminal_x_wins_for_player():
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]

    assert min_value(board, -math.inf, math.inf) == utility(board)


def test_min_value_terminal_o_wins_for_player():
    board = [
        ["O", "O", "O"],
        ["X", "X", None],
        [None, None, "X"],
    ]

    assert min_value(board, -math.inf, math.inf) == utility(board)


def test_min_value_terminal_draw():
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    assert min_value(board, -math.inf, math.inf) == 0


def test_max_value_terminal_x_wins_for_player():
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]

    assert max_value(board, -math.inf, math.inf) == utility(board)


def test_max_value_terminal_o_wins_for_player():
    board = [
        ["O", "O", "O"],
        ["X", "X", None],
        [None, None, "X"],
    ]

    assert max_value(board, -math.inf, math.inf) == utility(board)


def test_max_value_terminal_draw():
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]

    assert max_value(board, -math.inf, math.inf) == 0


def test_ai_play_empty_board_returns_valid_action():
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    move = ai_play(board)

    assert isinstance(move, tuple)
    assert len(move) == 2
    assert move in actions(board)


def test_ai_play_partial_board_returns_valid_action():
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]
    move = ai_play(board)

    assert move in actions(board)


def test_ai_play_winning_move():
    board = [
        ["X", "X", None],
        ["O", None, None],
        [None, None, None],
    ]

    assert ai_play(board) == (2, 0)


def test_ai_play_terminal_board_returns_available_action():
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]
    move = ai_play(board)

    assert move in actions(board)


def test_ai_play_matches_minimax_on_representative_boards():
    boards = [
        [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ],
        [
            ["X", None, None],
            [None, None, None],
            [None, None, None],
        ],
        [
            ["X", "X", None],
            ["O", None, None],
            [None, None, None],
        ],
        [
            ["X", "O", None],
            [None, "X", None],
            [None, None, "O"],
        ],
    ]

    for board in boards:
        assert ai_play(board) == minimax_ai_play(board)


def test_min_value_matches_minimax_on_non_terminal_boards():
    boards = [
        [
            ["X", "X", None],
            ["O", None, None],
            [None, None, None],
        ],
        [
            ["X", "O", None],
            [None, "X", None],
            [None, None, "O"],
        ],
    ]

    for board in boards:
        assert min_value(board, -math.inf, math.inf) == minimax_min_value(board)


def test_max_value_matches_minimax_on_non_terminal_boards():
    boards = [
        [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ],
        [
            ["X", None, None],
            [None, "O", None],
            [None, None, None],
        ],
    ]

    for board in boards:
        assert max_value(board, -math.inf, math.inf) == minimax_max_value(board)


def test_simulate_game_empty_board_returns_tie_with_alpha_beta():
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]

    while not terminal(board):
        move = ai_play(board)
        if move is None:
            break
        board = result(board, move)

    assert utility(board) == 0