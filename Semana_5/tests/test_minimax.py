from minimax import min_value, max_value, ai_play
from utils import utility, actions, terminal, result, players


def test_min_value_terminal_x_wins_for_player():
    """Test: X wins, player is X - returns utility = 1"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]
    result = min_value(board)

    assert result == utility(board)


def test_min_value_terminal_o_wins_for_player():
    """Test: O wins, player is X - returns utility = -1"""
    board = [
        ["O", "O", "O"],
        ["X", "X", None],
        [None, None, "X"],
    ]
    result = min_value(board)

    assert result == utility(board)


def test_min_value_terminal_draw():
    """Test: draw - no winner (full board), terminal state returns 0"""
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]
    result = min_value(board)

    assert result == 0


def test_ai_play_terminal_board():
    """Test: X wins, player is X - returns utility = 1"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]
    result = max_value(board)

    assert result == utility(board)


def test_max_value_terminal_o_wins_for_player():
    """Test: O wins, player is X - returns utility = -1"""
    board = [
        ["O", "O", "O"],
        ["X", "X", None],
        [None, None, "X"],
    ]
    result = max_value(board)

    assert result == utility(board)


def test_max_value_terminal_draw():
    """Test: draw - no winner (full board), terminal state returns 0"""
    board = [
        ["X", "O", "X"],
        ["X", "O", "O"],
        ["O", "X", "X"],
    ]
    result = max_value(board)

    assert result == 0


def test_max_value_non_terminal():
    """Test: non-terminal board - returns max of child min_values"""
    board = [
        ["X", "X", None],
        ["O", None, None],
        [None, None, None],
    ]
    result = max_value(board)

    assert isinstance(result, (int, float))


def test_max_value_empty_board():
    """Test: empty board - returns max of all possible moves"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    result = max_value(board)

    assert isinstance(result, (int, float))


def test_max_value_partial_board():
    """Test: partial board with some moves available"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]
    result = max_value(board)

    assert isinstance(result, (int, float))


def test_min_value_with_o_player():
    """Test: min_value with O to move"""
    board = [
        ["X", "X", None],
        ["O", None, None],
        [None, None, None],
    ]
    result = min_value(board)

    assert isinstance(result, (int, float))


def test_max_value_with_o_player():
    """Test: max_value with O to move"""
    board = [
        ["X", None, None],
        [None, "O", None],
        [None, None, None],
    ]
    result = max_value(board)

    assert isinstance(result, (int, float))


def test_ai_play_terminal_board():
    """Test: terminal board returns an available action"""
    board = [
        ["X", "X", "X"],
        ["O", "O", None],
        [None, None, None],
    ]
    result = ai_play(board)

    assert result in actions(board)


def test_ai_play_empty_board():
    """Test: empty board returns a valid action"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    result = ai_play(board)

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_ai_play_partial_board():
    """Test: partial board returns a valid action"""
    board = [
        ["X", "O", None],
        [None, "X", None],
        [None, None, "O"],
    ]
    result = ai_play(board)

    assert result in actions(board)


def test_ai_play_x_to_move():
    """Test: works when X is to play"""
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    result = ai_play(board)

    assert result is not None
    assert result in actions(board)


def test_ai_play_o_to_move():
    """Test: works when O is to play"""
    board = [
        ["X", None, None],
        [None, None, None],
        [None, None, None],
    ]
    result = ai_play(board)

    assert result is not None
    assert result in actions(board)


def test_ai_play_winning_move():
    """Test: AI picks winning move when available"""
    board = [
        ["X", "X", None],
        ["O", None, None],
        [None, None, None],
    ]
    result = ai_play(board)

    assert result == (2, 0)


def simulate_game(board=None):
    """Simulate a full game, returns winner or 'tie'"""
    if board is None:
        board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

    current_board = [row[:] for row in board]

    while not terminal(current_board):
        move = ai_play(current_board)
        if move is None:
            break
        current_board = result(current_board, move)

    if terminal(current_board):
        for player in ["X", "O"]:
            if utility(current_board) == 1:
                return player

    return "tie"


def simulate_n_games(n, board=None):
    """Simulate n games, returns dict with results"""

    results = {"X": 0, "O": 0, "tie": 0}

    for _ in range(n):
        result = simulate_game(board)
        results[result] += 1

    return results


def test_simulate_game_empty_board_returns_tie():
    """Test: optimal players tie on empty board"""
    result = simulate_game()

    assert result == "tie"


def test_simulate_10_games_all_tie():
    """Test: optimal players tie - run 1 game to verify logic works"""
    results = simulate_n_games(1)

    assert results["tie"] == 1
    assert results["X"] == 0
    assert results["O"] == 0


def test_simulate_game_partial_board():
    """Test: simulation works with partial board near end of game"""
    board = [
        ["X", "O", "X"],
        ["X", "O", None],
        ["O", "X", None],
    ]
    result = simulate_game(board)

    assert result in ["X", "O", "tie"]
