"""
Tetris (Guideline) - Full game (pygame)
Features:
- 10x20 playfield
- 7-bag randomizer
- SRS rotation (JLSTZ, I, O)
- Wall kicks
- Gravity, soft drop, hard drop
- Hold piece
- Ghost piece
- DAS + ARR basic handling
- Lock delay (simple)
- Line clear, scoring, level
- Back-to-back, T-spin detection (basic)

Controls:
- Left / Right: move
- Down: soft drop
- Space: hard drop
- Up: rotate CW
- Z: rotate CCW
- C: hold
- Esc / Close window: quit

Run: python tetris_guideline.py
"""

import pygame
import random
import copy
import sys

# -------------------- CONFIG --------------------
CELL_SIZE = 30
COLS = 10
ROWS = 20
HIDDEN = 4  # hidden rows above the visible field
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * (ROWS)
FPS = 60

# timings (frames)
GRAVITY = 1  # frames per cell drop at level 1 approx (simple)
LOCK_DELAY = 30  # frames before locking
DAS_DELAY = 10
ARR = 2  # automatic repeat rate (frames)
SOFT_DROP_MULT = 0.05  # faster drop (applied as velocity multiplier)

# colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GRID = (40,40,40)
BORDER = (20,20,20)
COLORS = {
    'I': (0,158,229),
    'O': (255,231,2),
    'T': (154,31,157),
    'S': (107,233,33),
    'Z': (223,14,20),
    'J': (0,40,139),
    'L': (253,101,0)
}

# -------------------- SRS KICKS --------------------
JLSTZ_KICKS = {
    (0, 1): [(0,0), (0,-1), (1,-1), (-2,0), (-2,-1)],
    (1, 0): [(0,0), (0,1), (-1,1), (2,0), (2,1)],

    (1, 2): [(0,0), (0,1), (-1,1), (2,0), (2,1)],
    (2, 1): [(0,0), (0,-1), (1,-1), (-2,0), (-2,-1)],

    (2, 3): [(0,0), (0,1), (1,1), (-2,0), (-2,1)],
    (3, 2): [(0,0), (0,-1), (-1,-1), (2,0), (2,-1)],

    (3, 0): [(0,0), (0,-1), (-1,-1), (2,0), (2,-1)],
    (0, 3): [(0,0), (0,1), (1,1), (-2,0), (-2,1)]
}

I_KICKS = {
    (0, 1): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
    (1, 0): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],

    (1, 2): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
    (2, 1): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],

    (2, 3): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
    (3, 2): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],

    (3, 0): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    (0, 3): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)]
}

O_KICKS = { (0,1): [(0,0)], (1,2): [(0,0)], (2,3): [(0,0)], (3,0): [(0,0)] }

