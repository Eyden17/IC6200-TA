# Semana 4: Búsqueda Informada (A* y Greedy)

## Descripción del algoritmo

Esta semana implementa dos estrategias de búsqueda informada sobre el mismo laberinto:

- **A\*** (`a_star_search`):
  - Usa `f(n) = g(n) + h(n)`.
  - `g(n)`: costo acumulado desde el inicio.
  - `h(n)`: distancia Manhattan hasta la meta.
  - Ordena la frontera por menor `total_cost` para explorar primero el nodo más prometedor.
- **Greedy Best-First Search** (`greedy_search`):
  - Usa solo la heurística `h(n)` (distancia Manhattan).
  - Prioriza nodos “más cerca” de la meta, sin considerar el costo acumulado.

Ambos algoritmos reutilizan utilidades de `Semana_3` para nodos, movimientos y reconstrucción de ruta.

## Instrucciones de instalación

No requiere librerías externas (solo módulos estándar de Python).

Opcional:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Instrucciones de ejecución

Desde la raíz del proyecto (`IC6200-TA`), ejecutar:

```bash
python Semana_4/a_star.py
```

El script imprime:

- `A* Path found: ...`
- `Greedy Path found: ...`
