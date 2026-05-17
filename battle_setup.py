import random
from settings import GRID_ROWS, GRID_COLS
from movement import move_unit, can_land_on_tile
from party_manager import characters_are_adjacent

RANDOM_BATTLE_ROOMS = ["orc_goblins", "bone_pack", "web_ambush"]
BASIC_MAX_TILE_PRESSURE = 1
HEAVY_MAX_TILE_PRESSURE = 2
DEBUFF_MAX_TILE_PRESSURE = 1
IMPERFECT_AIM_CHANCE = 0.35


def start_tutorial_battle(enemies, enemy_grid_data):
    # The tutorial fight is fixed so new runs start with a predictable test battle.
    enemies.clear()

    goblin = {
        "name": "Goblin",
        "type": "goblin",
        "board": "enemy",
        "row": 1,
        "col": 2,
        "hp": 15,
        "max_hp": 15,
        "attack_damage": 5,
        "attack_interval": 1,
        "turns_until_attack": 1
    }

    enemies.append(goblin)
    # Store the same enemy object on the grid so movement/rendering can find it.
    enemy_grid_data[goblin["row"]][goblin["col"]]["unit"] = goblin


def choose_random_battle_room(last_battle_room=None):
    possible_rooms = RANDOM_BATTLE_ROOMS.copy()

    if last_battle_room in possible_rooms and len(possible_rooms) > 1:
        possible_rooms.remove(last_battle_room)

    return random.choice(possible_rooms)


def start_map_battle(enemies, enemy_grid_data, last_battle_room=None):
    enemies.clear()
    battle_room = choose_random_battle_room(last_battle_room)

    if battle_room == "orc_goblins":
        start_orc_battle(enemies, enemy_grid_data)
    if battle_room == "bone_pack":
        start_bone_pack_battle(enemies, enemy_grid_data)
    if battle_room == "web_ambush":
        start_web_ambush_battle(enemies, enemy_grid_data)

    return battle_room


def start_orc_battle(enemies, enemy_grid_data):
    orc = {
        "name": "Orc",
        "type": "orc",
        "board": "enemy",
        "row": 1,
        "col": 2,
        "hp": 40,
        "max_hp": 40,
        "attack_damage": 10,
        "attack_interval": 2,
        "turns_until_attack": 2,
        "flip_x": True
    }

    goblins = [
        build_goblin(0, 0),
        build_goblin(1, 4),
        build_goblin(2, 1)
    ]

    add_enemy_to_grid(orc, enemies, enemy_grid_data)

    for goblin in goblins:
        add_enemy_to_grid(goblin, enemies, enemy_grid_data)


def build_goblin(row, col):
    return {
        "name": "Goblin",
        "type": "goblin",
        "board": "enemy",
        "row": row,
        "col": col,
        "hp": 15,
        "max_hp": 15,
        "attack_damage": 5,
        "attack_interval": 1,
        "turns_until_attack": 1,
        "flip_x": True
    }


def start_bone_pack_battle(enemies, enemy_grid_data):
    bone_caller = {
        "name": "Bone Caller",
        "type": "bone_caller",
        "board": "enemy",
        "row": 1,
        "col": 2,
        "hp": 60,
        "max_hp": 60,
        "attack_damage": 10,
        "attack_interval": 2,
        "turns_until_attack": 2,
        "heal_interval": 3,
        "turns_until_heal": 3,
        "heal_amount": 5,
        "spawn_bonus": 0,
        "flip_x": True
    }

    skeletons = [
        build_skeleton(0, 1, 30, 10, 2),
        build_skeleton(2, 3, 30, 10, 2)
    ]

    add_enemy_to_grid(bone_caller, enemies, enemy_grid_data)

    for skeleton in skeletons:
        add_enemy_to_grid(skeleton, enemies, enemy_grid_data)


