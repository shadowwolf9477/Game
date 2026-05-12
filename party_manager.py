import pygame

from settings import PLAYER_GRID_X, GRID_Y, GRID_SIZE, GRID_GAP
from loaders.battle_assets import load_character_idle_frames, load_character_battle_frames
from loaders.animation_loader import make_flipped_frames
from cards.card_effects import character_can_use_card
from Characters.archer import archer
from Characters.warrior import warrior


def make_party():
    # Copy character templates so each run can change HP/position safely.
    archer_character = archer.copy()
    warrior_character = warrior.copy()

    archer_character["idle_frames"] = load_character_idle_frames(archer_character)
    warrior_character["idle_frames"] = load_character_idle_frames(warrior_character)
    archer_character["attack_frames"] = load_character_battle_frames(archer_character, "attack_animation")
    warrior_character["attack_frames"] = load_character_battle_frames(warrior_character, "attack_animation")
    archer_character["death_frames"] = load_character_battle_frames(archer_character, "death_animation")
    warrior_character["death_frames"] = load_character_battle_frames(warrior_character, "death_animation")
    archer_character["idle_frames_flipped"] = make_flipped_frames(archer_character["idle_frames"])
    warrior_character["idle_frames_flipped"] = make_flipped_frames(warrior_character["idle_frames"])
    archer_character["attack_frames_flipped"] = make_flipped_frames(archer_character["attack_frames"])
    warrior_character["attack_frames_flipped"] = make_flipped_frames(warrior_character["attack_frames"])
    archer_character["death_frames_flipped"] = make_flipped_frames(archer_character["death_frames"])
    warrior_character["death_frames_flipped"] = make_flipped_frames(warrior_character["death_frames"])

    return [archer_character, warrior_character]


def place_party_on_grid(party, player_grid_data, reset_hp=False):
    # Write every party member into the player grid before a battle starts.
    for character in party:
        character["board"] = "player"
        character["shielding"] = None
        character["snared"] = 0
        character["reaction_locked"] = 0
        character["random_discard_next_turn"] = 0
        character["weak_attacks"] = 0
        character["block"] = 0
        character["death_frame_index"] = 0
        character["death_animation_done"] = False
        character["row"] = character["starting_row"]
        character["col"] = character["starting_col"]

        if reset_hp:
            character["current_hp"] = character["max_hp"]
        elif character["current_hp"] <= 0:
            # Dead characters limp into the next battle at 1 HP.
            character["current_hp"] = 1

        player_grid_data[character["row"]][character["col"]]["unit"] = character


def get_first_alive_character_index(party):
    for index, character in enumerate(party):
        if character["current_hp"] > 0:
            return index

    return None


def get_first_usable_character_index(party, card):
    for index, character in enumerate(party):
        if character_can_use_card(character, card):
            return index

    return None


def get_selected_character(party, selected_character_index):
    if len(party) == 0:
        return None

    if party[selected_character_index]["current_hp"] <= 0:
        first_alive_index = get_first_alive_character_index(party)

        if first_alive_index is None:
            return None

        return party[first_alive_index]

    return party[selected_character_index]


def get_clicked_character_index(party, mouse_pos):
    # Click a living character's board tile to choose who will use cards.
    for index, character in enumerate(party):
        if character["current_hp"] <= 0:
            continue

        x = PLAYER_GRID_X + character["col"] * (GRID_SIZE + GRID_GAP)
        y = GRID_Y + character["row"] * (GRID_SIZE + GRID_GAP)
        character_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

        if character_rect.collidepoint(mouse_pos):
            return index

    return None


def characters_are_adjacent(first_character, second_character):
    row_distance = abs(first_character["row"] - second_character["row"])
    col_distance = abs(first_character["col"] - second_character["col"])

    return row_distance + col_distance == 1


def get_shield_target(party, shielding_character):
    if shielding_character is None or shielding_character["current_hp"] <= 0:
        return None

    active_target = shielding_character.get("shielding")

    if active_target is not None:
        if active_target["current_hp"] > 0 and characters_are_adjacent(shielding_character, active_target):
            return active_target

        return None

    if party_has_active_shield(party):
        return None

    for character in party:
        if character is shielding_character or character["current_hp"] <= 0:
            continue

        if characters_are_adjacent(shielding_character, character):
            return character

    return None


def get_shield_button_rect(party, selected_character):
    shield_target = get_shield_target(party, selected_character)

    if shield_target is None:
        return None

    selected_x = PLAYER_GRID_X + selected_character["col"] * (GRID_SIZE + GRID_GAP)
    selected_y = GRID_Y + selected_character["row"] * (GRID_SIZE + GRID_GAP)
    target_x = PLAYER_GRID_X + shield_target["col"] * (GRID_SIZE + GRID_GAP)
    target_y = GRID_Y + shield_target["row"] * (GRID_SIZE + GRID_GAP)

    button_width = 180
    button_height = 44
    center_x = (selected_x + target_x + GRID_SIZE) // 2
    button_x = center_x - button_width // 2
    button_y = max(selected_y, target_y) + GRID_SIZE + 8

    return pygame.Rect(button_x, button_y, button_width, button_height)


def clear_party_shields(party):
    for character in party:
        character["shielding"] = None


def party_has_active_shield(party):
    for character in party:
        if character.get("shielding") is not None:
            return True

    return False


def clear_shields_involving_character(party, moved_character):
    for character in party:
        if character is moved_character or character.get("shielding") is moved_character:
            character["shielding"] = None


def remove_broken_shields(party):
    for character in party:
        shield_target = character.get("shielding")

        if shield_target is None:
            continue

        if (
            character["current_hp"] <= 0
            or shield_target["current_hp"] <= 0
            or not characters_are_adjacent(character, shield_target)
        ):
            character["shielding"] = None


def tick_party_statuses(party):
    status_keys = ["snared"]

    for character in party:
        for status_key in status_keys:
            if character.get(status_key, 0) > 0:
                character[status_key] -= 1


def tick_enemy_turn_statuses(party):
    for character in party:
        if character.get("reaction_locked", 0) > 0:
            character["reaction_locked"] -= 1
