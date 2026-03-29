"""
visualizer_ttt.py
-----------------
Visualizador Pygame para Tic-Tac-Toe con análisis Minimax paso a paso.

Coloca este archivo en la RAÍZ del proyecto (junto a minimax_core.py).
La carpeta Semana_5/ debe existir con minimax.py y utils.py intactos.

Requiere: pip install pygame

Controles:
  Mouse     → jugar en celda (turno humano)
  ESPACIO   → play/pause análisis IA
  N         → siguiente paso del análisis
  R         → reiniciar partida
  A         → toggle auto-play (IA vs IA)
  H         → toggle mostrar/ocultar análisis
  ESC       → salir
"""

import sys
import os
import time
import math
import pygame

# ── Importar adaptador (que a su vez importa los originales) ──────────────────
try:
    from minimax_core import (
        evaluate_candidates, candidate_generator,
        PLAYER_X, PLAYER_O,
        players, actions, result, terminal, utility
    )
except ImportError:
    print("ERROR: no se encontró minimax_core.py en el directorio actual.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
#  PALETA Y CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════

# Estética: dark slate con acentos warm-gold para X y cool-mint para O
C = {
    "bg":          (10,  12,  18),
    "bg2":         (16,  19,  28),
    "panel":       (20,  23,  35),
    "panel_b":     (35,  40,  58),
    "grid_line":   (40,  46,  68),
    "cell_hover":  (30,  35,  52),
    "cell_flash":  (50,  58,  85),
    "x_color":     (255, 190,  60),   # gold
    "x_dim":       (120,  88,  20),
    "o_color":     ( 80, 210, 180),   # mint
    "o_dim":       ( 25,  90,  76),
    "text":        (220, 225, 240),
    "text_dim":    ( 95, 102, 130),
    "text_hi":     (255, 255, 255),
    "accent":      (110, 140, 255),   # periwinkle
    "best":        ( 80, 210, 140),   # verde best-move
    "candidate":   (200, 160,  60),   # amarillo candidato activo
    "win_line":    (255, 220, 100),
    "btn":         (28,  33,  50),
    "btn_hover":   (42,  50,  76),
    "btn_active":  (55,  80, 160),
    "btn_b":       (55,  65,  95),
    "pos":         (255, 100, 100),   # valor negativo
    "neg":         (100, 200, 255),   # valor positivo (bueno para O)
    "zero":        (140, 145, 165),
    "success":     ( 80, 210, 140),
    "error":       (230,  80,  80),
}

CELL      = 160      # tamaño celda px
GRID_PAD  = 40       # margen exterior del tablero
PANEL_W   = 300      # ancho panel lateral
MARGIN    = 24
LINE_W    = 5        # grosor líneas de grilla
MARK_W    = 10       # grosor X y O

WIN_W  = GRID_PAD * 2 + CELL * 3 + MARGIN + PANEL_W + MARGIN
WIN_H  = GRID_PAD * 2 + CELL * 3 + MARGIN * 2
ANALYSIS_BOX_H = 190


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTADO DE LA APP
# ═══════════════════════════════════════════════════════════════════════════════

EMPTY_BOARD = lambda: [[None, None, None],
                        [None, None, None],
                        [None, None, None]]

class AppState:
    def __init__(self):
        self.board        = EMPTY_BOARD()
        self.human        = PLAYER_O      # el humano juega O por defecto
        self.autoplay     = False
        self.show_analysis= True

        # Análisis minimax
        self.gen          = None          # generador paso a paso
        self.gen_states   = []            # estados acumulados del generador
        self.gen_done     = False
        self.playing      = False         # play/pause del análisis
        self.step_delay   = 0.55          # segundos entre steps en play
        self._last_step   = 0.0

        # Estado actual del análisis (último yield)
        self.analysis     = None

        # Resultado final de evaluate_candidates (para panel)
        self.candidates   = []
        self.best_move    = None
        self.nodes_total  = 0

        # Juego
        self.game_over    = False
        self.winner       = None
        self.win_line     = None          # ((x1,y1),(x2,y2)) para dibujar línea

        # Animación de celdas
        self._cell_anim   = {}   # pos → phase 0→1 (aparición de marca)
        self._flash       = {}   # pos → phase (destello candidato)

        # Hover
        self.hover_cell   = None

        # Último movimiento IA
        self.last_ai_move = None

        self._ai_pending  = False   # IA debe jugar pero esperando análisis
        self.analysis_scroll = 0

    def reset(self):
        self.__init__()

    def swap_human(self):
        self.human = PLAYER_O if self.human == PLAYER_X else PLAYER_X
        self.reset()
        # Si IA va primero, preparar análisis
        if players(self.board) != self.human:
            self._start_ai_analysis()

    def is_human_turn(self):
        if self.autoplay:
            return False
        return players(self.board) == self.human

    def human_play(self, col, row):
        """Jugada del humano en celda (col, row)."""
        if self.game_over or not self.is_human_turn():
            return
        if self.board[row][col] is not None:
            return
        move = (col, row)
        self.board = result(self.board, move)
        self._cell_anim[(col, row)] = 0.0
        self._check_terminal()
        if not self.game_over:
            self._start_ai_analysis()

    def _start_ai_analysis(self):
        """Inicia el generador de análisis para el turno de la IA."""
        if self.game_over:
            return
        self.gen        = candidate_generator(self.board)
        self.gen_states = []
        self.gen_done   = False
        self.analysis   = None
        self.candidates = []
        self.best_move  = None
        self._ai_pending= True
        self._flash     = {}
        self.analysis_scroll = 0

    def step_analysis(self):
        """Avanza un paso en el generador de análisis."""
        if self.gen is None or self.gen_done:
            return
        try:
            state = next(self.gen)
            self.gen_states.append(state)
            self.analysis = state

            # Actualizar flash de candidato actual
            if state["move"] is not None:
                self._flash[state["move"]] = 0.0

            if state["done"]:
                self.gen_done  = True
                self.playing   = False
                self.best_move = state["best_move"]
                self.candidates= state["evaluated"]
                self.nodes_total = state["nodes"]
                if not self.show_analysis:
                    # Sin análisis visible, aplicar jugada inmediatamente
                    self._apply_ai_move()
        except StopIteration:
            self.gen_done = True
            self.playing  = False

    def apply_best_move(self):
        """Aplica la jugada elegida por la IA al tablero."""
        if self.best_move is None:
            return
        self._apply_ai_move()

    def _apply_ai_move(self):
        if self.best_move is None or self.game_over:
            return
        move = self.best_move
        self.last_ai_move = move
        self.board = result(self.board, move)
        self._cell_anim[move] = 0.0
        self._ai_pending = False
        self._check_terminal()
        if not self.game_over:
            if self.autoplay:
                self._start_ai_analysis()
            # Si es turno humano, no iniciar análisis

    def _check_terminal(self):
        if terminal(self.board):
            self.game_over = True
            self.playing   = False
            w = utility(self.board)
            self.winner = PLAYER_X if w == 1 else (PLAYER_O if w == -1 else None)
            self.win_line = _find_win_line(self.board)

    def auto_step(self):
        if not self.playing or self.gen_done:
            return
        now = time.time()
        if now - self._last_step >= self.step_delay:
            self._last_step = now
            self.step_analysis()

    def tick(self, dt):
        # Animar aparición de marcas
        for k in list(self._cell_anim):
            self._cell_anim[k] = min(1.0, self._cell_anim[k] + dt * 5)
        # Animar flash de candidatos
        for k in list(self._flash):
            self._flash[k] = min(1.0, self._flash[k] + dt * 4)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS GEOMÉTRICOS
# ═══════════════════════════════════════════════════════════════════════════════

def cell_rect(col, row):
    x = GRID_PAD + col * CELL
    y = GRID_PAD + row * CELL
    return pygame.Rect(x, y, CELL, CELL)

def cell_from_pos(mx, my):
    col = (mx - GRID_PAD) // CELL
    row = (my - GRID_PAD) // CELL
    if 0 <= col < 3 and 0 <= row < 3:
        cx = GRID_PAD + col * CELL
        cy = GRID_PAD + row * CELL
        if cx <= mx < cx + CELL and cy <= my < cy + CELL:
            return int(col), int(row)
    return None

def _find_win_line(board):
    """Retorna ((cx1,cy1),(cx2,cy2)) de la línea ganadora, o None."""
    def center(col, row):
        return (GRID_PAD + col * CELL + CELL // 2,
                GRID_PAD + row * CELL + CELL // 2)

    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0]:
            return (center(0, row), center(2, row))
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col]:
            return (center(col, 0), center(col, 2))
    if board[0][0] == board[1][1] == board[2][2] and board[0][0]:
        return (center(0, 0), center(2, 2))
    if board[0][2] == board[1][1] == board[2][0] and board[0][2]:
        return (center(2, 0), center(0, 2))
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  RENDERIZADO
# ═══════════════════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, screen, fonts, state: AppState):
        self.screen = screen
        self.f      = fonts
        self.s      = state
        self.W, self.H = screen.get_size()

        # Panel x
        self.px = GRID_PAD * 2 + CELL * 3 + MARGIN
        self.py = MARGIN
        self.pw = PANEL_W
        self.ph = self.H - MARGIN * 2

        # Superficies para alpha blending
        self._surf_cell = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
        # Rects de interacción reales (evita desalineación de clics)
        self._button_rects = {}
        self._analysis_box_rect = None
        self.analysis_max_scroll = 0

    # ── Entry point ───────────────────────────────────────────────────────────
    def draw(self):
        self._button_rects = {}
        self.screen.fill(C["bg"])
        self._draw_board_bg()
        self._draw_grid()
        self._draw_marks()
        self._draw_win_line()
        self._draw_panel()
        pygame.display.flip()

    # ── Tablero ───────────────────────────────────────────────────────────────
    def _draw_board_bg(self):
        bw = CELL * 3 + LINE_W
        bh = CELL * 3 + LINE_W
        bx = GRID_PAD - LINE_W // 2
        by = GRID_PAD - LINE_W // 2
        bg_rect = pygame.Rect(bx - 10, by - 10, bw + 20, bh + 20)
        pygame.draw.rect(self.screen, C["bg2"], bg_rect, border_radius=16)
        pygame.draw.rect(self.screen, C["panel_b"], bg_rect, 2, border_radius=16)

    def _draw_grid(self):
        s   = self.s
        ss  = s.analysis
        best_move    = s.best_move
        candidates   = {m: v for m, v in s.candidates}
        current_move = ss["move"] if (ss and not ss["done"]) else None
        evaluated    = {m for m, v in ss["evaluated"]} if ss else set()

        for row in range(3):
            for col in range(3):
                pos  = (col, row)
                rect = cell_rect(col, row)
                mark = s.board[row][col]

                # Fondo de celda
                base_color = C["bg2"]

                # Hover (solo si celda libre y turno humano)
                is_hover = (s.hover_cell == pos and mark is None
                            and s.is_human_turn() and not s.game_over)

                # Candidato actual en exploración
                is_current = (current_move == pos)
                # Ya evaluado (no el actual)
                is_evaluated = (pos in evaluated and pos != current_move
                                and s.show_analysis)
                # Mejor movimiento final
                is_best = (pos == best_move and s.gen_done and s.show_analysis)

                if is_best:
                    color = _lerp(C["bg2"], C["best"], 0.22)
                elif is_current and s.show_analysis:
                    phase = s._flash.get(pos, 1.0)
                    color = _lerp(C["bg2"], C["candidate"], 0.18 * _ease(phase))
                elif is_evaluated:
                    color = _lerp(C["bg2"], C["accent"], 0.10)
                elif is_hover:
                    color = C["cell_hover"]
                else:
                    color = C["bg2"]

                pygame.draw.rect(self.screen, color, rect)

                # Borde de celda especial
                if is_best:
                    pygame.draw.rect(self.screen, C["best"], rect, 2, border_radius=4)
                elif is_current and s.show_analysis:
                    pygame.draw.rect(self.screen, C["candidate"], rect, 2, border_radius=4)

                # Valor del candidato encima (si aplica y análisis visible)
                if s.show_analysis and mark is None and pos in candidates:
                    val = candidates[pos]
                    vc  = _val_color(val)
                    lbl = f"{val:+d}" if val != 0 else "0"
                    surf = self.f["small_bold"].render(lbl, True, vc)
                    self.screen.blit(surf, surf.get_rect(center=(rect.centerx, rect.bottom - 18)))

        # Líneas de grilla
        for i in range(1, 3):
            x = GRID_PAD + i * CELL
            y = GRID_PAD + i * CELL
            pygame.draw.line(self.screen, C["grid_line"],
                             (x, GRID_PAD), (x, GRID_PAD + CELL * 3), LINE_W)
            pygame.draw.line(self.screen, C["grid_line"],
                             (GRID_PAD, y), (GRID_PAD + CELL * 3, y), LINE_W)

    def _draw_marks(self):
        s = self.s
        for row in range(3):
            for col in range(3):
                mark = s.board[row][col]
                if mark is None:
                    continue
                rect  = cell_rect(col, row)
                phase = _ease(s._cell_anim.get((col, row), 1.0))
                cx, cy = rect.centerx, rect.centery
                pad = 28

                if mark == PLAYER_X:
                    color = _lerp(C["bg2"], C["x_color"], phase)
                    p1 = (rect.x + pad, rect.y + pad)
                    p2 = (rect.right - pad, rect.bottom - pad)
                    p3 = (rect.right - pad, rect.y + pad)
                    p4 = (rect.x + pad, rect.bottom - pad)
                    # Dibujar desde centro hacia afuera según phase
                    _draw_x_animated(self.screen, cx, cy, pad, phase, color, MARK_W)
                else:
                    color = _lerp(C["bg2"], C["o_color"], phase)
                    r     = int((CELL // 2 - pad) * phase)
                    if r > 2:
                        pygame.draw.circle(self.screen, color, (cx, cy), r, MARK_W)

    def _draw_win_line(self):
        if not self.s.win_line:
            return
        p1, p2 = self.s.win_line
        t       = time.time()
        alpha   = 0.7 + 0.3 * math.sin(t * 3)
        color   = _lerp(C["win_line"], C["text_hi"], alpha * 0.4)
        pygame.draw.line(self.screen, color, p1, p2, 7)

    # ── Panel lateral ─────────────────────────────────────────────────────────
    def _draw_panel(self):
        px, py, pw, ph = self.px, self.py, self.pw, self.ph
        s = self.s

        panel_rect = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, C["panel"], panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, C["panel_b"], panel_rect, 2, border_radius=12)

        cy = py + 20

        # ── Título
        cy = self._title("TIC-TAC-TOE", px, cy, pw)
        cy += 4
        cy = self._subtitle("Minimax Visualizer", px, cy, pw)
        cy += 14

        # ── Estado del juego
        cy = self._section("Estado", px, cy, pw)
        turn_str  = players(s.board)
        is_human  = s.is_human_turn() and not s.game_over

        if s.game_over:
            if s.winner:
                col = C["x_color"] if s.winner == PLAYER_X else C["o_color"]
                cy  = self._kv("Resultado", f"Gana {s.winner}", px, cy, pw, val_col=col, bold=True)
            else:
                cy  = self._kv("Resultado", "Empate", px, cy, pw, val_col=C["zero"], bold=True)
        else:
            turn_col = C["x_color"] if turn_str == PLAYER_X else C["o_color"]
            who      = "Humano" if is_human else "IA"
            cy = self._kv("Turno", f"{turn_str}  ({who})", px, cy, pw, val_col=turn_col)

        human_lbl = f"Humano = {s.human}"
        cy = self._kv("Modo", "Auto-play" if s.autoplay else human_lbl,
                      px, cy, pw, val_col=C["accent"] if s.autoplay else C["text_dim"])
        cy += 10

        # ── Análisis Minimax (solo si hay algo)
        if s.show_analysis and (s.candidates or (s.analysis and not s.gen_done)):
            cy = self._section("Análisis Minimax", px, cy, pw)
            box = pygame.Rect(px + 14, cy, pw - 28, ANALYSIS_BOX_H)
            self._analysis_box_rect = box
            pygame.draw.rect(self.screen, C["btn"], box, border_radius=8)
            pygame.draw.rect(self.screen, C["panel_b"], box, 1, border_radius=8)
            self._draw_analysis_in_box(box)
            cy = box.bottom + 10
        elif not s.show_analysis:
            self._analysis_box_rect = None
            cy = self._section("Análisis", px, cy, pw)
            cy = self._dim_text("(oculto — pulsa H)", px, cy, pw)
            cy += 10
        else:
            self._analysis_box_rect = None

        # ── Botones
        cy = self._section("Controles", px, cy, pw)
        cy = self._buttons(px, cy, pw)
        cy += 10

        # ── Atajos
        cy = self._section("Atajos", px, cy, pw)
        shortcuts = [
            ("Clic",    "Jugar celda"),
            ("ESPACIO", "Play/Pause análisis"),
            ("N",       "Siguiente paso"),
            ("A",       "Auto-play IA vs IA"),
            ("H",       "Mostrar/ocultar análisis"),
            ("R",       "Reiniciar"),
            ("ESC",     "Salir"),
        ]
        for key, desc in shortcuts:
            cy = self._shortcut(key, desc, px, cy, pw)

    def _candidates_table(self, px, cy, pw):
        """Mini tabla de candidatos evaluados."""
        s = self.s
        fi = self.f["tiny"]
        hdr_color = C["text_dim"]
        row_h = 19
        col_w = [55, 55, 60, 70]  # col, fila, valor, barra
        xs = [px + 14, px + 68, px + 122, px + 178]

        # Cabecera
        for txt, x in zip(["Col", "Fila", "Valor", ""], xs):
            surf = fi.render(txt, True, hdr_color)
            self.screen.blit(surf, (x, cy))
        cy += row_h

        for move, val in s.candidates:
            mx, my = move
            is_best = (move == s.best_move)
            row_col = C["best"] if is_best else C["text"]

            for txt, x in zip([str(mx), str(my), f"{val:+d}"], xs[:3]):
                c   = _val_color(val) if txt.startswith(("+", "-", "0")) else row_col
                if is_best and not txt.startswith(("+", "-", "0")):
                    c = C["best"]
                surf = fi.render(txt, True, c)
                self.screen.blit(surf, (x, cy))

            # Barra visual del valor
            bar_x = xs[3]
            bar_w = 50
            bar_h = 10
            bar_y = cy + 4
            pygame.draw.rect(self.screen, C["panel_b"],
                             (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            frac  = (val + 1) / 2   # −1→0, 0→0.5, 1→1
            fill  = max(2, int(bar_w * frac))
            pygame.draw.rect(self.screen, _val_color(val),
                             (bar_x, bar_y, fill, bar_h), border_radius=3)
            if is_best:
                pygame.draw.rect(self.screen, C["best"],
                                 (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
            cy += row_h

        return cy

    def _draw_analysis_in_box(self, box):
        """Dibuja análisis dentro de un contenedor fijo con clipping y scroll."""
        s = self.s
        prev_clip = self.screen.get_clip()
        inner = box.inflate(-12, -10)
        self.screen.set_clip(inner)

        fi = self.f["tiny"]
        row_h = 19
        # Clamp scroll antes de dibujar
        if s.analysis_scroll < 0:
            s.analysis_scroll = 0
        y = inner.y - s.analysis_scroll

        # Resumen
        if s.best_move and s.gen_done:
            bx, by_ = s.best_move
            txt = fi.render(f"Mejor mov.: col {bx}, fila {by_}", True, C["best"])
            self.screen.blit(txt, (inner.x, y))
            y += row_h

        if s.analysis:
            a = s.analysis
            if not a["done"] and a["move"]:
                mx, my_ = a["move"]
                txt = fi.render(f"Evaluando: col {mx}, fila {my_}", True, C["candidate"])
                self.screen.blit(txt, (inner.x, y))
                y += row_h
            if a["best_so_far"] and a["best_so_far"][0]:
                _bm, bv = a["best_so_far"]
                txt = fi.render(f"Mejor actual: {bv:+d}", True, _val_color(bv))
                self.screen.blit(txt, (inner.x, y))
                y += row_h

        txt = fi.render(f"Nodos eval.: {s.nodes_total}", True, C["text"])
        self.screen.blit(txt, (inner.x, y))
        y += row_h

        # Tabla de candidatos
        if s.candidates:
            y += 3
            xs = [inner.x, inner.x + 40, inner.x + 82, inner.x + 126]
            for txt_h, x in zip(["Col", "Fila", "Valor", ""], xs):
                hdr = fi.render(txt_h, True, C["text_dim"])
                self.screen.blit(hdr, (x, y))
            y += row_h

            for move, val in s.candidates:
                mx, my_ = move
                is_best = (move == s.best_move)
                for txtv, x in zip([str(mx), str(my_), f"{val:+d}"], xs[:3]):
                    c = _val_color(val) if txtv.startswith(("+", "-", "0")) else (C["best"] if is_best else C["text"])
                    surf = fi.render(txtv, True, c)
                    self.screen.blit(surf, (x, y))

                bar_x, bar_y = xs[3], y + 4
                bar_w, bar_h = 44, 10
                pygame.draw.rect(self.screen, C["panel_b"], (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                frac = (val + 1) / 2
                fill = max(2, int(bar_w * frac))
                pygame.draw.rect(self.screen, _val_color(val), (bar_x, bar_y, fill, bar_h), border_radius=3)
                if is_best:
                    pygame.draw.rect(self.screen, C["best"], (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
                y += row_h

        # Indicador de scroll cuando hay overflow
        content_h = (y + s.analysis_scroll) - inner.y
        max_scroll = max(0, content_h - inner.height)
        self.analysis_max_scroll = max_scroll
        if s.analysis_scroll > max_scroll:
            s.analysis_scroll = max_scroll
        if max_scroll > 0:
            ind = fi.render("Scroll: rueda mouse", True, C["text_dim"])
            self.screen.blit(ind, (inner.x, inner.bottom - ind.get_height()))

        self.screen.set_clip(prev_clip)

    # ── Botones del panel ─────────────────────────────────────────────────────
    def _buttons(self, px, cy, pw):
        s      = self.s
        mouse  = pygame.mouse.get_pos()
        bh     = 34
        gap    = 6
        bw2    = (pw - 28 - gap) // 2

        btn_defs = [
            ("↺ Reiniciar",      "reset",       pw - 28, bh, px + 14),
            ("⇄ Cambiar turno",  "swap",        bw2,     bh, px + 14),
            ("IA vs IA" + (" ●" if s.autoplay else ""), "autoplay", bw2, bh, px + 14 + bw2 + gap),
            (("▶ Siguiente" if not s.playing else "⏸ Pause"),
             "step_play",    bw2, bh, px + 14),
            ("✓ Aplicar IA" if s.gen_done and not s.game_over else "  Aplicar IA",
             "apply",        bw2, bh, px + 14 + bw2 + gap),
            (("◎ Ocultar análisis" if s.show_analysis else "◎ Ver análisis"),
             "toggle_h",    pw - 28, bh, px + 14),
        ]

        for label, action, bw, bheight, bx in btn_defs:
            rect   = pygame.Rect(bx, cy, bw, bheight)
            hover  = rect.collidepoint(mouse)
            active = (action == "autoplay" and s.autoplay)
            enabled= True
            if action in ("step_play", "apply") and (s.game_over or s.gen is None):
                enabled = False
            if action == "apply" and not (s.gen_done and not s.game_over):
                enabled = False

            bg = C["btn_active"] if active else (C["btn_hover"] if hover and enabled else C["btn"])
            bc = C["accent"]     if active else C["btn_b"]
            tc = C["text"] if enabled else C["text_dim"]
            if not enabled:
                bg = tuple(max(0, v - 8) for v in C["btn"])

            pygame.draw.rect(self.screen, bg, rect, border_radius=7)
            pygame.draw.rect(self.screen, bc, rect, 1, border_radius=7)
            surf = self.f["small"].render(label, True, tc)
            self.screen.blit(surf, surf.get_rect(center=rect.center))
            self._button_rects[action] = rect

            if bx + bw >= px + pw - 14:   # fin de fila
                cy += bheight + gap

        return cy + 4

    def hit_button(self, mouse_pos):
        """Retorna el nombre de la acción si el clic cayó en un botón."""
        for action, rect in self._button_rects.items():
            if rect.collidepoint(mouse_pos):
                return action
        return None

    def point_in_analysis_box(self, mouse_pos):
        return self._analysis_box_rect is not None and self._analysis_box_rect.collidepoint(mouse_pos)

    # ── Helpers texto ─────────────────────────────────────────────────────────
    def _title(self, text, px, cy, pw):
        surf = self.f["title"].render(text, True, C["text_hi"])
        self.screen.blit(surf, surf.get_rect(centerx=px + pw // 2, top=cy))
        return cy + surf.get_height() + 2

    def _subtitle(self, text, px, cy, pw):
        surf = self.f["subtitle"].render(text, True, C["accent"])
        self.screen.blit(surf, surf.get_rect(centerx=px + pw // 2, top=cy))
        return cy + surf.get_height() + 2

    def _section(self, text, px, cy, pw):
        surf = self.f["small_bold"].render(text.upper(), True, C["accent"])
        self.screen.blit(surf, (px + 14, cy))
        ly = cy + surf.get_height() + 3
        pygame.draw.line(self.screen, C["panel_b"], (px + 14, ly), (px + pw - 14, ly))
        return ly + 6

    def _kv(self, key, val, px, cy, pw, val_col=None, bold=False):
        fk   = self.f["small"]
        fv   = self.f["small_bold"] if bold else self.f["small"]
        vc   = val_col or C["text"]
        if key:
            sk = fk.render(key + ":", True, C["text_dim"])
            self.screen.blit(sk, (px + 14, cy))
        sv = fv.render(val, True, vc)
        self.screen.blit(sv, (px + pw - 14 - sv.get_width(), cy))
        return cy + max(sv.get_height(), self.f["small"].size("X")[1]) + 4

    def _dim_text(self, text, px, cy, pw):
        surf = self.f["small"].render(text, True, C["text_dim"])
        self.screen.blit(surf, surf.get_rect(centerx=px + pw // 2, top=cy))
        return cy + surf.get_height() + 4

    def _shortcut(self, key, desc, px, cy, pw):
        sk = self.f["tiny_bold"].render(key, True, C["accent"])
        sd = self.f["tiny"].render(desc, True, C["text_dim"])
        self.screen.blit(sk, (px + 14, cy))
        self.screen.blit(sd, (px + pw - 14 - sd.get_width(), cy))
        return cy + max(sk.get_height(), sd.get_height()) + 2


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS DE DIBUJO
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_x_animated(screen, cx, cy, pad, phase, color, width):
    """Dibuja X animada desde el centro hacia afuera."""
    ext = int((CELL // 2 - pad) * phase)
    if ext < 2:
        return
    pygame.draw.line(screen, color, (cx - ext, cy - ext), (cx + ext, cy + ext), width)
    pygame.draw.line(screen, color, (cx + ext, cy - ext), (cx - ext, cy + ext), width)

def _ease(t):
    return 1 - (1 - t) ** 2

def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def _val_color(val):
    if val > 0:
        return C["x_color"]   # positivo = bueno para X
    elif val < 0:
        return C["o_color"]   # negativo = bueno para O
    return C["zero"]


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    pygame.display.set_caption("Tic-Tac-Toe — Minimax Visualizer")
    screen = pygame.display.set_mode((WIN_W, WIN_H))

    # Fuentes
    pygame.font.init()
    fn = pygame.font.match_font("garamond,georgiabold,times,freesans,dejavusans")
    fn_mono = pygame.font.match_font("couriernew,dejavusansmono,mono")

    def mf(name, size, bold=False):
        f = pygame.font.Font(name, size)
        if bold:
            f.set_bold(True)
        return f

    fonts = {
        "title":      mf(fn, 20, bold=True),
        "subtitle":   mf(fn, 13),
        "bold":       mf(fn, 16, bold=True),
        "small":      mf(fn, 13),
        "small_bold": mf(fn, 13, bold=True),
        "tiny":       mf(fn_mono, 11),
        "tiny_bold":  mf(fn_mono, 11),
    }
    fonts["tiny_bold"].set_bold(True)

    state    = AppState()
    renderer = Renderer(screen, fonts, state)
    clock    = pygame.time.Clock()
    prev     = time.time()

    # Si IA va primero, preparar análisis
    if not state.is_human_turn():
        state._start_ai_analysis()

    running = True
    while running:
        now = time.time()
        dt  = now - prev
        prev = now

        # ── Eventos ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                cell = cell_from_pos(*event.pos)
                state.hover_cell = cell

            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_r:
                    state.reset()
                    if not state.is_human_turn():
                        state._start_ai_analysis()
                elif k == pygame.K_SPACE:
                    if state.gen and not state.gen_done:
                        state.playing = not state.playing
                        state._last_step = time.time()
                elif k == pygame.K_n:
                    state.step_analysis()
                elif k == pygame.K_a:
                    state.autoplay = not state.autoplay
                    if state.autoplay and not state.game_over:
                        state._start_ai_analysis()
                elif k == pygame.K_h:
                    state.show_analysis = not state.show_analysis
                elif k == pygame.K_UP:
                    state.analysis_scroll = max(0, state.analysis_scroll - 18)
                elif k == pygame.K_DOWN:
                    state.analysis_scroll = min(renderer.analysis_max_scroll, state.analysis_scroll + 18)

            elif event.type == pygame.MOUSEWHEEL:
                mp = pygame.mouse.get_pos()
                if renderer.point_in_analysis_box(mp):
                    # event.y > 0 = rueda arriba
                    state.analysis_scroll = max(
                        0,
                        min(renderer.analysis_max_scroll, state.analysis_scroll - event.y * 22)
                    )

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mp = event.pos
                # Botones del panel
                action = renderer.hit_button(mp)
                if action == "reset":
                    state.reset()
                    if not state.is_human_turn():
                        state._start_ai_analysis()
                elif action == "swap":
                    state.swap_human()
                elif action == "autoplay":
                    state.autoplay = not state.autoplay
                    if state.autoplay and not state.game_over:
                        state._start_ai_analysis()
                elif action == "step_play":
                    if state.playing:
                        state.playing = False
                    else:
                        if state.gen_done:
                            pass
                        else:
                            state.playing = True
                            state._last_step = time.time()
                elif action == "apply":
                    state.apply_best_move()
                    if state.autoplay and not state.game_over:
                        state._start_ai_analysis()
                elif action == "toggle_h":
                    state.show_analysis = not state.show_analysis
                else:
                    # Clic en tablero
                    cell = cell_from_pos(*mp)
                    if cell and state.is_human_turn() and not state.game_over:
                        col, row = cell
                        state.human_play(col, row)

        # ── Lógica ────────────────────────────────────────────────────────────
        state.auto_step()

        # Auto-apply cuando análisis termina en autoplay o análisis oculto
        if state.gen_done and state._ai_pending and not state.game_over:
            if state.autoplay or not state.show_analysis:
                state._apply_ai_move()
                if state.autoplay and not state.game_over:
                    time.sleep(0.3)
                    state._start_ai_analysis()
                    # Auto-completar si análisis oculto
                    if not state.show_analysis:
                        while not state.gen_done:
                            state.step_analysis()

        state.tick(dt)

        # ── Render ────────────────────────────────────────────────────────────
        renderer.draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
