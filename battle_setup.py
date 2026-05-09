def start_tutorial_battle(enemies, enemy_grid_data):
    enemies.clear()

    goblin = {
        "row": 1,
        "col": 2,
        "hp": 3
    }

    enemies.append(goblin)
    enemy_grid_data[goblin["row"]][goblin["col"]]["unit"] = goblin
