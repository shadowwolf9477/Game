import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP, BLUE, WHITE
from cards.card_effects import get_card_display_name


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


def draw_text_card(screen, font, card, character, x, y, width, height):
    # Temporary fallback for cards that do not have art yet.
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (30, 30, 40), card_rect)
    pygame.draw.rect(screen, WHITE, card_rect, 2)

    card_name = card["name"]

    if character is not None:
        card_name = get_card_display_name(card, character)

    card_font = pygame.font.Font(None, 30)
    small_card_font = pygame.font.Font(None, 26)

    name_text = card_font.render(card_name, True, WHITE)
    cost_text = small_card_font.render("Cost " + str(card["cost"]), True, WHITE)

    screen.blit(name_text, (x + 8, y + 14))
    screen.blit(cost_text, (x + 8, y + 58))

    if "damage" in card:
        damage_text = small_card_font.render("Dmg " + str(card["damage"]), True, WHITE)
        screen.blit(damage_text, (x + 8, y + 96))

    type_text = small_card_font.render(card["type"], True, WHITE)
    screen.blit(type_text, (x + 8, y + height - 34))


def get_clicked_card_index(hand, mouse_pos):
    # Return the hand slot index so main.py can remove/discard the exact card.
    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if card_rect.collidepoint(mouse_pos):
            return index

    return None


def draw_card_hand(screen, hand, mouse_pos, selected_card_index, selected_character=None, small_font=None):
    # Draw the current hand and track one hovered card for a larger preview.
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    hovered_card = None

    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if "image_path" in card:
            card_image = get_card_image(card["image_path"], (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(card_image, (x, HAND_Y))
        else:
            draw_text_card(screen, small_font, card, selected_character, x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

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

        if "image_path" in hovered_card:
            preview_image = get_card_image(hovered_card["image_path"], preview_size)
            screen.blit(preview_image, (preview_x, preview_y))
        else:
            draw_text_card(
                screen,
                small_font,
                hovered_card,
                selected_character,
                preview_x,
                preview_y,
                preview_size[0],
                preview_size[1]
            )
