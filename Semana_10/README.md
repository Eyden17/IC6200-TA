# Knowledge Representation

A propositional logic engine for representing and querying a knowledge base.
Sentences are built from symbols and logical connectives; the `model_check`
function determines whether a knowledge base entails a query by exhaustive
truth-table enumeration.

## Functions

### logic.py

**Classes**

- `EvaluationException` – Raised when a symbol is evaluated against a model
  that does not contain it.
- `Sentence` (abstract) – Base class for all logical sentences. Defines
  `evaluate(model)`, `formula()`, and `symbols()`.
- `Symbol(name)` – A propositional variable. `evaluate` returns
  `bool(model[name])` or raises `EvaluationException`.
- `Not(operand)` – Logical negation. `formula` renders as `¬`.
- `And(*conjuncts)` – Logical conjunction. `add(conjunct)` appends a new
  conjunct. `formula` renders operands joined by `∧`.
- `Or(*disjuncts)` – Logical disjunction. `add(disjunct)` appends a new
  disjunct. `formula` renders operands joined by `∨`.
- `Implication(antecedent, consequent)` – Material implication. `formula`
  renders as `antecedent => consequent`.
- `Biconditional(left, right)` – Logical biconditional. `formula` renders
  as `left <=> right`.

**Functions**

- `model_check(knowledge, query)` – Returns `True` if `knowledge` entails
  `query` under all possible truth assignments to the symbols involved.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick run (Harry Potter puzzle)

Windows:

```bash
python harry.py
```

Linux/macOS:

```bash
python3 harry.py
```

### Build a knowledge base in Python

```python
from logic import And, Not, Or, Implication, Biconditional, Symbol, model_check

rain = Symbol("rain")
sun  = Symbol("sun")

knowledge = And(
    Or(rain, sun),
    Implication(rain, Not(sun)),
)

print(model_check(knowledge, sun))   # True
print(model_check(knowledge, rain))  # False
```

## Testing

### Windows

```bash
python -m pytest
```

Run a specific file:

```bash
python -m pytest tests/test_logic.py
```

Run a specific test:

```bash
python -m pytest tests/test_logic.py::test_function_name
```

Run tests matching a pattern:

```bash
python -m pytest -k "symbol"
```

Run without coverage (faster):

```bash
python -m pytest --no-cov
```

### Linux/macOS

```bash
pytest
```

## Contributing

Short contributions are welcome and appreciated.

1. Fork the repository.
2. Create a branch for your change.
3. Make your update and keep it focused.
4. Run tests before submitting:
   - Windows: `python -m pytest`
   - Linux/macOS: `pytest`
5. Open a Pull Request with a clear description of what and why.

Please keep PRs small, readable, and related to a single improvement.
