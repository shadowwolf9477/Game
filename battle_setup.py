import random
from settings import GRID_ROWS, GRID_COLS
from movement import move_unit


def start_tutorial_battle(enemies, enemy_grid_data):
    # The tutorial fight is fixed so new runs start with a predictable test battle.
    enemies.clear()

    goblin = {
        "row": 1,
        "col": 2,
        "hp": 3
    }

    enemies.append(goblin)
    # Store the same enemy object on the grid so movement/rendering can find it.
    enemy_grid_data[goblin["row"]][goblin["col"]]["unit"] = goblin


def choose_goblin_attack(player_grid_data):
    # The current goblin pattern warns two random player tiles before damage.
    all_tiles = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            all_tiles.append((row, col))

    chosen_tiles = random.sample(all_tiles, 2)

    for row, col in chosen_tiles:
        # Battle resolution reads this later to decide if the player gets hit.
        player_grid_data[row][col]["incoming_attack"] = {
            "damage": 1
        }


def clear_incoming_attacks(player_grid_data):
    # Clear warning tiles after attacks resolve or when battle is won.
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            player_grid_data[row][col]["incoming_attack"] = None


def resolve_incoming_attacks(player, player_row, player_col, player_grid_data):
    if player["current_hp"] <= 0:
        return

    # Only the tile the player currently occupies can hurt them right now.
    current_tile = player_grid_data[player_row][player_col]
    incoming_attack = current_tile["incoming_attack"]

    if incoming_attack is not None:
        player["current_hp"] -= incoming_attack["damage"]

        if player["current_hp"] < 0:
            player["current_hp"] = 0


def move_enemy_random(enemy, enemy_grid_data):
    # Placeholder enemy movement until each enemy type gets its own behavior.
    direction = random.choice(["left", "right", "up", "down"])

    if direction == "left":
        move_unit(enemy, enemy_grid_data, 0, -1)
    if direction == "right":
        move_unit(enemy, enemy_grid_data, 0, 1)
    if direction == "up":
        move_unit(enemy, enemy_grid_data, -1, 0)
    if direction == "down":
        move_unit(enemy, enemy_grid_data, 1, 0)
