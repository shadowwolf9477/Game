import random

import pygame

from loaders.asset_paths import asset_path


def load_sound(path, volume=0.55):
    try:
        sound = pygame.mixer.Sound(asset_path(path))
        sound.set_volume(volume)
        return sound
    except pygame.error:
        return None


def load_battle_sounds():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error:
        return {
            "archer_attack": [],
            "warrior_attack": []
        }

    archer_attack = load_sound(
        "assets/sound effects/dennish18-arrow-body-impact-146419.mp3",
        0.5
    )
    warrior_attacks = []

    for sound_index in range(1, 5):
        sound = load_sound(
            "assets/sound effects/POL-metal-slams/POL-metal-slam-0" + str(sound_index) + ".wav",
            0.45
        )

        if sound is not None:
            warrior_attacks.append(sound)

    sounds = {
        "archer_attack": [],
        "warrior_attack": warrior_attacks
    }

    if archer_attack is not None:
        sounds["archer_attack"].append(archer_attack)

    return sounds


def play_character_attack_sound(battle_sounds, character):
    if character is None:
        return

    sound_key = "warrior_attack"

    if character["name"] == "Archer":
        sound_key = "archer_attack"

    possible_sounds = battle_sounds.get(sound_key, [])

    if possible_sounds:
        random.choice(possible_sounds).play()
