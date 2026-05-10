from game_state import PLAYER_TURN, GAME_OVER
from battle_setup import clear_incoming_attacks, resolve_incoming_attacks, move_enemy_random, choose_goblin_attack


def finish_enemy_attack(selected_character, player_row, player_col, player_grid_data, enemy_grid_data, enemies):
    # This runs once after the attack animation, so damage matches the visual hit.
    resolve_incoming_attacks(selected_character, player_row, player_col, player_grid_data)

    if selected_character["current_hp"] <= 0:
        # Return a requested screen change instead of changing main.py globals here.
        return GAME_OVER, None

    clear_incoming_attacks(player_grid_data)

    if enemies:
        # Current prototype moves only the first enemy.
        first_enemy = enemies[0]
        move_enemy_random(first_enemy, enemy_grid_data)

    # After enemy actions, preview the next enemy attack pattern.
    choose_goblin_attack(player_grid_data)

    return None, PLAYER_TURN
