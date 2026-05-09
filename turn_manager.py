from game_state import PLAYER_TURN, ENEMY_TURN
from battle_setup import clear_incoming_attacks, resolve_incoming_attacks, move_enemy_random, choose_goblin_attack


def run_enemy_turn(enemies, selected_character, player_row, player_col, player_grid_data, enemy_grid_data):
    if enemies:
        first_enemy = enemies[0]
        resolve_incoming_attacks(selected_character, player_row, player_col, player_grid_data)
        clear_incoming_attacks(player_grid_data)
        move_enemy_random(first_enemy, enemy_grid_data)
        choose_goblin_attack(player_grid_data)

    return PLAYER_TURN
