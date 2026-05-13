import pygame

from settings import SLEEVE_BLUE, WHITE
from cards.card_renderer import card_has_sleeve, draw_sleeve_outline, get_composed_card_image


def draw_reward_screen(screen, font, small_font, reward_mode, card_reward_choices, player_deck, deck_scroll_y, selected_sleeve, can_apply_sleeve):
    popup_rect = pygame.Rect(60, 90, 1080, 660)
    pygame.draw.rect(screen, (30, 30, 40), popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 2)

    title_text = font.render("Battle Reward", True, WHITE)
    screen.blit(title_text, (470, 120))

    if reward_mode == "choose_reward":
        new_card_rect = pygame.Rect(390, 310, 180, 70)
        sleeve_rect = pygame.Rect(630, 310, 180, 70)

        pygame.draw.rect(screen, WHITE, new_card_rect, 2)
        pygame.draw.rect(screen, WHITE, sleeve_rect, 2)

        screen.blit(font.render("New Card", True, WHITE), (410, 330))
        screen.blit(font.render("Sleeve", True, WHITE), (665, 330))
    if reward_mode == "choose_new_card":
        info_text = font.render("Choose a card", True, WHITE)
        screen.blit(info_text, (450, 175))
        for index, card in enumerate(card_reward_choices):
            card_x, card_y, card_rect = get_card_reward_rect(index)
            card_image = get_composed_card_image(card, None, card_rect.size)
            screen.blit(card_image, (card_x, card_y))

            pygame.draw.rect(screen, WHITE, card_rect, 3)





    if reward_mode == "choose_sleeve_card":
        info_text = font.render("Choose a card to sleeve", True, WHITE)
        screen.blit(info_text, (380, 175))

        hint_text = small_font.render("Mouse wheel to scroll. Click a white card to upgrade it.", True, WHITE)
        screen.blit(hint_text, (330, 215))

        for index, card in enumerate(player_deck):
            card_x, card_y, card_rect = get_reward_card_rect(index, deck_scroll_y)

            if card_y < 230 or card_y > 690:
                continue

            valid = can_apply_sleeve(selected_sleeve, card)
            card_image = get_composed_card_image(card, None, card_rect.size)
            screen.blit(card_image, (card_x, card_y))

            if valid:
                pygame.draw.rect(screen, WHITE, card_rect, 3)
            else:
                pygame.draw.rect(screen, (90, 90, 90), card_rect, 3)

            if card_has_sleeve(card):
                draw_sleeve_outline(screen, card_rect)
                sleeve_text = small_font.render("Sleeved", True, SLEEVE_BLUE)
                screen.blit(sleeve_text, (card_x + 8, card_y + card_rect.height - 35))


def get_reward_choice_click(mouse_pos):
    new_card_rect = pygame.Rect(390, 310, 180, 70)
    sleeve_rect = pygame.Rect(630, 310, 180, 70)

    if new_card_rect.collidepoint(mouse_pos):
        return "new_card"

    if sleeve_rect.collidepoint(mouse_pos):
        return "sleeve"

    return None


def get_clicked_reward_deck_card(player_deck, deck_scroll_y, mouse_pos):
    for index, card in enumerate(player_deck):
        card_x, card_y, card_rect = get_reward_card_rect(index, deck_scroll_y)

        if card_y < 230 or card_y > 690:
            continue

        if card_rect.collidepoint(mouse_pos):
            return card

    return None


def get_clicked_card_reward(card_reward_choices, mouse_pos):
    for index, card in enumerate(card_reward_choices):
        card_x, card_y, card_rect = get_card_reward_rect(index)

        if card_rect.collidepoint(mouse_pos):
            return card

    return None


def get_reward_card_rect(index, deck_scroll_y):
    card_x = 110 + (index % 4) * 260
    card_y = 250 + (index // 4) * 260 - deck_scroll_y
    card_rect = pygame.Rect(card_x, card_y, 180, 230)

    return card_x, card_y, card_rect

def get_card_reward_rect(index):
    card_x = 270 + index * 230
    card_y = 280
    card_rect = pygame.Rect(card_x, card_y, 170, 220)

    return card_x, card_y, card_rect
