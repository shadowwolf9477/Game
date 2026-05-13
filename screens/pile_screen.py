import pygame

from settings import WHITE
from cards.card_renderer import get_composed_card_image


PILE_BUTTON_WIDTH = 130
PILE_BUTTON_HEIGHT = 44
DRAW_PILE_BUTTON_RECT = pygame.Rect(20, 140, PILE_BUTTON_WIDTH, PILE_BUTTON_HEIGHT)
DISCARD_PILE_BUTTON_RECT = pygame.Rect(20, 192, PILE_BUTTON_WIDTH, PILE_BUTTON_HEIGHT)

PILE_POPUP_RECT = pygame.Rect(90, 70, 1020, 650)
PILE_CLOSE_RECT = pygame.Rect(1050, 88, 36, 36)
PILE_CARD_WIDTH = 180
PILE_CARD_HEIGHT = 230
PILE_CARD_GAP_X = 38
PILE_CARD_GAP_Y = 28
PILE_TOP_Y = 155
PILE_BOTTOM_Y = 685


def draw_pile_buttons(screen, font, draw_pile_count, discard_pile_count):
    draw_pile_button(screen, font, DRAW_PILE_BUTTON_RECT, "Deck", draw_pile_count)
    draw_pile_button(screen, font, DISCARD_PILE_BUTTON_RECT, "Discard", discard_pile_count)


def draw_pile_button(screen, font, rect, label, count):
    pygame.draw.rect(screen, (22, 24, 34), rect)
    pygame.draw.rect(screen, WHITE, rect, 2)

    text = font.render(label + ": " + str(count), True, WHITE)
    screen.blit(text, (rect.x + 8, rect.y + 9))


def get_clicked_pile_button(mouse_pos):
    if DRAW_PILE_BUTTON_RECT.collidepoint(mouse_pos):
        return "draw"

    if DISCARD_PILE_BUTTON_RECT.collidepoint(mouse_pos):
        return "discard"

    return None


def get_pile_view_close_clicked(mouse_pos):
    return PILE_CLOSE_RECT.collidepoint(mouse_pos)


def draw_pile_viewer(screen, font, small_font, title, cards, scroll_y):
    pygame.draw.rect(screen, (25, 25, 35), PILE_POPUP_RECT)
    pygame.draw.rect(screen, WHITE, PILE_POPUP_RECT, 2)

    title_text = font.render(title + " (" + str(len(cards)) + ")", True, WHITE)
    screen.blit(title_text, (130, 95))

    pygame.draw.rect(screen, (70, 25, 35), PILE_CLOSE_RECT)
    pygame.draw.rect(screen, WHITE, PILE_CLOSE_RECT, 2)
    close_text = small_font.render("X", True, WHITE)
    screen.blit(close_text, (PILE_CLOSE_RECT.x + 9, PILE_CLOSE_RECT.y + 6))

    hint_text = small_font.render("Mouse wheel to scroll", True, WHITE)
    screen.blit(hint_text, (130, 130))

    for index, card in enumerate(cards):
        card_x, card_y, card_rect = get_pile_card_rect(index, scroll_y)

        if card_y + PILE_CARD_HEIGHT < PILE_TOP_Y or card_y > PILE_BOTTOM_Y:
            continue

        card_image = get_composed_card_image(card, None, card_rect.size)
        screen.blit(card_image, (card_x, card_y))

        pygame.draw.rect(screen, WHITE, card_rect, 2)


def get_pile_card_rect(index, scroll_y):
    card_x = 130 + (index % 4) * (PILE_CARD_WIDTH + PILE_CARD_GAP_X)
    card_y = PILE_TOP_Y + (index // 4) * (PILE_CARD_HEIGHT + PILE_CARD_GAP_Y) - scroll_y
    card_rect = pygame.Rect(card_x, card_y, PILE_CARD_WIDTH, PILE_CARD_HEIGHT)

    return card_x, card_y, card_rect


def get_pile_max_scroll(cards):
    row_count = (len(cards) + 3) // 4
    content_height = row_count * (PILE_CARD_HEIGHT + PILE_CARD_GAP_Y)
    view_height = PILE_BOTTOM_Y - PILE_TOP_Y

    return max(0, content_height - view_height)
