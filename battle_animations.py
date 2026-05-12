import pygame

from settings import (
    PLAYER_GRID_X,
    ENEMY_GRID_X,
    GRID_Y,
    GRID_SIZE,
    GRID_GAP
)


PLAYER_ATTACK_FRAME_SPEED = 4
PLAYER_DEATH_FRAME_SPEED = 9
ENEMY_DEATH_FRAME_SPEED = 8
PROJECTILE_SPEED = 0.13


def get_tile_center(board_name, row, col):
    if board_name == "enemy":
        board_x = ENEMY_GRID_X
    else:
        board_x = PLAYER_GRID_X

    x = board_x + col * (GRID_SIZE + GRID_GAP) + GRID_SIZE // 2
    y = GRID_Y + row * (GRID_SIZE + GRID_GAP) + GRID_SIZE // 2

    return x, y


def make_player_attack_animation(character):
    return {
        "character": character,
        "frame_index": 0,
        "timer": 0
    }


def update_player_attack_animation(player_attack_animation):
    if player_attack_animation is None:
        return None

    player_attack_animation["timer"] += 1

    if player_attack_animation["timer"] >= PLAYER_ATTACK_FRAME_SPEED:
        player_attack_animation["timer"] = 0
        player_attack_animation["frame_index"] += 1

    character = player_attack_animation["character"]

    if player_attack_animation["frame_index"] >= len(character["attack_frames"]):
        return None

    return player_attack_animation


def make_enemy_death_animation(enemy):
    if enemy.get("flip_x", True):
        frames = enemy["death_frames_flipped"]
    else:
        frames = enemy["death_frames"]

    return {
        "frames": frames,
        "row": enemy["row"],
        "col": enemy["col"],
        "frame_index": 0,
        "timer": 0
    }


def queue_enemy_death_animations(enemies, enemy_death_animations):
    for enemy in enemies:
        if enemy["hp"] <= 0 and not enemy.get("death_animation_queued", False):
            enemy_death_animations.append(make_enemy_death_animation(enemy))
            enemy["death_animation_queued"] = True


def update_enemy_death_animations(enemy_death_animations):
    for animation in enemy_death_animations[:]:
        animation["timer"] += 1

        if animation["timer"] >= ENEMY_DEATH_FRAME_SPEED:
            animation["timer"] = 0
            animation["frame_index"] += 1

        if animation["frame_index"] >= len(animation["frames"]):
            enemy_death_animations.remove(animation)


def draw_enemy_death_animations(screen, enemy_death_animations):
    for animation in enemy_death_animations:
        frame_index = min(animation["frame_index"], len(animation["frames"]) - 1)
        image = animation["frames"][frame_index]
        x = ENEMY_GRID_X + animation["col"] * (GRID_SIZE + GRID_GAP)
        y = GRID_Y + animation["row"] * (GRID_SIZE + GRID_GAP)
        draw_x = x - (image.get_width() - GRID_SIZE) // 2
        draw_y = y - (image.get_height() - GRID_SIZE)
        screen.blit(image, (draw_x, draw_y))


def start_player_death_animations_from_hits(hits):
    for hit in hits:
        character = hit["target"]

        if character["current_hp"] <= 0 and not character.get("death_animation_done", False):
            character["death_frame_index"] = 0
            character["death_timer"] = 0
            character["death_animation_done"] = True


def update_party_death_animations(party):
    for character in party:
        if character["current_hp"] > 0 or not character.get("death_animation_done", False):
            continue

        character["death_timer"] = character.get("death_timer", 0) + 1

        if character["death_timer"] >= PLAYER_DEATH_FRAME_SPEED:
            character["death_timer"] = 0
            max_frame_index = len(character["death_frames"]) - 1

            if character["death_frame_index"] < max_frame_index:
                character["death_frame_index"] += 1


def make_arrow_projectile(acting_character, hits, arrow_image):
    if acting_character["name"] != "Archer" or not hits:
        return None

    first_target = hits[0]["target"]
    start_x, start_y = get_tile_center("player", acting_character["row"], acting_character["col"])
    end_x, end_y = get_tile_center("enemy", first_target["row"], first_target["col"])

    return {
        "image": arrow_image,
        "start": (start_x, start_y),
        "end": (end_x, end_y),
        "progress": 0
    }


def update_projectile_animations(projectile_animations):
    for projectile in projectile_animations[:]:
        projectile["progress"] += PROJECTILE_SPEED

        if projectile["progress"] >= 1:
            projectile_animations.remove(projectile)


def draw_projectile_animations(screen, projectile_animations):
    for projectile in projectile_animations:
        progress = projectile["progress"]
        start_x, start_y = projectile["start"]
        end_x, end_y = projectile["end"]
        draw_x = start_x + (end_x - start_x) * progress
        draw_y = start_y + (end_y - start_y) * progress
        image = projectile["image"]
        image_rect = image.get_rect(center=(draw_x, draw_y))
        screen.blit(image, image_rect)
