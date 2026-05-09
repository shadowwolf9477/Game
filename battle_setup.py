import random
from settings import GRID_ROWS, GRID_COLS
from movement import move_unit



def start_tutorial_battle(enemies, enemy_grid_data):
    enemies.clear()

    goblin = {
        "row": 1,
        "col": 2,
        "hp": 3
    }

    enemies.append(goblin)
    enemy_grid_data[goblin["row"]][goblin["col"]]["unit"] = goblin

def choose_goblin_attack(player_grid_data):
    all_tiles = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            all_tiles.append((row, col))

    chosen_tiles = random.sample(all_tiles, 2)

    for row, col in chosen_tiles:
        player_grid_data[row][col]["incoming_attack"] = {
            "damage": 1
        }
def clear_incoming_attacks(player_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            player_grid_data[row][col]["incoming_attack"] = None
def resolve_incoming_attacks(player, player_row, player_col, player_grid_data):
    current_tile = player_grid_data[player_row][player_col]
    incoming_attack = current_tile["incoming_attack"]

    if incoming_attack is not None:
        player["current_hp"] -= incoming_attack["damage"]
def move_enemy_random(enemy, enemy_grid_data):
    direction = random.choice(["left", "right", "up", "down"])

    if direction == "left":
        move_unit(enemy, enemy_grid_data, 0, -1)
    if direction == "right":
        move_unit(enemy, enemy_grid_data, 0, 1)
    if direction == "up":
        move_unit(enemy, enemy_grid_data, -1, 0)
    if direction == "down":
        move_unit(enemy, enemy_grid_data, 1, 0)


