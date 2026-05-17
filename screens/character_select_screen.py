import pygame

from button import Button
from Characters.archer import archer
from Characters.warrior import warrior
from settings import WHITE


CHARACTER_OPTION_WIDTH = 190
CHARACTER_OPTION_HEIGHT = 230
PARCHMENT_RECT = pygame.Rect(680, 50, 500, 700)
PARCHMENT_PADDING_X = 24
PARCHMENT_PADDING_TOP = 28
PARCHMENT_PADDING_BOTTOM = 38
PARCHMENT_TOP_ART_RATIO = 0.52
PARCHMENT_STAT_ONE_RATIO = 0.24
TEAM_SPECIAL_RECT = pygame.Rect(500, 385, 180, 170)
TEAM_PASSIVE_RECT = pygame.Rect(500, 575, 180, 120)
SELECTED_CHARACTER_DATA = {
    "Archer": archer,
    "Warrior": warrior
}
SELECTED_CHARACTER_ART_KEYS = {
    "Archer": "archer_selected",
    "Warrior": "warrior_selected"
}

CHARACTER_DISPLAY_TEXT = {
    "Archer": {
        "role": "Ranged attacker",
        "playstyle": "Fights from afar with piercing attacks and traps.",
        "passive": "Reaction Bonus: stronger reaction attacks by 25%."
    },
    "Warrior": {
        "role": "Frontline defender",
        "playstyle": "Protects friends while cleaving and shoving enemies.",
        "passive": "Guardian: takes reduced damage while shielding other allies by 25%."
    }
}

PARTNER_DISPLAY_TEXT = {
    ("Archer", "Warrior"): {
        "special": [
            "Crossfire Cleave",
            "Strike a cross-shaped area. The center takes the most damage."
        ],
        "passive": [
            "Pinning Team",
            "If Warrior and Archer hit the same enemy in one turn, that enemy is snared."
        ]
    }
}



def create_character_select_buttons():
    return {
        "archer": Button(105, 280, 160, 60, "Archer"),
        "warrior": Button(305, 280, 160, 60, "Warrior"),
        "start_game": Button(185, 370, 200, 60, "Start Game")
    }


def get_character_select_options(archer_button, warrior_button):
    return [
        {
            "button": archer_button,
            "frames_key": "archer_idle_frames",
            "sprite_pos": (130, 135),
            "option_rect": pygame.Rect(90, 100, CHARACTER_OPTION_WIDTH, CHARACTER_OPTION_HEIGHT)
        },
        {
            "button": warrior_button,
            "frames_key": "warrior_idle_frames",
            "sprite_pos": (330, 135),
            "option_rect": pygame.Rect(290, 100, CHARACTER_OPTION_WIDTH, CHARACTER_OPTION_HEIGHT)
        }
    ]


def draw_character_option_hover(screen, option_rect):
    hover_surface = pygame.Surface(option_rect.size, pygame.SRCALPHA)
    hover_surface.fill((30, 22, 12, 95))
    screen.blit(hover_surface, option_rect.topleft)
    pygame.draw.rect(screen, (245, 218, 150), option_rect, 3)


def get_partner_display_text(selected_party):
    if len(selected_party) < 2:
        return None

    partner_key = tuple(sorted(selected_party))
    return PARTNER_DISPLAY_TEXT.get(partner_key)


def draw_wrapped_text_in_rect(screen, font, lines, rect, color):
    x = rect.x + 10
    y = rect.y + 10
    max_width = rect.width - 20

    for line in lines:
        wrapped_lines = wrap_text_line(font, line, max_width)

        for wrapped_line in wrapped_lines:
            rendered_line = font.render(wrapped_line, True, color)
            screen.blit(rendered_line, (x, y))
            y += font.get_height()


def draw_team_bonus_boxes(screen, font, selected_party):
    box_color = (24, 18, 14)
    border_color = (120, 82, 38)
    text_color = (240, 220, 175)

    pygame.draw.rect(screen, box_color, TEAM_SPECIAL_RECT)
    pygame.draw.rect(screen, border_color, TEAM_SPECIAL_RECT, 3)

    pygame.draw.rect(screen, box_color, TEAM_PASSIVE_RECT)
    pygame.draw.rect(screen, border_color, TEAM_PASSIVE_RECT, 3)

    partner_text = get_partner_display_text(selected_party)

    if partner_text is None:
        return

    draw_wrapped_text_in_rect(screen, font, partner_text["special"], TEAM_SPECIAL_RECT, text_color)
    draw_wrapped_text_in_rect(screen, font, partner_text["passive"], TEAM_PASSIVE_RECT, text_color)


def get_parchment_section_rects():
    paper = PARCHMENT_RECT
    content_top = paper.y + PARCHMENT_PADDING_TOP
    content_bottom = paper.bottom - PARCHMENT_PADDING_BOTTOM
    content_height = content_bottom - content_top

    top_section_bottom = content_top + int(content_height * PARCHMENT_TOP_ART_RATIO)
    middle_section_bottom = top_section_bottom + int(content_height * PARCHMENT_STAT_ONE_RATIO)
    center_x = paper.x + paper.width // 2
    line_left = paper.x + PARCHMENT_PADDING_X
    line_right = paper.right - PARCHMENT_PADDING_X

    return {
        "top_left": pygame.Rect(line_left, content_top, center_x - line_left, top_section_bottom - content_top),
        "top_right": pygame.Rect(center_x, content_top, line_right - center_x, top_section_bottom - content_top),
        "stats_one": pygame.Rect(line_left, top_section_bottom, line_right - line_left, middle_section_bottom - top_section_bottom),
        "stats_two": pygame.Rect(line_left, middle_section_bottom, line_right - line_left, content_bottom - middle_section_bottom)
    }


