import pygame

from button import Button
from loaders.asset_paths import asset_path
from settings import (
    WHITE,
    GRID_SIZE,
    GRID_GAP,
    PLAYER_GRID_X,
    ENEMY_GRID_X,
    GRID_Y,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BATTLE_TITLE_X,
    BATTLE_TITLE_Y,
    HP_X,
    HP_Y
)
from battle_grid import draw_grid, draw_occupied_attack_damage_labels
from party_manager import get_shield_button_rect, get_shield_target


ENERGY_BAR_CACHE = {}
ENERGY_BAR_SOURCE_RECT = pygame.Rect(0, 20, 98, 16)
ENERGY_BAR_SCALE = 2
STATUS_ICON_CACHE = {}
STATUS_ICON_SIZE = 24
STATUS_DEFINITIONS = [
    {
        "key": "snared",
        "name": "Snared",
        "path": "assets/Status_effects/Icon_Entangled.webp",
        "description": "This character cannot move.",
        "remaining_label": "Turns left"
    },
    {
        "key": "reaction_locked",
        "name": "Reaction Locked",
        "path": "assets/Status_effects/Icon_Shackled.webp",
        "description": "This character cannot use reaction attacks.",
        "remaining_label": "Enemy turns left"
    },
    {
        "key": "random_discard_next_turn",
        "name": "Random Discard",
        "path": "assets/Status_effects/Icon_NoDraw.webp",
        "description": "At the next player turn, discard this many random cards.",
        "remaining_label": "Cards to discard"
    },
    {
        "key": "weak_attacks",
        "name": "Weak Attacks",
        "path": "assets/Status_effects/Icon_Frail.webp",
        "description": "This character's next attacks deal 50% less damage.",
        "remaining_label": "Attacks left"
    }
]


def create_battle_buttons():
    return {
        "end_turn": Button(870, 60, 220, 70, "End turn"),
        "play_card": Button(870, 140, 220, 70, "Play Card"),
        "team_special": Button(215, 144, 180, 44, "Team")
    }


def render_outlined_text(font, text, text_color, outline_color=(0, 0, 0)):
    base_text = font.render(text, True, text_color)
    outlined_text = pygame.Surface(
        (base_text.get_width() + 4, base_text.get_height() + 4),
        pygame.SRCALPHA
    )

    for offset_x, offset_y in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        outline_text = font.render(text, True, outline_color)
        outlined_text.blit(outline_text, (offset_x + 2, offset_y + 2))

    outlined_text.blit(base_text, (2, 2))

    return outlined_text


def get_energy_bar_image(image_path):
    # Crop the second-row bar from the UI sheet and scale it for readability.
    if image_path not in ENERGY_BAR_CACHE:
        sheet = pygame.image.load(asset_path(image_path)).convert_alpha()
        bar_image = sheet.subsurface(ENERGY_BAR_SOURCE_RECT)
        bar_image = pygame.transform.scale(
            bar_image,
            (
                ENERGY_BAR_SOURCE_RECT.width * ENERGY_BAR_SCALE,
                ENERGY_BAR_SOURCE_RECT.height * ENERGY_BAR_SCALE
            )
        )
        ENERGY_BAR_CACHE[image_path] = bar_image

    return ENERGY_BAR_CACHE[image_path]


def get_status_icon(image_path):
    if image_path not in STATUS_ICON_CACHE:
        icon = pygame.image.load(asset_path(image_path)).convert_alpha()
        icon = pygame.transform.smoothscale(icon, (STATUS_ICON_SIZE, STATUS_ICON_SIZE))
        STATUS_ICON_CACHE[image_path] = icon

    return STATUS_ICON_CACHE[image_path]


