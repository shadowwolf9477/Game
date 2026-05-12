import pygame
import random

from button import Button
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
    GRID_Y
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
    tick_traps
)
from maps.map_loader import generate_map
from screens.map_screen import draw_map_screen, get_clicked_map_node, complete_map_node
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

from battle_grid import create_grid_data
from loaders.battle_assets import load_battle_assets
from loaders.sound_assets import load_battle_sounds, play_character_attack_sound
from movement import move_unit, can_land_on_tile
from menus.game_over_menu import draw_game_over_menu
from battle_renderer import draw_battle, draw_reaction_warning_edges
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

from cards.card_renderer import draw_card_hand, get_clicked_card_index
from cards.card_effects import play_card, play_reaction_card, get_reaction_cost
from cards.card_targeting import get_card_preview_tiles
from cards.player_deck import build_starting_deck, shuffle_deck, draw_cards


# Pygame setup.
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)
# Smaller text keeps reward-card labels inside their temporary boxes.
small_font = pygame.font.Font(None, 34)
battle_sounds = load_battle_sounds()



# Shared menu and battle buttons.
# These are created once and reused while the game changes screen states.
start_button = Button(500, 220, 220, 70, "Start")
quit_button = Button(500, 310, 220, 70, "Quit")

archer_button = Button(450, 330, 330, 70, "Archer + Warrior")

end_turn_button = Button(870, 60, 220, 70, "End turn")
play_card_button = Button(870, 140, 220, 70, "Play Card")

play_again_button = Button(410, 390, 220, 70, "Play Again")
game_over_quit_button = Button(650, 390, 160, 70, "Quit")


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

# Enemy reaction state.
# Enemies move one board tile at a time, which can open reaction windows.
enemy_movement_queue = []
enemy_movement_timer = 0
enemy_movement_speed = 20
reaction_mode = False
reaction_enemy = None
reaction_options = []
damage_popups = []
enemy_death_animations = []
projectile_animations = []
player_attack_animation = None
pending_reward_after_deaths = False


# Battle assets.
# These frame lists are reused every frame instead of reloading images.
battle_background, enemy_assets = load_battle_assets()


def apply_enemy_assets(enemies, enemy_assets):
    for enemy in enemies:
        assets = enemy_assets[enemy["type"]]
        enemy["idle_frames"] = assets["idle_frames"]
        enemy["attack_frames"] = assets["attack_frames"]
        enemy["idle_frames_flipped"] = assets["idle_frames_flipped"]
        enemy["attack_frames_flipped"] = assets["attack_frames_flipped"]
        enemy["death_frames"] = assets["death_frames"]
        enemy["death_frames_flipped"] = assets["death_frames_flipped"]


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

    if not isinstance(card_result, dict):
        return

    player_attack_animation = make_player_attack_animation(acting_character)
    hits = card_result.get("hits", [])

    if not hits:
        return

    arrow_projectile = make_arrow_projectile(acting_character, hits, enemy_assets["arrow"])

    if arrow_projectile is not None:
        projectile_animations.append(arrow_projectile)

    add_damage_popups_from_hits(hits, "enemy")
    queue_enemy_death_animations(enemies, enemy_death_animations)
    play_character_attack_sound(battle_sounds, acting_character)


def apply_card_utility_result(card_result):
    global current_energy

    if not isinstance(card_result, dict):
        return

    if card_result.get("gain_energy", 0) > 0:
        current_energy = min(max_energy, current_energy + card_result["gain_energy"])

    if card_result.get("draw_cards", 0) > 0:
        draw_cards(draw_pile, discard_pile, player_hand, card_result["draw_cards"])

    for discard_count in range(card_result.get("discard_cards", 0)):
        if not player_hand:
            break

        discarded_card = random.choice(player_hand)
        player_hand.remove(discarded_card)
        discard_pile.append(discarded_card)

    if "trap" in card_result:
        place_trap_on_enemy_grid(card_result["trap"], enemy_grid_data)


