import pygame
import numpy as np
import random

class Ship:
    def __init__(self, size, orientation='H', position=(0,0), placed=False):
        self.size = size
        self.orientation = orientation
        self.position = position
        self.hits = 0
        self.placed = placed

    def is_sunk(self):
        return self.hits >= self.size
    
    def contains(self, row, col):
        r0, c0 = self.position
        for i in range(self.size):
            rr = r0 + (i if self.orientation == 'V' else 0)
            cc = c0 + (i if self.orientation == 'H' else 0)
            if rr == row and cc == col:
                return True
        return False
    
    # def get_outline_cells(self):
        r0, c0 = self.position
        cells = []

        if self.orientation == 'H':
            r1, r2 = r0 - 1, r0 + 1
            c1, c2 = c0 - 1, c0 + self.size
        else:
            r1, r2 = r0 - 1, r0 + self.size
            c1, c2 = c0 - 1, c0 + 1

        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if not self.contains(r, c):
                    cells.append((r, c))

        return cells

def put_ships_randoms(board, ships):
    grid = board.cells

    for ship in ships:
        ship.placed = False
        while not ship.placed:
            orientation = random.choice(['H', 'V'])
            ship.orientation = orientation

            if orientation == 'H':
                row = random.randint(0, board.rows - 1)
                col = random.randint(0, board.cols - ship.size)
            else:
                row = random.randint(0, board.rows - ship.size)
                col = random.randint(0, board.cols - 1)

            can_place = True
            for i in range(ship.size):
                r = row + (i if orientation == 'V' else 0)
                c = col + (i if orientation == 'H' else 0)
                if grid[r][c] != 1:
                    can_place = False
                    break

            if can_place:
                ship.position = (row, col)
                ship.placed = True
                for i in range(ship.size):
                    r = row + (i if orientation == 'V' else 0)
                    c = col + (i if orientation == 'H' else 0)
                    grid[r][c] = 2

def text_sunk_ships(window, sunk_list, start_x, start_y):
    font = pygame.font.SysFont(None, 32)
    title = font.render("SUNK SHIPS:", True, (255, 255, 0))
    window.blit(title, (start_x, start_y))

    dy = 40
    for ship in sunk_list:
        text = font.render(f"Ship size {ship.size}", True, WHITE)
        window.blit(text, (start_x, start_y + dy))
        dy += 30

class Board:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height

        self.cells = np.zeros((rows, cols), dtype=int)    
        self.clicked = np.zeros((rows, cols), dtype=int)

        self.block_w = width // cols
        self.block_h = height // rows

    def randomize_beach(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c] = 1

    def cell_from_mouse(self, pos):
        x, y = pos
        return y // self.block_h, x // self.block_w

    def click_cell(self, row, col):
        if self.clicked[row][col] == 0:
            self.clicked[row][col] = 1
            shots_fired = True
            return shots_fired

    def draw(self, window):
        for r in range(self.rows):
            for c in range(self.cols):
                rect = (c*self.block_w, r*self.block_h, self.block_w, self.block_h)

                if self.clicked[r][c] == 1:
                    if self.cells[r][c] == 2:
                        pygame.draw.rect(window, RED, rect)
                    else:
                        pygame.draw.rect(window, BLACK, rect)
                else:
                    pygame.draw.rect(window, WHITE, rect, 1)

    def draw_ship_outline(self, window, ship):
        r0, c0 = ship.position

        if ship.orientation == 'H':
            x = c0 * self.block_w
            y = r0 * self.block_h
            w = ship.size * self.block_w
            h = self.block_h
        else:
            x = c0 * self.block_w
            y = r0 * self.block_h
            w = self.block_w
            h = ship.size * self.block_h

        padding = 1
        rect = (x - padding, y - padding, w + padding*2, h + padding*2)
        pygame.draw.rect(window, (255, 255, 0), rect, 3)

# ===================== GAME STATES =====================

pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Ship")
clock = pygame.time.Clock()

WHITE = (255,255,255)
BLUE  = (0,0,255)
BLACK = (0,0,0)
RED   = (255,0,0)

ROWS = COLS = 10
GRID_SIZE = HEIGHT

font_big = pygame.font.SysFont(None, 72)
font_small = pygame.font.SysFont(None, 40)

# ===================== MAIN LOOP =====================

STATE_START = 0
STATE_PLAYING = 1
STATE_END = 2

state = STATE_START
shots = 0

def reset_game():
    global BOARD, ships, sunk_ships, shots
    BOARD = Board(ROWS, COLS, GRID_SIZE, GRID_SIZE)
    BOARD.randomize_beach()
    ships = [Ship(2), Ship(3), Ship(3), Ship(4), Ship(5)]
    put_ships_randoms(BOARD, ships)
    sunk_ships = []
    shots = 0

reset_game()

# ===================== MAIN LOOP =====================

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_START:
                state = STATE_PLAYING

            elif state == STATE_END:
                reset_game()
                state = STATE_PLAYING

            elif state == STATE_PLAYING:
                r, c = BOARD.cell_from_mouse(pygame.mouse.get_pos())
                
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if BOARD.click_cell(r, c):
                        shots += 1

                    if BOARD.cells[r][c] == 2:
                        for ship in ships:
                            if ship.contains(r, c):
                                ship.hits += 1
                                if ship.is_sunk() and ship not in sunk_ships:
                                    sunk_ships.append(ship)
                                break

                if len(sunk_ships) == len(ships):
                    state = STATE_END

    window.fill(BLUE)

    if state == STATE_START:
        text = font_big.render("BATTLE SHIP", True, WHITE)
        sub = font_small.render("Click to Start", True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
        window.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

    elif state == STATE_END:
        text = font_big.render("YOU WIN!", True, WHITE)
        sub = font_small.render(f"Shots taken: {shots}. Click to Restart", True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
        window.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

    elif state == STATE_PLAYING:
        BOARD.draw(window)

        for ship in sunk_ships:
            BOARD.draw_ship_outline(window, ship)

        text_sunk_ships(window, sunk_ships, GRID_SIZE + 10, 20)
        shot_txt = font_small.render(f"Shots: {shots}", True, WHITE)
        window.blit(shot_txt, (GRID_SIZE + 10, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(60)
