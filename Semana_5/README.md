# Semana 5: Minimax (Tic-Tac-Toe)

## Descripción del algoritmo

En esta semana se implementa **Minimax** para jugar Tic-Tac-Toe de forma óptima.

- El tablero es una matriz 3x3 con `"X"`, `"O"` o `None`.
- `max_value(board)` busca maximizar la utilidad para **X**.
- `min_value(board)` busca minimizar la utilidad para **O**.
- `utility(board)` evalúa estados terminales:
  - `1` si gana X
  - `-1` si gana O
  - `0` si hay empate
- `ai_play(board)` selecciona la mejor jugada posible según el turno.

## Instrucciones de instalación

Desde la carpeta `Semana_5`:

```bash
pip install -r requirements.txt
```

## Instrucciones de ejecución

Desde `Semana_5`, ejecutar el ejemplo:

```bash
python main.py
```

Para correr las pruebas:

```bash
pytest
```
