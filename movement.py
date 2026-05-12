from settings import GRID_ROWS, GRID_COLS


def move_unit(unit, grid_data, row_change, col_change):
    # Move a unit and keep the logical grid synced with the unit dictionary.
    old_row = unit["row"]
    old_col = unit["col"]
    next_row = old_row + row_change
    next_col = old_col + col_change

    # Reject moves outside this board instead of clamping them into a legal tile.
    if not can_land_on_tile(grid_data, next_row, next_col, unit):
        return False

    # Clear the old tile and place the same unit object on the new tile.
    grid_data[old_row][old_col]["unit"] = None
    unit["row"] = next_row
    unit["col"] = next_col
    grid_data[unit["row"]][unit["col"]]["unit"] = unit

    return True


def can_land_on_tile(grid_data, row, col, unit=None):
    if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
        return False

    if unit is not None:
        unit_board = unit.get("board")
        tile_board = grid_data[row][col].get("board")

        if unit_board is not None and tile_board is not None and unit_board != tile_board:
            return False

    tile_unit = grid_data[row][col]["unit"]

    return tile_unit is None or tile_unit is unit
