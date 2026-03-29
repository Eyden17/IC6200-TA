# 🔍 Maze Search Visualizer — Guía rápida

## Estructura de archivos

```
IC6200-TA/               ← raíz del proyecto
│
├── Semana_3/
│   ├── matrix.csv           ← laberinto (ya existente)
│   ├── csv_reader.py
│   ├── utils.py
│   └── search.py
│
└── Semana_4/
    ├── search_core.py       ← lógica de búsqueda con generadores
    ├── visualizer.py        ← interfaz Pygame
    └── a_star.py
```

---

## Instalación

```bash
pip install pygame
```

No se necesitan otras dependencias.

---

## Ejecución

Desde la raíz del proyecto:

```bash
python visualizer.py
```

---

## Controles

| Tecla       | Acción                         |
|-------------|--------------------------------|
| `ESPACIO`   | Play / Pause                   |
| `N`         | Avanzar un paso                |
| `R`         | Reiniciar                      |
| `1`         | DFS                            |
| `2`         | BFS                            |
| `3`         | A\*                            |
| `4`         | Greedy Best-First              |
| `↑`         | Aumentar velocidad             |
| `↓`         | Disminuir velocidad            |
| `ESC`       | Salir                          |

También puedes usar los botones del panel lateral con el mouse.

---

## Arquitectura

### `search_core.py`
Contiene la lógica de búsqueda reescrita como **generadores Python** (`yield`).
Cada iteración del generador emite un diccionario con:

```python
{
  "current":  (x, y),         # nodo que se está expandiendo
  "frontier": [(x,y), ...],   # open list actual
  "visited":  [(x,y), ...],   # closed list actual
  "path":     [(x,y), ...],   # camino final (solo cuando se encuentra meta)
  "done":     bool,
  "found":    bool,
}
```

Esto permite que el visualizador avance el algoritmo de a **un paso por frame** sin modificar la lógica interna.

### `visualizer.py`
Dividido en tres responsabilidades claras:

| Clase / Función | Responsabilidad |
|-----------------|-----------------|
| `load_maze()`   | Leer `matrix.csv` |
| `AppState`      | Estado completo de la app: algoritmo activo, generador, métricas, animaciones, play/pause/step |
| `Renderer`      | Todo el render Pygame: grilla, panel lateral, botones, leyenda |
| `main()`        | Bucle de eventos, integra estado + render |

### Animaciones
Cada celda que entra en la frontera, visitados o camino tiene una **fase de animación** (0→1) que se avanza en cada frame.
Se usa una curva ease-out cuadrática para suavizar las transiciones.

---

## Configuración rápida

Para cambiar el punto de inicio/meta, edita en `visualizer.py`:

```python
start = (0, 7)   # (columna, fila)
goal  = (10, 0)
```

Para cambiar el tamaño de las celdas:

```python
CELL_SIZE = 64   # px
```
