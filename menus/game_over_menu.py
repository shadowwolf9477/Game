import pygame

from button import Button
from settings import (
    WHITE,
    GAME_OVER_POPUP_X,
    GAME_OVER_POPUP_Y,
    GAME_OVER_POPUP_WIDTH,
    GAME_OVER_POPUP_HEIGHT,
    GAME_OVER_TEXT_X,
    GAME_OVER_TEXT_Y
)


def create_game_over_buttons():
    return {
        "play_again": Button(410, 390, 220, 70, "Play Again"),
        "quit": Button(650, 390, 160, 70, "Quit")
    }


def draw_game_over_menu(screen, font, play_again_button, quit_button):
    # Draw a centered popup over the frozen battle screen.
    popup_rect = pygame.Rect(
        GAME_OVER_POPUP_X,
        GAME_OVER_POPUP_Y,
        GAME_OVER_POPUP_WIDTH,
        GAME_OVER_POPUP_HEIGHT
    )

    pygame.draw.rect(screen, (30, 30, 40), popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 2)

    game_over_text = font.render("Game Over", True, WHITE)
    screen.blit(game_over_text, (GAME_OVER_TEXT_X, GAME_OVER_TEXT_Y))

    # Reuse normal Button objects so menu click handling stays simple.
    play_again_button.draw(screen, font)
    quit_button.draw(screen, font)
