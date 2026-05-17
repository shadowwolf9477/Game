import pygame
import random
import subprocess
import sys

from state.character_select_state import make_character_select_state
from state.battle_animation_runtime import make_battle_animation_runtime
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DARK_BG,
    WHITE,
    FPS,
    GRID_ROWS,
    GRID_COLS,
    GRID_SIZE,
    GRID_GAP,
    PLAYER_GRID_X,
    ENEMY_GRID_X,
    GRID_Y,
    HAND_X,
    HAND_Y,
    CARD_WIDTH,
    CARD_HEIGHT,
    CARD_GAP
)
from dev_menu import (
    toggle_dev_menu,
    dev_menu_is_open,
    draw_dev_menu,
    instant_kill_all_enemies,
    instant_kill_first_enemy,
    add_card_to_hand,
    add_card_to_deck,
    get_custom_card_ids,
    get_battle_room_files
)
from state.game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN, GAME_OVER, MAP, REWARD
from cards.card_sleeves import CARD_SLEEVES
from cards.sleeve_effects import apply_sleeve, can_apply_sleeve
from cards.card_effects import character_can_use_card
from cards.card_rewards import generate_card_rewards

from battle_setup import (
    start_tutorial_battle,
    start_map_battle,
    prepare_enemy_attacks,
    clear_incoming_attacks,
    clear_enemy_incoming_attacks,
    clear_dead_enemy_incoming_attacks,
    resolve_enemy_incoming_attacks,
    sync_enemy_grid,
    handle_enemy_deaths,
    place_trap_on_enemy_grid,
    trigger_enemy_traps,
    tick_traps,
    get_enemy_possible_movement_tiles,
    process_enemy_end_of_turn_fire
)
from maps.map_loader import generate_map
from screens.map_screen import draw_map_screen, get_clicked_map_node, complete_map_node, scroll_map
from screens.reward_screen import (
    draw_reward_screen,
    get_reward_choice_click,
    get_clicked_reward_deck_card,
    get_clicked_card_reward
)
from screens.pile_screen import (
    draw_pile_buttons,
    draw_pile_viewer,
    get_clicked_pile_button,
    get_pile_view_close_clicked,
    get_pile_max_scroll
)
from screens.battle_popups import (
    draw_discard_choice_overlay,
    draw_discard_animation,
    draw_swing_choice_popup,
    get_clicked_swing_direction
)
from screens.character_select_screen import (
    create_character_select_buttons,
    draw_character_select_screen,
    add_character_to_selection
)
from party_manager import (
    make_party,
    place_party_on_grid,
    get_selected_character,
    get_clicked_character_index,
    get_first_usable_character_index,
    get_shield_button_rect,
    get_shield_target,
    clear_party_shields,
    clear_shields_involving_character,
    remove_broken_shields,
    tick_party_statuses,
    tick_enemy_turn_statuses
)
from loaders.character_select_assets import load_character_select_assets
from battle_grid import create_grid_data
from loaders.battle_assets import load_battle_assets, apply_enemy_assets
from loaders.sound_assets import load_battle_sounds, play_character_attack_sound
from movement import move_unit, can_land_on_tile
from menus.home_menu import create_home_menu_buttons, draw_home_menu
from menus.game_over_menu import create_game_over_buttons, draw_game_over_menu
from battle_renderer import (
    create_battle_buttons,
    draw_battle,
    draw_reaction_warning_edges,
    draw_enemy_hover_tooltip,
    get_clicked_enemy
)
from state.animation_state import update_animation_frame
from damage_numbers import make_damage_popup, update_damage_popups, draw_damage_popups
from battle_animations import (
    make_player_attack_animation,
    update_player_attack_animation,
    queue_enemy_death_animations,
    update_enemy_death_animations,
    draw_enemy_death_animations,
    start_player_death_animations_from_hits,
    update_party_death_animations,
    make_arrow_projectile,
    update_projectile_animations,
    draw_projectile_animations
)
from battle_turn_logic import (
    build_enemy_movement_queue,
    finish_enemy_turn,
    get_next_attacking_enemy_index
)
from team_specials import (
    TEAM_SPECIAL_MAX_CHARGE,
    add_team_special_charge,
    get_charge_from_hits,
    get_crossfire_tiles,
    play_crossfire_cleave,
    team_special_is_ready
)

from cards.card_renderer import draw_card_hand, get_clicked_card_index
from cards.card_effects import play_card, play_reaction_card, get_reaction_cost
from cards.card_targeting import get_card_preview_tiles
from cards.player_deck import build_starting_deck, shuffle_deck, draw_cards
from cards.card_library import CARD_LIBRARY


# Pygame setup.
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)
# Smaller text keeps reward-card labels inside their temporary boxes.
small_font = pygame.font.Font(None, 34)
parchment_font = pygame.font.Font(None, 26)
battle_sounds = load_battle_sounds()

dev_buttons = []
selected_dev_card_index = 0
selected_battle_index = 0

# Screen buttons are created by the module that owns their layout.
home_menu_buttons = create_home_menu_buttons()
start_button = home_menu_buttons["start"]
card_editor_button = home_menu_buttons["card_editor"]
quit_button = home_menu_buttons["quit"]

character_select_buttons = create_character_select_buttons()
archer_button = character_select_buttons["archer"]
warrior_button = character_select_buttons["warrior"]
character_start_button = character_select_buttons["start_game"]

battle_buttons = create_battle_buttons()
end_turn_button = battle_buttons["end_turn"]
play_card_button = battle_buttons["play_card"]
team_special_button = battle_buttons["team_special"]

game_over_buttons = create_game_over_buttons()
play_again_button = game_over_buttons["play_again"]
game_over_quit_button = game_over_buttons["quit"]


# Player and battle state.
# party holds the two real characters. selected_character is the current card user.
party = []
selected_character_index = 0
selected_character = None

current_turn = PLAYER_TURN
battle_number = 0
last_battle_room = None

player_grid_data = create_grid_data("player")
enemy_grid_data = create_grid_data("enemy")
enemies = []


# Card state.
# player_deck is the permanent combat deck. draw_pile/hand/discard_pile
# are the temporary battle piles that reset between battles.
player_deck = []
draw_pile = []
player_hand = []
discard_pile = []
selected_card_index = None

max_energy = 3
current_energy = 3

# Combat pile viewer state.
# Draw pile view is a shuffled copy so it does not reveal exact draw order.
pile_view_title = None
pile_view_cards = []
pile_scroll_y = 0
target_pile_scroll_y = 0

# Map state.
# map_layers is generated after the tutorial fight and then remembered.
map_layers = []
current_map_layer = 0

# Reward state.
# reward_mode switches the popup between reward choice and deck-card choice.

reward_mode = "choose_reward"
deck_scroll_y = 0
target_deck_scroll_y = 0
selected_sleeve = None
card_reward_choices = []


# Character select state will grow when the screen becomes a real party picker.
character_select_state = make_character_select_state()

# Movement card planning state.
# Movement cards enter a preview mode first so the player can choose a path
# before the character actually moves.
movement_mode = False
movement_card = None
movement_card_user = None
movement_preview_path = []
movement_preview_row = 0
movement_preview_col = 0
movement_steps_left = 0
shove_mode = False
shove_target = None
shove_card_user = None
shove_steps_left = 0
shove_preview_path = []
shove_preview_row = 0
shove_preview_col = 0
shove_animation_queue = []
shove_animation_timer = 0
shove_animation_speed = 10
# Enemy reaction state.
# Enemies move one board tile at a time, which can open reaction windows.
enemy_movement_queue = []
enemy_movement_timer = 0
enemy_movement_speed = 20
reaction_mode = False
reaction_enemy = None
reaction_options = []
team_special_charge = 0
team_special_aim_mode = False
damage_popups = []
enemy_death_animations = []
projectile_animations = []
player_attack_animation = None
pending_reward_after_deaths = False
selected_enemy_for_movement = None
enemy_movement_preview_tiles = []
discard_choice_mode = False
pending_chosen_discards = 0
pending_draw_after_discard = 0
discard_choice_prompt = ""
discard_animation = None
swing_choice_mode = False
swing_choice_card_index = None
swing_choice_character = None


