from settings import GRID_COLS


def get_card_preview_tiles(card, selected_character):
    # Return enemy-board preview tiles for the selected attack card.
    if card is None:
        return []

    if card["effect"] == "pierce_row":
        # Pierce previews the whole row because it can hit multiple enemies there.
        player_row = selected_character["row"]
        preview_tiles = []

        for col in range(GRID_COLS):
            preview_tiles.append((player_row, col))

        return preview_tiles

    if card["effect"] == "bow_shot":
        # Bow Shot previews columns starting from the player's matching enemy column.
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        preview_tiles = []

        for distance in range(card["range"]):
            enemy_col = player_col + distance

            if enemy_col < GRID_COLS:
                preview_tiles.append((player_row, enemy_col))

        return preview_tiles

    # Movement and unsupported cards do not preview enemy tiles.
    return []
