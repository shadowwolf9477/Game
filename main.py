import pygame

from button import Button
from game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN, GAME_OVER
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, WHITE, FPS, GRID_ROWS, GRID_COLS

from battle_grid import create_grid_data
from battle_setup import start_tutorial_battle, choose_goblin_attack
from battle_assets import load_battle_assets
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


# Pygame setup.
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)


# Buttons.
start_button = Button(500, 220, 220, 70, "Start")
quit_button = Button(500, 310, 220, 70, "Quit")

archer_button = Button(500, 330, 220, 70, "Archer")

end_turn_button = Button(870, 60, 220, 70, "End turn")
play_card_button = Button(870, 140, 220, 70, "Play Card")

play_again_button = Button(410, 390, 220, 70, "Play Again")
game_over_quit_button = Button(650, 390, 160, 70, "Quit")


# Player and battle state.
player_row = 1
player_col = 2
selected_character = ""

current_turn = PLAYER_TURN

player_grid_data = create_grid_data()
enemy_grid_data = create_grid_data()
enemies = []


# Card state.
player_deck = []
draw_pile = []
player_hand = []
discard_pile = []
selected_card_index = None

max_energy = 3
current_energy = 3


# Movement card planning state.
movement_mode = False
movement_card = None
movement_preview_path = []
movement_preview_row = 0
movement_preview_col = 0
movement_steps_left = 0


# Battle assets.
player_idle_frames, satyr_idle_frames, satyr_attack_frames = load_battle_assets()


# Animation state.
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

