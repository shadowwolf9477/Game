import pygame

from settings import GRID_SIZE
from loaders.asset_paths import asset_path
from loaders.animation_loader import load_animation_frames, load_full_strip_frames, make_flipped_frames


TINY_RPG_ROOT = (
    "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
    "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/Characters(100x100)"
)
PLAYER_SPRITE_SCALE = 1.45


def load_character_idle_frames(character):
    # Character dictionaries own their sprite metadata so party members can differ.
    idle_animation = character["idle_animation"]

    if "strip_path" in idle_animation:
        sprite_size = int(GRID_SIZE * PLAYER_SPRITE_SCALE)

        return load_full_strip_frames(
            idle_animation["strip_path"],
            idle_animation["frame_width"],
            idle_animation["frame_height"],
            (sprite_size, sprite_size),
            True
        )

    return load_animation_frames(
        idle_animation["sheet_path"],
        idle_animation["frame_width"],
        idle_animation["frame_height"],
        idle_animation["row"],
        idle_animation["frame_count"],
        (GRID_SIZE, GRID_SIZE)
    )


def load_character_battle_frames(character, animation_key):
    animation = character[animation_key]
    sprite_scale = animation.get("sprite_scale", PLAYER_SPRITE_SCALE)
    sprite_size = int(GRID_SIZE * sprite_scale)

    return load_full_strip_frames(
        animation["strip_path"],
        animation["frame_width"],
        animation["frame_height"],
        (sprite_size, sprite_size),
        True,
        animation.get("stable_normalize", False)
    )


def tiny_rpg_path(character_name, animation_name):
    return (
        TINY_RPG_ROOT + "/" + character_name + "/" + character_name + "/"
        + character_name + "-" + animation_name + ".png"
    )


def load_tiny_rpg_asset(character_name, attack_name="Attack01", scale_multiplier=1.0, death_name="Death"):
    # New enemy sheets are consistent 100x100 strips, but attacks have different frame counts.
    sprite_size = int(GRID_SIZE * scale_multiplier)
    scale_size = (sprite_size, sprite_size)

    idle_frames = load_full_strip_frames(
        tiny_rpg_path(character_name, "Idle"),
        100,
        100,
        scale_size,
        True
    )
    attack_frames = load_full_strip_frames(
        tiny_rpg_path(character_name, attack_name),
        100,
        100,
        scale_size,
        True
    )
    death_frames = load_full_strip_frames(
        tiny_rpg_path(character_name, death_name),
        100,
        100,
        scale_size,
        True
    )

    return {
        "idle_frames": idle_frames,
        "idle_frames_flipped": make_flipped_frames(idle_frames),
        "attack_frames": attack_frames,
        "attack_frames_flipped": make_flipped_frames(attack_frames),
        "death_frames": death_frames,
        "death_frames_flipped": make_flipped_frames(death_frames)
    }


def load_battle_assets():
    # Forest battle background is scaled once and reused every battle frame.
    battle_background = pygame.image.load(
        asset_path("assets/battle backgorunds/SunshineForest1-1920x1080-2badc99775dd008482c8d6c9798f4ff2.jpg")
    ).convert()
    battle_background = pygame.transform.scale(battle_background, (1200, 800))

    goblin_assets = load_tiny_rpg_asset("Orc", "Attack01", 1.45)
    orc_assets = load_tiny_rpg_asset("Armored Orc", "Attack01", 1.65)
    skeleton_assets = load_tiny_rpg_asset("Skeleton", "Attack01", 1.45)
    bone_caller_assets = load_tiny_rpg_asset("Priest", "Attack", 1.5)
    crawler_assets = load_tiny_rpg_asset("Slime", "Attack01", 1.25)
    web_priest_assets = load_tiny_rpg_asset("Wizard", "Attack01", 1.5, "DEATH")

    counter_image = pygame.image.load(asset_path("assets/timer/Counter.png")).convert_alpha()
    counter_image = pygame.transform.scale(counter_image, (38, 38))
    arrow_image = pygame.image.load(
        asset_path(
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Arrow(Projectile)/Arrow02(100x100).png"
        )
    ).convert_alpha()
    arrow_image = pygame.transform.scale(arrow_image, (42, 42))

    enemy_assets = {
        "goblin": {
            **goblin_assets
        },
        "orc": {
            **orc_assets
        },
        "skeleton": {
            **skeleton_assets
        },
        "bone_caller": {
            **bone_caller_assets
        },
        "crawler": {
            **crawler_assets
        },
        "web_priest": {
            **web_priest_assets
        },
        "counter": counter_image,
        "arrow": arrow_image
    }

    return battle_background, enemy_assets