def wrap_text_line(font, text, max_width):
    words = text.split(" ")
    wrapped_lines = []
    current_line = ""

    for word in words:
        if current_line == "":
            test_line = word
        else:
            test_line = current_line + " " + word

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines


def draw_text_lines(screen, font, lines, x, y, color, max_width):
    for line in lines:
        wrapped_lines = wrap_text_line(font, line, max_width)

        for wrapped_line in wrapped_lines:
            rendered_line = font.render(wrapped_line, True, color)
            screen.blit(rendered_line, (x, y))
            y += font.get_height()


def draw_selected_character_art(screen, character_select_assets, character_name, slot_rect):
    art_key = SELECTED_CHARACTER_ART_KEYS.get(character_name)

    if art_key is None:
        return

    art_image = character_select_assets[art_key]
    art_width = min(150, slot_rect.width - 20)
    art_height = min(210, slot_rect.height - 40)
    art_image = pygame.transform.smoothscale(art_image, (art_width, art_height))
    art_rect = art_image.get_rect(center=slot_rect.center)
    screen.blit(art_image, art_rect)


def draw_selected_character_stats(screen, font, character_name, stats_rect):
    character_data = SELECTED_CHARACTER_DATA.get(character_name)
    display_text = CHARACTER_DISPLAY_TEXT.get(character_name, {})

    if character_data is None:
        return

    lines = [
        character_data["name"],
        display_text.get("role", ""),
        "HP: " + str(character_data["max_hp"]),
        "Tags: " + ", ".join(character_data.get("tags", [])),
        display_text.get("playstyle", ""),
        display_text.get("passive", "")
    ]

    text_x = stats_rect.x + 14
    text_y = stats_rect.y + 18
    text_width = stats_rect.width - 28
    draw_text_lines(screen, font, lines, text_x, text_y, (45, 24, 10), text_width)


def draw_selected_party_on_parchment(screen, small_font, character_select_assets, selected_party):
    section_rects = get_parchment_section_rects()

    if len(selected_party) >= 1:
        first_character_name = selected_party[0]
        draw_selected_character_art(screen, character_select_assets, first_character_name, section_rects["top_left"])
        draw_selected_character_stats(screen, small_font, first_character_name, section_rects["stats_one"])

    if len(selected_party) >= 2:
        second_character_name = selected_party[1]
        draw_selected_character_art(screen, character_select_assets, second_character_name, section_rects["top_right"])
        draw_selected_character_stats(screen, small_font, second_character_name, section_rects["stats_two"])


def draw_character_select_screen(
    screen,
    font,
    small_font,
    archer_button,
    warrior_button,
    start_game_button,
    character_select_assets,
    selected_party,
    mouse_pos
):
    screen.blit(character_select_assets["table"], (0, 0))

    parchment_image = character_select_assets["parchment"]
    screen.blit(parchment_image, PARCHMENT_RECT.topleft)
    draw_parchment_sections(screen)
    draw_selected_party_on_parchment(screen, small_font, character_select_assets, selected_party)
    draw_team_bonus_boxes(screen, small_font, selected_party)

    title_text = font.render("Character Select", True, WHITE)
    screen.blit(title_text, (330, 80))

    character_options = get_character_select_options(archer_button, warrior_button)

    for option in character_options:
        if option["button"].rect.collidepoint(mouse_pos):
            draw_character_option_hover(screen, option["option_rect"])

        frame = character_select_assets[option["frames_key"]][0]
        screen.blit(frame, option["sprite_pos"])
        option["button"].draw(screen, font)
    if len(selected_party) >= 2:
        start_game_button.draw(screen, font)


def add_character_to_selection(selected_party, character_name):
    if character_name in selected_party:
        return

    if len(selected_party) >= 2:
        return

    selected_party.append(character_name)


def draw_parchment_sections(screen):
    line_color = (75, 42, 18)
    section_rects = get_parchment_section_rects()
    top_section_bottom = section_rects["stats_one"].y
    middle_section_bottom = section_rects["stats_two"].y
    top_center_x = section_rects["top_right"].x
    line_left = section_rects["top_left"].x
    line_right = section_rects["top_right"].right
    content_top = section_rects["top_left"].y

    pygame.draw.line(
        screen,
        line_color,
        (line_left, top_section_bottom),
        (line_right, top_section_bottom),
        3
    )

    pygame.draw.line(
        screen,
        line_color,
        (line_left, middle_section_bottom),
        (line_right, middle_section_bottom),
        3
    )

    pygame.draw.line(
        screen,
        line_color,
        (top_center_x, content_top),
        (top_center_x, top_section_bottom),
        3
    )
