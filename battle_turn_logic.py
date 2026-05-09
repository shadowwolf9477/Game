from game_state import PLAYER_TURN, GAME_OVER
from battle_setup import clear_incoming_attacks, resolve_incoming_attacks, move_enemy_random, choose_goblin_attack


def finish_enemy_attack(selected_character, player_row, player_col, player_grid_data, enemy_grid_data, enemies):
    # This runs once after the enemy attack animation finishes.
    resolve_incoming_attacks(selected_character, player_row, player_col, player_grid_data)

    if selected_character["current_hp"] <= 0:
        return GAME_OVER, None

    clear_incoming_attacks(player_grid_data)

    if enemies:
        first_enemy = enemies[0]
        move_enemy_random(first_enemy, enemy_grid_data)

    choose_goblin_attack(player_grid_data)

    return None, PLAYER_TURN