# Battle assets.
# These frame lists are reused every frame instead of reloading images.
battle_background, enemy_assets = load_battle_assets()
character_select_assets = load_character_select_assets()

def get_reaction_protected_characters(party):
    protected_characters = []

    for character in party:
        shield_target = character.get("shielding")

        if shield_target is not None and shield_target["current_hp"] > 0:
            protected_characters.append(shield_target)

    return protected_characters


def get_reaction_character_for_card(card, party, moving_enemy, current_energy):
    protected_characters = get_reaction_protected_characters(party)

    if protected_characters:
        possible_characters = protected_characters
    else:
        possible_characters = party

    if current_energy < get_reaction_cost(card):
        return None

    for character in possible_characters:
        if character.get("shielding") is not None:
            continue

        if character.get("reaction_locked", 0) > 0:
            continue

        if not character_can_use_card(character, card):
            continue

        threatened_tiles = get_card_preview_tiles(card, character)

        if (moving_enemy["row"], moving_enemy["col"]) in threatened_tiles:
            return character

    return None


def get_reaction_options(player_hand, party, moving_enemy, current_energy):
    reaction_options = []

    for card_index, card in enumerate(player_hand):
        if card["type"] != "attack":
            continue

        if not card.get("can_react", True):
            continue

        reaction_character = get_reaction_character_for_card(card, party, moving_enemy, current_energy)

        if reaction_character is not None:
            reaction_options.append({
                "card_index": card_index,
                "character": reaction_character
            })

    return reaction_options


def get_reaction_option_for_card(reaction_options, card_index):
    for reaction_option in reaction_options:
        if reaction_option["card_index"] == card_index:
            return reaction_option

    return None


def add_damage_popups_from_hits(hits, board_name):
    if board_name == "enemy":
        board_x = ENEMY_GRID_X
    else:
        board_x = PLAYER_GRID_X

    for hit in hits:
        target = hit["target"]
        popup_x = board_x + target["col"] * (GRID_SIZE + GRID_GAP) + GRID_SIZE // 2
        popup_y = GRID_Y + target["row"] * (GRID_SIZE + GRID_GAP) + 8
        damage_popups.append(make_damage_popup(hit["damage"], popup_x, popup_y))


def handle_card_feedback(card_result, acting_character):
    global player_attack_animation
    global team_special_charge

    if not isinstance(card_result, dict):
        return

    player_attack_animation = make_player_attack_animation(acting_character)
    hits = card_result.get("hits", [])

    if not hits:
        return

    team_special_charge = add_team_special_charge(
        team_special_charge,
        get_charge_from_hits(hits)
    )

    arrow_projectile = make_arrow_projectile(acting_character, hits, enemy_assets["arrow"])

    if arrow_projectile is not None:
        projectile_animations.append(arrow_projectile)

    add_damage_popups_from_hits(hits, "enemy")
    queue_enemy_death_animations(enemies, enemy_death_animations)
    play_character_attack_sound(battle_sounds, acting_character)


def get_hand_card_rect(card_index):
    x = HAND_X + card_index * (CARD_WIDTH + CARD_GAP)
    return pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)


def start_discard_choice(discard_count, prompt, draw_after_discard=0):
    global discard_choice_mode
    global pending_chosen_discards
    global pending_draw_after_discard
    global discard_choice_prompt
    global selected_card_index
    global movement_mode
    global movement_card
    global movement_card_user
    global movement_preview_path
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left
    global shove_preview_path
    global shove_preview_row
    global shove_preview_col

    if discard_count <= 0 or not player_hand:
        if draw_after_discard > 0:
            draw_cards(draw_pile, discard_pile, player_hand, draw_after_discard)
        return

    # Chosen discard is a modal step: finish it before playing anything else.
    discard_choice_mode = True
    pending_chosen_discards += discard_count
    pending_draw_after_discard += draw_after_discard
    discard_choice_prompt = prompt
    selected_card_index = None
    movement_mode = False
    movement_card = None
    movement_card_user = None
    movement_preview_path = []
    shove_mode = False
    shove_target = None
    shove_card_user = None
    shove_steps_left = 0
    shove_preview_path = []
    shove_preview_row = 0
    shove_preview_col = 0


def choose_discard_card(card_index):
    global discard_choice_mode
    global pending_chosen_discards
    global pending_draw_after_discard
    global discard_choice_prompt
    global discard_animation
    global swing_choice_mode
    global swing_choice_card_index
    global swing_choice_character

    if card_index is None or card_index >= len(player_hand):
        return

    start_rect = get_hand_card_rect(card_index)
    discarded_card = player_hand.pop(card_index)
    discard_pile.append(discarded_card)

    discard_animation = {
        "card": discarded_card,
        "x": start_rect.x,
        "y": start_rect.y,
        "start_y": start_rect.y,
        "end_y": SCREEN_HEIGHT + CARD_HEIGHT,
        "timer": 0,
        "duration": 22
    }

    pending_chosen_discards -= 1

    if pending_chosen_discards <= 0 or not player_hand:
        discard_choice_mode = False
        pending_chosen_discards = 0
        discard_choice_prompt = ""

        if pending_draw_after_discard > 0:
            draw_cards(draw_pile, discard_pile, player_hand, pending_draw_after_discard)
            pending_draw_after_discard = 0


def update_discard_animation():
    global discard_animation

    if discard_animation is None:
        return

    discard_animation["timer"] += 1
    progress = discard_animation["timer"] / discard_animation["duration"]

    if progress >= 1:
        discard_animation = None
        return

    eased_progress = progress * progress
    discard_animation["y"] = discard_animation["start_y"] + (
        discard_animation["end_y"] - discard_animation["start_y"]
    ) * eased_progress


def card_needs_swing_choice(card, character):
    if card is None or character is None:
        return False

    if character.get("name") != "Warrior":
        return False

    if card["effect"] == "cleave_column":
        return True

    if card["effect"] == "basic_attack":
        return count_enemies_in_card_preview(card, character) > 1

    return False


def count_enemies_in_card_preview(card, character):
    preview_tiles = get_card_preview_tiles(card, character)
    enemy_count = 0

    for enemy in enemies:
        if (enemy["row"], enemy["col"]) in preview_tiles:
            enemy_count += 1

    return enemy_count


def can_afford_card(card):
    if card is None:
        return False

    return current_energy >= card["cost"]


def get_character_card_value(card, character, value_name, default=0):
    character_values = card.get("character_values", {})

    if character is not None:
        character_name = character.get("name")

        if character_name in character_values:
            if value_name in character_values[character_name]:
                return character_values[character_name][value_name]

    return card.get(value_name, default)


def card_uses_movement_preview(card):
    if card is None:
        return False

    if card["effect"] == "move":
        return True

    if card["effect"] != "custom_card":
        return False

    for effect in card.get("effects", []):
        if effect.get("type") in ["move_character", "charge_character"]:
            return True

    return False


def get_card_movement_range(card, character):
    if card["effect"] == "move":
        return card.get("move_range", 0)

    for effect in card.get("effects", []):
        effect_type = effect.get("type")

        if effect_type not in ["move_character", "charge_character"]:
            continue

        value_name = effect.get("distance_from", "move_distance")
        return get_character_card_value(card, character, value_name, card.get("move_distance", 1))

    return 0


def get_keyboard_direction(key, allow_arrow_keys=False):
    movement_keys = {
        pygame.K_a: (0, -1),
        pygame.K_d: (0, 1),
        pygame.K_w: (-1, 0),
        pygame.K_s: (1, 0)
    }

    if allow_arrow_keys:
        movement_keys.update({
            pygame.K_LEFT: (0, -1),
            pygame.K_RIGHT: (0, 1),
            pygame.K_UP: (-1, 0),
            pygame.K_DOWN: (1, 0)
        })

    return movement_keys.get(key, (0, 0))


