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


def draw_battle(
    screen,
    font,
    end_turn_button,
    selected_character,
    player_row,
    player_col,
    player_grid_data,
    enemies,
    player_image,
    satyr_image
):
    # Draw the basic battle UI.
    battle_text = font.render("Battle", True, WHITE)
    screen.blit(battle_text, (BATTLE_TITLE_X, BATTLE_TITLE_Y))

    end_turn_button.draw(screen, font)

    hp_text = font.render(
        "HP: " + str(selected_character["current_hp"]) + "/" + str(selected_character["max_hp"]),
        True,
        WHITE
    )
    screen.blit(hp_text, (HP_X, HP_Y))

    # Player side grid and player sprite.
    draw_grid(screen, PLAYER_GRID_X, GRID_Y, player_row, player_col, player_grid_data)

    player_x = PLAYER_GRID_X + player_col * (GRID_SIZE + GRID_GAP)
    player_y = GRID_Y + player_row * (GRID_SIZE + GRID_GAP)
    screen.blit(player_image, (player_x, player_y))

    # Enemy side grid and first enemy sprite.
    if enemies:
        first_enemy = enemies[0]
        draw_grid(screen, ENEMY_GRID_X, GRID_Y, first_enemy["row"], first_enemy["col"])

        enemy_x = ENEMY_GRID_X + first_enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = GRID_Y + first_enemy["row"] * (GRID_SIZE + GRID_GAP)
        screen.blit(satyr_image, (enemy_x, enemy_y))
    else:
        draw_grid(screen, ENEMY_GRID_X, GRID_Y)
