"""
visualizer.py  ─  Visualizador Pygame para algoritmos de búsqueda en laberinto
================================================================================
Coloca este archivo en la RAÍZ del proyecto (junto a matrix.csv).
Requiere: Python 3.8+ y pygame  →  pip install pygame

Controles:
  ESPACIO   Play / Pause
  N         Next step (un paso)
  R         Reset
  1         DFS
  2         BFS
  3         A*
  4         Greedy
  ↑ / ↓    Velocidad (más rápido / más lento)
  ESC       Salir
"""

import csv
import os
import sys
import time
import pygame

# ── Importar lógica de búsqueda ───────────────────────────────────────────────
# Si ejecutas, search_core.py debe estar en el mismo directorio.
try:
    from search_core import ALGORITHMS
except ImportError:
    print("ERROR: no se encontró search_core.py en el directorio actual.")
    print("Asegúrate de colocar visualizer.py y search_core.py en la misma carpeta.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN VISUAL
# ═══════════════════════════════════════════════════════════════════════════════

# Paleta de colores (estilo oscuro, accesible)
C = {
    "bg":           (15,  17,  23),   # fondo general
    "panel":        (22,  25,  35),   # panel lateral
    "panel_border": (40,  45,  60),   # borde panel
    "wall":         (38,  42,  55),   # celda obstáculo
    "wall_hi":      (55,  60,  80),   # borde de muro
    "empty":        (28,  32,  45),   # celda libre
    "grid_line":    (35,  40,  55),   # línea de grilla
    "visited":      (45,  80, 120),   # closed list
    "frontier":     (80, 160, 200),   # open list
    "current":      (255, 200,  50),  # nodo actual
    "path":         (80, 220, 140),   # camino final
    "start":        (100, 230, 100),  # inicio
    "goal":         (230,  80,  80),  # meta
    "text":         (210, 215, 230),  # texto principal
    "text_dim":     (100, 110, 135),  # texto secundario
    "text_hi":      (255, 255, 255),  # texto resaltado
    "accent":       ( 80, 160, 255),  # acento azul
    "btn":          (40,  48,  70),   # botón normal
    "btn_hover":    (55,  65,  95),   # botón hover
    "btn_active":   (60,  90, 160),   # botón activo/seleccionado
    "btn_border":   (70,  80, 110),   # borde botón
    "success":      ( 80, 220, 140),  # verde éxito
    "warning":      (255, 180,  50),  # amarillo advertencia
    "error":        (230,  80,  80),  # rojo error
}

# segundos por step (índice 0 = más lento)
# Ajustado para que Play se sienta responsivo desde el inicio.
SPEEDS = [0.8, 0.4, 0.2, 0.1, 0.05, 0.02]
SPEED_LABELS = ["x1", "x2", "x4", "x8", "x16", "x40"]
DEFAULT_SPEED_IDX = 2

CELL_SIZE   = 64   # px por celda (se recalcula automáticamente al iniciar)
PANEL_WIDTH = 340  # px panel lateral
MARGIN      = 20   # px margen exterior


# ═══════════════════════════════════════════════════════════════════════════════
#  LECTOR DE MATRIZ
# ═══════════════════════════════════════════════════════════════════════════════

def load_maze(path="matrix.csv"):
    """Carga el laberinto desde CSV. Busca en el directorio del script."""
    base = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(base, path)
    maze = []
    with open(full, "r") as f:
        for row in csv.reader(f):
            maze.append([float(v) for v in row])
    return maze


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTADO DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class AppState:
    def __init__(self, maze, start, goal):
        self.maze      = maze
        self.start     = start
        self.goal      = goal
        self.rows      = len(maze)
        self.cols      = len(maze[0])

        self.algo_names = list(ALGORITHMS.keys())   # ["DFS","BFS","A*","Greedy"]
        self.algo_idx   = 0                         # algoritmo seleccionado

        self.speed_idx  = DEFAULT_SPEED_IDX

        # Estado del generador
        self.generator  = None
        self.step_state = None   # último estado emitido por el generador

        # Métricas
        self.iterations    = 0
        self.frontier_size = 0
        self.visited_count = 0
        self.elapsed_ms    = 0
        self._start_time   = None

        # Control de reproducción
        self.playing   = False
        self.done      = False
        self._last_step_time = 0.0   # tiempo del último step automático

        # Animación: set de celdas con "alpha" animado (fase 0→1)
        # Cada entrada: { pos: phase }
        self._anim_frontier = {}
        self._anim_visited  = {}
        self._anim_path     = {}

        self.reset()

    # ── Propiedades de conveniencia ───────────────────────────────────────────
    @property
    def algo_name(self):
        return self.algo_names[self.algo_idx]

    @property
    def speed_s(self):
        return SPEEDS[self.speed_idx]

    @property
    def speed_label(self):
        return SPEED_LABELS[self.speed_idx]

    # ── Control ───────────────────────────────────────────────────────────────
    def reset(self):
        gen_fn          = ALGORITHMS[self.algo_name]
        self.generator  = gen_fn(self.maze, self.start, self.goal)
        self.step_state = {"current": None, "frontier": [self.start],
                           "visited": [], "path": None, "done": False, "found": False}
        self.iterations    = 0
        self.frontier_size = 1
        self.visited_count = 0
        self.elapsed_ms    = 0
        self._start_time   = None
        self.playing       = False
        self.done          = False
        self._last_step_time = 0.0
        self._anim_frontier  = {}
        self._anim_visited   = {}
        self._anim_path      = {}

    def set_algo(self, idx):
        self.algo_idx = idx
        self.reset()

    def toggle_play(self):
        if self.done:
            return
        self.playing = not self.playing
        if self.playing and self._start_time is None:
            self._start_time = time.time()

    def step(self):
        """Avanza un paso en el generador."""
        if self.done:
            return
        try:
            state = next(self.generator)
            self._apply_state(state)
        except StopIteration:
            self.done = True
            self.playing = False

    def _apply_state(self, state):
        prev_frontier = set(tuple(p) for p in (self.step_state["frontier"] or []))
        prev_visited  = set(tuple(p) for p in (self.step_state["visited"]  or []))

        self.step_state = state
        self.iterations    += 1
        self.frontier_size  = len(state["frontier"])
        self.visited_count  = len(state["visited"])

        if self._start_time is not None:
            self.elapsed_ms = int((time.time() - self._start_time) * 1000)

        # Registrar nuevas celdas para animación
        for pos in state["frontier"]:
            if tuple(pos) not in prev_frontier:
                self._anim_frontier[tuple(pos)] = 0.0

        for pos in state["visited"]:
            if tuple(pos) not in prev_visited:
                self._anim_visited[tuple(pos)] = 0.0

        if state["path"]:
            for pos in state["path"]:
                self._anim_path[tuple(pos)] = 0.0

        if state["done"]:
            self.done    = True
            self.playing = False

    def tick_animations(self, dt):
        """Avanza las fases de animación (dt en segundos)."""
        speed = dt * 6.0   # 6 unidades/segundo → completa en ~0.17 s
        for d in [self._anim_frontier, self._anim_visited, self._anim_path]:
            for k in list(d.keys()):
                d[k] = min(1.0, d[k] + speed)

    def auto_step(self):
        """Llama a step() si playing y es momento."""
        if not self.playing or self.done:
            return
        now = time.time()
        if now - self._last_step_time >= self.speed_s:
            self._last_step_time = now
            if self._start_time is None:
                self._start_time = time.time()
            self.step()

    def speed_up(self):
        self.speed_idx = min(self.speed_idx + 1, len(SPEEDS) - 1)

    def speed_down(self):
        self.speed_idx = max(self.speed_idx - 1, 0)


# ═══════════════════════════════════════════════════════════════════════════════
#  RENDERIZADO
# ═══════════════════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, screen, fonts, state: AppState):
        self.screen = screen
        self.fonts  = fonts
        self.state  = state
        self.W, self.H = screen.get_size()

        # Área de la grilla
        self.grid_x = MARGIN
        self.grid_y = MARGIN
        self.grid_w = state.cols * CELL_SIZE
        self.grid_h = state.rows * CELL_SIZE

        # Panel lateral
        self.panel_x = self.grid_x + self.grid_w + MARGIN
        self.panel_y = MARGIN
        self.panel_w = PANEL_WIDTH
        self.panel_h = self.H - 2 * MARGIN

        # Rects interactivos reales (se actualizan en cada draw)
        self._algo_button_rects = []
        self._control_button_rects = {}
        self._speed_button_rects = {}

        # Superficies de animación pre-creadas
        self._surf_visited  = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
        self._surf_frontier = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
        self._surf_path     = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)

    # ── Punto de entrada ──────────────────────────────────────────────────────
    def draw(self):
        # Limpiar y volver a poblar hitboxes en cada frame
        self._algo_button_rects = []
        self._control_button_rects = {}
        self._speed_button_rects = {}
        self.screen.fill(C["bg"])
        self._draw_grid()
        self._draw_panel()
        pygame.display.flip()

    # ── Grilla ────────────────────────────────────────────────────────────────
    def _cell_rect(self, x, y):
        """Rect de la celda (x=col, y=fila)."""
        px = self.grid_x + x * CELL_SIZE
        py = self.grid_y + y * CELL_SIZE
        return pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)

    def _draw_grid(self):
        s   = self.state
        ss  = s.step_state
        rows, cols = s.rows, s.cols

        frontier_set = set(tuple(p) for p in (ss["frontier"] or []))
        visited_set  = set(tuple(p) for p in (ss["visited"]  or []))
        path_set     = set(tuple(p) for p in (ss["path"]     or []))
        current      = tuple(ss["current"]) if ss["current"] else None

        for row in range(rows):
            for col in range(cols):
                pos  = (col, row)
                rect = self._cell_rect(col, row)
                is_wall = s.maze[row][col] == 1.0

                # ── Fondo de celda
                if is_wall:
                    pygame.draw.rect(self.screen, C["wall"], rect)
                    # Borde sutil en muros
                    pygame.draw.rect(self.screen, C["wall_hi"], rect, 1)
                else:
                    pygame.draw.rect(self.screen, C["empty"], rect)

                if not is_wall:
                    # ── Capas de estado (orden: visited → frontier → path → current)
                    if pos in visited_set and pos not in path_set:
                        phase = s._anim_visited.get(pos, 1.0)
                        alpha = int(210 * _ease(phase))
                        self._surf_visited.fill((0, 0, 0, 0))
                        self._surf_visited.fill((*C["visited"], alpha))
                        self.screen.blit(self._surf_visited, (rect.x + 1, rect.y + 1))

                    if pos in frontier_set:
                        phase = s._anim_frontier.get(pos, 1.0)
                        alpha = int(220 * _ease(phase))
                        self._surf_frontier.fill((0, 0, 0, 0))
                        self._surf_frontier.fill((*C["frontier"], alpha))
                        self.screen.blit(self._surf_frontier, (rect.x + 1, rect.y + 1))

                    if pos in path_set:
                        phase = s._anim_path.get(pos, 1.0)
                        alpha = int(240 * _ease(phase))
                        self._surf_path.fill((0, 0, 0, 0))
                        self._surf_path.fill((*C["path"], alpha))
                        self.screen.blit(self._surf_path, (rect.x + 1, rect.y + 1))

                    # ── Nodo actual (brillo pulsante)
                    if pos == current and not s.done:
                        t     = time.time()
                        pulse = 0.7 + 0.3 * abs((t % 1.0) * 2 - 1)
                        r2    = rect.inflate(-8, -8)
                        c_hi  = _lerp_color(C["current"], C["text_hi"], 0.3)
                        pygame.draw.rect(self.screen, _scale_color(C["current"], pulse), r2, border_radius=6)
                        pygame.draw.rect(self.screen, c_hi, r2, 2, border_radius=6)

                    # ── Inicio y meta
                    if pos == s.start:
                        self._draw_label(rect, "S", C["start"])
                    elif pos == s.goal:
                        self._draw_label(rect, "G", C["goal"])

                # ── Línea de grilla
                pygame.draw.rect(self.screen, C["grid_line"], rect, 1)

        # Borde del área de grilla
        grid_border = pygame.Rect(self.grid_x - 1, self.grid_y - 1,
                                  self.grid_w + 2, self.grid_h + 2)
        pygame.draw.rect(self.screen, C["panel_border"], grid_border, 2, border_radius=4)

    def _draw_label(self, rect, text, color):
        f   = self.fonts["bold"]
        surf = f.render(text, True, color)
        pos  = surf.get_rect(center=rect.center)
        self.screen.blit(surf, pos)

    # ── Panel lateral ─────────────────────────────────────────────────────────
    def _draw_panel(self):
        px, py, pw, ph = self.panel_x, self.panel_y, self.panel_w, self.panel_h

        # Fondo del panel
        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, C["panel"], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, C["panel_border"], panel_rect, 2, border_radius=10)

        cy = py + 18  # cursor Y

        # ── Título
        cy = self._panel_title("🔍 Maze Search Visualizer", px, cy, pw)
        cy += 6

        # ── Selector de algoritmo
        cy = self._section_label("Algoritmo", px, cy, pw)
        cy = self._algo_buttons(px, cy, pw)
        cy += 10

        # ── Estado
        cy = self._section_label("Estado", px, cy, pw)
        s  = self.state
        ss = s.step_state

        status_color = C["success"] if (s.done and ss.get("found")) \
                  else C["error"]   if (s.done and not ss.get("found")) \
                  else C["warning"] if s.playing \
                  else C["text_dim"]
        status_text  = "✓ Meta encontrada" if (s.done and ss.get("found")) \
                  else "✗ Sin solución"    if (s.done and not ss.get("found")) \
                  else "▶ Ejecutando"      if s.playing \
                  else "⏸ Pausado"
        cy = self._panel_kv("", status_text, px, cy, pw,
                             val_color=status_color, bold_val=True)
        cy += 4

        # ── Métricas
        cy = self._section_label("Métricas", px, cy, pw)
        cy = self._panel_kv("Iteraciones",   str(s.iterations),    px, cy, pw)
        cy = self._panel_kv("Frontera",      str(s.frontier_size), px, cy, pw,
                             val_color=C["frontier"])
        cy = self._panel_kv("Visitados",     str(s.visited_count), px, cy, pw,
                             val_color=C["visited"])
        path_len = len(ss["path"]) - 1 if ss.get("path") else "—"
        cy = self._panel_kv("Long. camino",  str(path_len),        px, cy, pw,
                             val_color=C["path"])
        cy = self._panel_kv("Tiempo (ms)",   str(s.elapsed_ms),    px, cy, pw)
        cy += 10

        # ── Controles de reproducción
        cy = self._section_label("Controles", px, cy, pw)
        cy = self._control_buttons(px, cy, pw)
        cy += 8

        # ── Control de velocidad
        cy = self._section_label("Velocidad", px, cy, pw)
        cy = self._speed_controls(px, cy, pw)
        cy += 12

        # ── Leyenda
        cy = self._section_label("Leyenda", px, cy, pw)
        legend = [
            (C["start"],    "Inicio (S)"),
            (C["goal"],     "Meta (G)"),
            (C["current"],  "Nodo actual"),
            (C["frontier"], "Frontera (open)"),
            (C["visited"],  "Visitados (closed)"),
            (C["path"],     "Camino final"),
            (C["wall"],     "Obstáculo"),
        ]
        for color, label in legend:
            cy = self._legend_item(color, label, px, cy, pw)
        cy += 10

        # ── Atajos de teclado
        cy = self._section_label("Atajos", px, cy, pw)
        shortcuts = [
            ("ESPACIO", "Play / Pause"),
            ("N",       "Siguiente paso"),
            ("R",       "Reiniciar"),
            ("1-4",     "Cambiar algoritmo"),
            ("↑ / ↓",  "Velocidad"),
            ("ESC",     "Salir"),
        ]
        for key, desc in shortcuts:
            cy = self._shortcut_row(key, desc, px, cy, pw)

    # ── Helpers de panel ──────────────────────────────────────────────────────
    def _panel_title(self, text, px, cy, pw):
        f    = self.fonts["title"]
        surf = f.render(text, True, C["text_hi"])
        self.screen.blit(surf, (px + (pw - surf.get_width()) // 2, cy))
        return cy + surf.get_height() + 4

    def _section_label(self, text, px, cy, pw):
        f    = self.fonts["small_bold"]
        surf = f.render(text.upper(), True, C["accent"])
        self.screen.blit(surf, (px + 14, cy))
        line_y = cy + surf.get_height() + 3
        pygame.draw.line(self.screen, C["panel_border"],
                         (px + 14, line_y), (px + pw - 14, line_y))
        return line_y + 6

    def _panel_kv(self, key, val, px, cy, pw,
                  val_color=None, bold_val=False):
        fk = self.fonts["small"]
        fv = self.fonts["small_bold"] if bold_val else self.fonts["small"]
        vc = val_color or C["text"]
        if key:
            sk = fk.render(key + ":", True, C["text_dim"])
            self.screen.blit(sk, (px + 14, cy))
        sv = fv.render(val, True, vc)
        self.screen.blit(sv, (px + pw - 14 - sv.get_width(), cy))
        return cy + max(sk.get_height() if key else 0, sv.get_height()) + 3

    def _algo_buttons(self, px, cy, pw):
        names  = self.state.algo_names
        bw     = (pw - 28 - (len(names) - 1) * 6) // len(names)
        bh     = 32
        mouse  = pygame.mouse.get_pos()
        for i, name in enumerate(names):
            bx   = px + 14 + i * (bw + 6)
            rect = pygame.Rect(bx, cy, bw, bh)
            active = (i == self.state.algo_idx)
            hover  = rect.collidepoint(mouse) and not active
            bg = C["btn_active"] if active else (C["btn_hover"] if hover else C["btn"])
            bc = C["accent"]     if active else C["btn_border"]
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, bc, rect, 1, border_radius=6)
            f    = self.fonts["small_bold"] if active else self.fonts["small"]
            tc   = C["text_hi"] if active else C["text"]
            surf = f.render(name, True, tc)
            self.screen.blit(surf, surf.get_rect(center=rect.center))
            self._algo_button_rects.append((rect, i))
        return cy + bh + 4

    def _control_buttons(self, px, cy, pw):
        s     = self.state
        mouse = pygame.mouse.get_pos()
        btns  = [
            ("▶" if not s.playing else "⏸", "play_pause", not s.done),
            ("▷ Step",                        "step",       not s.done),
            ("↺ Reset",                        "reset",      True),
        ]
        bw = (pw - 28 - 2 * 6) // 3
        bh = 34
        for i, (label, action, enabled) in enumerate(btns):
            bx   = px + 14 + i * (bw + 6)
            rect = pygame.Rect(bx, cy, bw, bh)
            hover = rect.collidepoint(mouse) and enabled
            bg  = C["btn_hover"] if hover else C["btn"]
            bc  = C["panel_border"]
            tc  = C["text"] if enabled else C["text_dim"]
            if not enabled:
                bg = _darken(C["btn"], 0.5)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, bc, rect, 1, border_radius=6)
            f    = self.fonts["small"]
            surf = f.render(label, True, tc)
            self.screen.blit(surf, surf.get_rect(center=rect.center))
            self._control_button_rects[action] = rect
        return cy + bh + 4

    def _speed_controls(self, px, cy, pw):
        s     = self.state
        mouse = pygame.mouse.get_pos()
        label = f"  {s.speed_label}  "
        # Botones − y +
        bw, bh = 30, 30
        # − botón
        rx = px + 14
        r  = pygame.Rect(rx, cy, bw, bh)
        hov = r.collidepoint(mouse)
        pygame.draw.rect(self.screen, C["btn_hover"] if hov else C["btn"], r, border_radius=6)
        pygame.draw.rect(self.screen, C["btn_border"], r, 1, border_radius=6)
        surf = self.fonts["bold"].render("−", True, C["text"])
        self.screen.blit(surf, surf.get_rect(center=r.center))
        self._speed_button_rects["slower"] = r

        # Etiqueta central
        lsurf = self.fonts["bold"].render(s.speed_label, True, C["accent"])
        lx    = px + 14 + bw + (pw - 28 - 2 * bw - lsurf.get_width()) // 2
        self.screen.blit(lsurf, (lx, cy + (bh - lsurf.get_height()) // 2))

        # + botón
        rx2 = px + pw - 14 - bw
        r2  = pygame.Rect(rx2, cy, bw, bh)
        hov2 = r2.collidepoint(mouse)
        pygame.draw.rect(self.screen, C["btn_hover"] if hov2 else C["btn"], r2, border_radius=6)
        pygame.draw.rect(self.screen, C["btn_border"], r2, 1, border_radius=6)
        surf2 = self.fonts["bold"].render("+", True, C["text"])
        self.screen.blit(surf2, surf2.get_rect(center=r2.center))
        self._speed_button_rects["faster"] = r2

        return cy + bh + 4

    def _legend_item(self, color, text, px, cy, pw):
        sq   = 13
        sy   = cy + 2
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(px + 14, sy, sq, sq), border_radius=3)
        pygame.draw.rect(self.screen, C["text_dim"],
                         pygame.Rect(px + 14, sy, sq, sq), 1, border_radius=3)
        f    = self.fonts["small"]
        surf = f.render(text, True, C["text_dim"])
        self.screen.blit(surf, (px + 14 + sq + 6, cy))
        return cy + surf.get_height() + 3

    def _shortcut_row(self, key, desc, px, cy, pw):
        fk   = self.fonts["small_bold"]
        fd   = self.fonts["small"]
        sk   = fk.render(key, True, C["accent"])
        sd   = fd.render(desc, True, C["text_dim"])
        self.screen.blit(sk, (px + 14, cy))
        self.screen.blit(sd, (px + pw - 14 - sd.get_width(), cy))
        return cy + max(sk.get_height(), sd.get_height()) + 2

    # ── Hit-testing de botones (para eventos de clic) ─────────────────────────
    def hit_algo_button(self, mouse_pos):
        for rect, idx in self._algo_button_rects:
            if rect.collidepoint(mouse_pos):
                return idx
        return None

    def hit_control_button(self, mouse_pos):
        for action, rect in self._control_button_rects.items():
            if rect.collidepoint(mouse_pos):
                return action
        return None

    def hit_speed_button(self, mouse_pos):
        for action, rect in self._speed_button_rects.items():
            if rect.collidepoint(mouse_pos):
                return action
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS DE COLOR
# ═══════════════════════════════════════════════════════════════════════════════

def _ease(t):
    """Ease-out cuadrático."""
    return 1 - (1 - t) ** 2

def _lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def _scale_color(c, factor):
    return tuple(min(255, int(v * factor)) for v in c)

def _darken(c, factor):
    return tuple(int(v * factor) for v in c)


# ═══════════════════════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    pygame.display.set_caption("Maze Search Visualizer")

    # Cargar laberinto
    maze  = load_maze("matrix.csv")
    rows  = len(maze)
    cols  = len(maze[0])
    start = (0, 7)    # (col, fila)
    goal  = (10, 0)

    # Escala inicial automática para que no se vea pequeña en pantallas grandes.
    info = pygame.display.Info()
    max_w = int(info.current_w * 0.92)
    max_h = int(info.current_h * 0.88)

    global CELL_SIZE
    cell_by_w = (max_w - (3 * MARGIN + PANEL_WIDTH)) // cols
    cell_by_h = (max_h - (2 * MARGIN)) // rows
    CELL_SIZE = max(48, min(100, cell_by_w, cell_by_h))

    # Tamaño de ventana final (ajustado a la celda calculada)
    W = MARGIN + cols * CELL_SIZE + MARGIN + PANEL_WIDTH + MARGIN
    H = MARGIN + rows * CELL_SIZE + MARGIN

    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)

    # Fuentes
    pygame.font.init()
    try:
        font_name = pygame.font.match_font("segoeui,helveticaneue,arial,ubuntu,freesans")
        fonts = {
            "title":      pygame.font.Font(font_name, 15),
            "bold":       pygame.font.Font(font_name, 18),
            "small_bold": pygame.font.Font(font_name, 13),
            "small":      pygame.font.Font(font_name, 13),
        }
        # Activar negrita en los que corresponde
        fonts["title"].set_bold(True)
        fonts["bold"].set_bold(True)
        fonts["small_bold"].set_bold(True)
    except Exception:
        fonts = {k: pygame.font.SysFont("sans", sz)
                 for k, sz in [("title",14),("bold",18),("small_bold",13),("small",13)]}

    state    = AppState(maze, start, goal)
    renderer = Renderer(screen, fonts, state)

    clock = pygame.time.Clock()
    prev_time = time.time()

    running = True
    while running:
        now = time.time()
        dt  = now - prev_time
        prev_time = now

        # ── Eventos ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Mantener interacciones correctas al redimensionar.
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                renderer = Renderer(screen, fonts, state)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    state.toggle_play()
                elif event.key == pygame.K_n:
                    state.step()
                elif event.key == pygame.K_r:
                    state.reset()
                elif event.key == pygame.K_1:
                    state.set_algo(0)
                elif event.key == pygame.K_2:
                    state.set_algo(1)
                elif event.key == pygame.K_3:
                    state.set_algo(2)
                elif event.key == pygame.K_4:
                    state.set_algo(3)
                elif event.key == pygame.K_UP:
                    state.speed_up()
                elif event.key == pygame.K_DOWN:
                    state.speed_down()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mp = event.pos
                # Botones de algoritmo
                idx = renderer.hit_algo_button(mp)
                if idx is not None:
                    state.set_algo(idx)
                    continue
                # Botones de control
                action = renderer.hit_control_button(mp)
                if action == "play_pause":
                    state.toggle_play()
                elif action == "step":
                    state.step()
                elif action == "reset":
                    state.reset()
                # Velocidad
                sv = renderer.hit_speed_button(mp)
                if sv == "faster":
                    state.speed_up()
                elif sv == "slower":
                    state.speed_down()

        # ── Lógica ────────────────────────────────────────────────────────────
        state.auto_step()
        state.tick_animations(dt)

        # ── Render ────────────────────────────────────────────────────────────
        renderer.draw()
        clock.tick(60)   # 60 fps máximo

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
