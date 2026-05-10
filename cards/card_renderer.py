import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP


def draw_card_hand(screen, hand, mouse_pos):
    # Draw small card images at the bottom of the screen.
    hovered_card = None

    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        card_image = pygame.image.load(card["image_path"]).convert_alpha()
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        screen.blit(card_image, (x, HAND_Y))

        if card_rect.collidepoint(mouse_pos):
            hovered_card = card

    # Draw a larger readable preview when hovering over a card.
    if hovered_card is not None:
        preview_width = 260
        preview_height = 364
        preview_x = 470
        preview_y = 120

        preview_image = pygame.image.load(hovered_card["image_path"]).convert_alpha()
        preview_image = pygame.transform.scale(preview_image, (preview_width, preview_height))
        screen.blit(preview_image, (preview_x, preview_y))