def draw_energy_bar(screen, current_energy, max_energy, x, y):
    # Each bar holds max_energy. Extra energy spills into another bar.
    empty_bar = get_energy_bar_image("assets/UI_BARS/empty_bar.png")
    filled_bar = get_energy_bar_image("assets/UI_BARS/energy_bar.png")

    if max_energy <= 0:
        return

    visible_bar_count = max(1, (max(0, current_energy) + max_energy - 1) // max_energy)
    bar_gap = 4

    for bar_index in range(visible_bar_count):
        bar_y = y + bar_index * (empty_bar.get_height() + bar_gap)
        energy_in_bar = current_energy - bar_index * max_energy
        energy_ratio = energy_in_bar / max_energy
        energy_ratio = max(0, min(energy_ratio, 1))
        filled_width = int(filled_bar.get_width() * energy_ratio)

        screen.blit(empty_bar, (x, bar_y))

        if filled_width > 0:
            filled_area = pygame.Rect(0, 0, filled_width, filled_bar.get_height())
            screen.blit(filled_bar, (x, bar_y), filled_area)


def get_character_active_statuses(character):
    active_statuses = []

    for status_definition in STATUS_DEFINITIONS:
        value = character.get(status_definition["key"], 0)

        if value > 0:
            active_status = status_definition.copy()
            active_status["value"] = value
            active_statuses.append(active_status)

    return active_statuses


def draw_character_status_icons(screen, character, tile_x, tile_y):
    active_statuses = get_character_active_statuses(character)
    hovered_status = None

    if not active_statuses:
        return None

    mouse_pos = pygame.mouse.get_pos()
    icon_gap = 4
    total_width = len(active_statuses) * STATUS_ICON_SIZE + (len(active_statuses) - 1) * icon_gap
    start_x = tile_x + (GRID_SIZE - total_width) // 2
    icon_y = tile_y + GRID_SIZE - STATUS_ICON_SIZE - 4
    count_font = pygame.font.Font(None, 20)

    for index, status in enumerate(active_statuses):
        icon_x = start_x + index * (STATUS_ICON_SIZE + icon_gap)
        icon_rect = pygame.Rect(icon_x, icon_y, STATUS_ICON_SIZE, STATUS_ICON_SIZE)
        icon = get_status_icon(status["path"])

        backing_rect = icon_rect.inflate(4, 4)
        backing = pygame.Surface(backing_rect.size, pygame.SRCALPHA)
        backing.fill((15, 15, 22, 135))
        screen.blit(backing, backing_rect)
        screen.blit(icon, icon_rect)

        value_text = render_outlined_text(count_font, str(status["value"]), WHITE)
        value_rect = value_text.get_rect(bottomright=(icon_rect.right + 3, icon_rect.bottom + 3))
        screen.blit(value_text, value_rect)

        if icon_rect.collidepoint(mouse_pos):
            hovered_status = {
                "status": status,
                "rect": icon_rect
            }

    return hovered_status


def draw_status_tooltip(screen, font, hovered_status):
    if hovered_status is None:
        return

    status = hovered_status["status"]
    icon_rect = hovered_status["rect"]
    lines = [
        status["name"],
        status["description"],
        status["remaining_label"] + ": " + str(status["value"])
    ]

    padding = 8
    rendered_lines = [font.render(line, True, WHITE) for line in lines]
    tooltip_width = max(line.get_width() for line in rendered_lines) + padding * 2
    tooltip_height = len(rendered_lines) * font.get_height() + padding * 2
    tooltip_x = icon_rect.centerx - tooltip_width // 2
    tooltip_y = icon_rect.y - tooltip_height - 8

    if tooltip_x < 8:
        tooltip_x = 8
    if tooltip_x + tooltip_width > SCREEN_WIDTH - 8:
        tooltip_x = SCREEN_WIDTH - tooltip_width - 8
    if tooltip_y < 8:
        tooltip_y = icon_rect.bottom + 8

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(screen, (20, 18, 28), tooltip_rect)
    pygame.draw.rect(screen, WHITE, tooltip_rect, 2)

    for index, rendered_line in enumerate(rendered_lines):
        screen.blit(rendered_line, (tooltip_rect.x + padding, tooltip_rect.y + padding + index * font.get_height()))


def draw_team_special_meter(screen, team_special_button, team_special_charge, team_special_max_charge):
    rect = team_special_button.rect
    ready = team_special_charge >= team_special_max_charge
    fill_ratio = 0

    if team_special_max_charge > 0:
        fill_ratio = team_special_charge / team_special_max_charge
        fill_ratio = max(0, min(fill_ratio, 1))

    background_color = (28, 22, 35)
    border_color = (245, 229, 155) if ready else (170, 150, 105)
    fill_color = (235, 194, 74) if ready else (100, 168, 225)
    text_color = (255, 245, 210)
    small_font = pygame.font.Font(None, 24)

    pygame.draw.rect(screen, background_color, rect)
    pygame.draw.rect(screen, border_color, rect, 2)

    fill_width = int((rect.width - 8) * fill_ratio)
    fill_rect = pygame.Rect(rect.x + 4, rect.y + rect.height - 13, fill_width, 8)
    pygame.draw.rect(screen, fill_color, fill_rect)

    label = "Team " + str(team_special_charge) + "/" + str(team_special_max_charge)

    if ready:
        label = "Team Ready"

    label_image = small_font.render(label, True, text_color)
    label_rect = label_image.get_rect(center=(rect.centerx, rect.y + 18))
    screen.blit(label_image, label_rect)


def draw_battle(
    screen,
    font,
    end_turn_button,
    play_card_button,
    team_special_button,
    team_special_charge,
    team_special_max_charge,
    party,
    selected_character,
    current_energy,
    max_energy,
    player_grid_data,
    enemy_grid_data,
    enemies,
    player_idle_frame_index,
    enemy_idle_frame_index,
    enemy_attack_frame_index,
    enemy_is_attacking,
    attacking_enemy_index,
    player_attack_animation,
    counter_image,
    player_preview_tiles,
    enemy_preview_tiles,
    enemy_movement_preview_tiles
):
    # Draw battle title, controls, and player resources.
    battle_text = font.render("Battle", True, WHITE)
    screen.blit(battle_text, (BATTLE_TITLE_X, BATTLE_TITLE_Y))

    end_turn_button.draw(screen, font)
    play_card_button.draw(screen, font)
    draw_team_special_meter(
        screen,
        team_special_button,
        team_special_charge,
        team_special_max_charge
    )

    for index, character in enumerate(party):
        hp_text = render_outlined_text(
            font,
            character["name"] + " HP: " + str(character["current_hp"]) + "/" + str(character["max_hp"])
            + " B:" + str(character.get("block", 0)),
            WHITE
        )
        screen.blit(hp_text, (HP_X, HP_Y + index * 34))

    draw_energy_bar(screen, current_energy, max_energy, HP_X, HP_Y + 78)

    # Player side uses real grid_data because it needs attack warnings.
    selected_row = None
    selected_col = None

    if selected_character is not None:
        selected_row = selected_character["row"]
        selected_col = selected_character["col"]

    draw_grid(
        screen,
        PLAYER_GRID_X,
        GRID_Y,
        selected_row,
        selected_col,
        player_grid_data,
        player_preview_tiles
    )

    hovered_status = None

    for character in party:
        player_x = PLAYER_GRID_X + character["col"] * (GRID_SIZE + GRID_GAP)
        player_y = GRID_Y + character["row"] * (GRID_SIZE + GRID_GAP)

        if character["current_hp"] <= 0 and character.get("death_animation_done", False):
            if character.get("flip_x"):
                frames = character["death_frames_flipped"]
            else:
                frames = character["death_frames"]

            frame_index = min(character.get("death_frame_index", 0), len(frames) - 1)

        elif (
            player_attack_animation is not None
            and player_attack_animation["character"] is character
        ):
            if character.get("flip_x"):
                frames = character["attack_frames_flipped"]
            else:
                frames = character["attack_frames"]

            frame_index = player_attack_animation["frame_index"] % len(frames)
            attack_draw_offset_x = character.get("attack_draw_offset_x", 0)

            if character.get("flip_x"):
                attack_draw_offset_x *= -1

        else:
            if character.get("flip_x"):
                frames = character["idle_frames_flipped"]
            else:
                frames = character["idle_frames"]

            frame_index = player_idle_frame_index % len(frames)
            attack_draw_offset_x = 0

        player_image = frames[frame_index]
        player_draw_x = player_x - (player_image.get_width() - GRID_SIZE) // 2
        player_draw_x += attack_draw_offset_x
        player_draw_y = player_y - (player_image.get_height() - GRID_SIZE)
        screen.blit(player_image, (player_draw_x, player_draw_y))
        character_hovered_status = draw_character_status_icons(screen, character, player_x, player_y)

        if character_hovered_status is not None:
            hovered_status = character_hovered_status

    draw_occupied_attack_damage_labels(screen, PLAYER_GRID_X, GRID_Y, player_grid_data)
    draw_status_tooltip(screen, pygame.font.Font(None, 26), hovered_status)

    draw_shield_button(screen, font, party, selected_character)

    if enemies:
        selected_enemy = enemies[0]

        draw_grid(
            screen,
            ENEMY_GRID_X,
            GRID_Y,
            selected_enemy["row"],
            selected_enemy["col"],
            enemy_grid_data,
            enemy_preview_tiles,
            enemy_movement_preview_tiles
        )

        for index, enemy in enumerate(enemies):
            enemy_x = ENEMY_GRID_X + enemy["col"] * (GRID_SIZE + GRID_GAP)
            enemy_y = GRID_Y + enemy["row"] * (GRID_SIZE + GRID_GAP)

            if enemy_is_attacking and index == attacking_enemy_index:
                if enemy.get("flip_x", True):
                    frames = enemy["attack_frames_flipped"]
                else:
                    frames = enemy["attack_frames"]

                enemy_image = frames[enemy_attack_frame_index % len(frames)]
            else:
                if enemy.get("flip_x", True):
                    frames = enemy["idle_frames_flipped"]
                else:
                    frames = enemy["idle_frames"]

                enemy_image = frames[enemy_idle_frame_index % len(frames)]

            enemy_draw_x = enemy_x - (enemy_image.get_width() - GRID_SIZE) // 2
            enemy_draw_y = enemy_y - (enemy_image.get_height() - GRID_SIZE)
            screen.blit(enemy_image, (enemy_draw_x, enemy_draw_y))
            draw_enemy_hp_badge(screen, enemy, enemy_draw_x, enemy_draw_y, enemy_image)
            draw_enemy_attack_counter(screen, font, counter_image, enemy, enemy_x, enemy_y)
    else:
        draw_grid(screen, ENEMY_GRID_X, GRID_Y, None, None, enemy_grid_data, enemy_preview_tiles, enemy_movement_preview_tiles)


def get_clicked_enemy(enemies, mouse_pos):
    for enemy in enemies:
        enemy_x = ENEMY_GRID_X + enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = GRID_Y + enemy["row"] * (GRID_SIZE + GRID_GAP)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, GRID_SIZE, GRID_SIZE)

        if enemy_rect.collidepoint(mouse_pos):
            return enemy

    return None


