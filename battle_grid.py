import pygame
from settings import GRID_ROWS, GRID_COLS, GRID_SIZE, GRID_GAP, WHITE , RED

def draw_grid(screen, start_x, start_y, selected_row=None, selected_col=None):
    for row in range(GRID_ROWS):
        y = start_y + row * (GRID_SIZE + GRID_GAP)
        for col in range(GRID_COLS):
            x = start_x + col * (GRID_SIZE + GRID_GAP)
            square = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if row == selected_row and col == selected_col:
                pygame.draw.rect(screen, RED, square, 2)
            else:
                pygame.draw.rect(screen, WHITE, square, 2)

            
