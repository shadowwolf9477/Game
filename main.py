import pygame
from button import Button
from game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN, GAME_OVER


from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, WHITE, GRID_SIZE, GRID_GAP , FPS

from battle_grid import draw_grid, create_grid_data
from battle_setup import start_tutorial_battle, choose_goblin_attack, clear_incoming_attacks, resolve_incoming_attacks, move_enemy_random
from turn_manager import run_enemy_turn
from animation_loader import load_animation_frames
from movement import move_unit





from Characters.archer import archer


pygame.init()
clock = pygame.time.Clock()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)
#buttons 
#main menu
start_button = Button(300, 170, 200, 60, "Start")
quit_button = Button(300, 250, 200, 60, "Quit")
#charcters 
archer_button = Button(300, 250, 200, 60, "Archer")
#battle
end_turn_button = Button(450,30,200,60, "End turn")
#game over
play_again_button = Button(230, 300, 180, 60, "Play Again")
game_over_quit_button = Button(410, 300, 140, 60, "Quit")

#Battle data 
player_row = 1
player_col = 2
selected_character = ""
current_turn = PLAYER_TURN
player_grid_data = create_grid_data()
enemy_grid_data = create_grid_data()
enemies = []
#assets

player_idle_frames = load_animation_frames(
    "assests/Eris Esra's Character Template 4.1/16x32/16x32 Idle-Sheet.png",
    32,
    32,
    1,
    4,
    (GRID_SIZE, GRID_SIZE)
)
satyr_idle_frames = load_animation_frames(
    "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
    32,
    32,
    0,
    6,
    (GRID_SIZE, GRID_SIZE)
)
satyr_attack_frames = load_animation_frames(
    "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
    32,
    32,
    3,
    7,
    (GRID_SIZE, GRID_SIZE)
)

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
                    player_row = selected_character["row"]
                    player_col = selected_character["col"]
                    player_grid_data[player_row][player_col]["unit"] = selected_character
                    current_state = BATTLE
                    start_tutorial_battle(enemies, enemy_grid_data)
                    choose_goblin_attack(player_grid_data)

            if current_state == BATTLE:
                if end_turn_button.is_clicked(event.pos) and current_turn == PLAYER_TURN:
                    if end_turn_button.is_clicked(event.pos):
                        current_turn = ENEMY_TURN
                        enemy_is_attacking = True
                        satyr_attack_frame_index = 0
                        satyr_attack_timer = 0
        
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





    screen.fill(DARK_BG)
    

    if current_state == HOME_MENU:
        start_button.draw(screen, font)
        quit_button.draw(screen, font)

    if current_state == CHARACTER_SELECT:
        title_text = font.render("Character Select", True, WHITE)
        screen.blit(title_text, (230, 100))
        archer_button.draw(screen, font)
    if current_state == BATTLE or current_state == GAME_OVER:   

        player_animation_timer += 1

        if player_animation_timer >= player_animation_speed:
            player_animation_timer = 0
            player_idle_frame_index += 1

            if player_idle_frame_index >= len(player_idle_frames):
                player_idle_frame_index = 0
        satyr_animation_timer += 1
        if satyr_animation_timer >= satyr_animation_speed:
            satyr_animation_timer = 0
            satyr_idle_frame_index += 1

        if satyr_idle_frame_index >= len(satyr_idle_frames):
            satyr_idle_frame_index = 0
        if current_turn == ENEMY_TURN and enemy_is_attacking:
            satyr_attack_timer += 1

            if satyr_attack_timer >= satyr_attack_speed:
                satyr_attack_timer = 0
                satyr_attack_frame_index += 1

            if satyr_attack_frame_index >= len(satyr_attack_frames):
                enemy_is_attacking = False
                resolve_incoming_attacks(selected_character, player_row, player_col, player_grid_data)
                if selected_character["current_hp"] <= 0:
                    current_state = GAME_OVER
                else:
                    clear_incoming_attacks(player_grid_data)

                    if enemies:
                        first_enemy = enemies[0]
                        move_enemy_random(first_enemy, enemy_grid_data)

                    choose_goblin_attack(player_grid_data)
                    current_turn = PLAYER_TURN



    if current_state == BATTLE or current_state == GAME_OVER:

        battle_text = font.render("Battle", True, WHITE)
        screen.blit(battle_text, (340, 100))
        end_turn_button.draw(screen , font)
        hp_text = font.render(
            "HP: " + str(selected_character["current_hp"]) + "/" + str(selected_character["max_hp"]),
            True,
            WHITE
        )
        screen.blit(hp_text, (60, 160))

        if enemies:
            first_enemy = enemies[0]
        draw_grid(screen, 60, 220, player_row, player_col, player_grid_data)

        player_image = player_idle_frames[player_idle_frame_index]

        player_x = 60 + player_col * (GRID_SIZE + GRID_GAP)
        player_y = 220 + player_row * (GRID_SIZE + GRID_GAP)

        screen.blit(player_image, (player_x, player_y))
        draw_grid(screen, 420, 220, first_enemy["row"], first_enemy["col"])
        if enemy_is_attacking:
            satyr_image = satyr_attack_frames[satyr_attack_frame_index]
        else:
            satyr_image = satyr_idle_frames[satyr_idle_frame_index]

        satyr_image = pygame.transform.flip(satyr_image, True, False)

                

        enemy_x = 420 + first_enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = 220 + first_enemy["row"] * (GRID_SIZE + GRID_GAP)

        screen.blit(satyr_image, (enemy_x, enemy_y))
        if current_state == GAME_OVER:
            popup_rect = pygame.Rect(220, 180, 360, 220)
            pygame.draw.rect(screen, (30, 30, 40), popup_rect)
            pygame.draw.rect(screen, WHITE, popup_rect, 2)

            game_over_text = font.render("Game Over", True, WHITE)
            screen.blit(game_over_text, (300, 220))

            play_again_button.draw(screen, font)
            game_over_quit_button.draw(screen, font)





    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
