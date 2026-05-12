from settings import GRID_ROWS, GRID_COLS


def character_can_use_card(character, card):
    if character is None or character["current_hp"] <= 0:
        return False

    # A shielding character is committed to protecting and cannot act with cards.
    if character.get("shielding") is not None:
        return False

    if card["effect"] == "move" and character.get("snared", 0) > 0:
        return False

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
    if character is not None and "character_names" in card and character["name"] in card["character_names"]:
        return card["character_names"][character["name"]]

    return card["name"]


def remove_dead_enemies(enemies):
    # Mutate the existing list so main.py keeps pointing at the same enemies object.
    enemies[:] = [enemy for enemy in enemies if enemy["hp"] > 0]


def play_basic_attack(card, selected_character, enemies):
    # Basic Attack changes shape depending on who uses it.
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    hits = []

    if selected_character["basic_attack_shape"] == "vertical_slash":
        target_rows = [player_row]

        if player_row + 1 < GRID_ROWS:
            target_rows.append(player_row + 1)
        elif player_row - 1 >= 0:
            target_rows.append(player_row - 1)

        for enemy in sorted(enemies, key=lambda enemy: (enemy["col"], enemy["row"])):
            if enemy["row"] in target_rows and enemy["col"] == player_col:
                damage_enemy(enemy, card["damage"], hits)
                break
    else:
        target_columns = []

        for distance in range(card["range"]):
            enemy_col = player_col + distance

            if enemy_col < GRID_COLS:
                target_columns.append(enemy_col)

        for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
            if enemy["row"] == player_row and enemy["col"] in target_columns:
                damage_enemy(enemy, card["damage"], hits)
                break

    return {
        "hits": hits
    }



def play_pierce_row(card, selected_character, enemies):
    # Pierce rewards lined-up enemies by hitting several targets in the row.
    targets_hit = 0
    max_targets = card["max_targets"]
    hits = []

    for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
        if enemy["row"] == selected_character["row"] and targets_hit < max_targets:
            damage_enemy(enemy, card["damage"], hits)
            targets_hit += 1

    return {
        "hits": hits
    }


def play_cleave_column(card, selected_character, enemies):
    # Cleave hits every enemy in the column matching the warrior's position.
    player_col = selected_character["col"]
    hits = []

    for enemy in enemies:
        if enemy["col"] == player_col:
            damage_enemy(enemy, card["damage"], hits)

    return {
        "hits": hits
    }


def damage_enemy(enemy, damage, hits):
    enemy["hp"] -= damage
    hits.append({
        "target": enemy,
        "damage": damage
    })


def start_move_card(card, selected_character, enemies):
    # Movement cards are paid/discarded first, then main.py previews the path.
    return "movement"


def play_deep_breath(card, selected_character, enemies):
    return {
        "gain_energy": card.get("gain_energy", 0),
        "draw_cards": card.get("draw_cards", 0),
        "discard_cards": card.get("discard_cards", 0)
    }


def start_shove_card(card, selected_character, enemies):
    target = get_first_enemy_in_row(selected_character, enemies)

    if target is None:
        return None

    return {
        "shove_target": target,
        "push_range": card.get("push_range", 2)
    }


def place_trap_card(card, selected_character, enemies):
    return {
        "trap": {
            "row": selected_character["row"],
            "col": selected_character["col"],
            "damage": card.get("trap_damage", 1),
            "duration": card.get("trap_duration", 4),
            "radius": card.get("trap_radius", 1)
        }
    }


def get_first_enemy_in_row(selected_character, enemies):
    for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
        if enemy["row"] == selected_character["row"]:
            return enemy

    return None


# Card effect IDs from card_library.py are looked up here.
CARD_EFFECTS = {
    "basic_attack": play_basic_attack,
    "pierce_row": play_pierce_row,
    "cleave_column": play_cleave_column,
    "move": start_move_card,
    "deep_breath": play_deep_breath,
    "shove": start_shove_card,
    "trap": place_trap_card
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

    card = get_modified_attack_card(card, selected_character)
    effect_function = CARD_EFFECTS[effect_name]
    result = effect_function(card, selected_character, enemies)

    if effect_name == "shove" and result is None:
        return False, current_energy + card["cost"], None

    return True, current_energy, result


def get_reaction_cost(card):
    return card["cost"] + 1


def play_reaction_card(card, selected_character, enemies, current_energy):
    if not character_can_use_card(selected_character, card):
        return False, current_energy, None

    if card["type"] != "attack":
        return False, current_energy, None

    reaction_cost = get_reaction_cost(card)

    if current_energy < reaction_cost:
        return False, current_energy, None

    effect_name = card["effect"]

    if effect_name not in CARD_EFFECTS:
        return False, current_energy, None

    reaction_card = get_modified_attack_card(card, selected_character)

    if selected_character["name"] == "Archer" and "damage" in reaction_card:
        boosted_damage = int(reaction_card["damage"] * 1.25)

        if boosted_damage <= reaction_card["damage"]:
            boosted_damage = reaction_card["damage"] + 1

        reaction_card["damage"] = boosted_damage

    current_energy -= reaction_cost

    effect_function = CARD_EFFECTS[effect_name]
    result = effect_function(reaction_card, selected_character, enemies)

    return True, current_energy, result


def get_modified_attack_card(card, selected_character):
    if card["type"] != "attack" or "damage" not in card:
        return card

    modified_card = card.copy()

    if selected_character.get("weak_attacks", 0) > 0:
        modified_card["damage"] = max(1, modified_card["damage"] // 2)
        selected_character["weak_attacks"] -= 1

    return modified_card
