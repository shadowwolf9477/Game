from settings import GRID_ROWS, GRID_COLS


def get_card_preview_tiles(card, selected_character):
    # Return enemy-board preview tiles for the selected attack card.
    if card is None or selected_character is None:
        return []

    if card["effect"] == "pierce_row":
        # Pierce previews the whole row because it can hit multiple enemies there.
        player_row = selected_character["row"]
        preview_tiles = []

        for col in range(GRID_COLS):
            preview_tiles.append((player_row, col))

        return preview_tiles

    if card["effect"] == "basic_attack":
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        preview_tiles = []

        if selected_character["basic_attack_shape"] == "vertical_slash":
            preview_rows = [player_row]

            if player_row + 1 < GRID_ROWS:
                preview_rows.append(player_row + 1)
            elif player_row - 1 >= 0:
                preview_rows.append(player_row - 1)

            for row in preview_rows:
                preview_tiles.append((row, player_col))
        else:
            # Archer previews columns starting from the matching enemy column.
            for distance in range(card["range"]):
                enemy_col = player_col + distance

                if enemy_col < GRID_COLS:
                    preview_tiles.append((player_row, enemy_col))

        return preview_tiles

    if card["effect"] == "cleave_column":
        player_col = selected_character["col"]
        preview_tiles = []

        for row in range(GRID_ROWS):
            preview_tiles.append((row, player_col))

        return preview_tiles

    if card["effect"] == "shove":
        player_row = selected_character["row"]
        preview_tiles = []

        for col in range(GRID_COLS):
            preview_tiles.append((player_row, col))

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