def draw_enemy_attack_counter(screen, font, counter_image, enemy, enemy_x, enemy_y):
    counter_x = enemy_x + GRID_SIZE - 32
    counter_y = enemy_y + GRID_SIZE - 32
    screen.blit(counter_image, (counter_x, counter_y))

    counter_text = render_outlined_text(font, str(enemy["turns_until_attack"]), WHITE)
    text_rect = counter_text.get_rect(center=(counter_x + 19, counter_y + 19))
    screen.blit(counter_text, text_rect)


def draw_enemy_hp_badge(screen, enemy, enemy_draw_x, enemy_draw_y, enemy_image):
    hp_font = pygame.font.Font(None, 24)
    hp_text = str(enemy["hp"]) + "/" + str(enemy["max_hp"])
    hp_image = hp_font.render(hp_text, True, WHITE)
    badge_x = enemy_draw_x + (enemy_image.get_width() - hp_image.get_width()) // 2 - 5
    badge_y = max(6, enemy_draw_y - hp_image.get_height() - 7)
    badge_rect = pygame.Rect(badge_x, badge_y, hp_image.get_width() + 10, hp_image.get_height() + 6)

    pygame.draw.rect(screen, (18, 18, 28), badge_rect)
    pygame.draw.rect(screen, (230, 230, 255), badge_rect, 1)
    screen.blit(hp_image, (badge_rect.x + 5, badge_rect.y + 3))


