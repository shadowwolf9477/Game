import pygame

from button import Button
from game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN, GAME_OVER
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, WHITE, FPS

from battle_grid import create_grid_data
from battle_setup import start_tutorial_battle, choose_goblin_attack
from battle_assets import load_battle_assets
from movement import move_unit
from menus.game_over_menu import draw_game_over_menu
from battle_renderer import draw_battle
from animation_state import update_animation_frame
from battle_turn_logic import finish_enemy_attack

from Characters.archer import archer


# Pygame setup.
pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)


# Buttons are created once, then drawn/checked depending on the current screen.
# Main menu buttons.
start_button = Button(300, 170, 200, 60, "Start")
quit_button = Button(300, 250, 200, 60, "Quit")

# Character select buttons.
archer_button = Button(300, 250, 200, 60, "Archer")

# Battle buttons.
end_turn_button = Button(450, 30, 200, 60, "End turn")

# Game over overlay buttons.
play_again_button = Button(230, 300, 180, 60, "Play Again")
game_over_quit_button = Button(410, 300, 140, 60, "Quit")


# Battle state data.
# player_row/player_col are kept for drawing and attack checks.
# selected_character also stores its own row/col for movement.py.
player_row = 1
player_col = 2
selected_character = ""

current_turn = PLAYER_TURN

# These hold tile data for the left and right battle grids.
player_grid_data = create_grid_data()
enemy_grid_data = create_grid_data()

# Enemy list supports one enemy now and multiple enemies later.
enemies = []


# Battle assets are loaded in battle_assets.py.
player_idle_frames, satyr_idle_frames, satyr_attack_frames = load_battle_assets()


# Animation state.
# Each animation has a current frame, a timer, and a speed.
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


# The game starts on the main menu.
current_state = HOME_MENU

running = True
while running:
    # Input section: read keyboard, mouse, and quit events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Temporary debug movement.
            # Later, cards will call movement.py instead of arrow keys.
            if current_state == BATTLE and current_turn == PLAYER_TURN:
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
            # Main menu input.
            if current_state == HOME_MENU:
                if quit_button.is_clicked(event.pos):
                    running = False

                if start_button.is_clicked(event.pos):
                    current_state = CHARACTER_SELECT

            # Character select input.
            if current_state == CHARACTER_SELECT:
                if archer_button.is_clicked(event.pos):
                    selected_character = archer
                    selected_character["row"] = selected_character["starting_row"]
                    selected_character["col"] = selected_character["starting_col"]

                    player_row = selected_character["row"]
                    player_col = selected_character["col"]
                    player_grid_data[player_row][player_col]["unit"] = selected_character

                    current_state = BATTLE

                    # battle_setup.py creates the tutorial enemy and first warning tiles.
                    start_tutorial_battle(enemies, enemy_grid_data)
                    choose_goblin_attack(player_grid_data)

            # Battle input.
            if current_state == BATTLE:
                if end_turn_button.is_clicked(event.pos) and current_turn == PLAYER_TURN:
                    current_turn = ENEMY_TURN
                    enemy_is_attacking = True
                    satyr_attack_frame_index = 0
                    satyr_attack_timer = 0

            # Game over overlay input.
            if current_state == GAME_OVER:
                if play_again_button.is_clicked(event.pos):
                    selected_character["current_hp"] = selected_character["max_hp"]

                    player_grid_data = create_grid_data()
                    enemy_grid_data = create_grid_data()
                    enemies.clear()

                    current_turn = PLAYER_TURN
                    current_state = CHARACTER_SELECT

                if game_over_quit_button.is_clicked(event.pos):
                    running = False


    # Clear the screen before drawing the current state.
    screen.fill(DARK_BG)

    # Main menu drawing.
    if current_state == HOME_MENU:
        start_button.draw(screen, font)
        quit_button.draw(screen, font)

    # Character select drawing.
    if current_state == CHARACTER_SELECT:
        title_text = font.render("Character Select", True, WHITE)
        screen.blit(title_text, (230, 100))
        archer_button.draw(screen, font)

    # Battle update section.
    # This runs for BATTLE and GAME_OVER so the battle stays visible behind the popup.
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

        # Enemy attack animation. Damage and movement happen only after the animation finishes.
        if current_turn == ENEMY_TURN and enemy_is_attacking:
            satyr_attack_timer += 1

            if satyr_attack_timer >= satyr_attack_speed:
                satyr_attack_timer = 0
                satyr_attack_frame_index += 1

                if satyr_attack_frame_index >= len(satyr_attack_frames):
                    enemy_is_attacking = False
                    satyr_attack_frame_index = 0

                    # battle_turn_logic.py resolves damage, death, enemy movement, and next warnings.
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

    # Battle drawing section.
    if current_state == BATTLE or current_state == GAME_OVER:
        player_image = player_idle_frames[player_idle_frame_index]

        if enemy_is_attacking:
            satyr_image = satyr_attack_frames[satyr_attack_frame_index]
        else:
            satyr_image = satyr_idle_frames[satyr_idle_frame_index]

        # Satyr art faces the wrong way by default, so flip it toward the player.
        satyr_image = pygame.transform.flip(satyr_image, True, False)

        # battle_renderer.py draws grids, HP, player sprite, and enemy sprite.
        draw_battle(
            screen,
            font,
            end_turn_button,
            selected_character,
            player_row,
            player_col,
            player_grid_data,
            enemies,
            player_image,
            satyr_image
        )

        # menus/game_over_menu.py draws a popup over the battle.
        if current_state == GAME_OVER:
            draw_game_over_menu(screen, font, play_again_button, game_over_quit_button)

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
