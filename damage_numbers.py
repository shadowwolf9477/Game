import pygame

from loaders.asset_paths import asset_path


DAMAGE_NUMBER_CACHE = {}
DIGIT_WIDTH = 24
DIGIT_HEIGHT = 32
ORANGE_ROW = 2


def get_damage_digit_images():
    if "digits" not in DAMAGE_NUMBER_CACHE:
        sheet = pygame.image.load(asset_path("assets/damage numbers/persona dmg.png")).convert_alpha()
        digit_rows = []

        for row in range(4):
            digits = []

            for digit in range(10):
                digit_rect = pygame.Rect(digit * DIGIT_WIDTH, row * DIGIT_HEIGHT, DIGIT_WIDTH, DIGIT_HEIGHT)
                digits.append(sheet.subsurface(digit_rect).copy())

            digit_rows.append(digits)

        DAMAGE_NUMBER_CACHE["digits"] = digit_rows

    return DAMAGE_NUMBER_CACHE["digits"]


def build_damage_number_image(damage, color_row=ORANGE_ROW):
    cache_key = (damage, color_row)

    if cache_key in DAMAGE_NUMBER_CACHE:
        return DAMAGE_NUMBER_CACHE[cache_key]

    digits = get_damage_digit_images()[color_row]
    damage_text = str(max(0, damage))
    number_image = pygame.Surface((len(damage_text) * DIGIT_WIDTH, DIGIT_HEIGHT), pygame.SRCALPHA)

    for index, digit_character in enumerate(damage_text):
        digit_image = digits[int(digit_character)]
        number_image.blit(digit_image, (index * DIGIT_WIDTH, 0))

    DAMAGE_NUMBER_CACHE[cache_key] = number_image

    return number_image


def make_damage_popup(damage, x, y):
    return {
        "damage": damage,
        "x": x,
        "y": y,
        "timer": 0,
        "duration": 38
    }


def update_damage_popups(damage_popups):
    active_popups = []

    for popup in damage_popups:
        popup["timer"] += 1

        if popup["timer"] < popup["duration"]:
            active_popups.append(popup)

    damage_popups[:] = active_popups


def draw_damage_popups(screen, damage_popups):
    for popup in damage_popups:
        number_image = build_damage_number_image(popup["damage"])
        progress = popup["timer"] / popup["duration"]

        if progress < 0.25:
            scale = 0.7 + progress * 2.4
        else:
            scale = 1.3 - (progress - 0.25) * 0.45

        alpha = 255

        if progress > 0.65:
            alpha = int(255 * (1 - progress) / 0.35)

        width = max(1, int(number_image.get_width() * scale))
        height = max(1, int(number_image.get_height() * scale))
        scaled_image = pygame.transform.scale(number_image, (width, height))
        scaled_image.set_alpha(max(0, min(255, alpha)))

        draw_x = popup["x"] - width // 2
        draw_y = popup["y"] - int(popup["timer"] * 1.3) - height // 2
        screen.blit(scaled_image, (draw_x, draw_y))
