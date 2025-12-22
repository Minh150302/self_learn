import pygame
import numpy as np
import random
import sys

# ==================== PARA =====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

ROWS, COLS = 15, 15
CELL_SIZE = 40
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

class CaroBoard:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = np.zeros((rows, cols), dtype=int)  # 0: empty, 1: X, 2: O

    def place_move(self, row, col, player):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.cells[row][col] == 0:
                self.cells[row][col] = player
                return True
        return False

    def check_winner(self):
        # Check rows, columns and diagonals for a winner
        
        # Check rows
        for r in range(self.rows):
            for c in range(self.cols - 4):
                if self.cells[r][c] != 0 and all(self.cells[r][c + i] == self.cells[r][c] for i in range(5)):
                    return self.cells[r][c]

        # Check columns
        for c in range(self.cols):
            for r in range(self.rows - 4):
                if self.cells[r][c] != 0 and all(self.cells[r + i][c] == self.cells[r][c] for i in range(5)):
                    return self.cells[r][c]

        # Check diagonals
        for r in range(self.rows - 4):
            for c in range(self.cols - 4):
                if self.cells[r][c] != 0 and all(self.cells[r + i][c + i] == self.cells[r][c] for i in range(5)):
                    return self.cells[r][c]

        for r in range(4, self.rows):
            for c in range(self.cols - 4):
                if self.cells[r][c] != 0 and all(self.cells[r - i][c + i] == self.cells[r][c] for i in range(5)):
                    return self.cells[r][c]

        return 0  # No winner yet


def draw_board(surface, board):
    for r in range(board.rows):
        for c in range(board.cols):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, BLACK, rect, 1)
            # if board.cells[r][c] == 1:
            #     pygame.draw.circle(surface, BLACK, rect.center, cell_size // 4)

            if board.cells[r][c] == 1:  # X
                pygame.draw.line(surface, BLACK, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(surface, BLACK, rect.topright, rect.bottomleft, 2)

            elif board.cells[r][c] == 2:  # O
                pygame.draw.circle(surface, RED, rect.center, CELL_SIZE // 3, 2)

def win_game(winner):
    print(f"Player {winner} wins!")

def win_screen(winner):
    font = pygame.font.SysFont(None, 74)
    text = font.render(f"Player {winner} wins!", True, RED)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)




pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caro")
clock = pygame.time.Clock()

board = CaroBoard(ROWS, COLS)
curr_player = 1
game_over = False



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pos = pygame.mouse.get_pos()
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            board.place_move(row, col, curr_player)
            winner = board.check_winner()
            if winner != 0:
                game_over = True
                win_game(winner)

            else:
                curr_player = 2 if curr_player == 1 else 1

    

    window.fill(WHITE)
    draw_board(window, board)

    if game_over:
        winner = board.check_winner()
        win_screen(winner)

    pygame.display.flip()
    clock.tick(60)