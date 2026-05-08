import pygame
from button import Button
from game_state import HOME_MENU, BATTLE , CHARACTER_SELECT

pygame.init()
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Roguelike Game")
font = pygame.font.Font(None, 50)
start_button = Button(300, 170, 200, 60, "Start")
quit_button = Button(300,250,200,60,"Quit")
current_state = HOME_MENU



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button.is_clicked(event.pos):
                running = False
            if start_button.is_clicked(event.pos):
                current_state = CHARACTER_SELECT
        if event.type == pygame.QUIT:
            running = False

    screen.fill(DARK_BG)
    
    start_button.draw(screen, font)
    quit_button.draw(screen, font)
    pygame.display.flip()

 


pygame.quit()

