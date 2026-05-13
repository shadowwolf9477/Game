from settings import GRID_ROWS, GRID_COLS


def get_card_preview_tiles(card, selected_character, swing_direction="right", attack_direction=None):
    # Return enemy-board preview tiles for the selected attack card.
    if card is None or selected_character is None:
        return []

    if card["effect"] == "pierce_row":
        # Pierce previews its limited row range because it can hit multiple enemies there.
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        preview_tiles = []

        for distance in range(card.get("range", GRID_COLS)):
            enemy_col = player_col + distance

            if enemy_col < GRID_COLS:
                preview_tiles.append((player_row, enemy_col))

        return preview_tiles

    if card["effect"] == "basic_attack":
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        preview_tiles = []

        if attack_direction is None:
            attack_direction = get_character_attack_direction(selected_character)

        if selected_character["basic_attack_shape"] == "vertical_slash":
            preview_tiles = get_warrior_basic_attack_tiles(selected_character, attack_direction)

        else:
            # Basic shots start one tile away and follow the character's facing.
            directions = [attack_direction]

            for direction in directions:
                for distance in range(1, card["range"] + 1):
                    if direction == "back":
                        enemy_col = player_col - distance
                    else:
                        enemy_col = player_col + distance

                    if 0 <= enemy_col < GRID_COLS:
                        preview_tiles.append((player_row, enemy_col))

        return preview_tiles

    if card["effect"] == "cleave_column":
        return get_warrior_swing_tiles(selected_character, swing_direction)

    if card["effect"] == "shove":
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        attack_direction = get_character_attack_direction(selected_character)
        preview_tiles = []

        if attack_direction == "back":
            target_col = player_col - 1
        else:
            target_col = player_col + 1

        if 0 <= target_col < GRID_COLS:
            preview_tiles.append((player_row, target_col))

        return preview_tiles

    if card["effect"] == "trap":
        center_row = selected_character["row"]
        center_col = selected_character["col"]
        preview_tiles = []
        trap_radius = card.get("trap_radius", 1)

        for row in range(center_row - trap_radius, center_row + trap_radius + 1):
            for col in range(center_col - trap_radius, center_col + trap_radius + 1):
                if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                    preview_tiles.append((row, col))

        return preview_tiles

    # Movement and unsupported cards do not preview enemy tiles.
    return []


def get_character_attack_direction(character):
    if character.get("flip_x", False):
        return "back"

    return "front"


def get_warrior_swing_tiles(selected_character, swing_direction):
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    preview_tiles = []
    attack_direction = get_character_attack_direction(selected_character)

    if attack_direction == "back":
        first_col = max(0, player_col - 1)
        second_col = first_col + 1
        skipped_middle_col = second_col
    else:
        second_col = min(GRID_COLS - 1, player_col + 1)
        first_col = second_col - 1
        skipped_middle_col = first_col

    target_cols = [first_col, second_col]

    for row in range(player_row - 1, player_row + 2):
        for col in target_cols:
            if row == player_row and col == skipped_middle_col:
                continue

            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                preview_tiles.append((row, col))

    return preview_tiles


def get_warrior_basic_attack_tiles(selected_character, attack_direction):
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    preview_tiles = []
    directions = ["front", "back"]

    if attack_direction is not None:
        directions = [attack_direction]

    for direction in directions:
        if direction == "back":
            target_col = max(0, player_col - 1)
        else:
            target_col = min(GRID_COLS - 1, player_col + 1)

        if target_col == player_col and 0 < player_col < GRID_COLS - 1:
            continue

        target_rows = [player_row]

        if player_row - 1 >= 0:
            target_rows.append(player_row - 1)
        elif player_row + 1 < GRID_ROWS:
            target_rows.append(player_row + 1)

        for row in target_rows:
            preview_tiles.append((row, target_col))

    return preview_tiles
