from cards.card_effects import damage_enemy
from settings import GRID_ROWS, GRID_COLS


TEAM_SPECIAL_MAX_CHARGE = 200
TEAM_SPECIAL_DAMAGE_CHARGE_CAP = 8
TEAM_SPECIAL_KILL_CHARGE = 10
CROSSFIRE_ROW_COLUMN_DAMAGE = 15
CROSSFIRE_CENTER_DAMAGE = 45


def get_crossfire_tiles(center_row, center_col):
    tiles = []

    for col in range(GRID_COLS):
        tiles.append((center_row, col))

    for row in range(GRID_ROWS):
        tile = (row, center_col)

        if tile not in tiles:
            tiles.append(tile)

    return tiles


def get_charge_from_hits(hits):
    total_damage = 0
    defeated_count = 0

    for hit in hits:
        total_damage += hit.get("damage", 0)

        if hit["target"]["hp"] <= 0:
            defeated_count += 1

    damage_charge = min(total_damage, TEAM_SPECIAL_DAMAGE_CHARGE_CAP)
    kill_charge = defeated_count * TEAM_SPECIAL_KILL_CHARGE

    return damage_charge + kill_charge


def add_team_special_charge(current_charge, gained_charge):
    next_charge = current_charge + gained_charge

    if next_charge > TEAM_SPECIAL_MAX_CHARGE:
        return TEAM_SPECIAL_MAX_CHARGE

    return next_charge


def team_special_is_ready(current_charge):
    return current_charge >= TEAM_SPECIAL_MAX_CHARGE


def play_crossfire_cleave(enemies, center_row, center_col):
    hits = []
    target_tiles = get_crossfire_tiles(center_row, center_col)

    for enemy in enemies:
        enemy_tile = (enemy["row"], enemy["col"])

        if enemy_tile not in target_tiles:
            continue

        damage = CROSSFIRE_ROW_COLUMN_DAMAGE

        if enemy_tile == (center_row, center_col):
            damage = CROSSFIRE_CENTER_DAMAGE

        damage_enemy(enemy, damage, hits)

    return {
        "hits": hits
    }
