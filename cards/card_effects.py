from settings import GRID_ROWS, GRID_COLS


def character_can_use_card(character, card):
    # Character-specific cards only allow named users.
    if "usable_characters" in card:
        return character["name"] in card["usable_characters"]

    # Generic cards can allow broad tags like ranged, melee, tank, etc.
    if "usable_tags" in card:
        for tag in character["tags"]:
            if tag in card["usable_tags"]:
                return True

        return False

    # Cards with no restrictions are neutral utility cards.
    return True


def get_card_display_name(card, character):
    # Some neutral cards get a different name depending on who uses them.
    if "character_names" in card and character["name"] in card["character_names"]:
        return card["character_names"][character["name"]]

    return card["name"]


def remove_dead_enemies(enemies):
    # Mutate the existing list so main.py keeps pointing at the same enemies object.
    enemies[:] = [enemy for enemy in enemies if enemy["hp"] > 0]


def play_basic_attack(card, selected_character, enemies):
    # Basic Attack changes shape depending on who uses it.
    player_row = selected_character["row"]
    player_col = selected_character["col"]

    if selected_character["basic_attack_shape"] == "vertical_slash":
        target_rows = [player_row]

        if player_row + 1 < GRID_ROWS:
            target_rows.append(player_row + 1)
        elif player_row - 1 >= 0:
            target_rows.append(player_row - 1)

        for enemy in sorted(enemies, key=lambda enemy: (enemy["col"], enemy["row"])):
            if enemy["row"] in target_rows and enemy["col"] == player_col:
                enemy["hp"] -= card["damage"]
                break
    else:
        target_columns = []

        for distance in range(card["range"]):
            enemy_col = player_col + distance

            if enemy_col < GRID_COLS:
                target_columns.append(enemy_col)

        for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
            if enemy["row"] == player_row and enemy["col"] in target_columns:
                enemy["hp"] -= card["damage"]
                break

    remove_dead_enemies(enemies)

    return None



def play_pierce_row(card, selected_character, enemies):
    # Pierce rewards lined-up enemies by hitting several targets in the row.
    targets_hit = 0
    max_targets = card["max_targets"]

    for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
        if enemy["row"] == selected_character["row"] and targets_hit < max_targets:
            enemy["hp"] -= card["damage"]
            targets_hit += 1

    remove_dead_enemies(enemies)

    return None


def play_cleave_column(card, selected_character, enemies):
    # Cleave hits every enemy in the column matching the warrior's position.
    player_col = selected_character["col"]

    for enemy in enemies:
        if enemy["col"] == player_col:
            enemy["hp"] -= card["damage"]

    remove_dead_enemies(enemies)

    return None


def start_move_card(card, selected_character, enemies):
    # Movement cards are paid/discarded first, then main.py previews the path.
    return "movement"


# Card effect IDs from card_library.py are looked up here.
CARD_EFFECTS = {
    "basic_attack": play_basic_attack,
    "pierce_row": play_pierce_row,
    "cleave_column": play_cleave_column,
    "move": start_move_card
}


def play_card(card, selected_character, enemies, current_energy):
    if not character_can_use_card(selected_character, card):
        return False, current_energy, None

    # Stop early if the player cannot afford the selected card.
    if current_energy < card["cost"]:
        return False, current_energy, None

    effect_name = card["effect"]

    # Unknown effects fail safely instead of crashing the battle loop.
    if effect_name not in CARD_EFFECTS:
        return False, current_energy, None

    current_energy -= card["cost"]

    effect_function = CARD_EFFECTS[effect_name]
    result = effect_function(card, selected_character, enemies)

    return True, current_energy, result
