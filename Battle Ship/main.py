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
    block_width = WIDTH // beach.shape[1]
    block_height = HEIGHT // beach.shape[0]
    for i in range(beach.shape[0]):
        for j in range(beach.shape[1]):
            if beach[i][j] == 1:
                pygame.draw.rect(window, WHITE, (j * block_width, i * block_height, block_width, block_height), 1)

def draw_ships(window, beach, ships):
    block_width = WIDTH // beach.shape[1]
    block_height = HEIGHT // beach.shape[0]
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

pygame.init()
WIDTH, HEIGHT = 600, 600
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


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                BEACH = beach_matrix(ROW, COL)
                for ship in ships:
                    ship.placed = False

    window.fill(BLUE)
    draw_beach(window, BEACH)
    for ship in ships:
        if not ship.placed:
            put_ships_randoms(BEACH, [ship])
        draw_ships(window, BEACH, ships)

    pygame.display.flip()

    clock.tick(60)
