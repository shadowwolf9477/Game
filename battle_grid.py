import pygame
from settings import GRID_ROWS, GRID_COLS, GRID_SIZE, GRID_GAP, WHITE, RED, ATTACK_WARNING, BLUE
from damage_numbers import BLACK_ROW, build_damage_number_image

TRAP_COLOR = (180, 70, 255)
MOVEMENT_PREVIEW_FILL = (8, 8, 12, 145)


def draw_grid(screen, start_x, start_y, selected_row=None, selected_col=None, grid_data=None, preview_tiles=None, movement_preview_tiles=None):
    # Draw one board grid.
    # Blue previews take priority so card paths are readable over danger tiles.
    if preview_tiles is None:
        preview_tiles = []

    if movement_preview_tiles is None:
        movement_preview_tiles = []

    for row in range(GRID_ROWS):
        y = start_y + row * (GRID_SIZE + GRID_GAP)

        for col in range(GRID_COLS):
            x = start_x + col * (GRID_SIZE + GRID_GAP)
            square = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

            tile_has_attack = grid_data and grid_data[row][col]["incoming_attack"] is not None
            tile_has_trap = grid_data and grid_data[row][col].get("effect") is not None
            tile_has_preview = (row, col) in preview_tiles
            tile_has_movement_preview = (row, col) in movement_preview_tiles

            if tile_has_movement_preview:
                preview_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                preview_surface.fill(MOVEMENT_PREVIEW_FILL)
                screen.blit(preview_surface, (x, y))

            # Border color shows the most important information for this tile.
            if tile_has_preview:
                pygame.draw.rect(screen, BLUE, square, 3)
            elif tile_has_attack:
                pygame.draw.rect(screen, ATTACK_WARNING, square, 4)
            elif tile_has_trap:
                pygame.draw.rect(screen, TRAP_COLOR, square, 4)
                trap_center = square.center
                pygame.draw.circle(screen, TRAP_COLOR, trap_center, 9)
            elif row == selected_row and col == selected_col:
                pygame.draw.rect(screen, RED, square, 2)
            else:
                pygame.draw.rect(screen, WHITE, square, 2)

            if tile_has_attack:
                damage = grid_data[row][col]["incoming_attack"]["damage"]
                tile_has_unit = grid_data[row][col]["unit"] is not None

                if not tile_has_unit:
                    draw_attack_damage_label(screen, square, damage)


def draw_attack_damage_label(screen, square, damage, compact=False):
    number_image = build_damage_number_image(damage, BLACK_ROW)

    if compact:
        max_width = int(GRID_SIZE * 0.42)
        max_height = int(GRID_SIZE * 0.34)
    else:
        max_width = int(GRID_SIZE * 0.72)
        max_height = int(GRID_SIZE * 0.58)

    scale = min(max_width / number_image.get_width(), max_height / number_image.get_height())
    scaled_size = (
        max(1, int(number_image.get_width() * scale)),
        max(1, int(number_image.get_height() * scale))
    )
    number_image = pygame.transform.scale(number_image, scaled_size)

    if compact:
        number_rect = number_image.get_rect(topright=(square.right - 5, square.top + 5))
    else:
        number_rect = number_image.get_rect(center=square.center)

    screen.blit(number_image, number_rect)


def draw_occupied_attack_damage_labels(screen, start_x, start_y, grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            tile = grid_data[row][col]

            if tile["unit"] is None or tile["incoming_attack"] is None:
                continue

            x = start_x + col * (GRID_SIZE + GRID_GAP)
            y = start_y + row * (GRID_SIZE + GRID_GAP)
            square = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            damage = tile["incoming_attack"]["damage"]
            draw_attack_damage_label(screen, square, damage, True)


def create_grid_data(board_name):
    # Create logical tile data separate from what is drawn on screen.
    grid = []

    for row in range(GRID_ROWS):
        grid_row = []

        for col in range(GRID_COLS):
            tile = {
                # board keeps player and enemy boards separate even though both use row/col.
                "board": board_name,
                # unit stores a character/enemy dictionary currently on this tile.
                "unit": None,
                # effect is reserved for future traps, hazards, buffs, etc.
                "effect": None,
                # incoming_attack creates orange danger warnings on the player grid.
                "incoming_attack": None
            }
            grid_row.append(tile)

        grid.append(grid_row)

    return grid
