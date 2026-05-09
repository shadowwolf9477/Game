from settings import GRID_SIZE
from animation_loader import load_animation_frames


def load_battle_assets():
    player_idle_frames = load_animation_frames(
        "assests/Eris Esra's Character Template 4.1/16x32/16x32 Idle-Sheet.png",
        32,
        32,
        1,
        4,
        (GRID_SIZE, GRID_SIZE)
    )

    satyr_idle_frames = load_animation_frames(
        "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
        32,
        32,
        0,
        6,
        (GRID_SIZE, GRID_SIZE)
    )

    satyr_attack_frames = load_animation_frames(
        "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
        32,
        32,
        3,
        7,
        (GRID_SIZE, GRID_SIZE)
    )

    return player_idle_frames, satyr_idle_frames, satyr_attack_frames
