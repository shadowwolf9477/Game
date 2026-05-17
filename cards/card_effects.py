from settings import GRID_ROWS, GRID_COLS


def character_can_use_card(character, card):
    if character is None or character["current_hp"] <= 0:
        return False

    if character.get("shielding") is not None:
        return False

    if card["effect"] == "move" and character.get("snared", 0) > 0:
        return False

    if "usable_characters" in card:
        return character["name"] in card["usable_characters"]

    if "usable_tags" in card:
        for tag in character["tags"]:
            if tag in card["usable_tags"]:
                return True

        return False

    return True


def get_card_display_name(card, character):
    if character is not None and "character_names" in card and character["name"] in card["character_names"]:
        return card["character_names"][character["name"]]

    return card["name"]


def remove_dead_enemies(enemies):
    enemies[:] = [enemy for enemy in enemies if enemy["hp"] > 0]


def damage_enemy(enemy, damage, hits):
    enemy["hp"] -= damage
    hits.append({
        "target": enemy,
        "damage": damage
    })


def get_character_attack_direction(character):
    if character.get("flip_x", False):
        return "back"

    return "front"


def play_basic_attack(card, selected_character, enemies):
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


def play_pierce_row(card, selected_character, enemies):
    targets_hit = 0
    max_targets = card["max_targets"]
    attack_range = card.get("range", GRID_COLS)
    hits = []
    target_columns = []
    attack_direction = get_character_attack_direction(selected_character)

    for distance in range(1, attack_range + 1):
        if attack_direction == "back":
            enemy_col = selected_character["col"] - distance
        else:
            enemy_col = selected_character["col"] + distance

        if 0 <= enemy_col < GRID_COLS:
            target_columns.append(enemy_col)

    if attack_direction == "back":
        sorted_enemies = sorted(enemies, key=lambda enemy: -enemy["col"])
    else:
        sorted_enemies = sorted(enemies, key=lambda enemy: enemy["col"])

    for enemy in sorted_enemies:
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

    for target_index in range(target_count):
        damage = base_damage

        if target_index < extra_damage:
            damage += 1

        damages.append(max(1, damage))

    return damages


def start_move_card(card, selected_character, enemies):
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


def play_mule_kick(card, selected_character, enemies):
    target = get_enemy_behind(selected_character, enemies)

    if target is None:
        return None

    hits = []
    damage = get_custom_card_value(card, selected_character, "damage", card.get("damage", 0))
    shove_distance = get_custom_card_value(
        card,
        selected_character,
        "shove_distance",
        card.get("shove_distance", 2)
    )

    damage_enemy(target, damage, hits)

    if target["hp"] <= 0:
        return {
            "hits": hits
        }

    return {
        "hits": hits,
        "shove_target": target,
        "push_range": shove_distance
    }