running = True
while running:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_state == BATTLE and current_turn == PLAYER_TURN:
                if movement_mode:
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

                    if movement_steps_left > 0 and (row_change != 0 or col_change != 0):
                        movement_preview_row += row_change
                        movement_preview_col += col_change

                        movement_preview_row = max(0, min(movement_preview_row, GRID_ROWS - 1))
                        movement_preview_col = max(0, min(movement_preview_col, GRID_COLS - 1))

                        movement_preview_path.append((movement_preview_row, movement_preview_col))
                        movement_steps_left -= 1

                    if event.key == pygame.K_e and len(movement_preview_path) > 0:
                        selected_character["row"] = movement_preview_row
                        selected_character["col"] = movement_preview_col

                        player_grid_data[player_row][player_col]["unit"] = None
                        player_grid_data[selected_character["row"]][selected_character["col"]]["unit"] = selected_character

                        player_row = selected_character["row"]
                        player_col = selected_character["col"]

                        movement_mode = False
                        movement_card = None
                        movement_preview_path = []


                else:
                    # Temporary debug movement until cards fully control movement.
                    if event.key == pygame.K_LEFT:
                        move_unit(selected_character, player_grid_data, 0, -1)
                    if event.key == pygame.K_RIGHT:
                        move_unit(selected_character, player_grid_data, 0, 1)
                    if event.key == pygame.K_UP:
                        move_unit(selected_character, player_grid_data, -1, 0)
                    if event.key == pygame.K_DOWN:
                        move_unit(selected_character, player_grid_data, 1, 0)

                    player_row = selected_character["row"]
                    player_col = selected_character["col"]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == HOME_MENU:
                if quit_button.is_clicked(event.pos):
                    running = False

                if start_button.is_clicked(event.pos):
                    current_state = CHARACTER_SELECT

            if current_state == CHARACTER_SELECT:
                if archer_button.is_clicked(event.pos):
                    selected_character = archer
                    selected_character["row"] = selected_character["starting_row"]
                    selected_character["col"] = selected_character["starting_col"]
                    selected_character["current_hp"] = selected_character["max_hp"]

                    player_row = selected_character["row"]
                    player_col = selected_character["col"]
                    player_grid_data[player_row][player_col]["unit"] = selected_character

                    player_deck = build_starting_deck(selected_character)
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
                clicked_card_index = get_clicked_card_index(player_hand, event.pos)

                if clicked_card_index is not None and current_turn == PLAYER_TURN and not movement_mode:
                    selected_card_index = clicked_card_index

                if play_card_button.is_clicked(event.pos) and selected_card_index is not None and current_turn == PLAYER_TURN and not movement_mode:
                    selected_card = player_hand[selected_card_index]

                    card_was_played, current_energy, card_result = play_card(
                        selected_card,
                        selected_character,
                        enemies,
                        current_energy
                    )

                    if card_was_played:
                        if card_result == "movement":
                            movement_mode = True
                            movement_card = selected_card
                            movement_preview_row = selected_character["row"]
                            movement_preview_col = selected_character["col"]
                            movement_preview_path = []
                            movement_steps_left = selected_card["move_range"]

                        played_card = player_hand.pop(selected_card_index)
                        discard_pile.append(played_card)
                        selected_card_index = None

                if end_turn_button.is_clicked(event.pos) and current_turn == PLAYER_TURN and not movement_mode:
                    # End of player turn: unplayed cards go to discard.
                    discard_pile.extend(player_hand)
                    player_hand.clear()

                    current_turn = ENEMY_TURN
                    enemy_is_attacking = True
                    selected_card_index = None
                    satyr_attack_frame_index = 0
                    satyr_attack_timer = 0

            if current_state == GAME_OVER:
                if play_again_button.is_clicked(event.pos):
                    selected_character["current_hp"] = selected_character["max_hp"]

                    player_grid_data = create_grid_data()
                    enemy_grid_data = create_grid_data()
                    enemies.clear()

                    selected_card_index = None
                    movement_mode = False
                    movement_card = None
                    movement_preview_path = []

                    current_turn = PLAYER_TURN
                    current_state = CHARACTER_SELECT

                if game_over_quit_button.is_clicked(event.pos):
                    running = False

    screen.fill(DARK_BG)

    if current_state == HOME_MENU:
        start_button.draw(screen, font)
        quit_button.draw(screen, font)

    if current_state == CHARACTER_SELECT:
        title_text = font.render("Character Select", True, WHITE)
        screen.blit(title_text, (430, 180))
        archer_button.draw(screen, font)

    if current_state == BATTLE or current_state == GAME_OVER:
        player_animation_timer, player_idle_frame_index = update_animation_frame(
            player_animation_timer,
            player_idle_frame_index,
            player_animation_speed,
            len(player_idle_frames)
        )

        satyr_animation_timer, satyr_idle_frame_index = update_animation_frame(
            satyr_animation_timer,
            satyr_idle_frame_index,
            satyr_animation_speed,
            len(satyr_idle_frames)
        )

        if current_turn == ENEMY_TURN and enemy_is_attacking:
            satyr_attack_timer += 1

            if satyr_attack_timer >= satyr_attack_speed:
                satyr_attack_timer = 0
                satyr_attack_frame_index += 1

                if satyr_attack_frame_index >= len(satyr_attack_frames):
                    enemy_is_attacking = False
                    satyr_attack_frame_index = 0

                    next_state, next_turn = finish_enemy_attack(
                        selected_character,
                        player_row,
                        player_col,
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
        player_image = player_idle_frames[player_idle_frame_index]

        if enemy_is_attacking:
            satyr_image = satyr_attack_frames[satyr_attack_frame_index]
        else:
            satyr_image = satyr_idle_frames[satyr_idle_frame_index]

        satyr_image = pygame.transform.flip(satyr_image, True, False)

        selected_card = None

        if selected_card_index is not None and selected_card_index < len(player_hand):
            selected_card = player_hand[selected_card_index]
        else:
            selected_card_index = None

        enemy_preview_tiles = get_card_preview_tiles(selected_card, selected_character)

        player_preview_tiles = []
        if movement_mode:
            player_preview_tiles = movement_preview_path

        draw_battle(
            screen,
            font,
            end_turn_button,
            play_card_button,
            selected_character,
            current_energy,
            player_row,
            player_col,
            player_grid_data,
            enemies,
            player_image,
            satyr_image,
            player_preview_tiles,
            enemy_preview_tiles
        )

        mouse_pos = pygame.mouse.get_pos()
        draw_card_hand(screen, player_hand, mouse_pos, selected_card_index)

        if movement_mode:
            confirm_text = font.render("Choose movement, then press E or Play Card", True, WHITE)

            screen.blit(confirm_text, (360, 720))

        if current_state == GAME_OVER:
            draw_game_over_menu(screen, font, play_again_button, game_over_quit_button)

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