def draw_reaction_warning_edges(screen):
    warning_color = (255, 30, 40, 130)
    edge_size = 34
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    pygame.draw.rect(overlay, warning_color, (0, 0, screen_width, edge_size))
    pygame.draw.rect(overlay, warning_color, (0, screen_height - edge_size, screen_width, edge_size))
    pygame.draw.rect(overlay, warning_color, (0, 0, edge_size, screen_height))
    pygame.draw.rect(overlay, warning_color, (screen_width - edge_size, 0, edge_size, screen_height))

    screen.blit(overlay, (0, 0))


def draw_enemy_hover_tooltip(screen, small_font, enemies, mouse_pos):
    hovered_enemy = get_hovered_enemy(enemies, mouse_pos)

    if hovered_enemy is None:
        return

    lines = wrap_tooltip_lines(small_font, build_enemy_tooltip_lines(hovered_enemy), 300)
    tooltip_width = 330
    line_height = small_font.get_height() + 4
    tooltip_height = 18 + len(lines) * line_height
    tooltip_x = mouse_pos[0] + 18
    tooltip_y = mouse_pos[1] + 18

    if tooltip_x + tooltip_width > SCREEN_WIDTH:
        tooltip_x = mouse_pos[0] - tooltip_width - 18

    if tooltip_y + tooltip_height > SCREEN_HEIGHT:
        tooltip_y = SCREEN_HEIGHT - tooltip_height - 10

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(screen, (18, 18, 28), tooltip_rect)
    pygame.draw.rect(screen, (230, 230, 255), tooltip_rect, 2)

    text_y = tooltip_y + 9

    for index, line in enumerate(lines):
        if index == 0:
            text_color = (255, 235, 170)
        else:
            text_color = WHITE

        text_image = small_font.render(line, True, text_color)
        screen.blit(text_image, (tooltip_x + 10, text_y))
        text_y += line_height


