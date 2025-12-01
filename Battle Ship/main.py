import pygame
import numpy as np
import math
import random

class Ship:
    def __init__(self, size, orientation = 'H', position = (0,0),placed = False):
        self.size = size  # size of the ship (number of blocks)
        self.orientation = orientation  # 'H' for horizontal, 'V' for vertical
        self.position = position  # (row, col) starting position
        self.hits = 0  # number of hits taken
        self.placed = placed  # the ship is placed on the board or not
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))


    def is_sunk(self):
        return self.hits >= self.size

def beach_matrix(rows, cols):
    matrix = np.zeros((rows, cols), dtype=int)
    for i in range(rows):
        for j in range(cols):
            # if random.random() < 0.2:
            matrix[i][j] = 1  # 1 represents a beach
    return matrix

def draw_beach(window, beach):
    block_width = broad_width // beach.shape[1]
    block_height = broad_height // beach.shape[0]
    for i in range(beach.shape[0]):
        for j in range(beach.shape[1]):
            if beach[i][j] == 1:
                pygame.draw.rect(window, WHITE, (j * block_width, i * block_height, block_width, block_height), 1)

def draw_ships(window, beach, ships):
    block_width = broad_width // beach.shape[1]
    block_height = broad_height // beach.shape[0]
    for ship in ships:
        r, c = ship.position
        for i in range(ship.size):
            if ship.orientation == 'H':
                pygame.draw.rect(window, ship.color, ( (c + i) * block_width, r * block_height, block_width, block_height))
            else:
                pygame.draw.rect(window, ship.color, ( c * block_width, (r + i) * block_height, block_width, block_height))

def put_ships_randoms(beach, ships):
    for ship in ships:
        ship.placed = False
        while not ship.placed:
            orientation = random.choice(['H', 'V'])
            ship.orientation = orientation
            if orientation == 'H':
                row = random.randint(0, beach.shape[0] - 1)
                col = random.randint(0, beach.shape[1] - ship.size)
            else:
                row = random.randint(0, beach.shape[0] - ship.size)
                col = random.randint(0, beach.shape[1] - 1)

            can_place = True
            for i in range(ship.size):
                r = row + (i if orientation == 'V' else 0)
                c = col + (i if orientation == 'H' else 0)
                if beach[r][c] != 1:
                    can_place = False
                    break

            if can_place:
                ship.position = (row, col)
                ship.placed = True
                for i in range(ship.size):
                    r = row + (i if orientation == 'V' else 0)
                    c = col + (i if orientation == 'H' else 0)
                    beach[r][c] = 2  # mark the ship's position on the beach

# map initialization

class Board:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height

        self.cells = np.zeros((rows, cols), dtype=int)      # 0: water, 1: beach, 2: ship
        self.clicked = np.zeros((rows, cols), dtype=int)    # 0: normal, 1: clicked

        self.block_w = width // cols
        self.block_h = height // rows

    def randomize_beach(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j] = 1

    def cell_from_mouse(self, pos):
        x, y = pos
        col = x // self.block_w
        row = y // self.block_h
        return row, col

    def click_cell(self, row, col):
        self.clicked[row][col] ^= 1   # toggle 0/1

    def draw(self, window):
        for i in range(self.rows):
            for j in range(self.cols):
                # Nếu click → tô xanh lá
                if self.clicked[i][j] == 1:
                    if self.cells[i][j] == 2:
                        pygame.draw.rect(window, RED,
                            (j*self.block_w, i*self.block_h, self.block_w, self.block_h))
                    else:
                        pygame.draw.rect(window, BLACK,
                            (j*self.block_w, i*self.block_h, self.block_w, self.block_h))
                else:
                    pygame.draw.rect(window, WHITE,
                        (j*self.block_w, i*self.block_h, self.block_w, self.block_h), 1)




pygame.init()
WIDTH, HEIGHT = 800, 600
clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Ship")

ROW, COL = 10, 10
BEACH = beach_matrix(ROW, COL)

ships = [Ship(2),Ship(3),Ship(3),Ship(4),Ship(5)]
# ships =[Ship(2), Ship(3, 'H', placed=True, position=(7,7)), Ship(5)]

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

broad_height = HEIGHT
broad_width = HEIGHT 

board = Board(10, 10, HEIGHT, HEIGHT)
board.randomize_beach()

while True:
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         pygame.quit()
    #         exit()
    #     if event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_r:
    #             BEACH = beach_matrix(ROW, COL)
    #             for ship in ships:
    #                 ship.placed = False

    # window.fill(BLUE)
    # draw_beach(window, BEACH)
    # for ship in ships:
    #     if not ship.placed:
    #         put_ships_randoms(BEACH, [ship])
    #     draw_ships(window, BEACH, ships)

    # pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            r, c = board.cell_from_mouse(pygame.mouse.get_pos())
            board.click_cell(r, c)

    window.fill(BLUE)
    board.draw(window)

    for ship in ships:
        if not ship.placed:
            put_ships_randoms(BEACH, [ship])
        draw_ships(window, BEACH, ships)

    pygame.display.flip()



    clock.tick(60)
