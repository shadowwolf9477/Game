import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP, BLUE


# Stores loaded/scaled card images so card art is not reloaded every frame.
CARD_IMAGE_CACHE = {}


def get_card_image(image_path, size):
    # Cache key includes size because the hand and hover preview use different scales.
    cache_key = (image_path, size)

    if cache_key not in CARD_IMAGE_CACHE:
        card_image = pygame.image.load(image_path).convert_alpha()
        card_image = pygame.transform.scale(card_image, size)
        CARD_IMAGE_CACHE[cache_key] = card_image

    return CARD_IMAGE_CACHE[cache_key]


def get_clicked_card_index(hand, mouse_pos):
    # Return the hand slot index so main.py can remove/discard the exact card.
    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if card_rect.collidepoint(mouse_pos):
            return index

    return None


def draw_card_hand(screen, hand, mouse_pos, selected_card_index):
    # Draw the current hand and track one hovered card for a larger preview.
    hovered_card = None

    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        card_image = get_card_image(card["image_path"], (CARD_WIDTH, CARD_HEIGHT))
        screen.blit(card_image, (x, HAND_Y))

        if index == selected_card_index:
            # Blue border marks the card that will be played if Play Card is clicked.
            pygame.draw.rect(screen, BLUE, card_rect, 4)

        if card_rect.collidepoint(mouse_pos):
            hovered_card = card

    # Draw a larger readable preview when hovering over a card.
    if hovered_card is not None:
        preview_size = (260, 364)
        preview_x = 470
        preview_y = 120

        preview_image = get_card_image(hovered_card["image_path"], preview_size)
        screen.blit(preview_image, (preview_x, preview_y))
