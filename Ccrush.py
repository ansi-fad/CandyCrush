import tkinter as tk
# Importăm biblioteca tkinter pentru a construi interfața grafică

from tkinter import ttk
# Importăm widget-uri moderne (buton, label, spinbox) din tkinter.ttk

import random
# Importăm modulul random pentru a genera bomboane aleatorii


# ================= CONSTANTE =================

COLOR_MAP = {
    0: '#eeeeee',      # Culoare pentru celula goală
    1: '#e74c3c',      # Culoare pentru bomboana tip 1 (roșu)
    2: '#f39c12',      # Culoare pentru bomboana tip 2 (portocaliu)
    3: '#2ecc71',      # Culoare pentru bomboana tip 3 (verde)
    4: '#3498db'       # Culoare pentru bomboana tip 4 (albastru)
}

CELL_SIZE = 40
# Dimensiunea fiecărei celule în pixeli

PADDING = 6
# Spațiu între celule

SWAP_COLOR = '#8e44ad'
# Culoare pentru evidențierea celulelor care se mută

MATCH_COLOR = '#c0392b'
# Culoare pentru evidențierea celulelor care fac match


# ================= LOGICA =================

class Formation:
    # Clasa care reprezintă o formație de bomboane (linie de minim 3)
    def __init__(self, cells):
        self.cells = set(cells)
        # Stocăm coordonatele celulelor care fac parte din formație (set pentru unicitate)
        self.score = len(self.cells) * 10
        # Scorul este proporțional cu numărul de celule


class Board:
    # Clasa care conține logica jocului (tabla)
    def __init__(self, rows, cols, seed=None):
        self.rows = rows
        # Număr de rânduri
        self.cols = cols
        # Număr de coloane
        self.rng = random.Random(seed)
        # Generator random controlat de seed
        self.grid = [
            [self.rng.randint(1, 4) for _ in range(cols)]
            for _ in range(rows)
        ]
        # Inițializăm tabla cu bomboane random

    def in_bounds(self, r, c):
        # Verifică dacă o poziție (r, c) este în interiorul tablei
        return 0 <= r < self.rows and 0 <= c < self.cols

    def cell(self, r, c):
        # Returnează valoarea celulei de la rândul r și coloana c
        return self.grid[r][c]

    def swap(self, a, b):
        # Schimbă valorile a două celule între ele
        (r1, c1), (r2, c2) = a, b
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

    def detect_formations(self):
        # Detectează toate liniile (orizontale și verticale) de minim 3 bomboane identice
        forms = []  # Lista de formații detectate

        # Detectare orizontală
        for r in range(self.rows):
            c = 0
            while c < self.cols - 2:  # Cel puțin 3 celule pentru a face o linie
                v = self.grid[r][c]
                if v != 0 and self.grid[r][c+1] == v and self.grid[r][c+2] == v:
                    cells = [(r, c), (r, c+1), (r, c+2)]
                    c2 = c + 3
                    while c2 < self.cols and self.grid[r][c2] == v:
                        cells.append((r, c2))
                        c2 += 1
                    forms.append(Formation(cells))
                    c = c2
                else:
                    c += 1

        # Detectare verticală
        for c in range(self.cols):
            r = 0
            while r < self.rows - 2:  # Cel puțin 3 celule pentru a face o linie
                v = self.grid[r][c]
                if v != 0 and self.grid[r+1][c] == v and self.grid[r+2][c] == v:
                    cells = [(r, c), (r+1, c), (r+2, c)]
                    r2 = r + 3
                    while r2 < self.rows and self.grid[r2][c] == v:
                        cells.append((r2, c))
                        r2 += 1
                    forms.append(Formation(cells))
                    r = r2
                else:
                    r += 1

        return forms
        # Returnează lista de formații detectate

    def apply_eliminations(self, forms):
        # Elimină bomboanele din formații (le setează la 0)
        for f in forms:
            for r, c in f.cells:
                self.grid[r][c] = 0

    def apply_gravity_and_refill(self):
        # Aplica gravitația și reumple tabla cu bomboane random
        for c in range(self.cols):
            write = self.rows - 1
            for r in range(self.rows - 1, -1, -1):
                if self.grid[r][c] != 0:
                    self.grid[write][c] = self.grid[r][c]
                    write -= 1
            for r in range(write, -1, -1):
                self.grid[r][c] = self.rng.randint(1, 4)


# ================= UI =================

