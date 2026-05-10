from settings import GRID_COLS


def remove_dead_enemies(enemies):
    # Mutate the existing list so main.py keeps pointing at the same enemies object.
    enemies[:] = [enemy for enemy in enemies if enemy["hp"] > 0]


def play_bow_shot(card, selected_character, enemies):
    # Bow Shot targets enemy-board columns based on where the player is standing.
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    target_columns = []

    for distance in range(card["range"]):
        enemy_col = player_col + distance

        if enemy_col < GRID_COLS:
            target_columns.append(enemy_col)

    # Only the first valid enemy in those columns takes damage.
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


def start_move_card(card, selected_character, enemies):
    # Movement cards are paid/discarded first, then main.py previews the path.
    return "movement"


# Card effect IDs from card_library.py are looked up here.
CARD_EFFECTS = {
    "bow_shot": play_bow_shot,
    "pierce_row": play_pierce_row,
    "move": start_move_card
}


def play_card(card, selected_character, enemies, current_energy):
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
