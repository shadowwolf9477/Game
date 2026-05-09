from settings import GRID_ROWS, GRID_COLS


def move_unit(unit, grid_data, row_change, col_change):
    old_row = unit["row"]
    old_col = unit["col"]

    unit["row"] += row_change
    unit["col"] += col_change

    unit["row"] = max(0, min(unit["row"], GRID_ROWS - 1))
    unit["col"] = max(0, min(unit["col"], GRID_COLS - 1))

    grid_data[old_row][old_col]["unit"] = None
    grid_data[unit["row"]][unit["col"]]["unit"] = unit