def get_clicked_grid_tile(mouse_pos, board_x):
    mouse_x, mouse_y = mouse_pos

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            tile_x = board_x + col * (GRID_SIZE + GRID_GAP)
            tile_y = GRID_Y + row * (GRID_SIZE + GRID_GAP)
            tile_rect = pygame.Rect(tile_x, tile_y, GRID_SIZE, GRID_SIZE)

            if tile_rect.collidepoint(mouse_x, mouse_y):
                return row, col

    return None


def start_movement_preview(card_index, character):
    global movement_mode
    global movement_card
    global movement_card_user
    global movement_preview_row
    global movement_preview_col
    global movement_preview_path
    global movement_steps_left

    if card_index is None or card_index >= len(player_hand):
        return False

    selected_card = player_hand[card_index]

    if not card_uses_movement_preview(selected_card):
        return False

    if not character_can_use_card(character, selected_card) or not can_afford_card(selected_card):
        return False

    move_range = get_card_movement_range(selected_card, character)

    if move_range <= 0:
        return False

    movement_mode = True
    movement_card = selected_card
    movement_card_user = character
    movement_preview_row = character["row"]
    movement_preview_col = character["col"]
    movement_preview_path = []
    movement_steps_left = move_range

    return True


def add_movement_preview_step(row_change, col_change):
    global movement_preview_row
    global movement_preview_col
    global movement_steps_left

    if not movement_mode or movement_card_user is None:
        return False

    if current_energy < movement_card["cost"]:
        return False

    next_row = movement_preview_row + row_change
    next_col = movement_preview_col + col_change

    if next_row < 0 or next_row >= GRID_ROWS or next_col < 0 or next_col >= GRID_COLS:
        return False

    previous_tile = None

    if len(movement_preview_path) >= 2:
        previous_tile = movement_preview_path[-2]
    elif len(movement_preview_path) == 1:
        previous_tile = (movement_card_user["row"], movement_card_user["col"])

    if previous_tile == (next_row, next_col):
        movement_preview_path.pop()
        movement_preview_row = next_row
        movement_preview_col = next_col
        movement_steps_left += 1
        return True

    if movement_steps_left <= 0:
        return False

    movement_preview_row = next_row
    movement_preview_col = next_col
    movement_preview_path.append((movement_preview_row, movement_preview_col))
    movement_steps_left -= 1

    return True


def click_movement_preview_tile(clicked_tile):
    global movement_preview_row
    global movement_preview_col
    global movement_steps_left

    if clicked_tile is None:
        return False

    clicked_row, clicked_col = clicked_tile

    if movement_preview_path and movement_preview_path[-1] == clicked_tile:
        movement_preview_path.pop()
        movement_steps_left += 1

        if movement_preview_path:
            movement_preview_row, movement_preview_col = movement_preview_path[-1]
        else:
            movement_preview_row = movement_card_user["row"]
            movement_preview_col = movement_card_user["col"]

        return True

    row_change = clicked_row - movement_preview_row
    col_change = clicked_col - movement_preview_col

    if abs(row_change) + abs(col_change) != 1:
        return False

    return add_movement_preview_step(row_change, col_change)


def get_movement_preview_tiles():
    if not movement_mode:
        return []

    preview_tiles = movement_preview_path.copy()

    if movement_steps_left <= 0:
        return preview_tiles

    for row_change, col_change in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        next_row = movement_preview_row + row_change
        next_col = movement_preview_col + col_change

        if 0 <= next_row < GRID_ROWS and 0 <= next_col < GRID_COLS:
            preview_tiles.append((next_row, next_col))

    return preview_tiles


def get_team_special_preview_tiles():
    mouse_tile = get_clicked_grid_tile(pygame.mouse.get_pos(), ENEMY_GRID_X)

    if mouse_tile is None:
        return []

    center_row, center_col = mouse_tile
    return get_crossfire_tiles(center_row, center_col)


def confirm_movement_card():
    global current_energy
    global selected_card_index
    global movement_mode
    global movement_card
    global movement_card_user
    global movement_preview_path

    if (
        not movement_mode
        or len(movement_preview_path) == 0
        or selected_card_index is None
        or not can_land_on_tile(player_grid_data, movement_preview_row, movement_preview_col, movement_card_user)
    ):
        return False

    selected_card = player_hand[selected_card_index]
    card_was_played, current_energy, card_result = play_card(
        selected_card,
        movement_card_user,
        enemies,
        current_energy
    )

    if not card_was_played:
        return False

    acting_character = movement_card_user

    handle_card_feedback(card_result, acting_character)
    handle_enemy_deaths(enemies, enemy_grid_data)
    clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

    if can_land_on_tile(player_grid_data, movement_preview_row, movement_preview_col, acting_character):
        player_grid_data[acting_character["row"]][acting_character["col"]]["unit"] = None
        acting_character["row"] = movement_preview_row
        acting_character["col"] = movement_preview_col
        player_grid_data[acting_character["row"]][acting_character["col"]]["unit"] = acting_character
        gain_block(acting_character, selected_card.get("block", 0))
        clear_shields_involving_character(party, acting_character)
        remove_broken_shields(party)

    played_card = player_hand.pop(selected_card_index)
    discard_pile.append(played_card)
    selected_card_index = None
    movement_mode = False
    movement_card = None
    movement_card_user = None
    movement_preview_path = []
    apply_card_utility_result(card_result)

    if start_shove_mode(card_result, acting_character):
        return True

    if len(enemies) == 0:
        queue_reward_after_battle()

    return True


def confirm_selected_card():
    if selected_card_index is None or selected_card_index >= len(player_hand):
        return False

    selected_card = player_hand[selected_card_index]
    selected_character = get_selected_character(party, selected_character_index)

    if not character_can_use_card(selected_character, selected_card):
        return False

    if card_uses_movement_preview(selected_card):
        return start_movement_preview(selected_card_index, selected_character)

    if card_needs_swing_choice(selected_card, selected_character) and can_afford_card(selected_card):
        start_swing_choice(selected_card_index, selected_character)
        return True

    return play_selected_non_movement_card(selected_card_index, selected_character)


def start_swing_choice(card_index, character):
    global swing_choice_mode
    global swing_choice_card_index
    global swing_choice_character
    global selected_card_index

    swing_choice_mode = True
    swing_choice_card_index = card_index
    swing_choice_character = character
    selected_card_index = card_index


def clear_swing_choice():
    global swing_choice_mode
    global swing_choice_card_index
    global swing_choice_character

    swing_choice_mode = False
    swing_choice_card_index = None
    swing_choice_character = None


def play_selected_non_movement_card(card_index, acting_character, swing_direction=None):
    global current_energy
    global selected_card_index

    if card_index is None or card_index >= len(player_hand):
        return False

    selected_card = player_hand[card_index]

    if not character_can_use_card(acting_character, selected_card):
        selected_card_index = None
        return False

    card_to_play = selected_card

    if swing_direction is not None:
        card_to_play = selected_card.copy()
        card_to_play["swing_direction"] = swing_direction

    card_was_played, current_energy, card_result = play_card(
        card_to_play,
        acting_character,
        enemies,
        current_energy
    )

    if not card_was_played:
        return False

    handle_card_feedback(card_result, acting_character)
    handle_enemy_deaths(enemies, enemy_grid_data)
    clear_dead_enemy_incoming_attacks(enemies, player_grid_data)
    apply_forced_charge_result(card_result, acting_character)
    played_card = player_hand.pop(card_index)
    discard_pile.append(played_card)
    selected_card_index = None
    apply_card_utility_result(card_result)

    if start_shove_mode(card_result, acting_character):
        return True

    if len(enemies) == 0:
        queue_reward_after_battle()

    return True


def resolve_swing_choice(swing_direction):
    if swing_direction is None:
        return

    if swing_choice_card_index is None or swing_choice_character is None:
        clear_swing_choice()
        return

    play_selected_non_movement_card(
        swing_choice_card_index,
        swing_choice_character,
        swing_direction
    )
    clear_swing_choice()