class CandyUI:
    # Clasa care se ocupă de interfața grafică și interacțiunea cu jucătorul
    def __init__(self, root):
        self.root = root
        # Fereastra principală
        self.board = Board(11, 11)
        # Tabla de joc
        self.score = 0
        # Scor total
        self.swaps = 0
        # Număr de mutări
        self.running = False
        # Flag pentru rularea automată

        self.swap_cells = set()
        # Celulele evidențiate la mutare
        self.match_cells = set()
        # Celulele evidențiate la match

        self.speed = 1400
        # Viteza inițială a animației (în ms)

        ctrl = ttk.Frame(root)
        # Creăm un frame pentru controale
        ctrl.pack(pady=6)
        # Plasăm frame-ul cu padding vertical

        ttk.Button(ctrl, text="Play", command=self.start).pack(side='left')
        # Buton Play care pornește jocul

        ttk.Button(ctrl, text="Stop", command=self.stop).pack(side='left', padx=5)
        # Buton Stop care oprește jocul

        ttk.Label(ctrl, text="Speed (ms):").pack(side='left', padx=10)
        # Etichetă pentru controlul vitezei

        self.speed_var = tk.IntVar(value=self.speed)
        # Variabilă pentru spinbox care controlează viteza

        ttk.Spinbox(
            ctrl, from_=300, to=3000, increment=200,
            textvariable=self.speed_var, width=6
        ).pack(side='left')
        # Spinbox pentru a ajusta viteza în milisecunde

        self.status = ttk.Label(ctrl, text="")
        # Label pentru afișarea scorului și numărului de mutări
        self.status.pack(side='left', padx=20)

        w = 11 * (CELL_SIZE + PADDING) + PADDING
        h = 11 * (CELL_SIZE + PADDING) + PADDING
        # Calculăm dimensiunea canvas-ului

        self.canvas = tk.Canvas(root, width=w, height=h, bg='white')
        # Creăm canvas-ul unde se va desena tabla
        self.canvas.pack()

        self.draw()
        # Desenăm tabla inițială
        self.update_status()
        # Actualizăm scorul și numărul de mutări

    def start(self):
        # Pornește rularea automată a jocului
        self.running = True
        self.loop()

    def stop(self):
        # Oprește jocul
        self.running = False
        self.swap_cells.clear()
        self.match_cells.clear()
        self.draw()
        # Șterge evidențierile și redesenează tabla

    def loop(self):
        # Bucla principală de rulare a jocului
        if not self.running:
            return

        self.speed = max(200, int(self.speed_var.get()))
        # Actualizează viteza conform spinbox-ului, minim 200ms

        move = self.find_any_swap()
        # Caută o mutare validă care să genereze un match
        if move is None:
            self.running = False
            return

        a, b = move
        # Coordonatele celulelor care se vor schimba
        self.swap_cells = {a, b}
        # Evidențiază mutarea
        self.draw()

        self.root.after(self.speed, lambda: self.apply_swap(a, b))
        # Aplică mutarea după delay-ul specificat de viteză

    def apply_swap(self, a, b):
        # Aplică mutarea pe tabla reală
        self.swap_cells.clear()
        # Șterge evidențierea mutării
        self.board.swap(a, b)
        # Schimbă valorile celulelor
        self.swaps += 1
        # Crește numărul de mutări
        self.draw()
        self.update_status()
        # Redesenăm tabla și actualizăm scorul
        self.root.after(self.speed, self.resolve_step)
        # Trecem la rezolvarea match-urilor după delay

    def resolve_step(self):
        # Rezolvă un pas de eliminare a match-urilor
        forms = self.board.detect_formations()
        if not forms:
            self.root.after(self.speed, self.loop)
            # Dacă nu există match-uri, continuăm cu următoarea mutare
            return

        self.match_cells = set()
        for f in forms:
            self.match_cells |= f.cells
        # Evidențiem celulele care fac match

        self.draw()
        self.root.after(self.speed, lambda: self.apply_forms(forms))
        # Aplicăm eliminările după delay

    def apply_forms(self, forms):
        # Aplică eliminarea bomboanelor și refill
        self.score += sum(f.score for f in forms)
        # Adăugăm punctele obținute
        self.board.apply_eliminations(forms)
        # Eliminăm bomboanele
        self.board.apply_gravity_and_refill()
        # Aplica gravitația și refill
        self.match_cells.clear()
        self.draw()
        self.update_status()
        self.root.after(self.speed, self.resolve_step)
        # Continuăm cu următoarele match-uri

    def find_any_swap(self):
        # Găsește prima mutare validă (care generează match)
        for r in range(11):
            for c in range(11):
                for dr, dc in ((1, 0), (0, 1)):
                    r2, c2 = r + dr, c + dc
                    if not self.board.in_bounds(r2, c2):
                        continue
                    copy = Board(11, 11)
                    copy.grid = [row[:] for row in self.board.grid]
                    # Cream o copie a tablei pentru simulare
                    copy.swap((r, c), (r2, c2))
                    if copy.detect_formations():
                        return (r, c), (r2, c2)
        return None
        # Nicio mutare validă găsită

    def draw(self):
        # Desenează tabla de joc
        self.canvas.delete("all")
        # Șterge toate elementele anterioare
        for r in range(11):
            for c in range(11):
                v = self.board.cell(r, c)
                # Valoarea bomboanei
                x1 = PADDING + c * (CELL_SIZE + PADDING)
                y1 = PADDING + r * (CELL_SIZE + PADDING)
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                outline = 'black'
                width = 2

                if (r, c) in self.swap_cells:
                    outline = SWAP_COLOR
                    width = 5
                    # Evidențiază celulele mutate
                elif (r, c) in self.match_cells:
                    outline = MATCH_COLOR
                    width = 5
                    # Evidențiază celulele care fac match

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLOR_MAP[v],
                    outline=outline,
                    width=width
                )
                # Creăm dreptunghiul pentru celulă

    def update_status(self):
        # Actualizează scorul și numărul de mutări
        self.status.config(text=f"Score: {self.score} | Swaps: {self.swaps}")


# ================= MAIN =================

if __name__ == "__main__":
    # Punctul de pornire al programului
    root = tk.Tk()
    # Creăm fereastra principală
    root.title("Candy Crush - Single File Full Demo")
    # Setăm titlul ferestrei
    CandyUI(root)
    # Inițializăm interfața CandyUI
    root.mainloop()
    # Pornim bucla principală Tkinter
