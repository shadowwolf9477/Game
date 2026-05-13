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
        attack_direction = get_character_attack_direction(selected_character)
        swing_tiles = get_warrior_basic_attack_tiles(selected_character, attack_direction)
        swing_direction = card.get("swing_direction", "right")

        for enemy in sort_enemies_for_basic_attack(enemies, selected_character, attack_direction, swing_direction):
            if (enemy["row"], enemy["col"]) in swing_tiles:
                damage_enemy(enemy, card["damage"], hits)
                break
    else:
        target_columns = []
        attack_direction = get_character_attack_direction(selected_character)

        for distance in range(1, card["range"] + 1):
            if attack_direction == "back":
                enemy_col = player_col - distance
            else:
                enemy_col = player_col + distance

            if 0 <= enemy_col < GRID_COLS:
                target_columns.append(enemy_col)

        if attack_direction == "back":
            sorted_enemies = sorted(enemies, key=lambda enemy: -enemy["col"])
        else:
            sorted_enemies = sorted(enemies, key=lambda enemy: enemy["col"])

        for enemy in sorted_enemies:
            if enemy["row"] == player_row and enemy["col"] in target_columns:
                damage_enemy(enemy, card["damage"], hits)
                break

    return {
        "hits": hits
    }


def get_character_attack_direction(character):
    if character.get("flip_x", False):
        return "back"

    return "front"



def play_pierce_row(card, selected_character, enemies):
    # Pierce rewards lined-up enemies by hitting several targets in the row.
    targets_hit = 0
    max_targets = card["max_targets"]
    attack_range = card.get("range", GRID_COLS)
    hits = []
    target_columns = []

    for distance in range(1,attack_range+1):
        enemy_col = selected_character["col"] + distance

        if enemy_col < GRID_COLS:
            target_columns.append(enemy_col)

    for enemy in sorted(enemies, key=lambda enemy: enemy["col"]):
        if (
            enemy["row"] == selected_character["row"]
            and enemy["col"] in target_columns
            and targets_hit < max_targets
        ):
            damage_enemy(enemy, card["damage"], hits)
            targets_hit += 1

    return {
        "hits": hits
    }


def play_cleave_column(card, selected_character, enemies):
    # Cleave is a side swing. Total damage is split, with the first target hit hardest.
    swing_direction = card.get("swing_direction", "right")
    swing_tiles = get_warrior_swing_tiles(selected_character, swing_direction)
    hits = []
    targets = []

    for enemy in sort_enemies_for_swing(enemies, selected_character, swing_direction):
        if (enemy["row"], enemy["col"]) in swing_tiles:
            targets.append(enemy)

    damages = split_degrading_damage(card["damage"], len(targets))

    for index, enemy in enumerate(targets):
        damage_enemy(enemy, damages[index], hits)

    return {
        "hits": hits
    }


def get_warrior_swing_tiles(selected_character, swing_direction):
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    swing_tiles = []
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
                swing_tiles.append((row, col))

    return swing_tiles


def get_warrior_basic_attack_tiles(selected_character, attack_direction):
    player_row = selected_character["row"]
    player_col = selected_character["col"]
    swing_tiles = []

    if attack_direction == "back":
        target_col = max(0, player_col - 1)
    else:
        target_col = min(GRID_COLS - 1, player_col + 1)

    if target_col == player_col and 0 < player_col < GRID_COLS - 1:
        return swing_tiles

    target_rows = [player_row]

    if player_row - 1 >= 0:
        target_rows.append(player_row - 1)
    elif player_row + 1 < GRID_ROWS:
        target_rows.append(player_row + 1)

    for row in target_rows:
        swing_tiles.append((row, target_col))

    return swing_tiles


def sort_enemies_for_swing(enemies, selected_character, swing_direction):
    player_row = selected_character["row"]

    if swing_direction == "left":
        return sorted(enemies, key=lambda enemy: (enemy["col"], abs(enemy["row"] - player_row), enemy["row"]))

    return sorted(enemies, key=lambda enemy: (-enemy["col"], abs(enemy["row"] - player_row), enemy["row"]))


def sort_enemies_for_basic_attack(enemies, selected_character, attack_direction, swing_direction="right"):
    player_row = selected_character["row"]

    if selected_character["basic_attack_shape"] == "vertical_slash":
        if swing_direction == "left":
            return sorted(enemies, key=lambda enemy: enemy["row"])

        return sorted(enemies, key=lambda enemy: -enemy["row"])

    if attack_direction == "back":
        return sorted(enemies, key=lambda enemy: (-enemy["col"], abs(enemy["row"] - player_row), enemy["row"]))

    return sorted(enemies, key=lambda enemy: (enemy["col"], abs(enemy["row"] - player_row), enemy["row"]))


def split_degrading_damage(total_damage, target_count):
    if target_count <= 0:
        return []

    base_damage = total_damage // target_count
    extra_damage = total_damage % target_count
    damages = []

    # Cleave splits its current damage across targets. Earlier targets in the
    # chosen swing order get leftover damage, so upgrades still scale cleanly.
    for target_index in range(target_count):
        damage = base_damage

        if target_index < extra_damage:
            damage += 1

        damages.append(max(1, damage))

    return damages


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
        "discard_cards": card.get("discard_cards", 0),
        "discard_prompt": "Discard a card"
    }


def start_shove_card(card, selected_character, enemies):
    target = get_enemy_directly_ahead(selected_character, enemies)

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


def get_enemy_directly_ahead(selected_character, enemies):
    target_col = selected_character["col"] + 1

    if get_character_attack_direction(selected_character) == "back":
        target_col = selected_character["col"] - 1

    for enemy in enemies:
        if enemy["row"] == selected_character["row"] and enemy["col"] == target_col:
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

    character_damage = modified_card.get("character_damage", {})

    if selected_character["name"] in character_damage:
        modified_card["damage"] = character_damage[selected_character["name"]]

    if selected_character.get("weak_attacks", 0) > 0:
        modified_card["damage"] = max(1, modified_card["damage"] // 2)
        selected_character["weak_attacks"] -= 1

    return modified_card