def apply_card_utility_result(card_result):
    global current_energy

    if not isinstance(card_result, dict):
        return

    if card_result.get("gain_energy", 0) > 0:
        current_energy += card_result["gain_energy"]

    draw_count = card_result.get("draw_cards", 0)
    discard_count = card_result.get("discard_cards", 0)

    if card_result.get("random_discard", False):
        for random_discard_index in range(discard_count):
            if not player_hand:
                break

            discarded_card = random.choice(player_hand)
            player_hand.remove(discarded_card)
            discard_pile.append(discarded_card)

        if draw_count > 0:
            draw_cards(draw_pile, discard_pile, player_hand, draw_count)
    elif discard_count > 0:
        start_discard_choice(
            discard_count,
            card_result.get("discard_prompt", "Discard a card"),
            draw_count
        )
    else:
        if draw_count > 0:
            draw_cards(draw_pile, discard_pile, player_hand, draw_count)


    if "trap" in card_result:
        place_trap_on_enemy_grid(card_result["trap"], enemy_grid_data)
 
    if "traps" in card_result:
        for trap in card_result["traps"]:
            place_trap_on_enemy_grid(trap, enemy_grid_data)


def apply_forced_charge_result(card_result, character):
    if not isinstance(card_result, dict) or "forced_charge" not in card_result:
        return False

    forced_charge = card_result["forced_charge"]
    distance = forced_charge.get("distance", 0)
    row_change = 0
    col_change = 1
    moved = False

    if character.get("flip_x", False):
        col_change = -1

    for step_index in range(distance):
        if not move_unit(character, player_grid_data, row_change, col_change):
            break

        moved = True

    if moved:
        clear_shields_involving_character(party, character)
        remove_broken_shields(party)

    return moved


def gain_block(character, amount):
    character["block"] = character.get("block", 0) + amount


def start_shove_mode(card_result, acting_character):
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left
    global shove_preview_path
    global shove_preview_row
    global shove_preview_col

    if not isinstance(card_result, dict) or "shove_target" not in card_result:
        return False

    shove_mode = True
    shove_target = card_result["shove_target"]
    shove_card_user = acting_character
    shove_steps_left = card_result.get("push_range", 2)
    shove_preview_path = []
    shove_preview_row = shove_target["row"]
    shove_preview_col = shove_target["col"]

    return True


def add_shove_preview_step(row_change, col_change):
    global shove_preview_row
    global shove_preview_col
    global shove_steps_left

    if not shove_mode or shove_target is None:
        return False

    next_row = shove_preview_row + row_change
    next_col = shove_preview_col + col_change

    if next_row < 0 or next_row >= GRID_ROWS or next_col < 0 or next_col >= GRID_COLS:
        return False

    previous_tile = None

    if len(shove_preview_path) >= 2:
        previous_tile = shove_preview_path[-2]
    elif len(shove_preview_path) == 1:
        previous_tile = (shove_target["row"], shove_target["col"])

    if previous_tile == (next_row, next_col):
        shove_preview_path.pop()
        shove_preview_row = next_row
        shove_preview_col = next_col
        shove_steps_left += 1
        return True

    if shove_steps_left <= 0:
        return False

    if not can_land_on_tile(enemy_grid_data, next_row, next_col, shove_target):
        return False

    shove_preview_row = next_row
    shove_preview_col = next_col
    shove_preview_path.append((shove_preview_row, shove_preview_col))
    shove_steps_left -= 1

    return True


def click_shove_preview_tile(clicked_tile):
    global shove_preview_row
    global shove_preview_col
    global shove_steps_left

    if clicked_tile is None:
        return False

    if shove_preview_path and shove_preview_path[-1] == clicked_tile:
        shove_preview_path.pop()
        shove_steps_left += 1

        if shove_preview_path:
            shove_preview_row, shove_preview_col = shove_preview_path[-1]
        else:
            shove_preview_row = shove_target["row"]
            shove_preview_col = shove_target["col"]

        return True

    row_change = clicked_tile[0] - shove_preview_row
    col_change = clicked_tile[1] - shove_preview_col

    if abs(row_change) + abs(col_change) != 1:
        return False

    return add_shove_preview_step(row_change, col_change)


def get_shove_preview_tiles():
    if not shove_mode or shove_target is None:
        return []

    preview_tiles = shove_preview_path.copy()

    if shove_steps_left <= 0:
        return preview_tiles

    for row_change, col_change in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        next_row = shove_preview_row + row_change
        next_col = shove_preview_col + col_change

        if can_land_on_tile(enemy_grid_data, next_row, next_col, shove_target):
            preview_tiles.append((next_row, next_col))

    return preview_tiles


def confirm_shove():
    global shove_animation_queue
    global shove_animation_timer

    if not shove_mode or shove_target is None or not shove_preview_path:
        return False

    shove_animation_queue = []

    last_row = shove_target["row"]
    last_col = shove_target["col"]

    for next_row, next_col in shove_preview_path:
        row_change = next_row - last_row
        col_change = next_col - last_col

        if abs(row_change) + abs(col_change) != 1:
            break

        shove_animation_queue.append({
            "enemy": shove_target,
            "row_change": row_change,
            "col_change": col_change
        })

        last_row = next_row
        last_col = next_col

    shove_animation_timer = 0
    clear_shove_preview_only()

    return True

def clear_shove_preview_only():
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left
    global shove_preview_path
    global shove_preview_row
    global shove_preview_col

    shove_mode = False
    shove_target = None
    shove_card_user = None
    shove_steps_left = 0
    shove_preview_path = []
    shove_preview_row = 0
    shove_preview_col = 0

def finish_shove(enemy_that_was_shoved=None):
    global shove_animation_queue
    global shove_animation_timer

    trap_hits = []

    if enemy_that_was_shoved is not None and enemy_that_was_shoved in enemies:
        trap_hits = trigger_enemy_traps(enemy_that_was_shoved, enemy_grid_data)

    if trap_hits:
        add_damage_popups_from_hits(trap_hits, "enemy")
        queue_enemy_death_animations(enemies, enemy_death_animations)
        handle_enemy_deaths(enemies, enemy_grid_data)
        clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

    shove_animation_queue = []
    shove_animation_timer = 0

    if len(enemies) == 0:
        queue_reward_after_battle()


def select_enemy_movement_preview(clicked_enemy):
    global selected_enemy_for_movement
    global enemy_movement_preview_tiles

    selected_enemy_for_movement = clicked_enemy

    if clicked_enemy is None:
        enemy_movement_preview_tiles = []
    else:
        enemy_movement_preview_tiles = get_enemy_possible_movement_tiles(
            clicked_enemy,
            enemy_grid_data,
            party
        )


def queue_reward_after_battle():
    global current_state
    global pending_reward_after_deaths
    global reward_mode
    global deck_scroll_y
    global target_deck_scroll_y
    global enemy_grid_data
    global movement_mode
    global movement_card
    global movement_card_user
    global movement_preview_path
    global enemy_movement_queue
    global reaction_mode
    global reaction_enemy
    global reaction_options
    global map_layers
    global current_map_layer

    # Winning a battle clears warnings and opens rewards after any death animation finishes.
    clear_incoming_attacks(player_grid_data)
    enemy_grid_data = create_grid_data("enemy")
    movement_mode = False
    movement_card = None
    movement_card_user = None
    movement_preview_path = []
    enemy_movement_queue = []
    reaction_mode = False
    reaction_enemy = None
    reaction_options = []
    reward_mode = "choose_reward"
    deck_scroll_y = 0
    target_deck_scroll_y = 0

    if len(map_layers) == 0:
        # The tutorial battle is fixed; the run map begins after it.
        map_layers = generate_map()
        current_map_layer = 0

    if enemy_death_animations:
        pending_reward_after_deaths = True
    else:
        current_state = REWARD


def finish_enemy_actions():
    next_state, next_turn = finish_enemy_turn(party, player_grid_data, enemies)

    if next_state is not None:
        return next_state, current_turn, current_energy

    next_current_turn = current_turn
    next_current_energy = current_energy

    if next_turn is not None:
        next_current_turn = next_turn
        next_current_energy = max_energy
        clear_party_shields(party)
        for character in party:
            character["block"] = 0
        discard_pile.extend(player_hand)
        player_hand.clear()
        draw_cards(draw_pile, discard_pile, player_hand, 5)
        discard_random_cards_for_status()
        tick_enemy_turn_statuses(party)
        tick_traps(enemy_grid_data)
        fire_hits = process_enemy_end_of_turn_fire(enemies, enemy_grid_data)

        if fire_hits:
            add_damage_popups_from_hits(fire_hits, "enemy")
            queue_enemy_death_animations(enemies, enemy_death_animations)
            handle_enemy_deaths(enemies, enemy_grid_data)
            clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

    return None, next_current_turn, next_current_energy


