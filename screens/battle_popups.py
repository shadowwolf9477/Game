import pygame

from cards.card_renderer import get_composed_card_image
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, CARD_WIDTH, CARD_HEIGHT


def draw_discard_choice_overlay(screen, font, small_font, prompt, discard_count):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    prompt_rect = pygame.Rect(340, 500, 520, 58)
    pygame.draw.rect(screen, (28, 24, 34), prompt_rect)
    pygame.draw.rect(screen, WHITE, prompt_rect, 2)

    prompt_text = prompt
    if discard_count > 1:
        prompt_text += " (" + str(discard_count) + " left)"

    title = font.render(prompt_text, True, WHITE)
    title_rect = title.get_rect(center=prompt_rect.center)
    screen.blit(title, title_rect)

    hint_text = small_font.render("Click a card in your hand to discard it", True, WHITE)
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 552))
    screen.blit(hint_text, hint_rect)


def draw_discard_animation(screen, selected_character, discard_animation):
    if discard_animation is None:
        return

    card_image = get_composed_card_image(
        discard_animation["card"],
        selected_character,
        (CARD_WIDTH, CARD_HEIGHT)
    )
    screen.blit(card_image, (int(discard_animation["x"]), int(discard_animation["y"])))


def get_swing_choice_rects():
    return {
        "left": pygame.Rect(500, 370, 80, 70),
        "right": pygame.Rect(620, 370, 80, 70)
    }


def get_clicked_swing_direction(mouse_pos):
    swing_rects = get_swing_choice_rects()

    for direction, rect in swing_rects.items():
        if rect.collidepoint(mouse_pos):
            return direction

    return None


def draw_swing_choice_popup(screen, font, small_font):
    popup_rect = pygame.Rect(440, 310, 320, 160)
    pygame.draw.rect(screen, (28, 24, 34), popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 3)

    title = small_font.render("Swing direction", True, WHITE)
    title_rect = title.get_rect(center=(popup_rect.centerx, popup_rect.y + 32))
    screen.blit(title, title_rect)

    swing_rects = get_swing_choice_rects()

    for direction, rect in swing_rects.items():
        pygame.draw.rect(screen, (45, 45, 60), rect)
        pygame.draw.rect(screen, WHITE, rect, 2)

        label = "L"
        if direction == "right":
            label = "R"

        label_text = font.render(label, True, WHITE)
        label_rect = label_text.get_rect(center=rect.center)
        screen.blit(label_text, label_rect)
