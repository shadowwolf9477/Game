import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP, BLUE, SLEEVE_BLUE, WHITE
from cards.card_effects import get_card_display_name


# Stores loaded/scaled card images so card art is not reloaded every frame.
CARD_IMAGE_CACHE = {}


def card_has_sleeve(card):
    return len(card.get("sleeves", [])) > 0


def draw_sleeve_outline(screen, card_rect):
    # Sleeved cards get a cyan frame so upgrades are visible in hand and rewards.
    pygame.draw.rect(screen, SLEEVE_BLUE, card_rect, 4)
    inner_rect = card_rect.inflate(-10, -10)
    pygame.draw.rect(screen, (170, 225, 255), inner_rect, 2)


def get_card_image(image_path, size):
    # Cache key includes size because the hand and hover preview use different scales.
    cache_key = (image_path, size)

    if cache_key not in CARD_IMAGE_CACHE:
        card_image = pygame.image.load(image_path).convert_alpha()
        card_image = pygame.transform.smoothscale(card_image, size)
        CARD_IMAGE_CACHE[cache_key] = card_image

    return CARD_IMAGE_CACHE[cache_key]


def get_card_image_path(card, character=None):
    if character is not None and "character_image_paths" in card:
        character_name = character["name"]

        if character_name in card["character_image_paths"]:
            return card["character_image_paths"][character_name]

    return card.get("image_path")


def draw_card_info_overlay(screen, card, character, x, y, width, height):
    # Card art is drawn very small in hand, so this keeps key info readable.
    overlay_height = 72
    overlay = pygame.Surface((width, overlay_height), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 190))
    screen.blit(overlay, (x, y + height - overlay_height))

    card_name = card["name"]

    if character is not None:
        card_name = get_card_display_name(card, character)

    name_font = pygame.font.Font(None, 25)
    stat_font = pygame.font.Font(None, 22)

    name_text = name_font.render(card_name, True, WHITE)
    cost_text = stat_font.render("Cost " + str(card["cost"]), True, WHITE)

    screen.blit(name_text, (x + 8, y + height - overlay_height + 8))
    screen.blit(cost_text, (x + 8, y + height - overlay_height + 36))

    if "damage" in card:
        damage_text = stat_font.render("Dmg " + str(card["damage"]), True, WHITE)
        screen.blit(damage_text, (x + 86, y + height - overlay_height + 36))


def draw_text_card(screen, font, card, character, x, y, width, height):
    # Temporary fallback for cards that do not have art yet.
    card_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (30, 30, 40), card_rect)
    if card_has_sleeve(card):
        draw_sleeve_outline(screen, card_rect)
    else:
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
        image_path = get_card_image_path(card, selected_character)

        if image_path is not None:
            card_image = get_card_image(image_path, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(card_image, (x, HAND_Y))
        else:
            draw_text_card(screen, small_font, card, selected_character, x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if image_path is not None and card_has_sleeve(card):
            draw_sleeve_outline(screen, card_rect)

        if index == selected_card_index:
            # Blue border marks the card that will be played if Play Card is clicked.
            pygame.draw.rect(screen, BLUE, card_rect, 4)

        if card_rect.collidepoint(mouse_pos):
            hovered_card = card

    # Draw a larger readable preview when hovering over a card.
    if hovered_card is not None:
        preview_size = (360, 504)
        preview_x = 420
        preview_y = 40
        preview_image_path = get_card_image_path(hovered_card, selected_character)

        if preview_image_path is not None:
            preview_image = get_card_image(preview_image_path, preview_size)
            screen.blit(preview_image, (preview_x, preview_y))
            if card_has_sleeve(hovered_card):
                preview_rect = pygame.Rect(preview_x, preview_y, preview_size[0], preview_size[1])
                draw_sleeve_outline(screen, preview_rect)
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
