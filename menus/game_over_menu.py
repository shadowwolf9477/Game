import pygame
from settings import WHITE


def draw_game_over_menu(screen, font, play_again_button, quit_button):
    popup_rect = pygame.Rect(220, 180, 360, 220)
    pygame.draw.rect(screen, (30, 30, 40), popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 2)

    game_over_text = font.render("Game Over", True, WHITE)
    screen.blit(game_over_text, (300, 220))

    play_again_button.draw(screen, font)
    quit_button.draw(screen, font)
