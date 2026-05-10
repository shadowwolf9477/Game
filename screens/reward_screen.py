import pygame

from settings import WHITE
from cards.card_effects import get_card_display_name


def draw_reward_screen(screen, font, small_font, reward_mode, player_deck, deck_scroll, selected_sleeve, can_apply_sleeve):
    # Reward popup sits on its own screen between combat victory and the map.
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

        new_card_text = font.render("New Card", True, WHITE)
        sleeve_text = font.render("Sleeve", True, WHITE)

        screen.blit(new_card_text, (410, 330))
        screen.blit(sleeve_text, (665, 330))

    if reward_mode == "choose_sleeve_card":
        info_text = font.render("Choose attack card", True, WHITE)
        screen.blit(info_text, (420, 175))

        visible_cards = player_deck[deck_scroll:deck_scroll + 8]

        for index, card in enumerate(visible_cards):
            card_x, card_y, card_rect = get_reward_card_rect(index)

            if can_apply_sleeve(selected_sleeve, card):
                pygame.draw.rect(screen, WHITE, card_rect, 2)
            else:
                pygame.draw.rect(screen, (90, 90, 90), card_rect, 2)

            name_text = small_font.render(get_card_display_name(card, None), True, WHITE)
            screen.blit(name_text, (card_x, card_y + 20))

            cost_text = small_font.render("Cost " + str(card["cost"]), True, WHITE)
            screen.blit(cost_text, (card_x, card_y + 70))

            if "damage" in card:
                damage_text = small_font.render("Dmg " + str(card["damage"]), True, WHITE)
                screen.blit(damage_text, (card_x, card_y + 115))


def get_reward_choice_click(mouse_pos):
    new_card_rect = pygame.Rect(390, 310, 180, 70)
    sleeve_rect = pygame.Rect(630, 310, 180, 70)

    if new_card_rect.collidepoint(mouse_pos):
        return "new_card"

    if sleeve_rect.collidepoint(mouse_pos):
        return "sleeve"

    return None


def get_clicked_reward_deck_card(player_deck, deck_scroll, mouse_pos):
    visible_cards = player_deck[deck_scroll:deck_scroll + 8]

    for index, card in enumerate(visible_cards):
        card_x, card_y, card_rect = get_reward_card_rect(index)

        if card_rect.collidepoint(mouse_pos):
            return card

    return None


def get_reward_card_rect(index):
    card_x = 150 + (index % 4) * 235
    card_y = 250 + (index // 4) * 220
    card_rect = pygame.Rect(card_x, card_y, 150, 180)

    return card_x, card_y, card_rect
