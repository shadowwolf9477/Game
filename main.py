import pygame

from button import Button
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DARK_BG,
    WHITE,
    FPS,
    GRID_ROWS,
    GRID_COLS
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
    resolve_enemy_incoming_attacks,
    sync_enemy_grid
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
    get_first_usable_character_index
)

from battle_grid import create_grid_data
from loaders.battle_assets import load_battle_assets
from movement import move_unit, can_land_on_tile
from menus.game_over_menu import draw_game_over_menu
from battle_renderer import draw_battle
from state.animation_state import update_animation_frame
from battle_turn_logic import finish_enemy_attack, get_next_attacking_enemy_index

from cards.card_renderer import draw_card_hand, get_clicked_card_index
from cards.card_effects import play_card
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

player_grid_data = create_grid_data()
enemy_grid_data = create_grid_data()
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
                                sync_enemy_grid(enemies, enemy_grid_data)
                                played_card = player_hand.pop(selected_card_index)
                                discard_pile.append(played_card)
                                selected_card_index = None

                                if len(enemies) == 0:
                                    # Winning a battle clears warnings and opens rewards before the map.
                                    clear_incoming_attacks(player_grid_data)
                                    enemy_grid_data = create_grid_data()
                                    movement_mode = False
                                    movement_card = None
                                    movement_card_user = None
                                    movement_preview_path = []
                                    reward_mode = "choose_reward"
                                    deck_scroll_y = 0
                                    target_deck_scroll_y = 0
                                    current_state = REWARD

                                    if len(map_layers) == 0:
                                        # The tutorial battle is fixed; the run map begins after it.
                                        map_layers = generate_map()
                                        current_map_layer = 0

                    # Temporary debug movement for the selected party member.
                    if event.key == pygame.K_LEFT:
                        move_unit(selected_character, player_grid_data, 0, -1)
                    if event.key == pygame.K_RIGHT:
                        move_unit(selected_character, player_grid_data, 0, 1)
                    if event.key == pygame.K_UP:
                        move_unit(selected_character, player_grid_data, -1, 0)
                    if event.key == pygame.K_DOWN:
                        move_unit(selected_character, player_grid_data, 1, 0)

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

                    player_grid_data = create_grid_data()
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

                    current_state = BATTLE
                    battle_number = 1

                    start_tutorial_battle(enemies, enemy_grid_data)
                    apply_enemy_assets(enemies, enemy_assets)
                    prepare_enemy_attacks(enemies, player_grid_data)

            if current_state == BATTLE:
                # Battle clicks either select cards, confirm movement, play cards, or end turn.
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
                            sync_enemy_grid(enemies, enemy_grid_data)
                            played_card = player_hand.pop(selected_card_index)
                            discard_pile.append(played_card)
                            selected_card_index = None
                            if len(enemies) == 0:
                                # Winning a battle clears warnings and opens rewards before the map.
                                clear_incoming_attacks(player_grid_data)
                                enemy_grid_data = create_grid_data()
                                selected_card_index = None
                                movement_mode = False
                                movement_card = None
                                movement_preview_path = []
                                reward_mode = "choose_reward"
                                deck_scroll_y = 0
                                target_deck_scroll_y = 0
                                current_state = REWARD

                                if len(map_layers) == 0:
                                    # The tutorial battle is fixed; the run map begins after it.
                                    map_layers = generate_map()
                                    current_map_layer = 0


                if end_turn_button.is_clicked(event.pos) and current_turn == PLAYER_TURN and not movement_mode:
                    # End of player turn: unplayed cards go to discard.
                    discard_pile.extend(player_hand)
                    player_hand.clear()

                    current_turn = ENEMY_TURN
                    enemy_is_attacking = True
                    attacking_enemy_index = get_next_attacking_enemy_index(enemies, -1)
                    selected_card_index = None
                    enemy_attack_frame_index = 0
                    enemy_attack_timer = 0

                    if attacking_enemy_index is None:
                        enemy_is_attacking = False
                        next_state, next_turn = finish_enemy_attack(
                            party,
                            player_grid_data,
                            enemy_grid_data,
                            enemies
                        )

                        if next_state is not None:
                            current_state = next_state

                        if next_turn is not None:
                            current_turn = next_turn
                            current_energy = max_energy
                            draw_cards(draw_pile, discard_pile, player_hand, 5)
            if current_state == MAP:
                clicked_node = get_clicked_map_node(map_layers, event.pos)

                if clicked_node is not None:
                    complete_map_node(map_layers, clicked_node)
                    current_map_layer = clicked_node["layer"]

                    if clicked_node["type"] == "battle" or clicked_node["type"] == "boss":
                        # Starting a map battle rebuilds grids and reshuffles the whole deck.
                        player_grid_data = create_grid_data()
                        enemy_grid_data = create_grid_data()
                        enemies.clear()

                        place_party_on_grid(party, player_grid_data)
                        selected_character = get_selected_character(party, selected_character_index)

                        battle_number += 1
                        start_map_battle(enemies, enemy_grid_data, battle_number)
                        apply_enemy_assets(enemies, enemy_assets)
                        prepare_enemy_attacks(enemies, player_grid_data)

                        selected_card_index = None
                        movement_mode = False
                        movement_card = None
                        movement_card_user = None
                        movement_preview_path = []
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
                    player_grid_data = create_grid_data()
                    enemy_grid_data = create_grid_data()
                    enemies.clear()

                    selected_card_index = None
                    movement_mode = False
                    movement_card = None
                    movement_card_user = None
                    movement_preview_path = []
                    map_layers = []

                    current_turn = PLAYER_TURN
                    current_state = CHARACTER_SELECT
                    battle_number = 0

                if game_over_quit_button.is_clicked(event.pos):
                    running = False

    deck_scroll_y += (target_deck_scroll_y - deck_scroll_y) * 0.2
    pile_scroll_y += (target_pile_scroll_y - pile_scroll_y) * 0.2

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
                    resolve_enemy_incoming_attacks(attacking_enemy, party, player_grid_data)
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

                            next_state, next_turn = finish_enemy_attack(
                                party,
                                player_grid_data,
                                enemy_grid_data,
                                enemies
                            )

                            if next_state is not None:
                                current_state = next_state

                            if next_turn is not None:
                                current_turn = next_turn
                                current_energy = max_energy
                                draw_cards(draw_pile, discard_pile, player_hand, 5)

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
            enemies,
            player_idle_frame_index,
            enemy_idle_frame_index,
            enemy_attack_frame_index,
            enemy_is_attacking,
            attacking_enemy_index,
            enemy_assets["counter"],
            player_preview_tiles,
            enemy_preview_tiles
        )

        mouse_pos = pygame.mouse.get_pos()
        draw_card_hand(screen, player_hand, mouse_pos, selected_card_index, selected_character, small_font)
        draw_pile_buttons(screen, small_font, len(draw_pile), len(discard_pile))

        if movement_mode:
            confirm_text = font.render("Choose movement, then press E or Play Card", True, WHITE)

            screen.blit(confirm_text, (360, 720))

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
