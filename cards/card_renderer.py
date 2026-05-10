import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP, BLUE


# Stores already-loaded/scaled card images so huge PNGs are not loaded every frame.
CARD_IMAGE_CACHE = {}


def get_card_image(image_path, size):
    # Load and scale a card image once, then reuse it.
    cache_key = (image_path, size)

    if cache_key not in CARD_IMAGE_CACHE:
        card_image = pygame.image.load(image_path).convert_alpha()
        card_image = pygame.transform.scale(card_image, size)
        CARD_IMAGE_CACHE[cache_key] = card_image

    return CARD_IMAGE_CACHE[cache_key]


def get_clicked_card_index(hand, mouse_pos):
    # Return the exact hand slot clicked, not just the card data.
    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if card_rect.collidepoint(mouse_pos):
            return index

    return None


def draw_card_hand(screen, hand, mouse_pos, selected_card_index):
    # Draw small card images at the bottom of the screen.
    hovered_card = None

    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        card_image = get_card_image(card["image_path"], (CARD_WIDTH, CARD_HEIGHT))
        screen.blit(card_image, (x, HAND_Y))

        if index == selected_card_index:
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
