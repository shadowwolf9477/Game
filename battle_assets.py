from settings import GRID_SIZE
from animation_loader import load_animation_frames


def load_character_idle_frames(character):
    # Character dictionaries own their sprite metadata so party members can differ.
    idle_animation = character["idle_animation"]

    return load_animation_frames(
        idle_animation["sheet_path"],
        idle_animation["frame_width"],
        idle_animation["frame_height"],
        idle_animation["row"],
        idle_animation["frame_count"],
        (GRID_SIZE, GRID_SIZE)
    )


def load_battle_assets():
    # Satyr idle: top row, 6 frames from the satyr sheet.
    satyr_idle_frames = load_animation_frames(
        "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
        32, 32, 0, 6, (GRID_SIZE, GRID_SIZE)
    )

    # Satyr attack: fourth row, 7 frames, used during the enemy turn.
    satyr_attack_frames = load_animation_frames(
        "assests/SATYR_sprite_sheet /SPRITE_SHEET.png",
        32, 32, 3, 7, (GRID_SIZE, GRID_SIZE)
    )

    return satyr_idle_frames, satyr_attack_frames
