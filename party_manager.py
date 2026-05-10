import pygame

from settings import PLAYER_GRID_X, GRID_Y, GRID_SIZE, GRID_GAP
from loaders.battle_assets import load_character_idle_frames
from cards.card_effects import character_can_use_card
from Characters.archer import archer
from Characters.warrior import warrior


def make_party():
    # Copy character templates so each run can change HP/position safely.
    archer_character = archer.copy()
    warrior_character = warrior.copy()

    archer_character["idle_frames"] = load_character_idle_frames(archer_character)
    warrior_character["idle_frames"] = load_character_idle_frames(warrior_character)

    return [archer_character, warrior_character]


def place_party_on_grid(party, player_grid_data, reset_hp=False):
    # Write every party member into the player grid before a battle starts.
    for character in party:
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