def gain_block(character, amount):
    character["block"] = character.get("block", 0) + amount


def start_shove_mode(card_result, acting_character):
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left

    if not isinstance(card_result, dict) or "shove_target" not in card_result:
        return False

    shove_mode = True
    shove_target = card_result["shove_target"]
    shove_card_user = acting_character
    shove_steps_left = card_result.get("push_range", 2)

    return True


def finish_shove():
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left

    trap_hits = []

    if shove_target in enemies:
        trap_hits = trigger_enemy_traps(shove_target, enemy_grid_data)

    if trap_hits:
        add_damage_popups_from_hits(trap_hits, "enemy")
        queue_enemy_death_animations(enemies, enemy_death_animations)
        handle_enemy_deaths(enemies, enemy_grid_data)
        clear_dead_enemy_incoming_attacks(enemies, player_grid_data)

    shove_mode = False
    shove_target = None
    shove_card_user = None
    shove_steps_left = 0

    if len(enemies) == 0:
        queue_reward_after_battle()


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

    return None, next_current_turn, next_current_energy


def reset_battle_animation_state():
    global player_attack_animation
    global pending_reward_after_deaths
    global shove_mode
    global shove_target
    global shove_card_user
    global shove_steps_left

    enemy_death_animations.clear()
    projectile_animations.clear()
    player_attack_animation = None
    pending_reward_after_deaths = False
    shove_mode = False
    shove_target = None
    shove_card_user = None
    shove_steps_left = 0


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
enemy_idle_frame_index = 0
enemy_animation_timer = 0
enemy_animation_speed = 16

enemy_attack_frame_index = 0
enemy_attack_timer = 0
enemy_attack_speed = 6
enemy_is_attacking = False
attacking_enemy_index = None

player_idle_frame_index = 0
player_animation_timer = 0
player_animation_speed = 16


current_state = HOME_MENU


