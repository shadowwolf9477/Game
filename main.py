import pygame

from button import Button
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DARK_BG,
    WHITE,
    FPS,
    GRID_ROWS,
    GRID_COLS,
    PLAYER_GRID_X,
    GRID_Y,
    GRID_SIZE,
    GRID_GAP
)
from game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN, GAME_OVER, MAP, REWARD
from cards.card_sleeves import CARD_SLEEVES
from cards.sleeve_effects import apply_sleeve, can_apply_sleeve

from battle_setup import start_tutorial_battle, choose_goblin_attack, clear_incoming_attacks
from map_loader import generate_map

from battle_grid import create_grid_data
from battle_assets import load_battle_assets, load_character_idle_frames
from movement import move_unit
from menus.game_over_menu import draw_game_over_menu
from battle_renderer import draw_battle
from animation_state import update_animation_frame
from battle_turn_logic import finish_enemy_attack

from cards.card_renderer import draw_card_hand, get_clicked_card_index
from cards.card_effects import play_card
from cards.card_targeting import get_card_preview_tiles
from cards.player_deck import build_starting_deck, shuffle_deck, draw_cards

from Characters.archer import archer
from Characters.warrior import warrior


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

# Map state.
# map_layers is generated after the tutorial fight and then remembered.
map_layers = []
current_map_layer = 0
completed = 0
available = 0

# Reward state.
# reward_mode switches the popup between reward choice and deck-card choice.
reward_mode = "choose_reward"
selected_deck_card_index = None
deck_scroll = 0
selected_sleeve = None



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
satyr_idle_frames, satyr_attack_frames = load_battle_assets()


# Animation state.
# Timers count game frames; frame indexes choose which sprite image to draw.
satyr_idle_frame_index = 0
satyr_animation_timer = 0
satyr_animation_speed = 20

satyr_attack_frame_index = 0
satyr_attack_timer = 0
satyr_attack_speed = 8
enemy_is_attacking = False

player_idle_frame_index = 0
player_animation_timer = 0
player_animation_speed = 20


current_state = HOME_MENU


def make_party():
    # Copy character templates so each run can change HP/position safely.
    archer_character = archer.copy()
    warrior_character = warrior.copy()

    archer_character["idle_frames"] = load_character_idle_frames(archer_character)
    warrior_character["idle_frames"] = load_character_idle_frames(warrior_character)

    return [archer_character, warrior_character]


def place_party_on_grid(party, player_grid_data, reset_hp=False):
    # Write every living party member into the player grid.
    for character in party:
        character["row"] = character["starting_row"]
        character["col"] = character["starting_col"]

        if reset_hp:
            character["current_hp"] = character["max_hp"]

        player_grid_data[character["row"]][character["col"]]["unit"] = character


def get_selected_character(party, selected_character_index):
    if len(party) == 0:
        return None

    return party[selected_character_index]


def get_clicked_character_index(party, mouse_pos):
    # Click the character's board tile to choose who will use cards.
    for index, character in enumerate(party):
        x = PLAYER_GRID_X + character["col"] * (GRID_SIZE + GRID_GAP)
        y = GRID_Y + character["row"] * (GRID_SIZE + GRID_GAP)
        character_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

        if character_rect.collidepoint(mouse_pos):
            return index

    return None