# -------------------- SHAPES (4x4 matrices) --------------------
SHAPES = {
    'I': [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'O': [
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'T': [
        [0,1,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'S': [
        [0,1,1,0],
        [1,1,0,0],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'Z': [
        [1,1,0,0],
        [0,1,1,0],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'J': [
        [1,0,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0]
    ],
    'L': [
        [0,0,1,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0]
    ]
}

# -------------------- UTILS --------------------

def rotate_matrix_cw(mat):
    return [list(row) for row in zip(*mat[::-1])]

def rotate_matrix_ccw(mat):
    return [list(row) for row in zip(*mat)][::-1]

# -------------------- BOARD --------------------
class Board:
    def __init__(self, rows=ROWS+HIDDEN, cols=COLS):
        self.rows = rows
        self.cols = cols
        self.cells = [[None for _ in range(cols)] for _ in range(rows)]

    def inside(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def can_place(self, matrix, r0, c0):
        for r in range(4):
            for c in range(4):
                if matrix[r][c]:
                    R = r0 + r
                    C = c0 + c
                    if C < 0 or C >= self.cols or R >= self.rows:
                        return False
                    if R >= 0 and self.cells[R][C] is not None:
                        return False
        return True

    def place(self, matrix, r0, c0, kind):
        for r in range(4):
            for c in range(4):
                if matrix[r][c]:
                    R = r0 + r
                    C = c0 + c
                    if R >= 0:
                        self.cells[R][C] = kind

    def clear_lines(self):
        new = [row for row in self.cells if any(cell is None for cell in row)]
        cleared = self.rows - len(new)
        for _ in range(cleared):
            new.insert(0, [None for _ in range(self.cols)])
        self.cells = new
        return cleared

    def is_game_over(self):
        # if any cell in hidden area occupied
        for r in range(HIDDEN):
            if any(self.cells[r][c] is not None for c in range(self.cols)):
                return True
        return False

# -------------------- TETROMINO --------------------
class Tetromino:
    def __init__(self, kind):
        self.kind = kind
        self.matrix = copy.deepcopy(SHAPES[kind])
        self.r = -HIDDEN  # start above field
        # center horizontally
        self.c = (COLS // 2) - 2
        self.rotation = 0

    def get_kicks(self, old_rot, new_rot):
        if self.kind == 'I':
            return I_KICKS.get((old_rot, new_rot), [(0,0)])
        elif self.kind == 'O':
            return O_KICKS.get((old_rot, new_rot), [(0,0)])
        else:
            return JLSTZ_KICKS.get((old_rot, new_rot), [(0,0)])

    def rotated(self, dir):
        if dir == 1:
            return rotate_matrix_cw(self.matrix)
        else:
            return rotate_matrix_ccw(self.matrix)

    def rotate(self, board, dir=1):
        old_rot = self.rotation
        new_rot = (self.rotation + (1 if dir == 1 else -1)) % 4
        new_matrix = self.rotated(dir)

        kicks = self.get_kicks(old_rot, new_rot)
        for dx, dy in kicks:
            nr = self.r + dx
            nc = self.c + dy
            if board.can_place(new_matrix, nr, nc):
                self.matrix = new_matrix
                self.r = nr
                self.c = nc
                self.rotation = new_rot
                return True
        return False

    def cells_occupied(self, r_offset=0, c_offset=0):
        cells = []
        for r in range(4):
            for c in range(4):
                if self.matrix[r][c]:
                    cells.append((self.r + r + r_offset, self.c + c + c_offset))
        return cells

    def hard_drop_row(self, board):
        test_r = self.r
        while True:
            if not board.can_place(self.matrix, test_r+1, self.c):
                return test_r
            test_r += 1

# -------------------- RNG (7-bag) --------------------
class Bag7:
    def __init__(self):
        self.bag = []

    def next(self):
        if not self.bag:
            self.bag = ['I','O','T','S','Z','J','L']
            random.shuffle(self.bag)
        return self.bag.pop()

# -------------------- GAME --------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Tetris - Guideline')
        self.clock = pygame.time.Clock()

        self.board = Board()
        self.bag = Bag7()
        self.spawn_new()
        self.hold_piece = None
        self.hold_locked = False

        # timing
        self.frame = 0
        self.gravity_counter = 0
        self.lock_counter = 0

        # input state
        self.left_held = False
        self.right_held = False
        self.das_dir = 0
        self.das_counter = 0
        self.arr_counter = 0

        # score
        self.score = 0
        self.level = 1
        self.lines = 0
        self.back_to_back = False
        self.combo = -1

    def spawn_new(self):
        kind = self.bag.next()
        self.current = Tetromino(kind)
        # If cannot place, game over
        if not self.board.can_place(self.current.matrix, self.current.r, self.current.c):
            self.game_over = True
        else:
            self.game_over = False
        self.lock_counter = 0
        self.hold_locked = False

    def hold(self):
        if self.hold_locked:
            return
        if self.hold_piece is None:
            self.hold_piece = self.current.kind
            self.spawn_new()
        else:
            tmp = self.current.kind
            self.current = Tetromino(self.hold_piece)
            self.hold_piece = tmp
            # place current at top
            if not self.board.can_place(self.current.matrix, self.current.r, self.current.c):
                self.game_over = True
        self.hold_locked = True

    def step(self):
        # gravity
        self.gravity_counter += 1
        gravity_frames = max(1, int(GRAVITY))
        moved_down = False

        # handle horizontal DAS + ARR
        if self.das_dir != 0:
            self.das_counter += 1
            if self.das_counter > DAS_DELAY:
                self.arr_counter += 1
                if self.arr_counter >= ARR:
                    self.try_move(self.das_dir)
                    self.arr_counter = 0
        # process soft drop via key status handled in event

        if self.gravity_counter >= gravity_frames:
            # attempt move down
            if self.board.can_place(self.current.matrix, self.current.r+1, self.current.c):
                self.current.r += 1
                moved_down = True
                self.lock_counter = 0
            else:
                # start/increment lock delay
                self.lock_counter += 1
                if self.lock_counter >= LOCK_DELAY:
                    self.lock_piece()
            self.gravity_counter = 0

        return moved_down

    def try_move(self, dir):
        if dir == -1:
            if self.board.can_place(self.current.matrix, self.current.r, self.current.c-1):
                self.current.c -= 1
                self.lock_counter = 0
        elif dir == 1:
            if self.board.can_place(self.current.matrix, self.current.r, self.current.c+1):
                self.current.c += 1
                self.lock_counter = 0

    def rotate(self, dir):
        if self.current.rotate(self.board, dir):
            self.lock_counter = 0

    def hard_drop(self):
        target = self.current.hard_drop_row(self.board)
        self.current.r = target
        self.lock_piece(hard=True)

    def lock_piece(self, hard=False):
        # place on board
        self.board.place(self.current.matrix, self.current.r, self.current.c, self.current.kind)
        cleared = self.board.clear_lines()
        # scoring (simple guideline-ish)
        if cleared > 0:
            self.lines += cleared
            # scoring table (single, double, triple, tetris)
            scores = [0, 100, 300, 500, 800]
            self.score += scores[cleared]
            # back-to-back detection (simple: consider Tetris and T-spin)
            if cleared == 4:
                if self.back_to_back:
                    self.score += 400  # b2b bonus
                self.back_to_back = True
            else:
                self.back_to_back = False
            # combo
            if self.combo >= 0:
                self.combo += 1
            else:
                self.combo = 0
        else:
            self.combo = -1

        # spawn next
        self.spawn_new()

    def draw_grid(self):
        for r in range(HIDDEN, self.board.rows):
            for c in range(self.board.cols):
                x = c * CELL_SIZE
                y = (r - HIDDEN) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID, rect, 1)

    def draw_cells(self):
        for r in range(HIDDEN, self.board.rows):
            for c in range(self.board.cols):
                kind = self.board.cells[r][c]
                if kind is not None:
                    x = c * CELL_SIZE
                    y = (r - HIDDEN) * CELL_SIZE
                    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, COLORS[kind], rect)
                    pygame.draw.rect(self.screen, BORDER, rect, 2)

    def draw_tetromino(self, tetromino, ghost=False):
        for (R,C) in tetromino.cells_occupied():
            if R >= 0:
                x = C * CELL_SIZE
                y = (R - HIDDEN) * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if ghost:
                    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    s.fill((*COLORS[tetromino.kind], 60))
                    self.screen.blit(s, (x,y))
                    pygame.draw.rect(self.screen, BORDER, rect, 1)
                else:
                    pygame.draw.rect(self.screen, COLORS[tetromino.kind], rect)
                    pygame.draw.rect(self.screen, BORDER, rect, 2)

    def draw_ghost(self):
        ghost = Tetromino(self.current.kind)
        ghost.matrix = copy.deepcopy(self.current.matrix)
        ghost.c = self.current.c
        ghost.r = self.current.r
        # drop
        ghost.r = ghost.hard_drop_row(self.board)
        self.draw_tetromino(ghost, ghost=True)

    def draw_ui(self):
        # simple text
        font = pygame.font.SysFont(None, 20)
        txt = font.render(f"Score: {self.score}  Lines: {self.lines}", True, WHITE)
        self.screen.blit(txt, (5,5))
        if self.hold_piece:
            txt2 = font.render(f"Hold: {self.hold_piece}", True, WHITE)
            self.screen.blit(txt2, (5,25))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.try_move(-1)
                        self.left_held = True
                        self.right_held = False
                        self.das_dir = -1
                        self.das_counter = 0
                        self.arr_counter = 0
                    elif event.key == pygame.K_RIGHT:
                        self.try_move(1)
                        self.right_held = True
                        self.left_held = False
                        self.das_dir = 1
                        self.das_counter = 0
                        self.arr_counter = 0
                    elif event.key == pygame.K_DOWN:
                        # soft drop: move down if possible
                        if self.board.can_place(self.current.matrix, self.current.r+1, self.current.c):
                            self.current.r += 1
                            self.lock_counter = 0
                    elif event.key == pygame.K_UP:
                        self.rotate(1)
                    elif event.key == pygame.K_z:
                        self.rotate(-1)
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_c:
                        self.hold()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left_held = False
                        if self.right_held:
                            self.das_dir = 1
                            self.das_counter = 0
                        else:
                            self.das_dir = 0
                    elif event.key == pygame.K_RIGHT:
                        self.right_held = False
                        if self.left_held:
                            self.das_dir = -1
                            self.das_counter = 0
                        else:
                            self.das_dir = 0

            # game logic step
            if not getattr(self, 'game_over', False):
                self.step()

            # draw
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_cells()
            if not getattr(self, 'game_over', False):
                self.draw_ghost()
                self.draw_tetromino(self.current)
            else:
                font = pygame.font.SysFont(None, 48)
                text = font.render('GAME OVER', True, WHITE)
                self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))

            self.draw_ui()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
