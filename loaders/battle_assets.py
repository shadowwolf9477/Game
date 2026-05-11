import pygame

from settings import GRID_SIZE
from loaders.animation_loader import load_animation_frames, load_strip_frames, make_flipped_frames


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
    # Forest battle background is scaled once and reused every battle frame.
    battle_background = pygame.image.load(
        "assests/battle backgorunds/SunshineForest1-1920x1080-2badc99775dd008482c8d6c9798f4ff2.jpg"
    ).convert()
    battle_background = pygame.transform.scale(battle_background, (1200, 800))

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

    orc_size = int(GRID_SIZE * 1.35)

    orc_idle_frames = load_strip_frames(
        "assests/Knight/noBKG_KnightIdle_strip.png",
        64, 64, 15, (orc_size, orc_size), True
    )

    orc_attack_frames = load_strip_frames(
        "assests/Knight/noBKG_KnightAttack_strip.png",
        96, 64, 33, (orc_size, orc_size), True, [6, 8, 9, 11, 12]
    )

    counter_image = pygame.image.load("assests/timer/Counter.png").convert_alpha()
    counter_image = pygame.transform.scale(counter_image, (38, 38))

    enemy_assets = {
        "goblin": {
            "idle_frames": satyr_idle_frames,
            "idle_frames_flipped": make_flipped_frames(satyr_idle_frames),
            "attack_frames": satyr_attack_frames,
            "attack_frames_flipped": make_flipped_frames(satyr_attack_frames)
        },
        "orc": {
            "idle_frames": orc_idle_frames,
            "idle_frames_flipped": make_flipped_frames(orc_idle_frames),
            "attack_frames": orc_attack_frames,
            "attack_frames_flipped": make_flipped_frames(orc_attack_frames)
        },
        "counter": counter_image
    }

    return battle_background, enemy_assets
