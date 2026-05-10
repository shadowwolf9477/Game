import pygame
from settings import GRID_ROWS, GRID_COLS, GRID_SIZE, GRID_GAP, WHITE, RED, ORANGE, BLUE


def draw_grid(screen, start_x, start_y, selected_row=None, selected_col=None, grid_data=None, preview_tiles=None):
    # Draw one grid. Orange = enemy attack warning. Blue = selected card preview.
    if preview_tiles is None:
        preview_tiles = []

    for row in range(GRID_ROWS):
        y = start_y + row * (GRID_SIZE + GRID_GAP)

        for col in range(GRID_COLS):
            x = start_x + col * (GRID_SIZE + GRID_GAP)
            square = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

            tile_has_attack = grid_data and grid_data[row][col]["incoming_attack"] is not None
            tile_has_preview = (row, col) in preview_tiles

            if tile_has_attack:
                pygame.draw.rect(screen, ORANGE, square, 2)
            elif tile_has_preview:
                pygame.draw.rect(screen, BLUE, square, 3)
            elif row == selected_row and col == selected_col:
                pygame.draw.rect(screen, RED, square, 2)
            else:
                pygame.draw.rect(screen, WHITE, square, 2)


def create_grid_data():
    # Create tile data for a grid. Later tiles can hold traps, units, attacks, etc.
    grid = []

    for row in range(GRID_ROWS):
        grid_row = []

        for col in range(GRID_COLS):
            tile = {
                "unit": None,
                "effect": None,
                "incoming_attack": None
            }
            grid_row.append(tile)

        grid.append(grid_row)

    return grid