def play_reckless_charge(card, selected_character, enemies):
    hits = []
    damage = get_custom_card_value(card, selected_character, "damage", card.get("damage", 0))
    move_distance = get_custom_card_value(
        card,
        selected_character,
        "move_distance",
        card.get("move_distance", 2)
    )
    target_tiles = get_forward_row_tiles(selected_character, move_distance)

    for enemy in enemies:
        if (enemy["row"], enemy["col"]) in target_tiles:
            damage_enemy(enemy, damage, hits)

    return {
        "hits": hits,
        "forced_charge": {
            "distance": move_distance
        }
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


def get_enemy_behind(selected_character, enemies):
    target_col = selected_character["col"] - 1

    if get_character_attack_direction(selected_character) == "back":
        target_col = selected_character["col"] + 1

    for enemy in enemies:
        if enemy["row"] == selected_character["row"] and enemy["col"] == target_col:
            return enemy

    return None


def get_forward_row_tiles(selected_character, distance):
    tiles = []
    attack_direction = get_character_attack_direction(selected_character)

    for step in range(1, distance + 1):
        if attack_direction == "back":
            col = selected_character["col"] - step
        else:
            col = selected_character["col"] + step

        if 0 <= col < GRID_COLS:
            tiles.append((selected_character["row"], col))

    return tiles


def get_custom_card_value(card, selected_character, value_name, default=0):
    character_values = card.get("character_values", {})
    character_name = selected_character["name"]

    if character_name in character_values:
        if value_name in character_values[character_name]:
            return character_values[character_name][value_name]

    return card.get(value_name, default)


def get_custom_preview_tile(card, selected_character):
    return card.get("player_preview_tile", {
        "row": selected_character["row"],
        "col": selected_character["col"]
    })


def get_relative_custom_target_tiles(card, selected_character):
    return get_relative_custom_tiles_from_layer(card, selected_character, "target_tiles")


def get_relative_custom_tiles_from_layer(card, selected_character, layer_name):
    target_tiles = []
    preview_tile = get_custom_preview_tile(card, selected_character)

    for tile in card.get(layer_name, []):
        row_offset = tile["row"] - preview_tile["row"]
        col_offset = tile["col"] - preview_tile["col"]

        if selected_character.get("flip_x", False):
            col_offset *= -1

        row = selected_character["row"] + row_offset
        col = selected_character["col"] + col_offset

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            target_tiles.append((row, col))

    return target_tiles


def get_enemy_on_tile(enemies, row, col):
    for enemy in enemies:
        if enemy["row"] == row and enemy["col"] == col:
            return enemy

    return None


def get_first_enemy_on_custom_tiles(card, selected_character, enemies):
    target_tiles = get_relative_custom_tiles_from_layer(card, selected_character, "hitbox_tiles")

    if not target_tiles:
        target_tiles = get_relative_custom_target_tiles(card, selected_character)

    for row, col in target_tiles:
        enemy = get_enemy_on_tile(enemies, row, col)

        if enemy is not None:
            return enemy

    return None


def run_custom_card_effect(card, selected_character, enemies):
    hits = []
    result = {
        "hits": hits
    }

    for effect in card.get("effects", []):
        effect_type = effect.get("type")

        if effect_type == "damage":
            amount = get_custom_card_value(card, selected_character, "damage", card.get("damage", 0))

            target_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("tiles_from", "hitbox_tiles")
            )

            if not target_tiles:
                target_tiles = get_relative_custom_target_tiles(card, selected_character)

            for row, col in target_tiles:
                enemy = get_enemy_on_tile(enemies, row, col)

                if enemy is not None:
                    damage_enemy(enemy, amount, hits)

        elif effect_type == "gain_block":
            amount = get_custom_card_value(card, selected_character, "block", card.get("block", 0))
            selected_character["block"] = selected_character.get("block", 0) + amount

        elif effect_type == "draw_cards":
            amount = get_custom_card_value(card, selected_character, "draw", card.get("draw", 0))
            result["draw_cards"] = amount

        elif effect_type == "discard_cards":
            amount = get_custom_card_value(card, selected_character, "discard", card.get("discard", 0))
            result["discard_cards"] = amount
            result["discard_prompt"] = "Discard a card"

        elif effect_type == "move_character":
            return "movement"

        elif effect_type == "charge_character":
            distance = get_custom_card_value(card, selected_character, "move_distance", card.get("move_distance", 1))
            result["move_range"] = distance
            result["start_move"] = True

        elif effect_type == "shove":
            target = get_first_enemy_on_custom_tiles(card, selected_character, enemies)

            if target is None:
                continue

            distance = get_custom_card_value(card, selected_character, "shove_distance", card.get("shove_distance", 1))

            result["shove_target"] = target
            result["push_range"] = distance

        elif effect_type == "apply_status":
            status_name = effect.get("status")

            if status_name is None:
                continue

            duration = get_custom_card_value(
                card,
                selected_character,
                "status_duration",
                card.get("status_duration", 1)
            )

            stacks = get_custom_card_value(
                card,
                selected_character,
                "status_stacks",
                card.get("status_stacks", 1)
            )

            fire_stacks = get_custom_card_value(
                card,
                selected_character,
                "fire_stacks",
                card.get("fire_stacks", stacks)
            )

            target_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("tiles_from", "hitbox_tiles")
            )

            if not target_tiles:
                target_tiles = get_relative_custom_target_tiles(card, selected_character)

            for row, col in target_tiles:
                enemy = get_enemy_on_tile(enemies, row, col)

                if enemy is not None:
                    if status_name == "fire":
                        enemy["fire_stacks"] = enemy.get("fire_stacks", 0) + fire_stacks
                    else:
                        enemy[status_name] = max(enemy.get(status_name, 0), duration)

        elif effect_type == "place_trap":
            trap_damage = get_custom_card_value(card, selected_character, "damage", card.get("damage", 0))
            trap_duration = get_custom_card_value(card, selected_character, "trap_duration", card.get("trap_duration", 3))
            trap_radius = get_custom_card_value(card, selected_character, "trap_radius", card.get("trap_radius", 1))
            status_duration = get_custom_card_value(card, selected_character, "status_duration", card.get("status_duration", 1))

            result["traps"] = result.get("traps", [])

            trap_place_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("place_tiles_from", "trap_place_tiles")
            )

            trap_hitbox_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("trigger_tiles_from", "trap_hitbox_tiles")
            )

            if not trap_place_tiles:
                trap_place_tiles = [(selected_character["row"], selected_character["col"])]

            if not trap_hitbox_tiles:
                trap_hitbox_tiles = trap_place_tiles

            for row, col in trap_place_tiles:
                result["traps"].append({
                    "kind": "trap",
                    "row": row,
                    "col": col,
                    "damage": trap_damage,
                    "duration": trap_duration,
                    "radius": trap_radius,
                    "trigger_tiles": [
                        {"row": trigger_row, "col": trigger_col}
                        for trigger_row, trigger_col in trap_hitbox_tiles
                    ],
                    "status": effect.get("status"),
                    "status_duration": status_duration,
                    "snare_until_gone": effect.get("snare_until_gone", False)
                })

        elif effect_type == "place_fire_trap":
            result["traps"] = result.get("traps", [])

            trap_duration = get_custom_card_value(card, selected_character, "trap_duration", card.get("trap_duration", 3))
            fire_stacks = get_custom_card_value(card, selected_character, "fire_stacks", card.get("fire_stacks", 1))

            trap_place_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("place_tiles_from", "trap_place_tiles")
            )

            trap_hitbox_tiles = get_relative_custom_tiles_from_layer(
                card,
                selected_character,
                effect.get("trigger_tiles_from", "trap_hitbox_tiles")
            )

            if not trap_place_tiles:
                trap_place_tiles = [(selected_character["row"], selected_character["col"])]

            if not trap_hitbox_tiles:
                trap_hitbox_tiles = trap_place_tiles

            for row, col in trap_hitbox_tiles:
                result["traps"].append({
                    "kind": "fire_floor",
                    "row": row,
                    "col": col,
                    "duration": trap_duration,
                    "fire_stacks_on_enter": fire_stacks,
                    "entry_damage": effect.get("entry_damage", 2),
                    "stay_damage": effect.get("stay_damage", 2),
                    "source_place_tiles": [
                        {"row": place_row, "col": place_col}
                        for place_row, place_col in trap_place_tiles
                    ]
                })

    return result


