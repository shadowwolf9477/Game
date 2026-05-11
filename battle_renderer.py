import pygame

from settings import (
    WHITE,
    GRID_SIZE,
    GRID_GAP,
    PLAYER_GRID_X,
    ENEMY_GRID_X,
    GRID_Y,
    BATTLE_TITLE_X,
    BATTLE_TITLE_Y,
    HP_X,
    HP_Y
)
from battle_grid import draw_grid


ENERGY_BAR_CACHE = {}
ENERGY_BAR_SOURCE_RECT = pygame.Rect(0, 20, 98, 16)
ENERGY_BAR_SCALE = 2


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
        sheet = pygame.image.load(image_path).convert_alpha()
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


def draw_energy_bar(screen, current_energy, max_energy, x, y):
    # Draw an empty bar, then clip the filled bar to match current energy.
    empty_bar = get_energy_bar_image("assests/UI BARS/empty_bar.png")
    filled_bar = get_energy_bar_image("assests/UI BARS/energy_bar.png")

    screen.blit(empty_bar, (x, y))

    if max_energy <= 0:
        return

    energy_ratio = current_energy / max_energy
    energy_ratio = max(0, min(energy_ratio, 1))
    filled_width = int(filled_bar.get_width() * energy_ratio)

    if filled_width > 0:
        filled_area = pygame.Rect(0, 0, filled_width, filled_bar.get_height())
        screen.blit(filled_bar, (x, y), filled_area)


def draw_battle(
    screen,
    font,
    end_turn_button,
    play_card_button,
    party,
    selected_character,
    current_energy,
    max_energy,
    player_grid_data,
    enemies,
    player_idle_frame_index,
    enemy_idle_frame_index,
    enemy_attack_frame_index,
    enemy_is_attacking,
    attacking_enemy_index,
    counter_image,
    player_preview_tiles,
    enemy_preview_tiles
):
    # Draw battle title, controls, and player resources.
    battle_text = font.render("Battle", True, WHITE)
    screen.blit(battle_text, (BATTLE_TITLE_X, BATTLE_TITLE_Y))

    end_turn_button.draw(screen, font)
    play_card_button.draw(screen, font)

    for index, character in enumerate(party):
        hp_text = render_outlined_text(
            font,
            character["name"] + " HP: " + str(character["current_hp"]) + "/" + str(character["max_hp"]),
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

    for character in party:
        player_x = PLAYER_GRID_X + character["col"] * (GRID_SIZE + GRID_GAP)
        player_y = GRID_Y + character["row"] * (GRID_SIZE + GRID_GAP)

        if character.get("flip_x"):
            frames = character["idle_frames_flipped"]
        else:
            frames = character["idle_frames"]

        player_image = frames[player_idle_frame_index % len(frames)]

        screen.blit(player_image, (player_x, player_y))

    if enemies:
        selected_enemy = enemies[0]

        draw_grid(
            screen,
            ENEMY_GRID_X,
            GRID_Y,
            selected_enemy["row"],
            selected_enemy["col"],
            None,
            enemy_preview_tiles
        )

        for index, enemy in enumerate(enemies):
            enemy_x = ENEMY_GRID_X + enemy["col"] * (GRID_SIZE + GRID_GAP)
            enemy_y = GRID_Y + enemy["row"] * (GRID_SIZE + GRID_GAP)

            enemy_hp_text = render_outlined_text(font, "HP: " + str(enemy["hp"]), WHITE)
            screen.blit(enemy_hp_text, (enemy_x, enemy_y - 45))

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
            draw_enemy_attack_counter(screen, font, counter_image, enemy, enemy_x, enemy_y)
    else:
        draw_grid(screen, ENEMY_GRID_X, GRID_Y, None, None, None, enemy_preview_tiles)


def draw_enemy_attack_counter(screen, font, counter_image, enemy, enemy_x, enemy_y):
    counter_x = enemy_x + GRID_SIZE - 32
    counter_y = enemy_y + GRID_SIZE - 32
    screen.blit(counter_image, (counter_x, counter_y))

    counter_text = render_outlined_text(font, str(enemy["turns_until_attack"]), WHITE)
    text_rect = counter_text.get_rect(center=(counter_x + 19, counter_y + 19))
    screen.blit(counter_text, text_rect)