def reset_battle_animation_state():
    global player_attack_animation
    global pending_reward_after_deaths
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left
    global shove_preview_path
    global shove_preview_row
    global shove_preview_col
    global shove_animation_queue
    global shove_animation_timer
    global selected_enemy_for_movement
    global enemy_movement_preview_tiles
    global discard_choice_mode
    global pending_chosen_discards
    global pending_draw_after_discard
    global discard_choice_prompt
    global discard_animation
    global swing_choice_mode
    global swing_choice_card_index
    global swing_choice_character

    enemy_death_animations.clear()
    projectile_animations.clear()
    player_attack_animation = None
    pending_reward_after_deaths = False
    shove_mode = False
    shove_target = None
    shove_card_user = None
    shove_steps_left = 0
    shove_preview_path = []
    shove_preview_row = 0
    shove_preview_col = 0
    shove_animation_queue = []
    shove_animation_timer = 0
    selected_enemy_for_movement = None
    enemy_movement_preview_tiles = []
    discard_choice_mode = False
    pending_chosen_discards = 0
    pending_draw_after_discard = 0
    discard_choice_prompt = ""
    discard_animation = None
    swing_choice_mode = False
    swing_choice_card_index = None
    swing_choice_character = None


def reset_battle_input_state():
    global selected_card_index
    global movement_mode
    global movement_card
    global movement_card_user
    global movement_preview_path
    global enemy_movement_queue
    global reaction_mode
    global reaction_enemy
    global reaction_options
    global team_special_aim_mode

    selected_card_index = None
    movement_mode = False
    movement_card = None
    movement_card_user = None
    movement_preview_path = []
    enemy_movement_queue = []
    reaction_mode = False
    reaction_enemy = None
    reaction_options = []
    team_special_aim_mode = False


def resolve_team_special(center_tile):
    global team_special_charge
    global team_special_aim_mode

    if center_tile is None or not team_special_is_ready(team_special_charge):
        return False

    center_row, center_col = center_tile
    card_result = play_crossfire_cleave(enemies, center_row, center_col)
    hits = card_result.get("hits", [])

    if hits:
        add_damage_popups_from_hits(hits, "enemy")
        queue_enemy_death_animations(enemies, enemy_death_animations)
        handle_enemy_deaths(enemies, enemy_grid_data)
        clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

    team_special_charge = 0
    team_special_aim_mode = False

    if len(enemies) == 0:
        queue_reward_after_battle()

    return True


def start_selected_party_tutorial_battle():
    global party
    global selected_character_index
    global selected_character
    global player_grid_data
    global enemy_grid_data
    global player_deck
    global draw_pile
    global player_hand
    global discard_pile
    global current_energy
    global current_state
    global battle_number
    global team_special_charge

    party = make_party()
    selected_character_index = 0
    selected_character = get_selected_character(party, selected_character_index)

    player_grid_data = create_grid_data("player")
    enemy_grid_data = create_grid_data("enemy")
    enemies.clear()
    place_party_on_grid(party, player_grid_data, True)

    player_deck = build_starting_deck(party)
    draw_pile = shuffle_deck(player_deck)
    player_hand = []
    discard_pile = []
    draw_cards(draw_pile, discard_pile, player_hand, 5)

    reset_battle_input_state()
    reset_battle_animation_state()

    current_energy = max_energy
    current_state = BATTLE
    battle_number = 1
    team_special_charge = 0

    start_tutorial_battle(enemies, enemy_grid_data)
    apply_enemy_assets(enemies, enemy_assets)
    prepare_enemy_attacks(enemies, player_grid_data)


def discard_random_cards_for_status():
    for character in party:
        discards_to_make = character.get("random_discard_next_turn", 0)

        for discard_index in range(discards_to_make):
            if not player_hand:
                break

            discarded_card = random.choice(player_hand)
            player_hand.remove(discarded_card)
            discard_pile.append(discarded_card)

        character["random_discard_next_turn"] = 0


# Animation state.
# Timers count game frames; frame indexes choose which sprite image to draw.
battle_animation_runtime = make_battle_animation_runtime()
enemy_idle_frame_index = battle_animation_runtime["enemy_idle_frame_index"]
enemy_animation_timer = battle_animation_runtime["enemy_animation_timer"]
enemy_animation_speed = battle_animation_runtime["enemy_animation_speed"]
enemy_attack_frame_index = battle_animation_runtime["enemy_attack_frame_index"]
enemy_attack_timer = battle_animation_runtime["enemy_attack_timer"]
enemy_attack_speed = battle_animation_runtime["enemy_attack_speed"]
enemy_is_attacking = battle_animation_runtime["enemy_is_attacking"]
attacking_enemy_index = battle_animation_runtime["attacking_enemy_index"]
player_idle_frame_index = battle_animation_runtime["player_idle_frame_index"]
player_animation_timer = battle_animation_runtime["player_animation_timer"]
player_animation_speed = battle_animation_runtime["player_animation_speed"]


current_state = HOME_MENU


