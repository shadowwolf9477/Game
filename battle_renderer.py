
from settings import WHITE, GRID_SIZE, GRID_GAP
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
    battle_text = font.render("Battle", True, WHITE)
    screen.blit(battle_text, (340, 100))

    end_turn_button.draw(screen, font)

    hp_text = font.render(
        "HP: " + str(selected_character["current_hp"]) + "/" + str(selected_character["max_hp"]),
        True,
        WHITE
    )
    screen.blit(hp_text, (60, 160))

    draw_grid(screen, 60, 220, player_row, player_col, player_grid_data)

    player_x = 60 + player_col * (GRID_SIZE + GRID_GAP)
    player_y = 220 + player_row * (GRID_SIZE + GRID_GAP)
    screen.blit(player_image, (player_x, player_y))

    if enemies:
        first_enemy = enemies[0]
        draw_grid(screen, 420, 220, first_enemy["row"], first_enemy["col"])

        enemy_x = 420 + first_enemy["col"] * (GRID_SIZE + GRID_GAP)
        enemy_y = 220 + first_enemy["row"] * (GRID_SIZE + GRID_GAP)
        screen.blit(satyr_image, (enemy_x, enemy_y))
    else:
        draw_grid(screen, 420, 220)