running = True
while running:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_state == BATTLE and current_turn == PLAYER_TURN:
                selected_character = get_selected_character(party, selected_character_index)

                if event.key == pygame.K_g:
                    # G cancels card/user selection and exits movement preview.
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

                    if row_change != 0 or col_change != 0:
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

                    if event.key == pygame.K_e and len(movement_preview_path) > 0 and selected_card_index is not None:
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

                        if selected_card["effect"] == "move":
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
                                    selected_deck_card_index = None
                                    deck_scroll = 0
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

        if event.type == pygame.MOUSEBUTTONDOWN:
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

                    start_tutorial_battle(enemies, enemy_grid_data)
                    choose_goblin_attack(player_grid_data)

            if current_state == BATTLE:
                # Battle clicks either select cards, confirm movement, play cards, or end turn.
                clicked_card_index = get_clicked_card_index(player_hand, event.pos)
                clicked_character_index = get_clicked_character_index(party, event.pos)

                if clicked_character_index is not None and not movement_mode:
                    selected_character_index = clicked_character_index
                    selected_character = get_selected_character(party, selected_character_index)

                    if selected_card_index is not None and current_turn == PLAYER_TURN:
                        selected_card = player_hand[selected_card_index]

                        if selected_card["effect"] == "move":
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
                if play_card_button.is_clicked(event.pos) and movement_mode and len(movement_preview_path) > 0 and selected_card_index is not None:
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

                    if selected_card["effect"] == "move":
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
                                selected_deck_card_index = None
                                deck_scroll = 0
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
                    selected_card_index = None
                    satyr_attack_frame_index = 0
                    satyr_attack_timer = 0
            if current_state == MAP:
                # Map nodes remember what has been completed and unlock the next layer.
                for layer in map_layers:
                    for node in layer:
                        node_rect = pygame.Rect(node["x"] - 25, node["y"] - 25, 50, 50)

                        if node["available"] and node_rect.collidepoint(event.pos):
                            node["completed"] = True
                            node["available"] = False
                            current_map_layer = node["layer"]

                            next_layer_number = current_map_layer + 1

                            if next_layer_number < len(map_layers):
                                for next_node in map_layers[next_layer_number]:
                                    next_node["available"] = True

                            if node["type"] == "battle" or node["type"] == "boss":
                                # Starting a map battle rebuilds grids and reshuffles the whole deck.
                                player_grid_data = create_grid_data()
                                enemy_grid_data = create_grid_data()
                                enemies.clear()

                                place_party_on_grid(party, player_grid_data)
                                selected_character = get_selected_character(party, selected_character_index)

                                start_tutorial_battle(enemies, enemy_grid_data)
                                choose_goblin_attack(player_grid_data)

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

                            if node["type"] == "rest":
                                # Rest is a placeholder reward node: heal a little, then stay on map.
                                for character in party:
                                    character["current_hp"] += 2

                                    if character["current_hp"] > character["max_hp"]:
                                        character["current_hp"] = character["max_hp"]

                            if node["type"] == "shop":
                                print("Shop clicked")

                            if node["type"] == "upgrade":
                                print("Upgrade clicked")

                            if node["type"] == "event":
                                print("Event clicked")
            if current_state == REWARD:
                # Reward popup first chooses a reward type, then may ask for a deck card.
                if reward_mode == "choose_reward":
                    new_card_rect = pygame.Rect(390, 310, 180, 70)
                    sleeve_rect = pygame.Rect(630, 310, 180, 70)

                    if new_card_rect.collidepoint(event.pos):
                        print("New card reward later")

                    if sleeve_rect.collidepoint(event.pos):
                        # Premium Sleeve modifies one valid card already in the deck.
                        selected_sleeve = CARD_SLEEVES["premium_sleeve"]
                        reward_mode = "choose_sleeve_card"


                elif reward_mode == "choose_sleeve_card":
                    visible_cards = player_deck[deck_scroll:deck_scroll + 8]

                    for index, card in enumerate(visible_cards):
                        card_x = 150 + (index % 4) * 235
                        card_y = 250 + (index // 4) * 220
                        card_rect = pygame.Rect(card_x, card_y, 150, 180)

                        if card_rect.collidepoint(event.pos):
                            # apply_sleeve returns False for invalid cards, such as movement cards.
                            if apply_sleeve(selected_sleeve, card):
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

                if game_over_quit_button.is_clicked(event.pos):
                    running = False

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
        # Map nodes are circles for now; later these can become event images.
        title_text = font.render("Map", True, WHITE)
        screen.blit(title_text, (560, 30))

        for layer in map_layers:
            for node in layer:
                color = (90, 90, 90)

                if node["completed"]:
                    # Completed nodes show the path the player already took.
                    color = (80, 220, 120)

                if node["available"]:
                    # Available nodes are the only ones the player can click.
                    color = (0, 180, 255)

                pygame.draw.circle(screen, color, (node["x"], node["y"]), 25)

                label_text = font.render(node["type"], True, WHITE)
                screen.blit(label_text, (node["x"] + 40, node["y"] - 15))


    if current_state == BATTLE or current_state == GAME_OVER:
        # Keep idle animations moving while battle or game-over overlay is visible.
        max_character_idle_frames = max(len(character["idle_frames"]) for character in party)
        player_animation_timer, player_idle_frame_index = update_animation_frame(
            player_animation_timer,
            player_idle_frame_index,
            player_animation_speed,
            max_character_idle_frames
        )

        satyr_animation_timer, satyr_idle_frame_index = update_animation_frame(
            satyr_animation_timer,
            satyr_idle_frame_index,
            satyr_animation_speed,
            len(satyr_idle_frames)
        )

        if current_turn == ENEMY_TURN and enemy_is_attacking:
            # Enemy damage resolves after the attack animation finishes.
            satyr_attack_timer += 1

            if satyr_attack_timer >= satyr_attack_speed:
                satyr_attack_timer = 0
                satyr_attack_frame_index += 1

                if satyr_attack_frame_index >= len(satyr_attack_frames):
                    enemy_is_attacking = False
                    satyr_attack_frame_index = 0

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
        if enemy_is_attacking:
            satyr_image = satyr_attack_frames[satyr_attack_frame_index]
        else:
            satyr_image = satyr_idle_frames[satyr_idle_frame_index]

        satyr_image = pygame.transform.flip(satyr_image, True, False)

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
            player_grid_data,
            enemies,
            player_idle_frame_index,
            satyr_image,
            player_preview_tiles,
            enemy_preview_tiles
        )

        mouse_pos = pygame.mouse.get_pos()
        draw_card_hand(screen, player_hand, mouse_pos, selected_card_index, selected_character, small_font)

        if movement_mode:
            confirm_text = font.render("Choose movement, then press E or Play Card", True, WHITE)

            screen.blit(confirm_text, (360, 720))

        if current_state == GAME_OVER:
            draw_game_over_menu(screen, font, play_again_button, game_over_quit_button)
    if current_state == REWARD:
        # Reward popup sits on its own screen between combat victory and the map.
        popup_rect = pygame.Rect(60, 90, 1080, 660)
        pygame.draw.rect(screen, (30, 30, 40), popup_rect)
        pygame.draw.rect(screen, WHITE, popup_rect, 2)

        title_text = font.render("Battle Reward", True, WHITE)
        screen.blit(title_text, (470, 120))


        if reward_mode == "choose_reward":
            # New Card is a placeholder; Sleeve is the first working reward type.
            new_card_rect = pygame.Rect(390, 310, 180, 70)
            sleeve_rect = pygame.Rect(630, 310, 180, 70)

            pygame.draw.rect(screen, WHITE, new_card_rect, 2)
            pygame.draw.rect(screen, WHITE, sleeve_rect, 2)

            new_card_text = font.render("New Card", True, WHITE)
            sleeve_text = font.render("Sleeve", True, WHITE)

            screen.blit(new_card_text, (410, 330))
            screen.blit(sleeve_text, (665, 330))

        if reward_mode == "choose_sleeve_card":
            # Show deck cards so the sleeve can upgrade one existing card.
            info_text = font.render("Choose attack card", True, WHITE)
            screen.blit(info_text, (420, 175))


            visible_cards = player_deck[deck_scroll:deck_scroll + 8]

            for index, card in enumerate(visible_cards):
                card_x = 150 + (index % 4) * 235
                card_y = 250 + (index // 4) * 220
                card_rect = pygame.Rect(card_x, card_y, 150, 180)



                if can_apply_sleeve(selected_sleeve, card):
                    # White border means this card is valid for the selected sleeve.
                    pygame.draw.rect(screen, WHITE, card_rect, 2)
                else:
                    # Gray border means clicking will not apply the sleeve.
                    pygame.draw.rect(screen, (90, 90, 90), card_rect, 2)


                name_text = small_font.render(card["name"], True, WHITE)

                screen.blit(name_text, (card_x, card_y + 20))

                cost_text = small_font.render("Cost " + str(card["cost"]), True, WHITE)

                screen.blit(cost_text, (card_x, card_y + 70))

                if "damage" in card:
                    damage_text = small_font.render("Dmg " + str(card["damage"]), True, WHITE)

                    screen.blit(damage_text, (card_x, card_y + 115))


    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