running = True
while running:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            if current_state == MAP:
                scroll_map(-event.y * 60)
            if current_state == REWARD and reward_mode == "choose_sleeve_card":

                target_deck_scroll_y -= event.y * 60

                max_scroll = max(0, ((len(player_deck) + 3) // 4) * 260 - 420)

                if target_deck_scroll_y < 0:
                    target_deck_scroll_y = 0

                if target_deck_scroll_y > max_scroll:
                    target_deck_scroll_y = max_scroll

            if current_state == BATTLE and pile_view_title is not None:
                target_pile_scroll_y -= event.y * 60
                max_scroll = get_pile_max_scroll(pile_view_cards)

                if target_pile_scroll_y < 0:
                    target_pile_scroll_y = 0

                if target_pile_scroll_y > max_scroll:
                    target_pile_scroll_y = max_scroll
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_7 and (event.mod & pygame.KMOD_ALT):
                toggle_dev_menu()
                continue

            if dev_menu_is_open():
                continue

            if current_state == BATTLE and reaction_mode:
                if event.key == pygame.K_g:
                    reaction_mode = False
                    reaction_enemy = None
                    reaction_options = []
                    selected_card_index = None

                continue

            if current_state == BATTLE and pending_reward_after_deaths:
                continue

            if current_state == BATTLE and current_turn == PLAYER_TURN:
                selected_character = get_selected_character(party, selected_character_index)

                if discard_choice_mode:
                    continue

                if event.key == pygame.K_g:
                    # G cancels card/user selection and exits movement preview.
                    pile_view_title = None
                    pile_view_cards = []
                    pile_scroll_y = 0
                    target_pile_scroll_y = 0
                    selected_card_index = None
                    movement_mode = False
                    movement_card = None
                    movement_card_user = None
                    movement_preview_path = []
                    shove_mode = False
                    shove_target = None
                    shove_card_user = None
                    shove_steps_left = 0
                    shove_preview_path = []
                    shove_preview_row = 0
                    shove_preview_col = 0
                    clear_swing_choice()
                    clear_party_shields(party)

                elif swing_choice_mode:
                    continue

                elif event.key == pygame.K_r and selected_character is not None:
                    selected_character["flip_x"] = not selected_character.get("flip_x", False)

                elif shove_mode:
                    row_change, col_change = get_keyboard_direction(event.key)

                    if row_change != 0 or col_change != 0:
                        add_shove_preview_step(row_change, col_change)

                    if event.key == pygame.K_e:
                        confirm_shove()

                elif movement_mode and selected_card_index is not None:
                    # WASD builds a planned movement path while in card movement mode.
                    row_change, col_change = get_keyboard_direction(event.key)

                    if row_change != 0 or col_change != 0:
                        add_movement_preview_step(row_change, col_change)

                    if event.key == pygame.K_e:
                        confirm_movement_card()

                else:
                    row_change, col_change = get_keyboard_direction(event.key)

                    if (row_change != 0 or col_change != 0) and selected_character.get("snared", 0) == 0:
                        if move_unit(selected_character, player_grid_data, row_change, col_change):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)

                        continue

                    debug_row_change, debug_col_change = get_keyboard_direction(event.key, True)

                    if (
                        event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
                        and selected_character.get("snared", 0) == 0
                    ):
                        if move_unit(selected_character, player_grid_data, debug_row_change, debug_col_change):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)

                        continue

                    if event.key == pygame.K_e and selected_card_index is not None:
                        confirm_selected_card()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if dev_menu_is_open():
                continue

            if current_state == BATTLE and current_turn == PLAYER_TURN:
                if discard_choice_mode or reaction_mode or pending_reward_after_deaths:
                    continue

                if team_special_aim_mode:
                    team_special_aim_mode = False
                    continue

                if shove_mode:
                    confirm_shove()
                    continue

                if movement_mode:
                    confirm_movement_card()
                    continue

                if selected_card_index is not None and not swing_choice_mode:
                    confirm_selected_card()
                    continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if dev_menu_is_open():
                for button in dev_buttons:
                    if button.clicked(event.pos):
                        action = button.action

                        if action == "kill_first":
                            instant_kill_first_enemy(enemies)
                            handle_enemy_deaths(enemies, enemy_grid_data)

                        elif action == "kill_all":
                            instant_kill_all_enemies(enemies)
                            handle_enemy_deaths(enemies, enemy_grid_data)

                        elif action == "prev_card":
                            selected_dev_card_index -= 1

                        elif action == "next_card":
                            selected_dev_card_index += 1

                        elif action == "add_hand":
                            custom_cards = get_custom_card_ids()
                            if custom_cards:
                                card_id = custom_cards[selected_dev_card_index % len(custom_cards)]
                                add_card_to_hand(card_id, player_hand, CARD_LIBRARY)

                        elif action == "add_deck":
                            custom_cards = get_custom_card_ids()
                            if custom_cards:
                                card_id = custom_cards[selected_dev_card_index % len(custom_cards)]
                                add_card_to_deck(card_id, player_deck, CARD_LIBRARY)

                        elif action == "prev_battle":
                            selected_battle_index -= 1

                        elif action == "next_battle":
                            selected_battle_index += 1

                        elif action == "load_battle":
                            print("Battle loading button pressed. Hook this to your JSON battle loader.")

                continue

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            continue

        if current_state == HOME_MENU:
            # Home menu only chooses between leaving or character select.

            if start_button.is_clicked(event.pos):
                current_state = CHARACTER_SELECT

            if card_editor_button.is_clicked(event.pos):
                subprocess.Popen([sys.executable, "cards/custom_card_editor.py"])

            if quit_button.is_clicked(event.pos):
                running = False

        if current_state == CHARACTER_SELECT:
            selected_party = character_select_state["selected_party"]

            if archer_button.is_clicked(event.pos):
                add_character_to_selection(selected_party, "Archer")
                continue

            if warrior_button.is_clicked(event.pos):
                add_character_to_selection(selected_party, "Warrior")
                continue

            if len(selected_party) >= 2 and character_start_button.is_clicked(event.pos):
                start_selected_party_tutorial_battle()
                continue

        if current_state == BATTLE:
            # Battle clicks either select cards, confirm movement, play cards, or end turn.
            if pending_reward_after_deaths:
                continue

            if team_special_aim_mode:
                clicked_enemy_tile = get_clicked_grid_tile(event.pos, ENEMY_GRID_X)
                resolve_team_special(clicked_enemy_tile)
                continue

            if discard_choice_mode:
                clicked_card_index = get_clicked_card_index(player_hand, event.pos)
                choose_discard_card(clicked_card_index)
                continue

            if swing_choice_mode:
                resolve_swing_choice(get_clicked_swing_direction(event.pos))
                continue

            if shove_mode:
                if play_card_button.is_clicked(event.pos):
                    confirm_shove()
                    continue

                clicked_enemy_tile = get_clicked_grid_tile(event.pos, ENEMY_GRID_X)
                click_shove_preview_tile(clicked_enemy_tile)
                continue

            if reaction_mode:
                clicked_card_index = get_clicked_card_index(player_hand, event.pos)
                reaction_option = get_reaction_option_for_card(reaction_options, clicked_card_index)

                if reaction_option is not None:
                    selected_card = player_hand[clicked_card_index]
                    reaction_character = reaction_option["character"]
                    card_was_played, current_energy, card_result = play_reaction_card(
                        selected_card,
                        reaction_character,
                        enemies,
                        current_energy
                    )

                    if card_was_played:
                        handle_card_feedback(card_result, reaction_character)
                        handle_enemy_deaths(enemies, enemy_grid_data)
                        clear_dead_enemy_incoming_attacks(enemies, player_grid_data)
                        played_card = player_hand.pop(clicked_card_index)
                        discard_pile.append(played_card)
                        selected_card_index = None

                        if reaction_enemy not in enemies:
                            enemy_movement_queue = [
                                movement_step for movement_step in enemy_movement_queue
                                if movement_step["enemy"] is not reaction_enemy
                            ]

                        reaction_mode = False
                        reaction_enemy = None
                        reaction_options = []

                        if len(enemies) == 0:
                            queue_reward_after_battle()

                continue

            if pile_view_title is not None:
                if get_pile_view_close_clicked(event.pos):
                    pile_view_title = None
                    pile_view_cards = []
                    pile_scroll_y = 0
                    target_pile_scroll_y = 0

                continue

            clicked_pile_button = get_clicked_pile_button(event.pos)

            if clicked_pile_button == "draw":
                pile_view_title = "Deck"
                pile_view_cards = shuffle_deck(draw_pile)
                pile_scroll_y = 0
                target_pile_scroll_y = 0
                selected_card_index = None
                continue

            if clicked_pile_button == "discard":
                pile_view_title = "Discard"
                pile_view_cards = discard_pile.copy()
                pile_scroll_y = 0
                target_pile_scroll_y = 0
                selected_card_index = None
                continue

            if (
                team_special_button.is_clicked(event.pos)
                and current_turn == PLAYER_TURN
                and team_special_is_ready(team_special_charge)
                and not movement_mode
                and not shove_mode
            ):
                team_special_aim_mode = True
                selected_card_index = None
                select_enemy_movement_preview(None)
                continue

            selected_character = get_selected_character(party, selected_character_index)
            shield_button_rect = get_shield_button_rect(party, selected_character)
            clicked_enemy = get_clicked_enemy(enemies, event.pos)

            if movement_mode:
                if play_card_button.is_clicked(event.pos):
                    confirm_movement_card()
                    continue

                clicked_player_tile = get_clicked_grid_tile(event.pos, PLAYER_GRID_X)
                click_movement_preview_tile(clicked_player_tile)
                continue

            if clicked_enemy is not None:
                select_enemy_movement_preview(clicked_enemy)
                selected_card_index = None
                movement_mode = False
                movement_card = None
                movement_card_user = None
                movement_preview_path = []
                continue
            elif event.pos[0] >= ENEMY_GRID_X and event.pos[1] >= GRID_Y:
                select_enemy_movement_preview(None)

            if (
                shield_button_rect is not None
                and shield_button_rect.collidepoint(event.pos)
                and current_turn == PLAYER_TURN
                and not movement_mode
            ):
                shield_target = get_shield_target(party, selected_character)
                already_shielding = selected_character.get("shielding") is shield_target
                clear_party_shields(party)

                if not already_shielding:
                    selected_character["shielding"] = shield_target

                selected_card_index = None
                continue

            clicked_card_index = get_clicked_card_index(player_hand, event.pos)
            clicked_character_index = get_clicked_character_index(party, event.pos)

            if clicked_character_index is not None and not movement_mode:
                if selected_card_index is not None and current_turn == PLAYER_TURN:
                    selected_card = player_hand[selected_card_index]

                    if not character_can_use_card(party[clicked_character_index], selected_card):
                        selected_card_index = None
                        movement_mode = False
                        movement_card = None
                        movement_card_user = None
                        movement_preview_path = []
                        clear_swing_choice()

                selected_character_index = clicked_character_index
                selected_character = get_selected_character(party, selected_character_index)

                if selected_card_index is not None and current_turn == PLAYER_TURN:
                    selected_card = player_hand[selected_card_index]

                    if card_uses_movement_preview(selected_card) and current_energy >= selected_card["cost"]:
                        # Movement preview starts after choosing who will move, but costs nothing yet.
                        start_movement_preview(selected_card_index, selected_character)

            if clicked_card_index is not None and current_turn == PLAYER_TURN and not movement_mode:
                selected_card_index = clicked_card_index
                selected_card = player_hand[selected_card_index]

                if not character_can_use_card(selected_character, selected_card):
                    usable_character_index = get_first_usable_character_index(party, selected_card)

                    if usable_character_index is None:
                        selected_card_index = None
                    else:
                        selected_character_index = usable_character_index
                        selected_character = get_selected_character(party, selected_character_index)

            if (
                play_card_button.is_clicked(event.pos)
                and movement_mode
            ):
                confirm_movement_card()

            if play_card_button.is_clicked(event.pos) and selected_card_index is not None and current_turn == PLAYER_TURN and not movement_mode:
                confirm_selected_card()


            if end_turn_button.is_clicked(event.pos) and current_turn == PLAYER_TURN and not movement_mode and not shove_mode:
                # Keep the hand through enemy movement so attack cards can react.
                tick_party_statuses(party)
                current_turn = ENEMY_TURN
                enemy_is_attacking = True
                attacking_enemy_index = get_next_attacking_enemy_index(enemies, -1)
                selected_card_index = None
                enemy_attack_frame_index = 0
                enemy_attack_timer = 0
                reaction_mode = False
                reaction_enemy = None
                reaction_options = []

                if attacking_enemy_index is None:
                    enemy_is_attacking = False
                    enemy_movement_queue = build_enemy_movement_queue(enemies, enemy_grid_data, party)
                    enemy_movement_timer = 0
        if current_state == MAP:
            clicked_node = get_clicked_map_node(map_layers, event.pos)

            if clicked_node is not None:
                complete_map_node(map_layers, clicked_node)
                current_map_layer = clicked_node["layer"]

                if clicked_node["type"] == "battle" or clicked_node["type"] == "boss":
                    # Starting a map battle rebuilds grids and reshuffles the whole deck.
                    player_grid_data = create_grid_data("player")
                    enemy_grid_data = create_grid_data("enemy")
                    enemies.clear()

                    place_party_on_grid(party, player_grid_data)
                    selected_character = get_selected_character(party, selected_character_index)

                    battle_number += 1
                    last_battle_room = start_map_battle(enemies, enemy_grid_data, last_battle_room)
                    apply_enemy_assets(enemies, enemy_assets)
                    prepare_enemy_attacks(enemies, player_grid_data)

                    reset_battle_input_state()
                    reset_battle_animation_state()
                    player_hand.clear()
                    discard_pile.clear()
                    draw_pile = shuffle_deck(player_deck)
                    discard_pile.clear()

                    draw_cards(draw_pile, discard_pile, player_hand, 5)

                    current_turn = PLAYER_TURN
                    current_energy = max_energy
                    current_state = BATTLE

                if clicked_node["type"] == "rest":
                    # Rest is a placeholder reward node: heal a little, then stay on map.
                    for character in party:
                        character["current_hp"] += 2

                        if character["current_hp"] > character["max_hp"]:
                            character["current_hp"] = character["max_hp"]

                if clicked_node["type"] == "shop":
                    print("Shop clicked")

                if clicked_node["type"] == "upgrade":
                    print("Upgrade clicked")

                if clicked_node["type"] == "event":
                    print("Event clicked")
        if current_state == REWARD:
            # Reward popup first chooses a reward type, then may ask for a deck card.
            if reward_mode == "choose_reward":
                reward_choice = get_reward_choice_click(event.pos)

                if reward_choice == "new_card":
                    card_reward_choices = generate_card_rewards(party, 3)
                    reward_mode = "choose_new_card"


                if reward_choice == "sleeve":
                    # Premium Sleeve modifies one valid card already in the deck.
                    selected_sleeve = CARD_SLEEVES["premium_sleeve"]
                    reward_mode = "choose_sleeve_card"
                    deck_scroll_y = 0
                    target_deck_scroll_y = 0

            elif reward_mode == "choose_new_card":
                clicked_card = get_clicked_card_reward(card_reward_choices, event.pos)

                if clicked_card is not None:
                    player_deck.append(clicked_card.copy())
                    card_reward_choices = []
                    current_state = MAP

            elif reward_mode == "choose_sleeve_card":
                clicked_card = get_clicked_reward_deck_card(player_deck, deck_scroll_y, event.pos)

                if clicked_card is not None and apply_sleeve(selected_sleeve, clicked_card):
                    current_state = MAP





        if current_state == GAME_OVER:
            if play_again_button.is_clicked(event.pos):
                # Reset board state, then return to character select for a fresh run.
                party = []
                selected_character = None
                selected_character_index = 0
                player_grid_data = create_grid_data("player")
                enemy_grid_data = create_grid_data("enemy")
                enemies.clear()

                selected_card_index = None
                reset_battle_input_state()
                team_special_charge = 0
                character_select_state["selected_party"].clear()
                map_layers = []
                reset_battle_animation_state()

                current_turn = PLAYER_TURN
                current_state = CHARACTER_SELECT
                battle_number = 0
                last_battle_room = None

            if game_over_quit_button.is_clicked(event.pos):
                running = False

    deck_scroll_y += (target_deck_scroll_y - deck_scroll_y) * 0.2
    pile_scroll_y += (target_pile_scroll_y - pile_scroll_y) * 0.2
    update_damage_popups(damage_popups)
    update_discard_animation()
    update_enemy_death_animations(enemy_death_animations)
    update_projectile_animations(projectile_animations)
    update_party_death_animations(party)
    player_attack_animation = update_player_attack_animation(player_attack_animation)
    if shove_animation_queue:
        shove_animation_timer += 1

    if shove_animation_timer >= shove_animation_speed:
        shove_animation_timer = 0
        shove_step = shove_animation_queue.pop(0)
        shoved_enemy = shove_step["enemy"]

        if shoved_enemy in enemies:
            moved = move_unit(
                shoved_enemy,
                enemy_grid_data,
                shove_step["row_change"],
                shove_step["col_change"]
            )

            if not moved:
                shove_animation_queue = []

            if not shove_animation_queue:
                finish_shove(shoved_enemy)
        else:
            shove_animation_queue = []
            shove_animation_timer = 0
    if pending_reward_after_deaths and not enemy_death_animations:
        pending_reward_after_deaths = False
        current_state = REWARD

    screen.fill(DARK_BG)

    if current_state == HOME_MENU:
        draw_home_menu(screen, font, start_button, quit_button, card_editor_button)

    if current_state == CHARACTER_SELECT:
        draw_character_select_screen(
            screen,
            font,
            parchment_font,
            archer_button,
            warrior_button,
            character_start_button,
            character_select_assets,
            character_select_state["selected_party"],
            pygame.mouse.get_pos()
        )
    if current_state == MAP:
        draw_map_screen(screen, font, map_layers)

    if current_state == BATTLE or current_state == GAME_OVER:
        # Keep idle animations moving while battle or game-over overlay is visible.
        max_character_idle_frames = max(len(character["idle_frames"]) for character in party)
        player_animation_timer, player_idle_frame_index = update_animation_frame(
            player_animation_timer,
            player_idle_frame_index,
            player_animation_speed,
            max_character_idle_frames
        )

        max_enemy_idle_frames = 1
        if enemies:
            max_enemy_idle_frames = max(len(enemy["idle_frames"]) for enemy in enemies)

        enemy_animation_timer, enemy_idle_frame_index = update_animation_frame(
            enemy_animation_timer,
            enemy_idle_frame_index,
            enemy_animation_speed,
            max_enemy_idle_frames
        )

        if current_turn == ENEMY_TURN and enemy_is_attacking:
            # Enemy damage resolves after the attack animation finishes.
            enemy_attack_timer += 1

            if enemy_attack_timer >= enemy_attack_speed:
                enemy_attack_timer = 0
                enemy_attack_frame_index += 1

                attack_frames = enemies[attacking_enemy_index]["attack_frames"]

                if enemy_attack_frame_index >= len(attack_frames):
                    attacking_enemy = enemies[attacking_enemy_index]
                    enemy_hits = resolve_enemy_incoming_attacks(attacking_enemy, party, player_grid_data)
                    add_damage_popups_from_hits(enemy_hits, "player")
                    start_player_death_animations_from_hits(enemy_hits)
                    clear_enemy_incoming_attacks(attacking_enemy, player_grid_data)

                    if all(character["current_hp"] <= 0 for character in party):
                        current_state = GAME_OVER
                        enemy_is_attacking = False
                        attacking_enemy_index = None
                    else:
                        attacking_enemy_index = get_next_attacking_enemy_index(enemies, attacking_enemy_index)
                        enemy_attack_frame_index = 0

                        if attacking_enemy_index is None:
                            enemy_is_attacking = False
                            enemy_movement_queue = build_enemy_movement_queue(enemies, enemy_grid_data, party)
                            enemy_movement_timer = 0

        if current_turn == ENEMY_TURN and not enemy_is_attacking and current_state == BATTLE:
            if reaction_mode:
                pass
            elif enemy_movement_queue:
                enemy_movement_timer += 1

                if enemy_movement_timer >= enemy_movement_speed:
                    enemy_movement_timer = 0
                    movement_step = enemy_movement_queue.pop(0)
                    moving_enemy = movement_step["enemy"]

                    if moving_enemy in enemies:
                        enemy_moved = move_unit(
                            moving_enemy,
                            enemy_grid_data,
                            movement_step["row_change"],
                            movement_step["col_change"]
                        )

                        if enemy_moved and selected_enemy_for_movement is moving_enemy:
                            select_enemy_movement_preview(moving_enemy)

                        if not enemy_moved:
                            enemy_movement_queue = [
                                queued_step for queued_step in enemy_movement_queue
                                if queued_step["enemy"] is not moving_enemy
                            ]

                        if enemy_moved:
                            trap_hits = trigger_enemy_traps(moving_enemy, enemy_grid_data)

                            if trap_hits:
                                add_damage_popups_from_hits(trap_hits, "enemy")
                                queue_enemy_death_animations(enemies, enemy_death_animations)
                                handle_enemy_deaths(enemies, enemy_grid_data)
                                if selected_enemy_for_movement not in enemies:
                                    select_enemy_movement_preview(None)
                                elif selected_enemy_for_movement is not None:
                                    select_enemy_movement_preview(selected_enemy_for_movement)
                                clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

                                if moving_enemy not in enemies:
                                    enemy_movement_queue = [
                                        queued_step for queued_step in enemy_movement_queue
                                        if queued_step["enemy"] is not moving_enemy
                                    ]

                                    if len(enemies) == 0:
                                        queue_reward_after_battle()

                                    continue

                            reaction_options = get_reaction_options(
                                player_hand,
                                party,
                                moving_enemy,
                                current_energy
                            )

                            if reaction_options:
                                reaction_mode = True
                                reaction_enemy = moving_enemy
                                selected_card_index = None
            else:
                next_state, next_turn, next_energy = finish_enemy_actions()

                if next_state is not None:
                    current_state = next_state

                current_turn = next_turn
                current_energy = next_energy

    if current_state == BATTLE or current_state == GAME_OVER:
        # Draw the battle underneath game-over so the loss still has context.
        screen.blit(battle_background, (0, 0))

        selected_card = None

        if selected_card_index is not None and selected_card_index < len(player_hand):
            selected_card = player_hand[selected_card_index]
        else:
            # If the selected card was removed, clear the old hand index.
            selected_card_index = None

        selected_character = get_selected_character(party, selected_character_index)
        swing_preview_direction = "right"
        if swing_choice_mode:
            swing_preview_direction = "right"

        attack_preview_direction = None

        enemy_preview_tiles = get_card_preview_tiles(
            selected_card,
            selected_character,
            swing_preview_direction,
            attack_preview_direction
        )

        player_preview_tiles = []
        if movement_mode:
            # Movement previews happen on the player grid, attack previews on enemy grid.
            player_preview_tiles = get_movement_preview_tiles()

        if shove_mode:
            enemy_preview_tiles = get_shove_preview_tiles()

        if team_special_aim_mode:
            enemy_preview_tiles = get_team_special_preview_tiles()

        draw_battle(
            screen,
            font,
            end_turn_button,
            play_card_button,
            team_special_button,
            team_special_charge,
            TEAM_SPECIAL_MAX_CHARGE,
            party,
            selected_character,
            current_energy,
            max_energy,
            player_grid_data,
            enemy_grid_data,
            enemies,
            player_idle_frame_index,
            enemy_idle_frame_index,
            enemy_attack_frame_index,
            enemy_is_attacking,
            attacking_enemy_index,
            player_attack_animation,
            enemy_assets["counter"],
            player_preview_tiles,
            enemy_preview_tiles,
            enemy_movement_preview_tiles
        )

        draw_enemy_death_animations(screen, enemy_death_animations)
        draw_projectile_animations(screen, projectile_animations)
        draw_damage_popups(screen, damage_popups)

        mouse_pos = pygame.mouse.get_pos()
        draw_enemy_hover_tooltip(screen, small_font, enemies, mouse_pos)
        reaction_card_indices = []

        if reaction_mode:
            draw_reaction_warning_edges(screen)
            reaction_card_indices = [
                reaction_option["card_index"] for reaction_option in reaction_options
            ]

        if swing_choice_mode:
            draw_swing_choice_popup(screen, font, small_font)

        if discard_choice_mode:
            draw_discard_choice_overlay(
                screen,
                font,
                small_font,
                discard_choice_prompt,
                pending_chosen_discards
            )

        hand_mouse_pos = mouse_pos
        if discard_choice_mode:
            hand_mouse_pos = (-999, -999)

        draw_card_hand(
            screen,
            player_hand,
            hand_mouse_pos,
            selected_card_index,
            selected_character,
            small_font,
            reaction_card_indices
        )

        draw_discard_animation(screen, selected_character, discard_animation)

        if not discard_choice_mode:
            draw_pile_buttons(screen, small_font, len(draw_pile), len(discard_pile))

        if movement_mode:
            confirm_text = font.render("Click path tiles. Right-click, E, or Play Card confirms.", True, WHITE)

            screen.blit(confirm_text, (360, 720))

        if shove_mode:
            shove_text = font.render("Click shove path. Right-click, E, or Play Card confirms.", True, WHITE)
            screen.blit(shove_text, (360, 720))

        if reaction_mode:
            reaction_text = font.render("Reaction! Click a red card or press G", True, WHITE)
            screen.blit(reaction_text, (310, 720))

        if team_special_aim_mode:
            special_text = font.render("Team Special: click an enemy tile to aim the cross.", True, WHITE)
            screen.blit(special_text, (250, 720))

        if current_state == GAME_OVER:
            draw_game_over_menu(screen, font, play_again_button, game_over_quit_button)

        if pile_view_title is not None:
            draw_pile_viewer(screen, font, small_font, pile_view_title, pile_view_cards, pile_scroll_y)

    if current_state == REWARD:
        draw_reward_screen(
            screen,
            font,
            small_font,
            reward_mode,
            card_reward_choices,
            player_deck,
            deck_scroll_y,
            selected_sleeve,
            can_apply_sleeve)
    if dev_menu_is_open():
        dev_buttons = draw_dev_menu(
            screen,
            enemies,
            player_hand,
            player_deck,
            CARD_LIBRARY,
            selected_dev_card_index,
            selected_battle_index
        )


    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
