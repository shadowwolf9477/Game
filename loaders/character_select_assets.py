import pygame

from loaders.asset_paths import asset_path
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from Characters.archer import archer
from Characters.warrior import warrior
from loaders.battle_assets import load_character_idle_frames

def load_character_select_assets():
    table_image = pygame.image.load(
        asset_path("assets/cahrcter selcet screen assets/Table.jpg")
    ).convert()

    table_image = pygame.transform.scale(
        table_image,
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    parchment_image = pygame.image.load(
        asset_path("assets/cahrcter selcet screen assets/Parchment.png")
    ).convert_alpha()

    parchment_image = pygame.transform.rotate(parchment_image, -90)

    parchment_image = pygame.transform.smoothscale(
        parchment_image,
        (500, 700)
    )

    archer_selected = pygame.image.load(
        asset_path("assets/cahrcter selcet screen assets/Archer_selected.png")
    ).convert_alpha()
    warrior_selected = pygame.image.load(
        asset_path("assets/cahrcter selcet screen assets/Warrior_selected.webp")
    ).convert_alpha()
    archer_idle_frames = load_character_idle_frames(archer)
    warrior_idle_frames = load_character_idle_frames(warrior)
    return {
        "table": table_image,
        "parchment": parchment_image,
        "archer_selected": archer_selected,
        "warrior_selected" : warrior_selected,
        "archer_idle_frames": archer_idle_frames,
        "warrior_idle_frames": warrior_idle_frames

    }

def get_selected_art_key(character_name):
    if character_name == "Archer":
        return "archer_selected"

    if character_name == "Warrior":
        return "warrior_selected"

    return None
