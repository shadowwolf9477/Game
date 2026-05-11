from settings import GRID_ROWS, GRID_COLS


def move_unit(unit, grid_data, row_change, col_change):
    # Move a unit and keep the logical grid synced with the unit dictionary.
    old_row = unit["row"]
    old_col = unit["col"]

    # Clamp movement so debug movement and enemies stay on their board.
    unit["row"] += row_change
    unit["col"] += col_change

    unit["row"] = max(0, min(unit["row"], GRID_ROWS - 1))
    unit["col"] = max(0, min(unit["col"], GRID_COLS - 1))

    if grid_data[unit["row"]][unit["col"]]["unit"] is not None:
        unit["row"] = old_row
        unit["col"] = old_col
        return False

    # Clear the old tile and place the same unit object on the new tile.
    grid_data[old_row][old_col]["unit"] = None
    grid_data[unit["row"]][unit["col"]]["unit"] = unit

    return True


def can_land_on_tile(grid_data, row, col, unit=None):
    if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
        return False

    tile_unit = grid_data[row][col]["unit"]

    return tile_unit is None or tile_unit is unit