def wrap_tooltip_lines(font, lines, max_width):
    wrapped_lines = []

    for line in lines:
        words = line.split(" ")
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


def get_hovered_enemy(enemies, mouse_pos):
    for enemy in enemies:
        enemy_x = ENEMY_GRID_X + enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = GRID_Y + enemy["row"] * (GRID_SIZE + GRID_GAP)
        hover_rect = pygame.Rect(enemy_x, enemy_y - 35, GRID_SIZE, GRID_SIZE + 35)
        hover_rect = hover_rect.inflate(35, 20)

        if hover_rect.collidepoint(mouse_pos):
            return enemy

    return None


def build_enemy_tooltip_lines(enemy):
    lines = [
        enemy["name"],
        "HP: " + str(enemy["hp"]) + "/" + str(enemy["max_hp"]),
        "Attack: " + str(enemy["attack_damage"]) + " dmg",
        "Timer: " + str(enemy["turns_until_attack"]) + "/" + str(enemy["attack_interval"]) + " turns",
        "Pattern: " + get_enemy_pattern_text(enemy),
        "Move: " + get_enemy_move_text(enemy)
    ]

    applied_status = get_enemy_applied_status_text(enemy)

    if applied_status:
        lines.append("Applies: " + applied_status)

    active_status = get_enemy_active_status_text(enemy)

    if active_status:
        lines.append("Status: " + active_status)

    return lines


def get_enemy_pattern_text(enemy):
    enemy_type = enemy["type"]

    if enemy_type == "orc":
        return "Smashes the best 2x2 around players."

    if enemy_type == "bone_caller":
        return "Hits the most crowded row."

    if enemy_type == "skeleton":
        attack_range = enemy.get("attack_range", 1)

        if enemy.get("can_split", False):
            return "Hits row range " + str(attack_range) + ". Splits at half HP."

        return "Hits row range " + str(attack_range) + "."

    if enemy_type == "crawler":
        return "Targets the closest character."

    if enemy_type == "web_priest":
        return "Hexes around an exposed character."

    return "Targets weak characters and escape tiles."


def get_enemy_move_text(enemy):
    enemy_type = enemy["type"]

    if enemy_type == "orc":
        return "After attacking, jumps toward characters."

    if enemy_type == "crawler":
        return "Moves toward living characters."

    if enemy_type == "skeleton":
        return "Moves up to 2 squares toward characters."

    if enemy_type in ["bone_caller", "web_priest"]:
        return "Keeps away from living characters."

    return "Moves toward living characters."


def get_enemy_applied_status_text(enemy):
    enemy_type = enemy["type"]

    if enemy_type == "crawler":
        return "Snare: cannot move next turn."

    if enemy_type == "web_priest":
        return "Reaction lock, discard, weak attacks."

    if enemy_type == "bone_caller":
        return "Heals allies. Gains dmg when enemies spawn."

    return ""


def get_enemy_active_status_text(enemy):
    statuses = []

    if enemy.get("spawn_bonus", 0) > 0:
        statuses.append("+" + str(enemy["spawn_bonus"]) + " attack")

    if enemy.get("can_split", False) and enemy["hp"] <= enemy.get("split_threshold", 0):
        statuses.append("will split")

    if enemy.get("turns_until_heal", 0) > 0:
        statuses.append("heal in " + str(enemy["turns_until_heal"]))

    return ", ".join(statuses)


def draw_shield_button(screen, font, party, selected_character):
    button_rect = get_shield_button_rect(party, selected_character)

    if button_rect is None:
        return

    shield_target = get_shield_target(party, selected_character)
    is_active = selected_character.get("shielding") is shield_target

    if is_active:
        button_color = (85, 190, 255)
        button_text = "Shielding"
    else:
        button_color = (255, 255, 255)
        button_text = "Shield?"

    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)

    text_image = font.render(button_text, True, (0, 0, 0))
    text_rect = text_image.get_rect(center=button_rect.center)
    screen.blit(text_image, text_rect)