def build_skeleton(row, col, hp, attack_damage, attack_range):
    return {
        "name": "Skeleton",
        "type": "skeleton",
        "board": "enemy",
        "row": row,
        "col": col,
        "hp": hp,
        "max_hp": hp,
        "attack_damage": attack_damage,
        "attack_range": attack_range,
        "attack_interval": 1,
        "turns_until_attack": 1,
        "split_threshold": max(1, hp // 2),
        "can_split": hp > 1,
        "flip_x": True
    }


def start_web_ambush_battle(enemies, enemy_grid_data):
    web_priest = {
        "name": "Web Priest",
        "type": "web_priest",
        "board": "enemy",
        "row": 1,
        "col": 2,
        "hp": 40,
        "max_hp": 40,
        "attack_damage": 10,
        "attack_interval": 2,
        "turns_until_attack": 2,
        "status_effect": "reaction_locked",
        "status_duration": 2,
        "flip_x": True
    }

    crawler_positions = [(0, 0), (0, 4), (1, 0), (2, 1), (2, 4)]
    add_enemy_to_grid(web_priest, enemies, enemy_grid_data)

    for row, col in crawler_positions:
        add_enemy_to_grid(build_crawler(row, col), enemies, enemy_grid_data)


def build_crawler(row, col):
    return {
        "name": "Crawler",
        "type": "crawler",
        "board": "enemy",
        "row": row,
        "col": col,
        "hp": 15,
        "max_hp": 15,
        "attack_damage": 5,
        "attack_interval": 1,
        "turns_until_attack": 1,
        "status_effect": "snared",
        "status_duration": 1,
        "flip_x": True
    }


def add_enemy_to_grid(enemy, enemies, enemy_grid_data):
    enemy["board"] = "enemy"
    enemies.append(enemy)
    enemy_grid_data[enemy["row"]][enemy["col"]]["unit"] = enemy


def sync_enemy_grid(enemies, enemy_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            enemy_grid_data[row][col]["unit"] = None

    for enemy in enemies:
        enemy_grid_data[enemy["row"]][enemy["col"]]["unit"] = enemy


def place_trap_on_enemy_grid(trap, enemy_grid_data):
    row = trap["row"]
    col = trap["col"]

    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        enemy_grid_data[row][col]["effect"] = trap


def trigger_enemy_traps(enemy, enemy_grid_data):
    hits = []

    tile = enemy_grid_data[enemy["row"]][enemy["col"]]
    trap = tile.get("effect")

    if trap is None:
        return hits

    if trap.get("kind") == "fire_floor":
        entry_damage = trap.get("entry_damage", 2)
        fire_stacks = trap.get("fire_stacks_on_enter", 1)

        enemy["hp"] -= entry_damage
        apply_fire_to_enemy(enemy, fire_stacks)

        hits.append({
            "target": enemy,
            "damage": entry_damage
        })

        return hits

    row_distance = abs(enemy["row"] - trap["row"])
    col_distance = abs(enemy["col"] - trap["col"])

    if row_distance <= trap.get("radius", 0) and col_distance <= trap.get("radius", 0):
        enemy["hp"] -= trap["damage"]
        hits.append({
            "target": enemy,
            "damage": trap["damage"]
        })

        if trap.get("snare_until_gone", False):
            enemy["trapped"] = max(enemy.get("trapped", 0), trap.get("duration", 1))

    return hits


def tick_traps(enemy_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            trap = enemy_grid_data[row][col].get("effect")

            if trap is None:
                continue

            trap["duration"] -= 1

            if trap["duration"] <= 0:
                enemy_grid_data[row][col]["effect"] = None


def handle_enemy_deaths(enemies, enemy_grid_data):
    dead_enemies = [enemy for enemy in enemies if enemy["hp"] <= 0]

    if dead_enemies:
        enemies[:] = [enemy for enemy in enemies if enemy["hp"] > 0]
        sync_enemy_grid(enemies, enemy_grid_data)


def handle_enemy_splits(enemies, enemy_grid_data):
    split_skeletons = [
        enemy for enemy in enemies
        if enemy["type"] == "skeleton"
        and enemy.get("can_split", False)
        and enemy["hp"] > 1
        and enemy["hp"] <= enemy["split_threshold"]
    ]

    for skeleton in split_skeletons:
        split_skeleton(skeleton, enemies, enemy_grid_data)

    sync_enemy_grid(enemies, enemy_grid_data)


def notify_bone_callers_of_spawn(enemies, spawned_enemy_count):
    for enemy in enemies:
        if enemy["type"] == "bone_caller" and enemy["hp"] > 0:
            enemy["spawn_bonus"] = enemy.get("spawn_bonus", 0) + spawned_enemy_count


def split_skeleton(skeleton, enemies, enemy_grid_data):
    first_split_hp, second_split_hp = split_remaining_hp(skeleton["hp"])
    split_damage = max(1, skeleton["attack_damage"] // 2)
    split_range = max(1, skeleton.get("attack_range", 1) // 2)
    split_tiles = [(skeleton["row"], skeleton["col"])]
    split_tiles.extend(get_empty_adjacent_enemy_tiles(skeleton, enemy_grid_data))

    enemies.remove(skeleton)
    spawned_enemy_count = 0

    for tile_index, (row, col) in enumerate(split_tiles[:2]):
        split_hp = first_split_hp

        if tile_index == 1:
            split_hp = second_split_hp

        new_skeleton = build_skeleton(row, col, split_hp, split_damage, split_range)
        new_skeleton["can_split"] = split_hp > 1
        copy_loaded_enemy_assets(skeleton, new_skeleton)
        enemies.append(new_skeleton)
        spawned_enemy_count += 1

    if spawned_enemy_count > 0:
        notify_bone_callers_of_spawn(enemies, spawned_enemy_count)

    if len(split_tiles) == 0:
        skeleton["can_split"] = False
        enemies.append(skeleton)


def split_remaining_hp(current_hp):
    split_hp = max(1, current_hp // 2)

    return split_hp, split_hp


def copy_loaded_enemy_assets(source_enemy, target_enemy):
    # Split enemies are created mid-battle, after main.py has already loaded enemy art.
    # Copy the parent frames so newborn skeletons can render immediately.
    asset_keys = [
        "idle_frames",
        "idle_frames_flipped",
        "attack_frames",
        "attack_frames_flipped",
        "death_frames",
        "death_frames_flipped"
    ]

    for asset_key in asset_keys:
        if asset_key in source_enemy:
            target_enemy[asset_key] = source_enemy[asset_key]


def get_empty_adjacent_enemy_tiles(enemy, enemy_grid_data):
    adjacent_tiles = []
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    for row_change, col_change in directions:
        row = enemy["row"] + row_change
        col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, row, col):
            adjacent_tiles.append((row, col))

    random.shuffle(adjacent_tiles)

    return adjacent_tiles


def prepare_enemy_attacks(enemies, player_grid_data):
    for enemy in enemies:
        if enemy["turns_until_attack"] <= 1:
            if enemy["type"] == "orc":
                choose_orc_attack(enemy, player_grid_data)
            elif enemy["type"] == "bone_caller":
                choose_bone_caller_attack(enemy, player_grid_data)
            elif enemy["type"] == "skeleton":
                choose_skeleton_attack(enemy, player_grid_data)
            elif enemy["type"] == "crawler":
                choose_crawler_attack(enemy, player_grid_data)
            elif enemy["type"] == "web_priest":
                choose_web_priest_attack(enemy, player_grid_data)
            else:
                choose_goblin_attack(enemy, player_grid_data)


def choose_goblin_attack(enemy, player_grid_data):
    target = get_lowest_hp_living_character_from_grid(player_grid_data)

    if target is None:
        add_random_attacks(enemy, player_grid_data, 2)
        return

    target_tiles = []
    escape_tiles = get_adjacent_player_tiles(target["row"], target["col"])

    if random.random() >= IMPERFECT_AIM_CHANCE:
        target_tiles.append((target["row"], target["col"]))

    if escape_tiles:
        random.shuffle(escape_tiles)
        target_tiles.extend(escape_tiles)

    if not target_tiles:
        target_tiles.append((target["row"], target["col"]))

    add_low_pressure_attacks(
        player_grid_data,
        target_tiles,
        enemy,
        2,
        BASIC_MAX_TILE_PRESSURE
    )


def add_random_attacks(enemy, player_grid_data, attack_count):
    all_tiles = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            all_tiles.append((row, col))

    add_low_pressure_attacks(
        player_grid_data,
        all_tiles,
        enemy,
        attack_count,
        BASIC_MAX_TILE_PRESSURE
    )


def choose_orc_attack(enemy, player_grid_data):
    start_row, start_col = get_best_2x2_start_for_players(player_grid_data, enemy)

    for row in range(start_row, min(start_row + 2, GRID_ROWS)):
        for col in range(start_col, min(start_col + 2, GRID_COLS)):
            add_pressure_limited_attack(
                player_grid_data,
                row,
                col,
                enemy,
                HEAVY_MAX_TILE_PRESSURE
            )


def choose_bone_caller_attack(enemy, player_grid_data):
    target_row = get_best_bone_caller_row(player_grid_data)

    for col in range(GRID_COLS):
        add_pressure_limited_attack(
            player_grid_data,
            target_row,
            col,
            enemy,
            HEAVY_MAX_TILE_PRESSURE,
            enemy["attack_damage"] + enemy.get("spawn_bonus", 0)
        )


def choose_skeleton_attack(enemy, player_grid_data):
    target = get_closest_living_character_from_grid(enemy, player_grid_data)
    target_row = enemy["row"]

    if target is not None:
        target_row = target["row"]

    attack_range = max(1, enemy.get("attack_range", 1))
    target_cols = get_column_window_around_target(target, attack_range)

    for col in target_cols:
        add_pressure_limited_attack(
            player_grid_data,
            target_row,
            col,
            enemy,
            BASIC_MAX_TILE_PRESSURE
        )


def choose_crawler_attack(enemy, player_grid_data):
    target = get_closest_living_character_from_grid(enemy, player_grid_data)

    if target is None:
        target_row = enemy["row"]
        target_col = enemy["col"]
    else:
        target_row = target["row"]
        target_col = target["col"]

    add_pressure_limited_attack(
        player_grid_data,
        target_row,
        target_col,
        enemy,
        HEAVY_MAX_TILE_PRESSURE,
        status_effect=enemy["status_effect"],
        status_duration=enemy["status_duration"]
    )


def choose_web_priest_attack(enemy, player_grid_data):
    target = get_most_exposed_living_character_from_grid(player_grid_data)

    if target is None:
        center_row = random.randint(0, GRID_ROWS - 1)
        center_col = random.randint(0, GRID_COLS - 1)
    else:
        center_row = target["row"]
        center_col = target["col"]

        if random.random() < IMPERFECT_AIM_CHANCE:
            nearby_tiles = get_adjacent_player_tiles(center_row, center_col)

            if nearby_tiles:
                center_row, center_col = random.choice(nearby_tiles)

    pattern = random.choice(["x", "plus"])
    target_tiles = []

    if pattern == "x":
        offsets = [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)]

        for row_offset, col_offset in offsets:
            target_tiles.append((center_row + row_offset, center_col + col_offset))
    else:
        for row in range(GRID_ROWS):
            target_tiles.append((row, center_col))

        for col in range(GRID_COLS):
            target_tiles.append((center_row, col))

    target_tiles = list(dict.fromkeys(target_tiles))

    for row, col in target_tiles:
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            add_pressure_limited_attack(
                player_grid_data,
                row,
                col,
                enemy,
                DEBUFF_MAX_TILE_PRESSURE,
                status_effect=enemy["status_effect"],
                status_duration=enemy["status_duration"],
                random_discard_next_turn=1,
                weak_attacks=2
            )


def get_living_characters_from_grid(player_grid_data):
    living_characters = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            character = player_grid_data[row][col].get("unit")

            if character is not None and character.get("current_hp", 0) > 0:
                living_characters.append(character)

    return living_characters


def get_lowest_hp_living_character_from_grid(player_grid_data):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return None

    return min(living_characters, key=lambda character: character["current_hp"])


def get_most_exposed_living_character_from_grid(player_grid_data):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return None

    return min(living_characters, key=lambda character: character.get("block", 0))


def get_closest_living_character_from_grid(enemy, player_grid_data):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return None

    return min(
        living_characters,
        key=lambda character: get_tile_distance(
            enemy["row"],
            enemy["col"],
            character["row"],
            character["col"]
        )
    )


def get_tile_distance(start_row, start_col, target_row, target_col):
    return abs(start_row - target_row) + abs(start_col - target_col)


def get_adjacent_player_tiles(row, col):
    adjacent_tiles = []

    for row_change, col_change in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        target_row = row + row_change
        target_col = col + col_change

        if 0 <= target_row < GRID_ROWS and 0 <= target_col < GRID_COLS:
            adjacent_tiles.append((target_row, target_col))

    return adjacent_tiles


def get_most_crowded_player_row(player_grid_data):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return random.randint(0, GRID_ROWS - 1)

    row_scores = [0 for row in range(GRID_ROWS)]

    for character in living_characters:
        row_scores[character["row"]] += 1

    best_score = max(row_scores)
    best_rows = [
        row for row, score in enumerate(row_scores)
        if score == best_score
    ]

    return random.choice(best_rows)


def get_best_bone_caller_row(player_grid_data):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return get_lowest_pressure_row(player_grid_data)

    best_row = 0
    best_score = None

    for row in range(GRID_ROWS):
        player_count = sum(1 for character in living_characters if character["row"] == row)
        pressure = get_row_pressure(player_grid_data, row)
        score = player_count * 10 - pressure

        if best_score is None or score > best_score:
            best_score = score
            best_row = row

    return best_row


def get_lowest_pressure_row(player_grid_data):
    return min(
        range(GRID_ROWS),
        key=lambda row: get_row_pressure(player_grid_data, row)
    )


def get_best_2x2_start_for_players(player_grid_data, enemy):
    living_characters = get_living_characters_from_grid(player_grid_data)

    if not living_characters:
        return (
            random.randint(0, GRID_ROWS - 2),
            random.randint(0, GRID_COLS - 2)
        )

    best_start = (0, 0)
    best_score = None

    for start_row in range(GRID_ROWS - 1):
        for start_col in range(GRID_COLS - 1):
            hit_count = 0
            closest_distance = 99
            pressure = 0

            for character in living_characters:
                in_box = (
                    start_row <= character["row"] <= start_row + 1
                    and start_col <= character["col"] <= start_col + 1
                )

                if in_box:
                    hit_count += 1

                closest_distance = min(
                    closest_distance,
                    get_tile_distance(start_row, start_col, character["row"], character["col"])
                )

            for row in range(start_row, start_row + 2):
                for col in range(start_col, start_col + 2):
                    pressure += get_tile_pressure(player_grid_data, row, col)

            score = hit_count * 100 - closest_distance - pressure * 25

            if best_score is None or score > best_score:
                best_score = score
                best_start = (start_row, start_col)

    return best_start


def get_column_window_around_target(target, attack_range):
    if target is None:
        return list(range(min(attack_range, GRID_COLS)))

    half_range = attack_range // 2
    start_col = target["col"] - half_range
    end_col = start_col + attack_range

    if start_col < 0:
        end_col -= start_col
        start_col = 0

    if end_col > GRID_COLS:
        start_col -= end_col - GRID_COLS
        end_col = GRID_COLS

    start_col = max(0, start_col)

    return list(range(start_col, end_col))


def get_tile_pressure(player_grid_data, row, col):
    incoming_attack = player_grid_data[row][col].get("incoming_attack")

    if incoming_attack is None:
        return 0

    return len(incoming_attack.get("attacks", []))


def get_row_pressure(player_grid_data, row):
    pressure = 0

    for col in range(GRID_COLS):
        pressure += get_tile_pressure(player_grid_data, row, col)

    return pressure


def add_low_pressure_attacks(
    player_grid_data,
    candidate_tiles,
    enemy,
    attack_count,
    max_tile_pressure,
    damage=None,
    status_effect=None,
    status_duration=None,
    random_discard_next_turn=0,
    weak_attacks=0
):
    unique_tiles = list(dict.fromkeys(candidate_tiles))
    random.shuffle(unique_tiles)
    unique_tiles.sort(key=lambda tile: get_tile_pressure(player_grid_data, tile[0], tile[1]))
    attacks_added = 0

    for row, col in unique_tiles:
        if attacks_added >= attack_count:
            break

        attack_was_added = add_pressure_limited_attack(
            player_grid_data,
            row,
            col,
            enemy,
            max_tile_pressure,
            damage,
            status_effect,
            status_duration,
            random_discard_next_turn,
            weak_attacks
        )

        if attack_was_added:
            attacks_added += 1

    return attacks_added


def add_pressure_limited_attack(
    player_grid_data,
    row,
    col,
    enemy,
    max_tile_pressure,
    damage=None,
    status_effect=None,
    status_duration=None,
    random_discard_next_turn=0,
    weak_attacks=0
):
    if get_tile_pressure(player_grid_data, row, col) >= max_tile_pressure:
        return False

    add_incoming_attack(
        player_grid_data,
        row,
        col,
        enemy,
        damage,
        status_effect,
        status_duration,
        random_discard_next_turn,
        weak_attacks
    )

    return True


def add_incoming_attack(
    player_grid_data,
    row,
    col,
    enemy,
    damage=None,
    status_effect=None,
    status_duration=None,
    random_discard_next_turn=0,
    weak_attacks=0
):
    if damage is None:
        damage = enemy["attack_damage"]

    incoming_attack = player_grid_data[row][col]["incoming_attack"]

    if incoming_attack is None:
        incoming_attack = {
            "damage": 0,
            "attacks": []
        }
        player_grid_data[row][col]["incoming_attack"] = incoming_attack

    attack = {
        "damage": damage,
        "source": enemy
    }

    if status_effect is not None:
        attack["status_effect"] = status_effect

    if status_duration is not None:
        attack["status_duration"] = status_duration

    if random_discard_next_turn > 0:
        attack["random_discard_next_turn"] = random_discard_next_turn

    if weak_attacks > 0:
        attack["weak_attacks"] = weak_attacks

    incoming_attack["attacks"].append(attack)
    incoming_attack["damage"] += damage


def clear_incoming_attacks(player_grid_data):
    # Clear warning tiles after attacks resolve or when battle is won.
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            player_grid_data[row][col]["incoming_attack"] = None


def clear_enemy_incoming_attacks(enemy, player_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            incoming_attack = player_grid_data[row][col]["incoming_attack"]

            if incoming_attack is None:
                continue

            incoming_attack["attacks"] = [
                attack for attack in incoming_attack["attacks"]
                if attack.get("source") is not enemy
            ]
            refresh_incoming_attack_tile(player_grid_data, row, col)


def clear_dead_enemy_incoming_attacks(enemies, player_grid_data):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            incoming_attack = player_grid_data[row][col]["incoming_attack"]

            if incoming_attack is None:
                continue

            incoming_attack["attacks"] = [
                attack for attack in incoming_attack["attacks"]
                if any(attack.get("source") is enemy for enemy in enemies)
            ]
            refresh_incoming_attack_tile(player_grid_data, row, col)


def refresh_incoming_attack_tile(player_grid_data, row, col):
    incoming_attack = player_grid_data[row][col]["incoming_attack"]

    if incoming_attack is None:
        return

    if len(incoming_attack["attacks"]) == 0:
        player_grid_data[row][col]["incoming_attack"] = None
        return

    incoming_attack["damage"] = sum(attack["damage"] for attack in incoming_attack["attacks"])


def resolve_incoming_attacks(player, player_row, player_col, player_grid_data):
    if player["current_hp"] <= 0:
        return

    # Only the tile the player currently occupies can hurt them right now.
    current_tile = player_grid_data[player_row][player_col]
    incoming_attack = current_tile["incoming_attack"]

    if incoming_attack is not None:
        player["current_hp"] -= incoming_attack["damage"]

        if player["current_hp"] < 0:
            player["current_hp"] = 0


def resolve_enemy_incoming_attacks(enemy, party, player_grid_data):
    hits = []

    for character in party:
        if character["current_hp"] <= 0:
            continue

        current_tile = player_grid_data[character["row"]][character["col"]]
        incoming_attack = current_tile["incoming_attack"]

        if incoming_attack is not None:
            matching_attacks = [
                attack for attack in incoming_attack["attacks"]
                if attack.get("source") is enemy
            ]

            if not matching_attacks:
                continue

            damage_target = get_shielding_character(party, character)
            damage = sum(attack["damage"] for attack in matching_attacks)

            damage = get_shielded_damage(
                damage_target,
                character,
                damage
            )

            damage = apply_block_to_damage(damage_target, damage)

            damage_target["current_hp"] -= damage
            hits.append({
                "target": damage_target,
                "damage": damage
            })

            if damage_target["current_hp"] < 0:
                damage_target["current_hp"] = 0

            for attack in matching_attacks:
                apply_attack_status(damage_target, attack)

    return hits


def apply_attack_status(character, incoming_attack):
    status_effect = incoming_attack.get("status_effect")

    if character["current_hp"] <= 0:
        return

    if status_effect is not None:
        status_duration = incoming_attack.get("status_duration", 1)
        character[status_effect] = max(character.get(status_effect, 0), status_duration)

    if incoming_attack.get("random_discard_next_turn", 0) > 0:
        character["random_discard_next_turn"] = max(
            character.get("random_discard_next_turn", 0),
            incoming_attack["random_discard_next_turn"]
        )

    if incoming_attack.get("weak_attacks", 0) > 0:
        character["weak_attacks"] = max(
            character.get("weak_attacks", 0),
            incoming_attack["weak_attacks"]
        )


def apply_block_to_damage(character, damage):
    block = character.get("block", 0)

    if block <= 0 or damage <= 0:
        return damage

    blocked_damage = min(block, damage)
    character["block"] = block - blocked_damage

    return damage - blocked_damage


def get_shielding_character(party, protected_character):
    for character in party:
        if character is protected_character or character["current_hp"] <= 0:
            continue

        if character.get("shielding") is protected_character and characters_are_adjacent(character, protected_character):
            return character

    return protected_character


def get_shielded_damage(damage_target, protected_character, damage):
    # Warrior passive only reduces damage taken FOR allies.
    # Direct hits to the Warrior are full damage.

    if damage_target is protected_character:
        return damage

    if damage_target["name"] != "Warrior":
        return damage

    reduced_damage = int(damage * 0.75)

    if damage > 0:
        reduced_damage = max(1, reduced_damage)

    return reduced_damage


def move_enemy_random(enemy, enemy_grid_data):
    # Placeholder enemy movement until each enemy type gets its own behavior.
    direction = random.choice(["left", "right", "up", "down"])

    if direction == "left":
        move_unit(enemy, enemy_grid_data, 0, -1)
    if direction == "right":
        move_unit(enemy, enemy_grid_data, 0, 1)
    if direction == "up":
        move_unit(enemy, enemy_grid_data, -1, 0)
    if direction == "down":
        move_unit(enemy, enemy_grid_data, 1, 0)


def get_enemy_random_movement_steps(enemy, enemy_grid_data):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)

    for row_change, col_change in directions:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            return [{
                "enemy": enemy,
                "row_change": row_change,
                "col_change": col_change,
                "is_final_step": True
            }]

    return []


def get_enemy_possible_movement_tiles(enemy, enemy_grid_data, party):
    if enemy["type"] == "orc":
        return get_orc_possible_movement_tiles(enemy, enemy_grid_data, party)

    if enemy["type"] == "skeleton":
        return get_skeleton_possible_movement_tiles(enemy, enemy_grid_data, party)

    if enemy["type"] == "crawler":
        return get_crawler_possible_movement_tiles(enemy, enemy_grid_data, party)

    if enemy["type"] in ["bone_caller", "web_priest"]:
        return get_support_enemy_possible_movement_tiles(enemy, enemy_grid_data, party)

    return get_goblin_possible_movement_tiles(enemy, enemy_grid_data, party)


def get_random_step_possible_movement_tiles(enemy, enemy_grid_data):
    possible_tiles = []
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    for row_change, col_change in directions:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            possible_tiles.append((next_row, next_col))

    return possible_tiles


def get_goblin_possible_movement_tiles(enemy, enemy_grid_data, party):
    preferred_steps = get_chase_preferred_steps(enemy, party)
    possible_tiles = []

    for row_change, col_change in preferred_steps:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            possible_tiles.append((next_row, next_col))

    if possible_tiles:
        return possible_tiles

    return get_random_step_possible_movement_tiles(enemy, enemy_grid_data)


def get_goblin_movement_steps(enemy, enemy_grid_data, party):
    return get_one_step_movement_toward_goal(enemy, enemy_grid_data, party)


def get_support_enemy_possible_movement_tiles(enemy, enemy_grid_data, party):
    possible_tiles = get_random_step_possible_movement_tiles(enemy, enemy_grid_data)
    target = get_closest_living_character(enemy, party)

    if target is None:
        return possible_tiles

    possible_tiles.sort(
        key=lambda tile: get_tile_distance(tile[0], tile[1], target["row"], target["col"]),
        reverse=True
    )

    return possible_tiles


def get_support_enemy_movement_steps(enemy, enemy_grid_data, party):
    possible_tiles = get_support_enemy_possible_movement_tiles(enemy, enemy_grid_data, party)

    if not possible_tiles:
        return []

    target_row, target_col = possible_tiles[0]

    return [{
        "enemy": enemy,
        "row_change": target_row - enemy["row"],
        "col_change": target_col - enemy["col"],
        "is_final_step": True
    }]


def get_skeleton_possible_movement_tiles(enemy, enemy_grid_data, party=None):
    possible_tiles = []

    for row_change in range(-2, 3):
        for col_change in range(-2, 3):
            if row_change == 0 and col_change == 0:
                continue

            if abs(row_change) + abs(col_change) > 2:
                continue

            target_row = enemy["row"] + row_change
            target_col = enemy["col"] + col_change

            if can_land_on_tile(enemy_grid_data, target_row, target_col, enemy):
                possible_tiles.append((target_row, target_col))

    target = get_closest_living_character(enemy, party) if party is not None else None

    if target is not None:
        possible_tiles.sort(
            key=lambda tile: get_tile_distance(tile[0], tile[1], target["row"], target["col"])
        )

    return possible_tiles


def get_skeleton_movement_steps(enemy, enemy_grid_data, party=None):
    possible_tiles = get_skeleton_possible_movement_tiles(enemy, enemy_grid_data, party)

    if not possible_tiles:
        return []

    for target_row, target_col in possible_tiles:
        row_change = target_row - enemy["row"]
        col_change = target_col - enemy["col"]
        step_paths = [
            build_step_path(enemy, row_change, col_change, True),
            build_step_path(enemy, row_change, col_change, False)
        ]
        random.shuffle(step_paths)

        for step_path in step_paths:
            if path_is_clear(enemy, enemy_grid_data, step_path):
                return step_path

    return []


def get_crawler_possible_movement_tiles(enemy, enemy_grid_data, party):
    preferred_steps = get_crawler_preferred_steps(enemy, party)
    possible_tiles = []

    for row_change, col_change in preferred_steps:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            possible_tiles.append((next_row, next_col))

    if possible_tiles:
        return possible_tiles

    return get_random_step_possible_movement_tiles(enemy, enemy_grid_data)


def get_crawler_movement_steps(enemy, enemy_grid_data, party):
    target_character = get_closest_living_character(enemy, party)

    if target_character is None:
        return get_enemy_random_movement_steps(enemy, enemy_grid_data)

    preferred_steps = get_crawler_preferred_steps(enemy, party)

    for step_row_change, step_col_change in preferred_steps:
        if step_row_change == 0 and step_col_change == 0:
            continue

        next_row = enemy["row"] + step_row_change
        next_col = enemy["col"] + step_col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            return [{
                "enemy": enemy,
                "row_change": step_row_change,
                "col_change": step_col_change,
                "is_final_step": True
            }]

    return get_enemy_random_movement_steps(enemy, enemy_grid_data)


def get_crawler_preferred_steps(enemy, party):
    return get_chase_preferred_steps(enemy, party)


def get_one_step_movement_toward_goal(enemy, enemy_grid_data, party):
    preferred_steps = get_chase_preferred_steps(enemy, party)

    for row_change, col_change in preferred_steps:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            return [{
                "enemy": enemy,
                "row_change": row_change,
                "col_change": col_change,
                "is_final_step": True
            }]

    return get_enemy_random_movement_steps(enemy, enemy_grid_data)


def get_chase_preferred_steps(enemy, party):
    target_character = get_closest_living_character(enemy, party)

    if target_character is None:
        return []

    row_change = get_direction_step(enemy["row"], target_character["row"])
    col_change = get_direction_step(enemy["col"], target_character["col"])
    preferred_steps = []

    if abs(enemy["col"] - target_character["col"]) >= abs(enemy["row"] - target_character["row"]):
        preferred_steps.append((0, col_change))
        preferred_steps.append((row_change, 0))
    else:
        preferred_steps.append((row_change, 0))
        preferred_steps.append((0, col_change))

    return [
        (row_change, col_change)
        for row_change, col_change in preferred_steps
        if row_change != 0 or col_change != 0
    ]


def get_closest_living_character(enemy, party):
    living_characters = [character for character in party if character["current_hp"] > 0]

    if not living_characters:
        return None

    return min(
        living_characters,
        key=lambda character: abs(enemy["row"] - character["row"]) + abs(enemy["col"] - character["col"])
    )


def get_direction_step(start_value, target_value):
    if target_value > start_value:
        return 1

    if target_value < start_value:
        return -1

    return 0


def move_orc_like_knight(enemy, enemy_grid_data):
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1)
    ]
    random.shuffle(knight_moves)

    for row_change, col_change in knight_moves:
        next_row = enemy["row"] + row_change
        next_col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            move_unit(enemy, enemy_grid_data, row_change, col_change)
            return


def get_orc_knight_movement_steps(enemy, enemy_grid_data, party=None):
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1)
    ]
    target_character = get_closest_living_character(enemy, party) if party is not None else None

    if target_character is not None:
        knight_moves.sort(
            key=lambda move: get_tile_distance(
                enemy["row"] + move[0],
                enemy["col"] + move[1],
                target_character["row"],
                target_character["col"]
            )
        )
    else:
        random.shuffle(knight_moves)

    for row_change, col_change in knight_moves:
        target_row = enemy["row"] + row_change
        target_col = enemy["col"] + col_change

        if not can_land_on_tile(enemy_grid_data, target_row, target_col, enemy):
            continue

        step_paths = [
            build_step_path(enemy, row_change, col_change, True),
            build_step_path(enemy, row_change, col_change, False)
        ]
        random.shuffle(step_paths)

        for step_path in step_paths:
            if path_is_clear(enemy, enemy_grid_data, step_path):
                return step_path

    return []