CARD_EFFECTS = {
    "basic_attack": play_basic_attack,
    "pierce_row": play_pierce_row,
    "cleave_column": play_cleave_column,
    "move": start_move_card,
    "deep_breath": play_deep_breath,
    "shove": start_shove_card,
    "mule_kick": play_mule_kick,
    "reckless_charge": play_reckless_charge,
    "trap": place_trap_card,
    "custom_card": run_custom_card_effect
}


def play_card(card, selected_character, enemies, current_energy):
    if not character_can_use_card(selected_character, card):
        return False, current_energy, None

    if current_energy < card["cost"]:
        return False, current_energy, None

    effect_name = card["effect"]

    if effect_name not in CARD_EFFECTS:
        return False, current_energy, None

    current_energy -= card["cost"]

    card = get_modified_attack_card(card, selected_character)
    effect_function = CARD_EFFECTS[effect_name]
    result = effect_function(card, selected_character, enemies)

    if result is None:
        return False, current_energy + card["cost"], None

    return True, current_energy, result


def get_reaction_cost(card):
    return card["cost"] + 1


def play_reaction_card(card, selected_character, enemies, current_energy):
    if not character_can_use_card(selected_character, card):
        return False, current_energy, None

    if card["type"] != "attack":
        return False, current_energy, None

    if not card.get("can_react", True):
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
