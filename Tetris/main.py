import pygame
import numpy as np
import random

class Tetromino:
    # Define the shapes of the tetrominoes
    SHAPES = {
        'O': [[1, 1],
              [1, 1]],
        'I': [[1, 1, 1, 1]],
        'S': [[0, 1, 1],
              [1, 1, 0]],
        'Z': [[1, 1, 0],
              [0, 1, 1]],
        'L': [[1, 0, 0],
              [1, 1, 1]],
        'J': [[0, 0, 1],
              [1, 1, 1]],
        'T': [[0, 1, 0],
              [1, 1, 1]]
    }
    def __init__(self, shape, position=(0,0)):
        self.shape = shape
        self.position = position  # (row, col)

    def rotate(self):
        shape_matrix = Tetromino.SHAPES[self.shape]
        rotated = [list(row) for row in zip(*shape_matrix[::-1])]
        Tetromino.SHAPES[self.shape] = rotated

    def get_color(self):
        colors = {
            'O': O_COLOR,
            'I': I_COLOR,
            'S': S_COLOR,
            'Z': Z_COLOR,
            'L': L_COLOR,
            'J': J_COLOR,
            'T': T_COLOR
        }
        return colors[self.shape]

    def draw(self, surface, block_size):
        shape_matrix = Tetromino.SHAPES[self.shape]
        r0, c0 = self.position
        for r in range(len(shape_matrix)):
            for c in range(len(shape_matrix[0])):
                if shape_matrix[r][c] == 1:
                    rect = ( (c0 + c) * block_size, (r0 + r) * block_size, block_size, block_size)
                    pygame.draw.rect(surface, self.get_color(), rect)

class board:
    # Define the Tetris board and its methods
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.cells = np.zeros((rows, cols), dtype=int)

    def draw(self, surface):
        block_h = surface.get_height() // self.rows
        block_w = block_h
        for r in range(self.rows):
            for c in range(self.cols):
                rect = (c*block_w, r*block_h, block_w, block_h)
                if self.cells[r][c] == 0:
                    pygame.draw.rect(surface, WHITE, rect, 1)
                else:
                    pygame.draw.rect(surface, BLACK, rect)

    def add_tetromino(self, tetromino):
        shape = Tetromino.SHAPES[tetromino.shape]
        r0, c0 = tetromino.position
        for r in range(len(shape)):
            for c in range(len(shape[0])):
                if shape[r][c] == 1:
                    self.cells[r0 + r][c0 + c] = 1
    
    # def clear_lines(self):
    #     new_cells = [row for row in self.cells if not all(cell == 1 for cell in row)]
    #     lines_cleared = self.rows - len(new_cells)
    #     for _ in range(lines_cleared):
    #         new_cells.insert(0, np.zeros(self.cols, dtype=int))
    #     self.cells = np.array(new_cells)

def add_new_tetromino(board):
    shape = random.choice(list(Tetromino.SHAPES.keys()))
    position = (0, board.cols // 2 - len(Tetromino.SHAPES[shape][0]) // 2)
    tetromino = Tetromino(shape, position)
    board.add_tetromino(tetromino)

pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

board = board()
shape = Tetromino('I')
shape = Tetromino('O')
shape = Tetromino('L')
shape = Tetromino('J')
shape = Tetromino('Z')
shape = Tetromino('S')
shape = Tetromino('T')


# ===================== COLOR =====================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# O_COLOR = (255, 165, 0)
# I_COLOR = (0, 255, 255)
# S_COLOR = (0, 255, 0)
# Z_COLOR = (255, 0, 0)
# L_COLOR = (255, 165, 0)
# J_COLOR = (0, 0, 255)
# T_COLOR = (128, 0, 128)

O_COLOR = (255, 231, 2)
I_COLOR = (0, 158, 229)
S_COLOR = (223, 14, 20)
Z_COLOR = (107, 233, 33)
L_COLOR = (253, 101, 0)
J_COLOR = (0, 40, 139)
T_COLOR = (154, 31, 157)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        

    window.fill(BLACK)

    board.draw(window)
    shape.draw(window, WIDTH // board.cols)

    pygame.display.flip()
    clock.tick(60)