running = True
while running:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            if current_state == REWARD and reward_mode == "choose_sleeve_card":

                target_deck_scroll_y -= event.y * 60

                max_scroll = max(0, ((len(player_deck) + 3) // 4) * 220 - 420)

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
                    clear_party_shields(party)

                elif shove_mode:
                    row_change = 0
                    col_change = 0

                    if event.key == pygame.K_LEFT:
                        col_change = -1
                    if event.key == pygame.K_RIGHT:
                        col_change = 1
                    if event.key == pygame.K_UP:
                        row_change = -1
                    if event.key == pygame.K_DOWN:
                        row_change = 1

                    if row_change != 0 or col_change != 0:
                        while shove_steps_left > 0:
                            if not move_unit(shove_target, enemy_grid_data, row_change, col_change):
                                break

                            shove_steps_left -= 1

                        finish_shove()

                elif movement_mode:
                    # Arrow keys build a planned movement path while in card movement mode.
                    row_change = 0
                    col_change = 0

                    if event.key == pygame.K_LEFT:
                        col_change = -1
                    if event.key == pygame.K_RIGHT:
                        col_change = 1
                    if event.key == pygame.K_UP:
                        row_change = -1
                    if event.key == pygame.K_DOWN:
                        row_change = 1

                    if (
                        (row_change != 0 or col_change != 0)
                        and current_energy >= movement_card["cost"]
                    ):
                        # Clamp preview movement so the planned path stays inside the player grid.
                        next_row = movement_preview_row + row_change
                        next_col = movement_preview_col + col_change

                        next_row = max(0, min(next_row, GRID_ROWS - 1))
                        next_col = max(0, min(next_col, GRID_COLS - 1))

                        previous_tile = None

                        if len(movement_preview_path) >= 2:
                            previous_tile = movement_preview_path[-2]
                        elif len(movement_preview_path) == 1:
                            previous_tile = (movement_card_user["row"], movement_card_user["col"])

                        if previous_tile == (next_row, next_col):
                            # Walking back onto the previous tile undoes the last planned step.
                            movement_preview_path.pop()
                            movement_preview_row = next_row
                            movement_preview_col = next_col
                            movement_steps_left += 1

                        elif movement_steps_left > 0:
                            movement_preview_row = next_row
                            movement_preview_col = next_col
                            movement_preview_path.append((movement_preview_row, movement_preview_col))
                            movement_steps_left -= 1

                    if (
                        event.key == pygame.K_e
                        and len(movement_preview_path) > 0
                        and selected_card_index is not None
                        and can_land_on_tile(player_grid_data, movement_preview_row, movement_preview_col, movement_card_user)
                    ):
                        # E confirms the movement card, then spends/discards it.
                        selected_card = player_hand[selected_card_index]
                        card_was_played, current_energy, card_result = play_card(
                            selected_card,
                            movement_card_user,
                            enemies,
                            current_energy
                        )

                        if card_was_played:
                            player_grid_data[movement_card_user["row"]][movement_card_user["col"]]["unit"] = None
                            movement_card_user["row"] = movement_preview_row
                            movement_card_user["col"] = movement_preview_col
                            player_grid_data[movement_card_user["row"]][movement_card_user["col"]]["unit"] = movement_card_user
                            gain_block(movement_card_user, selected_card.get("block", 0))
                            clear_shields_involving_character(party, movement_card_user)
                            remove_broken_shields(party)

                            played_card = player_hand.pop(selected_card_index)
                            discard_pile.append(played_card)
                            selected_card_index = None

                            movement_mode = False
                            movement_card = None
                            movement_card_user = None
                            movement_preview_path = []


                else:
                    if event.key == pygame.K_e and selected_card_index is not None:
                        # E quick-plays the selected non-movement card with the selected character.
                        selected_card = player_hand[selected_card_index]

                        if not character_can_use_card(selected_character, selected_card):
                            selected_card = None
                            selected_card_index = None
                            continue

                        if selected_card["effect"] == "move" and current_energy >= selected_card["cost"]:
                            movement_mode = True
                            movement_card = selected_card
                            movement_card_user = selected_character
                            movement_preview_row = selected_character["row"]
                            movement_preview_col = selected_character["col"]
                            movement_preview_path = []
                            movement_steps_left = selected_card["move_range"]
                        else:
                            card_was_played, current_energy, card_result = play_card(
                                selected_card,
                                selected_character,
                                enemies,
                                current_energy
                            )

                            if card_was_played:
                                handle_card_feedback(card_result, selected_character)
                                handle_enemy_deaths(enemies, enemy_grid_data)
                                clear_dead_enemy_incoming_attacks(enemies, player_grid_data)
                                played_card = player_hand.pop(selected_card_index)
                                discard_pile.append(played_card)
                                selected_card_index = None
                                apply_card_utility_result(card_result)

                                if start_shove_mode(card_result, selected_character):
                                    continue

                                if len(enemies) == 0:
                                    queue_reward_after_battle()

                    # Temporary debug movement for the selected party member.
                    if event.key == pygame.K_LEFT and selected_character.get("snared", 0) == 0:
                        if move_unit(selected_character, player_grid_data, 0, -1):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)
                    if event.key == pygame.K_RIGHT and selected_character.get("snared", 0) == 0:
                        if move_unit(selected_character, player_grid_data, 0, 1):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)
                    if event.key == pygame.K_UP and selected_character.get("snared", 0) == 0:
                        if move_unit(selected_character, player_grid_data, -1, 0):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)
                    if event.key == pygame.K_DOWN and selected_character.get("snared", 0) == 0:
                        if move_unit(selected_character, player_grid_data, 1, 0):
                            clear_shields_involving_character(party, selected_character)
                            remove_broken_shields(party)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == HOME_MENU:
                # Home menu only chooses between leaving or character select.
                if quit_button.is_clicked(event.pos):
                    running = False

                if start_button.is_clicked(event.pos):
                    current_state = CHARACTER_SELECT

            if current_state == CHARACTER_SELECT:
                if archer_button.is_clicked(event.pos):
                    # Character selection starts the fixed tutorial fight with two characters.
                    party = make_party()
                    selected_character_index = 0
                    selected_character = get_selected_character(party, selected_character_index)

                    player_grid_data = create_grid_data("player")
                    enemy_grid_data = create_grid_data("enemy")
                    place_party_on_grid(party, player_grid_data, True)

                    player_deck = build_starting_deck(party)
                    draw_pile = shuffle_deck(player_deck)
                    player_hand = []
                    discard_pile = []
                    draw_cards(draw_pile, discard_pile, player_hand, 5)

                    selected_card_index = None
                    current_energy = max_energy
                    movement_mode = False
                    movement_card = None
                    movement_preview_path = []
                    enemy_movement_queue = []
                    reaction_mode = False
                    reaction_enemy = None
                    reaction_options = []
                    reset_battle_animation_state()

                    current_state = BATTLE
                    battle_number = 1

                    start_tutorial_battle(enemies, enemy_grid_data)
                    apply_enemy_assets(enemies, enemy_assets)
                    prepare_enemy_attacks(enemies, player_grid_data)

            if current_state == BATTLE:
                # Battle clicks either select cards, confirm movement, play cards, or end turn.
                if pending_reward_after_deaths:
                    continue

                if shove_mode:
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

                selected_character = get_selected_character(party, selected_character_index)
                shield_button_rect = get_shield_button_rect(party, selected_character)

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
                            continue

                    selected_character_index = clicked_character_index
                    selected_character = get_selected_character(party, selected_character_index)

                    if selected_card_index is not None and current_turn == PLAYER_TURN:
                        selected_card = player_hand[selected_card_index]

                        if selected_card["effect"] == "move" and current_energy >= selected_card["cost"]:
                            # Movement preview starts after choosing who will move, but costs nothing yet.
                            movement_mode = True
                            movement_card = selected_card
                            movement_card_user = selected_character
                            movement_preview_row = selected_character["row"]
                            movement_preview_col = selected_character["col"]
                            movement_preview_path = []
                            movement_steps_left = selected_card["move_range"]

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
                    and len(movement_preview_path) > 0
                    and selected_card_index is not None
                    and can_land_on_tile(player_grid_data, movement_preview_row, movement_preview_col, movement_card_user)
                ):
                    # In movement mode, the Play Card button confirms and pays for the card.
                    selected_card = player_hand[selected_card_index]
                    card_was_played, current_energy, card_result = play_card(
                        selected_card,
                        movement_card_user,
                        enemies,
                        current_energy
                    )

                    if card_was_played:
                        player_grid_data[movement_card_user["row"]][movement_card_user["col"]]["unit"] = None
                        movement_card_user["row"] = movement_preview_row
                        movement_card_user["col"] = movement_preview_col
                        player_grid_data[movement_card_user["row"]][movement_card_user["col"]]["unit"] = movement_card_user
                        gain_block(movement_card_user, selected_card.get("block", 0))
                        clear_shields_involving_character(party, movement_card_user)
                        remove_broken_shields(party)

                        played_card = player_hand.pop(selected_card_index)
                        discard_pile.append(played_card)
                        selected_card_index = None

                        movement_mode = False
                        movement_card = None
                        movement_card_user = None
                        movement_preview_path = []

                if play_card_button.is_clicked(event.pos) and selected_card_index is not None and current_turn == PLAYER_TURN and not movement_mode:
                    selected_card = player_hand[selected_card_index]
                    selected_character = get_selected_character(party, selected_character_index)

                    if not character_can_use_card(selected_character, selected_card):
                        selected_card_index = None
                        continue

                    if selected_card["effect"] == "move" and current_energy >= selected_card["cost"]:
                        # Movement cards enter preview first; energy is spent on confirmation.
                        movement_mode = True
                        movement_card = selected_card
                        movement_card_user = selected_character
                        movement_preview_row = selected_character["row"]
                        movement_preview_col = selected_character["col"]
                        movement_preview_path = []
                        movement_steps_left = selected_card["move_range"]
                    else:
                        # play_card spends energy, runs the card effect, and reports special modes.
                        card_was_played, current_energy, card_result = play_card(
                            selected_card,
                            selected_character,
                            enemies,
                            current_energy
                        )

                        if card_was_played:
                            handle_card_feedback(card_result, selected_character)
                            handle_enemy_deaths(enemies, enemy_grid_data)
                            clear_dead_enemy_incoming_attacks(enemies, player_grid_data)
                            played_card = player_hand.pop(selected_card_index)
                            discard_pile.append(played_card)
                            selected_card_index = None
                            apply_card_utility_result(card_result)

                            if start_shove_mode(card_result, selected_character):
                                continue

                            if len(enemies) == 0:
                                queue_reward_after_battle()


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

                        selected_card_index = None
                        movement_mode = False
                        movement_card = None
                        movement_card_user = None
                        movement_preview_path = []
                        enemy_movement_queue = []
                        reaction_mode = False
                        reaction_enemy = None
                        reaction_options = []
                        reset_battle_animation_state()
                        discard_pile.extend(player_hand)
                        player_hand.clear()
                        discard_pile.extend(draw_pile)
                        draw_pile.clear()

                        draw_pile = shuffle_deck(discard_pile)
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
                        player_deck.append(clicked_card)
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
                    movement_mode = False
                    movement_card = None
                    movement_card_user = None
                    movement_preview_path = []
                    enemy_movement_queue = []
                    reaction_mode = False
                    reaction_enemy = None
                    reaction_options = []
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
    update_enemy_death_animations(enemy_death_animations)
    update_projectile_animations(projectile_animations)
    update_party_death_animations(party)
    player_attack_animation = update_player_attack_animation(player_attack_animation)

    if pending_reward_after_deaths and not enemy_death_animations:
        pending_reward_after_deaths = False
        current_state = REWARD

    screen.fill(DARK_BG)

    if current_state == HOME_MENU:
        # Home menu draws only the global Start/Quit choices.
        start_button.draw(screen, font)
        quit_button.draw(screen, font)

    if current_state == CHARACTER_SELECT:
        # Character select currently starts the fixed Archer + Warrior party.
        title_text = font.render("Character Select", True, WHITE)
        screen.blit(title_text, (430, 180))
        archer_button.draw(screen, font)
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
        enemy_preview_tiles = get_card_preview_tiles(selected_card, selected_character)

        player_preview_tiles = []
        if movement_mode:
            # Movement previews happen on the player grid, attack previews on enemy grid.
            player_preview_tiles = movement_preview_path

        draw_battle(
            screen,
            font,
            end_turn_button,
            play_card_button,
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
            enemy_preview_tiles
        )

        draw_enemy_death_animations(screen, enemy_death_animations)
        draw_projectile_animations(screen, projectile_animations)
        draw_damage_popups(screen, damage_popups)

        mouse_pos = pygame.mouse.get_pos()
        reaction_card_indices = []

        if reaction_mode:
            draw_reaction_warning_edges(screen)
            reaction_card_indices = [
                reaction_option["card_index"] for reaction_option in reaction_options
            ]

        draw_card_hand(
            screen,
            player_hand,
            mouse_pos,
            selected_card_index,
            selected_character,
            small_font,
            reaction_card_indices
        )
        draw_pile_buttons(screen, small_font, len(draw_pile), len(discard_pile))

        if movement_mode:
            confirm_text = font.render("Choose movement, then press E or Play Card", True, WHITE)

            screen.blit(confirm_text, (360, 720))

        if shove_mode:
            shove_text = font.render("Choose shove direction with arrow keys", True, WHITE)
            screen.blit(shove_text, (360, 720))

        if reaction_mode:
            reaction_text = font.render("Reaction! Click a red card or press G", True, WHITE)
            screen.blit(reaction_text, (310, 720))

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



    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
