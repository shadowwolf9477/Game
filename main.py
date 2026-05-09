import pygame
from button import Button
from game_state import HOME_MENU, BATTLE, CHARACTER_SELECT, PLAYER_TURN, ENEMY_TURN

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, WHITE
from battle_grid import draw_grid, create_grid_data
from battle_setup import start_tutorial_battle


from Characters.archer import archer


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

font = pygame.font.Font(None, 50)
#buttons 
start_button = Button(300, 170, 200, 60, "Start")
quit_button = Button(300, 250, 200, 60, "Quit")
archer_button = Button(300, 250, 200, 60, "Archer")
end_turn_button = Button(450,30,200,60, "End turn")
#Battle data 
player_row = 1
player_col = 2
selected_character = ""
current_turn = PLAYER_TURN
player_grid_data = create_grid_data()
enemy_grid_data = create_grid_data()
enemies = []



current_state = HOME_MENU

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            

            if current_state == BATTLE and current_turn == PLAYER_TURN:
                old_row = player_row
                old_col = player_col
                if event.key == pygame.K_LEFT:
                    player_col -= 1
                    player_row = max(0, min(player_row, 2))
                    player_col = max(0, min(player_col, 4))
                    player_grid_data[old_row][old_col]["unit"] = None
                    player_grid_data[player_row][player_col]["unit"] = selected_character

                if event.key == pygame.K_RIGHT:
                    player_col += 1
                    player_row = max(0, min(player_row, 2))
                    player_col = max(0, min(player_col, 4))
                    player_grid_data[old_row][old_col]["unit"] = None
                    player_grid_data[player_row][player_col]["unit"] = selected_character
                if event.key == pygame.K_UP:
                    player_row -= 1
                    player_row = max(0, min(player_row, 2))
                    player_col = max(0, min(player_col, 4))
                    player_grid_data[old_row][old_col]["unit"] = None
                    player_grid_data[player_row][player_col]["unit"] = selected_character
                if event.key == pygame.K_DOWN:
                    player_row += 1
                    player_row = max(0, min(player_row, 2))
                    player_col = max(0, min(player_col, 4))
                    player_grid_data[old_row][old_col]["unit"] = None
                    player_grid_data[player_row][player_col]["unit"] = selected_character



        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == HOME_MENU:
                if quit_button.is_clicked(event.pos):
                    running = False

                if start_button.is_clicked(event.pos):
                    current_state = CHARACTER_SELECT

            if current_state == CHARACTER_SELECT:
                if archer_button.is_clicked(event.pos):
                    selected_character = archer
                    player_row = selected_character["starting_row"]
                    player_col = selected_character["starting_col"]
                    player_grid_data[player_row][player_col]["unit"] = selected_character
                    current_state = BATTLE
                    start_tutorial_battle(enemies, enemy_grid_data)

            if current_state == BATTLE:
                if end_turn_button.is_clicked(event.pos):
                    current_turn = ENEMY_TURN


    screen.fill(DARK_BG)

    if current_state == HOME_MENU:
        start_button.draw(screen, font)
        quit_button.draw(screen, font)

    if current_state == CHARACTER_SELECT:
        title_text = font.render("Character Select", True, WHITE)
        screen.blit(title_text, (230, 100))
        archer_button.draw(screen, font)

    if current_state == BATTLE:
        battle_text = font.render("Battle", True, WHITE)
        screen.blit(battle_text, (340, 100))
        end_turn_button.draw(screen , font)
        first_enemy = enemies[0]
        first_enemy["row"]
        first_enemy["col"]
        draw_grid(screen, 60, 220, player_row, player_col)
        draw_grid(screen, 420, 220)





    pygame.display.flip()

pygame.quit()
