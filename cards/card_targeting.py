from settings import GRID_COLS


def get_card_preview_tiles(card, selected_character):
    # Return enemy-side preview tiles for attack cards.
    if card is None:
        return []

    if card["effect"] == "pierce_row":
        player_row = selected_character["row"]
        preview_tiles = []

        for col in range(GRID_COLS):
            preview_tiles.append((player_row, col))

        return preview_tiles

    if card["effect"] == "bow_shot":
        player_row = selected_character["row"]
        player_col = selected_character["col"]
        preview_tiles = []

        for distance in range(1, card["range"] + 1):
            enemy_col = player_col + distance

            if enemy_col < GRID_COLS:
                preview_tiles.append((player_row, enemy_col))

        return preview_tiles


    return []