def get_orc_possible_movement_tiles(enemy, enemy_grid_data, party=None):
    possible_tiles = []
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1)
    ]

    for row_change, col_change in knight_moves:
        target_row = enemy["row"] + row_change
        target_col = enemy["col"] + col_change

        if not can_land_on_tile(enemy_grid_data, target_row, target_col, enemy):
            continue

        step_paths = [
            build_step_path(enemy, row_change, col_change, True),
            build_step_path(enemy, row_change, col_change, False)
        ]

        for step_path in step_paths:
            if path_is_clear(enemy, enemy_grid_data, step_path):
                possible_tiles.append((target_row, target_col))
                break

    target_character = get_closest_living_character(enemy, party) if party is not None else None

    if target_character is not None:
        possible_tiles.sort(
            key=lambda tile: get_tile_distance(tile[0], tile[1], target_character["row"], target_character["col"])
        )

    return possible_tiles


def build_step_path(enemy, row_change, col_change, row_first):
    steps = []

    if row_first:
        add_axis_steps(steps, enemy, row_change, 0)
        add_axis_steps(steps, enemy, 0, col_change)
    else:
        add_axis_steps(steps, enemy, 0, col_change)
        add_axis_steps(steps, enemy, row_change, 0)

    if steps:
        steps[-1]["is_final_step"] = True

    return steps


