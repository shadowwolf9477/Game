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
    satyr_image,
    player_preview_tiles,
    enemy_preview_tiles
):
    # Draw battle title, controls, and player resources.
    battle_text = font.render("Battle", True, WHITE)
    screen.blit(battle_text, (BATTLE_TITLE_X, BATTLE_TITLE_Y))

    end_turn_button.draw(screen, font)
    play_card_button.draw(screen, font)

    for index, character in enumerate(party):
        hp_text = font.render(
            character["name"] + " HP: " + str(character["current_hp"]) + "/" + str(character["max_hp"]),
            True,
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
        player_image = character["idle_frames"][player_idle_frame_index % len(character["idle_frames"])]

        if character.get("flip_x"):
            player_image = pygame.transform.flip(player_image, True, False)

        screen.blit(player_image, (player_x, player_y))

    # Enemy side currently renders the first enemy only.
    # This will need a loop when multi-enemy battles are added.
    if enemies:
        first_enemy = enemies[0]

        draw_grid(
            screen,
            ENEMY_GRID_X,
            GRID_Y,
            first_enemy["row"],
            first_enemy["col"],
            None,
            enemy_preview_tiles
        )

        enemy_x = ENEMY_GRID_X + first_enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = GRID_Y + first_enemy["row"] * (GRID_SIZE + GRID_GAP)

        enemy_hp_text = font.render("HP: " + str(first_enemy["hp"]), True, WHITE)
        screen.blit(enemy_hp_text, (enemy_x, enemy_y - 45))

        screen.blit(satyr_image, (enemy_x, enemy_y))
    else:
        draw_grid(screen, ENEMY_GRID_X, GRID_Y, None, None, None, enemy_preview_tiles)
