# Semana 3: Búsqueda en Laberinto (DFS y BFS)

## Descripción del algoritmo

En esta semana se resuelve un laberinto representado en una matriz (`matrix.csv`) usando búsqueda no informada.

- `solve(..., algo="dfs")` implementa **Depth-First Search (DFS)**:
  - Expande primero nodos más profundos.
  - Inserta nuevos nodos al inicio de la frontera.
- `solve(..., algo="bfs")` implementa **Breadth-First Search (BFS)**:
  - Expande primero nodos por niveles.
  - Inserta nuevos nodos al final de la frontera.
- La clase `Node` guarda posición y referencia al padre para reconstruir la ruta.
- `build_path` reconstruye el camino desde la meta hasta el inicio.

## Instrucciones de instalación

No requiere librerías externas (solo módulos estándar de Python).

Opcionalmente, puedes crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Instrucciones de ejecución

Desde la raíz del proyecto (`IC6200-TA`), ejecutar:

```bash
python Semana_3/search.py
```

El script imprime el camino encontrado entre `start` y `goal`.
