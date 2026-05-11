import random
from settings import GRID_ROWS, GRID_COLS
from movement import move_unit, can_land_on_tile


def start_tutorial_battle(enemies, enemy_grid_data):
    # The tutorial fight is fixed so new runs start with a predictable test battle.
    enemies.clear()

    goblin = {
        "name": "Goblin",
        "type": "goblin",
        "row": 1,
        "col": 2,
        "hp": 3,
        "attack_damage": 1,
        "attack_interval": 1,
        "turns_until_attack": 1
    }

    enemies.append(goblin)
    # Store the same enemy object on the grid so movement/rendering can find it.
    enemy_grid_data[goblin["row"]][goblin["col"]]["unit"] = goblin


def start_map_battle(enemies, enemy_grid_data, battle_number):
    enemies.clear()

    if battle_number == 2:
        start_orc_battle(enemies, enemy_grid_data)
    else:
        start_tutorial_battle(enemies, enemy_grid_data)


def start_orc_battle(enemies, enemy_grid_data):
    orc = {
        "name": "Orc",
        "type": "orc",
        "row": 1,
        "col": 2,
        "hp": 8,
        "attack_damage": 2,
        "attack_interval": 2,
        "turns_until_attack": 2,
        "flip_x": True
    }

    goblins = [
        build_goblin(0, 0),
        build_goblin(1, 4),
        build_goblin(2, 1)
    ]

    add_enemy_to_grid(orc, enemies, enemy_grid_data)

    for goblin in goblins:
        add_enemy_to_grid(goblin, enemies, enemy_grid_data)


def build_goblin(row, col):
    return {
        "name": "Goblin",
        "type": "goblin",
        "row": row,
        "col": col,
        "hp": 3,
        "attack_damage": 1,
        "attack_interval": 1,
        "turns_until_attack": 1,
        "flip_x": True
    }


def add_enemy_to_grid(enemy, enemies, enemy_grid_data):
    enemies.append(enemy)
    enemy_grid_data[enemy["row"]][enemy["col"]]["unit"] = enemy


def sync_enemy_grid(enemies, enemy_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            enemy_grid_data[row][col]["unit"] = None

    for enemy in enemies:
        enemy_grid_data[enemy["row"]][enemy["col"]]["unit"] = enemy


def prepare_enemy_attacks(enemies, player_grid_data):
    for enemy in enemies:
        if enemy["turns_until_attack"] <= 1:
            if enemy["type"] == "orc":
                choose_orc_attack(enemy, player_grid_data)
            else:
                choose_goblin_attack(enemy, player_grid_data)


def choose_goblin_attack(enemy, player_grid_data):
    # The current goblin pattern warns two random player tiles before damage.
    all_tiles = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            all_tiles.append((row, col))

    chosen_tiles = random.sample(all_tiles, 2)

    for row, col in chosen_tiles:
        # Battle resolution reads this later to decide if the player gets hit.
        player_grid_data[row][col]["incoming_attack"] = {
            "damage": enemy["attack_damage"],
            "source": enemy
        }


def choose_orc_attack(enemy, player_grid_data):
    # Orc warns a compact heavy strike.
    attack_height = 2
    attack_width = 2
    start_row = random.randint(0, GRID_ROWS - attack_height)
    start_col = random.randint(0, max(0, GRID_COLS - min(attack_width, GRID_COLS)))

    for row in range(start_row, min(start_row + attack_height, GRID_ROWS)):
        for col in range(start_col, min(start_col + attack_width, GRID_COLS)):
            player_grid_data[row][col]["incoming_attack"] = {
                "damage": enemy["attack_damage"],
                "source": enemy
            }


def clear_incoming_attacks(player_grid_data):
    # Clear warning tiles after attacks resolve or when battle is won.
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            player_grid_data[row][col]["incoming_attack"] = None


def clear_enemy_incoming_attacks(enemy, player_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            incoming_attack = player_grid_data[row][col]["incoming_attack"]

            if incoming_attack is not None and incoming_attack.get("source") is enemy:
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


def resolve_enemy_incoming_attacks(enemy, party, player_grid_data):
    for character in party:
        if character["current_hp"] <= 0:
            continue

        current_tile = player_grid_data[character["row"]][character["col"]]
        incoming_attack = current_tile["incoming_attack"]

        if incoming_attack is not None and incoming_attack.get("source") is enemy:
            character["current_hp"] -= incoming_attack["damage"]

            if character["current_hp"] < 0:
                character["current_hp"] = 0


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


def move_orc_like_knight(enemy, enemy_grid_data):
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1)
    ]
    random.shuffle(knight_moves)

    for row_change, col_change in knight_moves:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            move_unit(enemy, enemy_grid_data, row_change, col_change)
            return
