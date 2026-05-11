from state.game_state import PLAYER_TURN, GAME_OVER
from battle_setup import move_enemy_random, move_orc_like_knight, prepare_enemy_attacks


def finish_enemy_attack(party, player_grid_data, enemy_grid_data, enemies):
    if all(character["current_hp"] <= 0 for character in party):
        # Return a requested screen change instead of changing main.py globals here.
        return GAME_OVER, None

    for enemy in enemies:
        enemy_attacked = enemy["turns_until_attack"] <= 1

        if enemy["turns_until_attack"] <= 1:
            enemy["turns_until_attack"] = enemy["attack_interval"]
        else:
            enemy["turns_until_attack"] -= 1

        if enemy["type"] == "orc":
            if enemy_attacked:
                move_orc_like_knight(enemy, enemy_grid_data)
        else:
            move_enemy_random(enemy, enemy_grid_data)

    # After enemy actions, preview the next enemy attack pattern.
    prepare_enemy_attacks(enemies, player_grid_data)

    return None, PLAYER_TURN


def get_next_attacking_enemy_index(enemies, current_index):
    for index in range(current_index + 1, len(enemies)):
        if enemies[index]["turns_until_attack"] <= 1:
            return index

    return None
