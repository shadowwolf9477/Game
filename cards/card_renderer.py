import pygame
from settings import HAND_X, HAND_Y, CARD_WIDTH, CARD_HEIGHT, CARD_GAP, BLUE, SLEEVE_BLUE, WHITE, BLACK
from cards.card_effects import get_card_display_name
from loaders.asset_paths import asset_path


# Stores loaded/scaled card images so card art is not reloaded every frame.
CARD_IMAGE_CACHE = {}
COMPOSED_CARD_CACHE = {}

ATTACK_TEMPLATE_PATH = "assets/card_templtes/Attack template.png"
SKILL_TEMPLATE_PATH = "assets/card_templtes/skill template.png"


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
        card_image = pygame.image.load(asset_path(image_path)).convert_alpha()
        card_image = pygame.transform.smoothscale(card_image, size)
        CARD_IMAGE_CACHE[cache_key] = card_image

    return CARD_IMAGE_CACHE[cache_key]


def get_card_template_path(card):
    if card["type"] == "attack":
        return ATTACK_TEMPLATE_PATH

    return SKILL_TEMPLATE_PATH


def get_card_image_path(card, character=None):
    if character is not None and "character_image_paths" in card:
        character_name = character["name"]

        if character_name in card["character_image_paths"]:
            return card["character_image_paths"][character_name]

    return card.get("image_path")


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


def get_composed_card_image(card, character, size):
    display_name = get_card_display_name(card, character)
    image_path = get_card_image_path(card, character)
    cache_key = (
        id(card),
        display_name,
        card.get("cost"),
        card.get("damage"),
        card.get("range"),
        card.get("max_targets"),
        card.get("move_range"),
        card.get("type"),
        image_path,
        size
    )

    if cache_key not in COMPOSED_CARD_CACHE:
        COMPOSED_CARD_CACHE[cache_key] = compose_card_image(card, character, size)

    return COMPOSED_CARD_CACHE[cache_key]


def compose_card_image(card, character, size):
    template = get_card_image(get_card_template_path(card), size).copy()
    width, height = size

    draw_card_art(template, card, character, width, height)
    draw_card_cost(template, card, width, height)
    draw_card_name(template, card, character, width, height)
    draw_card_description(template, card, character, width, height)

    return template


def draw_card_art(card_surface, card, character, width, height):
    image_path = get_card_image_path(card, character)

    if image_path is None:
        return

    art_rect = pygame.Rect(
        int(width * 0.15),
        int(height * 0.19),
        int(width * 0.72),
        int(height * 0.31)
    )

    art_image = pygame.image.load(asset_path(image_path)).convert_alpha()
    art_image = scale_image_to_cover(art_image, art_rect.size)
    art_x = art_rect.x + (art_rect.width - art_image.get_width()) // 2
    art_y = art_rect.y + (art_rect.height - art_image.get_height()) // 2

    clip_rect = card_surface.get_clip()
    card_surface.set_clip(art_rect)
    card_surface.blit(art_image, (art_x, art_y))
    card_surface.set_clip(clip_rect)


def scale_image_to_cover(image, target_size):
    target_width, target_height = target_size
    width_ratio = target_width / image.get_width()
    height_ratio = target_height / image.get_height()
    scale = max(width_ratio, height_ratio)
    scaled_size = (
        max(1, int(image.get_width() * scale)),
        max(1, int(image.get_height() * scale))
    )

    return pygame.transform.smoothscale(image, scaled_size)


def draw_card_cost(card_surface, card, width, height):
    cost_font = pygame.font.Font(None, max(20, int(height * 0.14)))
    cost_text = render_text_with_outline(str(card["cost"]), cost_font, WHITE, (85, 35, 20), 2)
    cost_rect = cost_text.get_rect(center=(int(width * 0.095), int(height * 0.08)))
    card_surface.blit(cost_text, cost_rect)


def draw_card_name(card_surface, card, character, width, height):
    card_name = get_card_display_name(card, character)
    name_font = pygame.font.Font(None, max(18, int(height * 0.088)))
    draw_text_fit_center(
        card_surface,
        card_name,
        name_font,
        pygame.Rect(int(width * 0.19), int(height * 0.045), int(width * 0.66), int(height * 0.075)),
        WHITE,
        (60, 25, 25)
    )


def draw_card_description(card_surface, card, character, width, height):
    description = build_card_description(card, character)
    desc_font = pygame.font.Font(None, max(15, int(height * 0.069)))
    desc_rect = pygame.Rect(
        int(width * 0.14),
        int(height * 0.64),
        int(width * 0.72),
        int(height * 0.24)
    )
    draw_wrapped_text(card_surface, description, desc_font, desc_rect, WHITE, (35, 25, 25))


