import pygame
import numpy as np
import random

# ===================== COLORS =====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (40, 40, 40)

O_COLOR = (255, 231, 2)
I_COLOR = (0, 158, 229)
S_COLOR = (223, 14, 20)
Z_COLOR = (107, 233, 33)
L_COLOR = (253, 101, 0)
J_COLOR = (0, 40, 139)
T_COLOR = (154, 31, 157)
BORDER_COLOR = (20, 20, 20)

# ===================== TETROMINO ROTA =====================

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
O_KICKS = {
    (0,1): [(0,0)],
    (1,2): [(0,0)],
    (2,3): [(0,0)],
    (3,0): [(0,0)]
}


class Tetromino:
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

    def __init__(self, shape, position=(0, 0)):
        self.shape = shape
        self.position = position
        self.matrix = [row[:] for row in Tetromino.SHAPES[shape]]  # tránh ghi đè
        self.rotation = 0

    # def rotate(self):
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]

    def rotate(self, board, direction):
        """
        direction = +1 (CW) hoặc -1 (CCW)
        """
        old_matrix = self.matrix
        old_rot = self.rotation

        # --- step 1: rotate matrix
        if direction == 1:  # CW
            new_matrix = [list(row) for row in zip(*self.matrix[::-1])]
            new_rot = (self.rotation + 1) % 4
        else:               # CCW
            new_matrix = [list(row) for row in zip(*self.matrix)][::-1]
            new_rot = (self.rotation - 1) % 4

        # chọn wall kick table
        if self.shape == "I":
            kicks = I_KICKS
        elif self.shape == "O":
            kicks = O_KICKS
        else:
            kicks = JLSTZ_KICKS

        test_offsets = kicks.get((self.rotation, new_rot), [(0,0)])

        # thử từng kick
        for dx, dy in test_offsets:
            new_x = self.position[0] + dx
            new_y = self.position[1] + dy

            if board.can_place(new_matrix, new_x, new_y):
                self.matrix = new_matrix
                self.rotation = new_rot
                self.position = (new_x, new_y)
                return True

        return False  # xoay thất bại

    def get_color(self):
        return {
            'O': O_COLOR, 'I': I_COLOR, 'S': S_COLOR,
            'Z': Z_COLOR, 'L': L_COLOR, 'J': J_COLOR, 'T': T_COLOR
        }[self.shape]

    def draw(self, surface, block_size):
        r0, c0 = self.position
        color = self.get_color()

        for r in range(len(self.matrix)):
            for c in range(len(self.matrix[0])):
                if self.matrix[r][c] == 1:
                    x = (c0 + c) * block_size
                    y = (r0 + r) * block_size
                    rect = pygame.Rect(x, y, block_size, block_size)

                    pygame.draw.rect(surface, color, rect)               # fill
                    pygame.draw.rect(surface, BORDER_COLOR, rect, 2)      # border



class Board:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.cells = np.zeros((rows, cols), dtype=int)

    def draw(self, surface, block_size):
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * block_size
                y = r * block_size
                rect = pygame.Rect(x, y, block_size, block_size)

                if self.cells[r][c] == 0:
                    pygame.draw.rect(surface, GRID_COLOR, rect, 1)
                else:
                    pygame.draw.rect(surface, WHITE, rect)
                    pygame.draw.rect(surface, BLACK, rect, 2)

    def can_place(self, matrix, r0, c0):
        rows = len(matrix)
        cols = len(matrix[0])

        for r in range(rows):
            for c in range(cols):
                if matrix[r][c] == 1:
                    R = r0 + r
                    C = c0 + c
                    # check bounds
                    if R < 0 or R >= self.rows or C < 0 or C >= self.cols:
                        return False
                    # check collision
                    if self.cells[R][C] != 0:
                        return False
        return True


pygame.init()
WIDTH, HEIGHT = 800, 600  # đúng tỉ lệ của tetris
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris Demo")
clock = pygame.time.Clock()

board = Board()
block_size = 30  # mỗi ô 30px

# thử tất cả các shape
# test_shapes = ['I', 'L', 'J', 'Z', 'S', 'T']
# shapes = [Tetromino(shape, (i*3, 2)) for i, shape in enumerate(test_shapes)]
test_shapes = ['S']
shapes = [Tetromino(shape, (0, i*3)) for i, shape in enumerate(test_shapes)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            for shp in shapes:
                if event.key == pygame.K_z:
                    shp.rotate(board, -1)  # CCW
                elif event.key == pygame.K_x:
                    shp.rotate(board, 1)   # CW

                    

    window.fill(BLACK)
    board.draw(window, block_size)

    for shp in shapes:
        shp.draw(window, block_size)

    pygame.display.flip()
    clock.tick(60)
