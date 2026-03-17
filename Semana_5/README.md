# Minimax Tic-Tac-Toe

A Tic-Tac-Toe AI implementation using the Minimax algorithm. The AI plays optimally and will never lose.

## Functions

### utils.py

- `is_free_to_mark(board, movement)` - Checks if a position is available
- `players(board)` - Returns which player moves next (X or O)
- `actions(board)` - Returns all available moves
- `result(board, action)` - Returns the board after taking an action
- `terminal(board)` - Checks if the game is over
- `utility(board, player)` - Returns the score for a terminal state (+1 win, -1 loss, 0 draw)

### minimax.py

- `min_value(board, player)` - Minimax function that minimizes the maximum value
- `max_value(board, player)` - Minimax function that maximizes the minimum value

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Testing

Run all tests:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_utils.py
pytest tests/test_minimax.py
```

Run a specific test function:

```bash
pytest tests/test_utils.py::test_function_name
```

Run tests matching a pattern:

```bash
pytest -k "test_name"
```

Run without coverage (faster):

```bash
pytest --no-cov
```
