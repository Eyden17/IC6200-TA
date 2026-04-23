# CSP Backtracking

This project demonstrates a simple constraint satisfaction problem (CSP) solver using recursive backtracking.

The example schedules courses `A` through `G` across three days while enforcing pairwise `!=` constraints so conflicting courses are not assigned to the same day.

## Project Structure

- `cps_backtracking/main.py` - Defines the sample CSP, runs the backtracking search, and prints the solution
- `cps_backtracking/csp/csp.py` - Contains the `Course` and `CSP` classes
- `cps_backtracking/csp/__init__.py` - Re-exports the package API

## How It Works

The solver uses these pieces:

- `Course` - Represents a variable with a name, domain, and assigned value
- `initialize()` - Creates one `Course` object for each variable
- `is_consistent(course, assigned_courses)` - Checks whether the current assignment violates any `!=` constraint
- `backtracking(course, remaining_courses, assigned_courses)` - Recursively assigns values and backtracks when a constraint is violated
- `main()` - Builds the sample problem and prints either the solution or `No solution found`

## Sample Problem

The built-in example in `cps_backtracking/main.py` uses:

- Variables: `A`, `B`, `C`, `D`, `E`, `F`, `G`
- Domain: `Monday`, `Tuesday`, `Wednesday`
- Constraints:
  - `A!=B`
  - `A!=C`
  - `B!=C`
  - `B!=D`
  - `B!=E`
  - `C!=E`
  - `C!=F`
  - `D!=E`
  - `E!=F`
  - `E!=G`
  - `F!=G`

## Installation

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Run

Run the sample solver from the repository root:

```bash
python cps_backtracking/main.py
```

On systems where `python` points to Python 2, use:

```bash
python3 cps_backtracking/main.py
```

## Example Output

The exact assignment depends on the search order, but the script prints one valid solution in this format:

```text
A: Monday
B: Tuesday
C: Wednesday
D: Monday
E: Wednesday
F: Tuesday
G: Monday
```

## Testing

The repository includes `pytest` and coverage configuration in `pyproject.toml`. If tests are added under `tests/`, you can run them with:

```bash
pytest
```
