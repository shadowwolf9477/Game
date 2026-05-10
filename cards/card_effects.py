def play_pierce_row(card, selected_character, enemies):
    # Hit enemies in the player's row, stopping after max_targets.
    targets_hit = 0
    max_targets = card["max_targets"]

    for enemy in enemies:
        if enemy["row"] == selected_character["row"] and targets_hit < max_targets:
            enemy["hp"] -= card["damage"]
            targets_hit += 1


CARD_EFFECTS = {
    "pierce_row": play_pierce_row
}


def play_card(card, selected_character, enemies):
    # Look up the effect function by card["effect"].
    effect_name = card["effect"]
    effect_function = CARD_EFFECTS[effect_name]

    effect_function(card, selected_character, enemies)