def add_axis_steps(steps, enemy, row_change, col_change):
    if row_change != 0:
        step_direction = 1

        if row_change < 0:
            step_direction = -1

        for step_index in range(abs(row_change)):
            steps.append({
                "enemy": enemy,
                "row_change": step_direction,
                "col_change": 0,
                "is_final_step": False
            })

    if col_change != 0:
        step_direction = 1

        if col_change < 0:
            step_direction = -1

        for step_index in range(abs(col_change)):
            steps.append({
                "enemy": enemy,
                "row_change": 0,
                "col_change": step_direction,
                "is_final_step": False
            })


def path_is_clear(enemy, enemy_grid_data, steps):
    current_row = enemy["row"]
    current_col = enemy["col"]

    for step in steps:
        current_row += step["row_change"]
        current_col += step["col_change"]

        if not can_land_on_tile(enemy_grid_data, current_row, current_col, enemy):
            return False

    return True


def process_enemy_healing(enemies):
    for enemy in enemies:
        if enemy["type"] != "bone_caller":
            continue

        if enemy["turns_until_heal"] <= 1:
            heal_random_ally(enemy, enemies)
            enemy["turns_until_heal"] = enemy["heal_interval"]
        else:
            enemy["turns_until_heal"] -= 1


def heal_random_ally(healer, enemies):
    heal_targets = [
        enemy for enemy in enemies
        if enemy is not healer and enemy["hp"] > 0 and "max_hp" in enemy
    ]

    if not heal_targets:
        return

    heal_target = random.choice(heal_targets)
    heal_target["hp"] += healer.get("heal_amount", 10)

    if heal_target["hp"] > heal_target["max_hp"]:
        heal_target["hp"] = heal_target["max_hp"]


def apply_fire_to_enemy(enemy, stacks):
    enemy["fire_stacks"] = enemy.get("fire_stacks", 0) + stacks


def tick_enemy_fire(enemy):
    fire_stacks = enemy.get("fire_stacks", 0)

    if fire_stacks <= 0:
        return None

    damage = fire_stacks * 3
    enemy["hp"] -= damage
    enemy["fire_stacks"] = max(0, fire_stacks - 1)

    return {
        "target": enemy,
        "damage": damage
    }


def process_enemy_end_of_turn_fire(enemies, enemy_grid_data):
    hits = []

    for enemy in enemies:
        if enemy["hp"] <= 0:
            continue

        tile = enemy_grid_data[enemy["row"]][enemy["col"]]
        floor_effect = tile.get("effect")

        if floor_effect is not None and floor_effect.get("kind") == "fire_floor":
            stay_damage = floor_effect.get("stay_damage", 2)
            enemy["hp"] -= stay_damage
            hits.append({
                "target": enemy,
                "damage": stay_damage
            })

        fire_hit = tick_enemy_fire(enemy)

        if fire_hit is not None:
            hits.append(fire_hit)

    return hits