def build_card_description(card, character):
    if card["effect"] == "move":
        description = "Move up to " + str(card["move_range"]) + " tiles."

        if card.get("block", 0) > 0:
            description += " Gain " + str(card["block"]) + " block."

        return description

    if card["effect"] == "deep_breath":
        return "Gain 1 energy. Discard 1 card. Draw 1 card."

    if card["effect"] == "shove":
        return "Push the first enemy in your row " + str(card.get("push_range", 2)) + " tiles."

    if card["effect"] == "trap":
        return "Set a radius " + str(card.get("trap_radius", 1)) + " trap for " + str(card.get("trap_duration", 4)) + " turns."

    if card["effect"] == "pierce_row":
        return "Deal " + str(card["damage"]) + " damage. Range " + str(card.get("range", 3)) + ". Hits up to " + str(card["max_targets"]) + "."

    if card["effect"] == "cleave_column":
        return "Choose left or right. Split " + str(card["damage"]) + " damage across the swing."

    if card["effect"] == "basic_attack":
        if character is not None and character.get("name") == "Warrior":
            damage = card.get("character_damage", {}).get("Warrior", card["damage"])
            return "Deal " + str(damage) + " damage in the faced direction. Hits 1 enemy."

        damage = card.get("character_damage", {}).get("Archer", card["damage"])
        return "Deal " + str(damage) + " damage. Range " + str(card["range"]) + " in faced direction. Hits 1."

    return card.get("description", "")


def draw_text_fit_center(surface, text, font, rect, color, outline_color):
    text_image = render_text_with_outline(text, font, color, outline_color, 2)

    while text_image.get_width() > rect.width and font.get_height() > 10:
        font = pygame.font.Font(None, font.get_height() - 2)
        text_image = render_text_with_outline(text, font, color, outline_color, 2)

    text_rect = text_image.get_rect(center=rect.center)
    surface.blit(text_image, text_rect)


def draw_wrapped_text(surface, text, font, rect, color, outline_color):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = word

        if current_line:
            test_line = current_line + " " + word

        if font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    max_lines = max(1, rect.height // max(1, font.get_height()))
    lines = lines[:max_lines]
    total_height = len(lines) * font.get_height()
    y = rect.y + (rect.height - total_height) // 2

    for line in lines:
        line_image = render_text_with_outline(line, font, color, outline_color, 2)
        line_rect = line_image.get_rect(centerx=rect.centerx, y=y)
        surface.blit(line_image, line_rect)
        y += font.get_height()


def render_text_with_outline(text, font, color, outline_color, outline_size):
    base_text = font.render(text, True, color)
    outlined_text = pygame.Surface(
        (
            base_text.get_width() + outline_size * 2,
            base_text.get_height() + outline_size * 2
        ),
        pygame.SRCALPHA
    )

    for offset_x in range(-outline_size, outline_size + 1):
        for offset_y in range(-outline_size, outline_size + 1):
            if offset_x == 0 and offset_y == 0:
                continue

            outline_text = font.render(text, True, outline_color)
            outlined_text.blit(outline_text, (offset_x + outline_size, offset_y + outline_size))

    outlined_text.blit(base_text, (outline_size, outline_size))

    return outlined_text


def get_clicked_card_index(hand, mouse_pos):
    # Return the hand slot index so main.py can remove/discard the exact card.
    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)

        if card_rect.collidepoint(mouse_pos):
            return index

    return None


def draw_card_hand(
    screen,
    hand,
    mouse_pos,
    selected_card_index,
    selected_character=None,
    small_font=None,
    reaction_card_indices=None
):
    # Draw the current hand and track one hovered card for a larger preview.
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    if reaction_card_indices is None:
        reaction_card_indices = []

    hovered_card = None

    for index, card in enumerate(hand):
        x = HAND_X + index * (CARD_WIDTH + CARD_GAP)
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
        card_image = get_composed_card_image(card, selected_character, (CARD_WIDTH, CARD_HEIGHT))
        screen.blit(card_image, (x, HAND_Y))

        if card_has_sleeve(card):
            draw_sleeve_outline(screen, card_rect)

        if index == selected_card_index:
            # Blue border marks the card that will be played if Play Card is clicked.
            pygame.draw.rect(screen, BLUE, card_rect, 4)

        if index in reaction_card_indices:
            pygame.draw.rect(screen, (255, 70, 70), card_rect, 6)
            inner_rect = card_rect.inflate(-10, -10)
            pygame.draw.rect(screen, (255, 235, 120), inner_rect, 3)

        if card_rect.collidepoint(mouse_pos):
            hovered_card = card

    # Draw a larger readable preview when hovering over a card.
    if hovered_card is not None:
        preview_size = (360, 504)
        preview_x = 420
        preview_y = 40
        preview_image = get_composed_card_image(hovered_card, selected_character, preview_size)
        screen.blit(preview_image, (preview_x, preview_y))

        if card_has_sleeve(hovered_card):
            preview_rect = pygame.Rect(preview_x, preview_y, preview_size[0], preview_size[1])
            draw_sleeve_outline(screen, preview_rect)
