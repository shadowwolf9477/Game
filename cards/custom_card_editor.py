import copy
import json
import os
import pygame

pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 920
FPS = 60

GRID_ROWS = 3
GRID_COLS = 5
TILE_SIZE = 82

CUSTOM_CARD_FOLDER = os.path.join("cards", "custom_cards")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (80, 80, 80)
GREEN = (50, 165, 130)
LIGHT_GREEN = (100, 220, 180)
BLUE = (90, 150, 255)
RED = (230, 80, 80)
YELLOW = (240, 210, 80)
PURPLE = (170, 100, 230)
ORANGE = (240, 150, 60)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Custom Card Maker")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 27)
big_font = pygame.font.SysFont(None, 44)
small_font = pygame.font.SysFont(None, 21)


def draw_text(surface, text, x, y, color=BLACK, font_obj=font):
    img = font_obj.render(str(text), True, color)
    surface.blit(img, (x, y))


def draw_wrapped_text(surface, text, x, y, max_chars, color=BLACK, font_obj=small_font, line_height=20):
    words = text.split(" ")
    line = ""

    for word in words:
        test_line = line + word + " "

        if len(test_line) > max_chars:
            draw_text(surface, line, x, y, color, font_obj)
            y += line_height
            line = word + " "
        else:
            line = test_line

    if line:
        draw_text(surface, line, x, y, color, font_obj)


class TextBox:
    def __init__(self, x, y, w, h, text="", label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.label = label
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode

    def draw(self, surface):
        if self.label:
            draw_text(surface, self.label, self.rect.x, self.rect.y - 22, BLACK, small_font)

        border_color = BLUE if self.active else DARK_GRAY
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 3)

        shown_text = self.text[-48:]
        draw_text(surface, shown_text, self.rect.x + 8, self.rect.y + 8, BLACK, small_font)


class Button:
    def __init__(self, x, y, w, h, text, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        draw_text(surface, self.text, self.rect.x + 8, self.rect.y + 9, BLACK, small_font)


def safe_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default


def safe_float(text, default=0.0):
    try:
        return float(text)
    except ValueError:
        return default


def number_to_text(value, default="0"):
    if value is None:
        return default

    return str(value)


card_name_box = TextBox(40, 80, 430, 42, "New Card", "Card Name")
card_id_box = TextBox(40, 150, 430, 42, "new_card", "Card ID / file name")

cost_box = TextBox(40, 220, 130, 38, "1", "Cost")
thickness_box = TextBox(190, 220, 130, 38, "0.5", "Thickness")
rarity_box = TextBox(340, 220, 130, 38, "common", "Rarity")

image_path_box = TextBox(
    40,
    285,
    580,
    38,
    "assets/card_templtes/card art/example.png",
    "Image Path"
)

damage_box = TextBox(40, 370, 130, 38, "0", "Damage")
block_box = TextBox(190, 370, 130, 38, "0", "Block")
draw_box = TextBox(340, 370, 130, 38, "0", "Draw")
discard_box = TextBox(490, 370, 130, 38, "0", "Discard")

move_distance_box = TextBox(40, 445, 130, 38, "1", "Move / Charge")
shove_distance_box = TextBox(190, 445, 130, 38, "1", "Shove Tiles")
trap_duration_box = TextBox(340, 445, 130, 38, "3", "Trap Turns")
trap_radius_box = TextBox(490, 445, 130, 38, "1", "Trap Radius")

description_box = TextBox(
    40,
    835,
    700,
    42,
    "Deal {damage} damage. Gain {block} block.",
    "Description"
)

always_text_boxes = [
    card_name_box,
    card_id_box,
    cost_box,
    thickness_box,
    rarity_box,
    image_path_box,
    description_box,
]

stat_boxes = {
    "damage": damage_box,
    "block": block_box,
    "draw": draw_box,
    "discard": discard_box,
    "move_distance": move_distance_box,
    "shove_distance": shove_distance_box,
    "trap_duration": trap_duration_box,
    "trap_radius": trap_radius_box,
}

usable_characters = {
    "Archer": True,
    "Warrior": False,
}

selected_tiles = set()
player_tile = (1, 0)
effect_order = []

move_direction = "any"
trap_snares = False

per_character_enabled = False
current_variant_character = "Archer"

character_values = {
    "Archer": {
        "damage": "2",
        "block": "0",
        "draw": "0",
        "discard": "0",
        "move_distance": "1",
        "shove_distance": "2",
        "trap_duration": "3",
        "trap_radius": "1",
    },
    "Warrior": {
        "damage": "5",
        "block": "0",
        "draw": "0",
        "discard": "0",
        "move_distance": "1",
        "shove_distance": "3",
        "trap_duration": "3",
        "trap_radius": "1",
    }
}

saved_card_files = []
selected_saved_card_index = 0
loaded_card_message = "No card loaded."

character_buttons = {
    "Archer": Button(40, 520, 130, 38, "Archer", LIGHT_GREEN),
    "Warrior": Button(190, 520, 130, 38, "Warrior", GRAY),
}

per_character_button = Button(340, 520, 180, 38, "Per Character: No", GRAY)
variant_archer_button = Button(530, 520, 130, 35, "Edit Archer", LIGHT_GREEN)
variant_warrior_button = Button(670, 520, 130, 35, "Edit Warrior", GRAY)

direction_buttons = {
    "any": Button(40, 605, 90, 35, "Any", LIGHT_GREEN),
    "forward": Button(140, 605, 90, 35, "Forward", GRAY),
    "back": Button(240, 605, 90, 35, "Back", GRAY),
    "up": Button(340, 605, 90, 35, "Up", GRAY),
    "down": Button(440, 605, 90, 35, "Down", GRAY),
}

trap_snare_button = Button(540, 605, 180, 35, "Trap Snare: No", GRAY)

effect_buttons = [
    Button(800, 500, 160, 35, "Add Damage", RED),
    Button(970, 500, 160, 35, "Add Block", BLUE),
    Button(1140, 500, 160, 35, "Add Draw", YELLOW),

    Button(800, 545, 160, 35, "Add Discard", ORANGE),
    Button(970, 545, 160, 35, "Add Move", LIGHT_GREEN),
    Button(1140, 545, 160, 35, "Add Charge", GREEN),

    Button(800, 590, 160, 35, "Add Shove", BLUE),
    Button(970, 590, 160, 35, "Add Trap", PURPLE),
]

save_button = Button(40, 885, 180, 30, "Save Card", LIGHT_GREEN)
clear_effects_button = Button(230, 885, 180, 30, "Clear Effects", RED)

prev_saved_button = Button(515, 85, 38, 32, "<", GRAY)
next_saved_button = Button(558, 85, 38, 32, ">", GRAY)
load_saved_button = Button(605, 85, 100, 32, "Load Card", LIGHT_GREEN)
new_card_button = Button(710, 85, 95, 32, "New Card", YELLOW)
refresh_saved_button = Button(515, 125, 120, 32, "Refresh", GRAY)


def refresh_saved_card_files():
    global saved_card_files
    global selected_saved_card_index

    os.makedirs(CUSTOM_CARD_FOLDER, exist_ok=True)
    saved_card_files = []

    for file_name in os.listdir(CUSTOM_CARD_FOLDER):
        if file_name.endswith(".json"):
            saved_card_files.append(file_name)

    saved_card_files.sort()

    if selected_saved_card_index >= len(saved_card_files):
        selected_saved_card_index = max(0, len(saved_card_files) - 1)


def get_selected_saved_card_file_name():
    if not saved_card_files:
        return "No saved cards"

    return saved_card_files[selected_saved_card_index]


def card_uses_stat(stat_name):
    for effect in effect_order:
        effect_type = effect.get("type")

        if stat_name == "damage" and effect_type in ["damage", "place_trap"]:
            return True

        if stat_name == "block" and effect_type == "gain_block":
            return True

        if stat_name == "draw" and effect_type == "draw_cards":
            return True

        if stat_name == "discard" and effect_type == "discard_cards":
            return True

        if stat_name == "move_distance" and effect_type in ["move_character", "charge_character"]:
            return True

        if stat_name == "shove_distance" and effect_type == "shove":
            return True

        if stat_name == "trap_duration" and effect_type == "place_trap":
            return True

        if stat_name == "trap_radius" and effect_type == "place_trap":
            return True

    return False


def get_visible_stat_boxes():
    visible = []

    for stat_name, box in stat_boxes.items():
        if card_uses_stat(stat_name):
            visible.append(box)

    return visible


def get_all_visible_text_boxes():
    return always_text_boxes + get_visible_stat_boxes()


def save_current_variant_values():
    if not per_character_enabled:
        return

    character_values[current_variant_character] = {
        "damage": damage_box.text,
        "block": block_box.text,
        "draw": draw_box.text,
        "discard": discard_box.text,
        "move_distance": move_distance_box.text,
        "shove_distance": shove_distance_box.text,
        "trap_duration": trap_duration_box.text,
        "trap_radius": trap_radius_box.text,
    }


def load_variant_values(character_name):
    values = character_values[character_name]

    damage_box.text = values["damage"]
    block_box.text = values["block"]
    draw_box.text = values["draw"]
    discard_box.text = values["discard"]
    move_distance_box.text = values["move_distance"]
    shove_distance_box.text = values["shove_distance"]
    trap_duration_box.text = values["trap_duration"]
    trap_radius_box.text = values["trap_radius"]


def switch_variant_character(character_name):
    global current_variant_character

    save_current_variant_values()
    current_variant_character = character_name
    load_variant_values(character_name)


def make_card_preview_description(card_data):
    description = card_data["description"]

    replacements = {
        "{damage}": str(card_data.get("damage", 0)),
        "{block}": str(card_data.get("block", 0)),
        "{draw}": str(card_data.get("draw", 0)),
        "{discard}": str(card_data.get("discard", 0)),
        "{range}": str(len(card_data.get("target_tiles", []))),
        "{move_distance}": str(card_data.get("move_distance", 0)),
        "{shove_distance}": str(card_data.get("shove_distance", 0)),
        "{trap_duration}": str(card_data.get("trap_duration", 0)),
        "{trap_radius}": str(card_data.get("trap_radius", 0)),
    }

    for key, value in replacements.items():
        description = description.replace(key, value)

    return description


def get_number_values_from_text_values(text_values):
    return {
        "damage": safe_int(text_values["damage"], 0),
        "block": safe_int(text_values["block"], 0),
        "draw": safe_int(text_values["draw"], 0),
        "discard": safe_int(text_values["discard"], 0),
        "move_distance": safe_int(text_values["move_distance"], 1),
        "shove_distance": safe_int(text_values["shove_distance"], 1),
        "trap_duration": safe_int(text_values["trap_duration"], 3),
        "trap_radius": safe_int(text_values["trap_radius"], 1),
    }


def build_character_values_for_save():
    save_current_variant_values()

    saved_values = {}

    for character_name, enabled in usable_characters.items():
        if not enabled:
            continue

        saved_values[character_name] = get_number_values_from_text_values(character_values[character_name])

    return saved_values


def build_card_data():
    card_data = {
        "id": card_id_box.text.strip(),
        "name": card_name_box.text.strip(),
        "cost": safe_int(cost_box.text, 1),
        "thickness": safe_float(thickness_box.text, 0.5),
        "type": "attack",
        "rarity": rarity_box.text.strip(),
        "image_path": image_path_box.text.strip(),

        "damage": safe_int(damage_box.text, 0) if card_uses_stat("damage") else 0,
        "block": safe_int(block_box.text, 0) if card_uses_stat("block") else 0,
        "draw": safe_int(draw_box.text, 0) if card_uses_stat("draw") else 0,
        "discard": safe_int(discard_box.text, 0) if card_uses_stat("discard") else 0,
        "move_distance": safe_int(move_distance_box.text, 1) if card_uses_stat("move_distance") else 0,
        "shove_distance": safe_int(shove_distance_box.text, 1) if card_uses_stat("shove_distance") else 0,
        "trap_duration": safe_int(trap_duration_box.text, 3) if card_uses_stat("trap_duration") else 0,
        "trap_radius": safe_int(trap_radius_box.text, 1) if card_uses_stat("trap_radius") else 0,

        "description": description_box.text,

        "usable_characters": [
            name for name, enabled in usable_characters.items()
            if enabled
        ],

        "player_preview_tile": {
            "row": player_tile[0],
            "col": player_tile[1],
        },

        "target_tiles": [
            {"row": row, "col": col}
            for row, col in sorted(selected_tiles)
        ],

        "effects": effect_order,
    }

    if per_character_enabled:
        card_data["character_values"] = build_character_values_for_save()

    card_data["preview_description"] = make_card_preview_description(card_data)
    return card_data


def save_card():
    global loaded_card_message

    save_current_variant_values()
    os.makedirs(CUSTOM_CARD_FOLDER, exist_ok=True)

    card_data = build_card_data()
    card_id = card_data["id"]

    if not card_id:
        loaded_card_message = "Card needs an ID."
        return

    file_path = os.path.join(CUSTOM_CARD_FOLDER, card_id + ".json")

    with open(file_path, "w") as file:
        json.dump(card_data, file, indent=4)

    loaded_card_message = "Saved: " + card_id + ".json"
    refresh_saved_card_files()


def reset_editor_to_new_card():
    global selected_tiles, player_tile, effect_order
    global move_direction, trap_snares, per_character_enabled
    global current_variant_character, character_values, loaded_card_message

    card_name_box.text = "New Card"
    card_id_box.text = "new_card"
    cost_box.text = "1"
    thickness_box.text = "0.5"
    rarity_box.text = "common"
    image_path_box.text = "assets/card_templtes/card art/example.png"

    damage_box.text = "0"
    block_box.text = "0"
    draw_box.text = "0"
    discard_box.text = "0"
    move_distance_box.text = "1"
    shove_distance_box.text = "1"
    trap_duration_box.text = "3"
    trap_radius_box.text = "1"

    description_box.text = "Deal {damage} damage. Gain {block} block."

    usable_characters["Archer"] = True
    usable_characters["Warrior"] = False

    selected_tiles = set()
    player_tile = (1, 0)
    effect_order = []

    move_direction = "any"
    trap_snares = False
    per_character_enabled = False
    current_variant_character = "Archer"

    character_values = {
        "Archer": {
            "damage": "2",
            "block": "0",
            "draw": "0",
            "discard": "0",
            "move_distance": "1",
            "shove_distance": "2",
            "trap_duration": "3",
            "trap_radius": "1",
        },
        "Warrior": {
            "damage": "5",
            "block": "0",
            "draw": "0",
            "discard": "0",
            "move_distance": "1",
            "shove_distance": "3",
            "trap_duration": "3",
            "trap_radius": "1",
        }
    }

    loaded_card_message = "Started new card."


def load_card_into_editor(card_data, file_name):
    global selected_tiles, player_tile, effect_order
    global move_direction, trap_snares, per_character_enabled
    global current_variant_character, character_values, loaded_card_message

    card_name_box.text = card_data.get("name", "New Card")
    card_id_box.text = card_data.get("id", file_name.replace(".json", ""))

    cost_box.text = number_to_text(card_data.get("cost", 1), "1")
    thickness_box.text = number_to_text(card_data.get("thickness", 0.5), "0.5")
    rarity_box.text = card_data.get("rarity", "common")
    image_path_box.text = card_data.get("image_path", "assets/card_templtes/card art/example.png")

    damage_box.text = number_to_text(card_data.get("damage", 0))
    block_box.text = number_to_text(card_data.get("block", 0))
    draw_box.text = number_to_text(card_data.get("draw", 0))
    discard_box.text = number_to_text(card_data.get("discard", 0))
    move_distance_box.text = number_to_text(card_data.get("move_distance", 1), "1")
    shove_distance_box.text = number_to_text(card_data.get("shove_distance", 1), "1")
    trap_duration_box.text = number_to_text(card_data.get("trap_duration", 3), "3")
    trap_radius_box.text = number_to_text(card_data.get("trap_radius", 1), "1")

    description_box.text = card_data.get("description", "")

    usable = card_data.get("usable_characters", ["Archer"])
    usable_characters["Archer"] = "Archer" in usable
    usable_characters["Warrior"] = "Warrior" in usable

    preview_tile = card_data.get("player_preview_tile", {"row": 1, "col": 0})
    player_tile = (int(preview_tile.get("row", 1)), int(preview_tile.get("col", 0)))

    selected_tiles = set()
    for tile in card_data.get("target_tiles", []):
        selected_tiles.add((int(tile.get("row", 0)), int(tile.get("col", 0))))

    effect_order = copy.deepcopy(card_data.get("effects", []))

    move_direction = "any"
    trap_snares = False

    for effect in effect_order:
        if "direction" in effect:
            move_direction = effect["direction"]

        if effect.get("type") == "place_trap":
            trap_snares = effect.get("snare_until_gone", False)

    per_character_enabled = "character_values" in card_data
    current_variant_character = "Archer"

    character_values = {
        "Archer": {
            "damage": damage_box.text,
            "block": block_box.text,
            "draw": draw_box.text,
            "discard": discard_box.text,
            "move_distance": move_distance_box.text,
            "shove_distance": shove_distance_box.text,
            "trap_duration": trap_duration_box.text,
            "trap_radius": trap_radius_box.text,
        },
        "Warrior": {
            "damage": damage_box.text,
            "block": block_box.text,
            "draw": draw_box.text,
            "discard": discard_box.text,
            "move_distance": move_distance_box.text,
            "shove_distance": shove_distance_box.text,
            "trap_duration": trap_duration_box.text,
            "trap_radius": trap_radius_box.text,
        }
    }

    if per_character_enabled:
        saved_character_values = card_data.get("character_values", {})

        for character_name in ["Archer", "Warrior"]:
            if character_name in saved_character_values:
                values = saved_character_values[character_name]
                character_values[character_name] = {
                    "damage": number_to_text(values.get("damage", 0)),
                    "block": number_to_text(values.get("block", 0)),
                    "draw": number_to_text(values.get("draw", 0)),
                    "discard": number_to_text(values.get("discard", 0)),
                    "move_distance": number_to_text(values.get("move_distance", 1), "1"),
                    "shove_distance": number_to_text(values.get("shove_distance", 1), "1"),
                    "trap_duration": number_to_text(values.get("trap_duration", 3), "3"),
                    "trap_radius": number_to_text(values.get("trap_radius", 1), "1"),
                }

        if usable_characters.get("Archer", False):
            current_variant_character = "Archer"
        elif usable_characters.get("Warrior", False):
            current_variant_character = "Warrior"

        load_variant_values(current_variant_character)

    loaded_card_message = "Loaded: " + file_name


def load_selected_saved_card():
    global loaded_card_message

    if not saved_card_files:
        loaded_card_message = "No saved cards."
        return

    file_name = saved_card_files[selected_saved_card_index]
    file_path = os.path.join(CUSTOM_CARD_FOLDER, file_name)

    try:
        with open(file_path, "r") as file:
            card_data = json.load(file)

        load_card_into_editor(card_data, file_name)

    except Exception as error:
        loaded_card_message = "Load failed: " + str(error)


def draw_saved_card_loader(surface):
    loader_rect = pygame.Rect(500, 35, 320, 150)
    pygame.draw.rect(surface, WHITE, loader_rect)
    pygame.draw.rect(surface, BLACK, loader_rect, 2)

    draw_text(surface, "Saved Cards", loader_rect.x + 12, loader_rect.y + 10, BLACK, small_font)
    draw_text(surface, get_selected_saved_card_file_name()[-30:], loader_rect.x + 12, loader_rect.y + 38, BLACK, small_font)

    prev_saved_button.draw(surface)
    next_saved_button.draw(surface)
    load_saved_button.draw(surface)
    new_card_button.draw(surface)
    refresh_saved_button.draw(surface)

    draw_wrapped_text(surface, loaded_card_message, loader_rect.x + 12, loader_rect.y + 112, 36, DARK_GRAY, small_font, 17)


def draw_visible_stat_boxes(surface):
    visible_boxes = get_visible_stat_boxes()

    for index, box in enumerate(visible_boxes):
        row = index // 4
        col = index % 4

        box.rect.x = 40 + col * 150
        box.rect.y = 370 + row * 75
        box.draw(surface)

    if not visible_boxes:
        draw_text(surface, "No stat boxes needed yet. Add an effect first.", 40, 370, DARK_GRAY, small_font)


def draw_card_preview(surface, card_data):
    card_rect = pygame.Rect(40, 665, 280, 115)
    pygame.draw.rect(surface, GREEN, card_rect)
    pygame.draw.rect(surface, BLACK, card_rect, 3)

    title = card_data["name"]

    if per_character_enabled:
        title += " (" + current_variant_character + ")"

    draw_text(surface, title, card_rect.x + 15, card_rect.y + 10, WHITE, font)
    draw_text(surface, "Cost: " + str(card_data["cost"]), card_rect.x + 15, card_rect.y + 40, WHITE, small_font)
    draw_text(surface, "Thickness: " + str(card_data["thickness"]), card_rect.x + 15, card_rect.y + 61, WHITE, small_font)
    draw_text(surface, "Art: " + os.path.basename(card_data.get("image_path", ""))[-22:], card_rect.x + 15, card_rect.y + 82, WHITE, small_font)


def draw_grid(surface):
    start_x = 930
    start_y = 100

    draw_text(surface, "Left click blue squares for card hitbox/range.", 840, 50, BLACK, small_font)
    draw_text(surface, "Right click a square to move player preview.", 840, 75, BLACK, small_font)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(start_x + col * TILE_SIZE, start_y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            color = WHITE

            if (row, col) in selected_tiles:
                color = BLUE

            if (row, col) == player_tile:
                color = GREEN

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 3)

            if (row, col) == player_tile:
                draw_text(surface, "P", rect.x + 32, rect.y + 25, WHITE, big_font)


def get_grid_square_from_mouse(pos):
    start_x = 930
    start_y = 100
    x, y = pos

    col = (x - start_x) // TILE_SIZE
    row = (y - start_y) // TILE_SIZE

    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        return int(row), int(col)

    return None


def add_effect(effect_type):
    if effect_type == "damage":
        effect_order.append({"type": "damage", "amount_from": "damage", "target_tiles_from_card": True})

    elif effect_type == "block":
        effect_order.append({"type": "gain_block", "amount_from": "block"})

    elif effect_type == "draw":
        effect_order.append({"type": "draw_cards", "amount_from": "draw"})

    elif effect_type == "discard":
        effect_order.append({"type": "discard_cards", "amount_from": "discard"})

    elif effect_type == "move":
        effect_order.append({"type": "move_character", "distance_from": "move_distance", "direction": move_direction})

    elif effect_type == "charge":
        effect_order.append({"type": "charge_character", "distance_from": "move_distance", "direction": move_direction})

    elif effect_type == "shove":
        effect_order.append({"type": "shove", "distance_from": "shove_distance", "direction": move_direction})

    elif effect_type == "trap":
        effect_order.append({
            "type": "place_trap",
            "center": "player_position",
            "damage_from": "damage",
            "duration_from": "trap_duration",
            "radius_from": "trap_radius",
            "snare_until_gone": trap_snares,
        })


def handle_effect_order_click(mouse_pos):
    box = pygame.Rect(760, 690, 650, 195)
    y = box.y + 45

    for index, effect in enumerate(effect_order):
        x_button = pygame.Rect(box.x + 300, y - 2, 24, 22)
        up_button = pygame.Rect(box.x + 335, y - 2, 24, 22)
        down_button = pygame.Rect(box.x + 370, y - 2, 24, 22)

        if x_button.collidepoint(mouse_pos):
            effect_order.pop(index)
            return True

        if up_button.collidepoint(mouse_pos):
            if index > 0:
                effect_order[index], effect_order[index - 1] = effect_order[index - 1], effect_order[index]
            return True

        if down_button.collidepoint(mouse_pos):
            if index < len(effect_order) - 1:
                effect_order[index], effect_order[index + 1] = effect_order[index + 1], effect_order[index]
            return True

        y += 24

    return False


def draw_effect_order(surface):
    box = pygame.Rect(760, 690, 650, 195)
    pygame.draw.rect(surface, WHITE, box)
    pygame.draw.rect(surface, BLACK, box, 3)

    draw_text(surface, "Effect Order: top happens first", box.x + 15, box.y + 10, BLACK, font)

    y = box.y + 45

    for index, effect in enumerate(effect_order):
        text = str(index + 1) + ". " + effect["type"]

        if "direction" in effect:
            text += " / " + effect["direction"]

        if effect.get("type") == "place_trap":
            text += " / snare " + str(effect.get("snare_until_gone", False))

        draw_text(surface, text, box.x + 15, y, BLACK, small_font)

        x_button = pygame.Rect(box.x + 300, y - 2, 24, 22)
        pygame.draw.rect(surface, RED, x_button)
        pygame.draw.rect(surface, BLACK, x_button, 2)
        draw_text(surface, "X", x_button.x + 6, x_button.y + 2, BLACK, small_font)

        up_button = pygame.Rect(box.x + 335, y - 2, 24, 22)
        pygame.draw.rect(surface, GRAY, up_button)
        pygame.draw.rect(surface, BLACK, up_button, 2)
        draw_text(surface, "^", up_button.x + 7, up_button.y + 2, BLACK, small_font)

        down_button = pygame.Rect(box.x + 370, y - 2, 24, 22)
        pygame.draw.rect(surface, GRAY, down_button)
        pygame.draw.rect(surface, BLACK, down_button, 2)
        draw_text(surface, "v", down_button.x + 7, down_button.y + 2, BLACK, small_font)

        y += 24

    draw_text(surface, "X = delete", box.x + 430, box.y + 45, DARK_GRAY, small_font)
    draw_text(surface, "^ = move up", box.x + 430, box.y + 70, DARK_GRAY, small_font)
    draw_text(surface, "v = move down", box.x + 430, box.y + 95, DARK_GRAY, small_font)


refresh_saved_card_files()

running = True

while running:
    clock.tick(FPS)
    screen.fill((245, 245, 245))

    card_data = build_card_data()

    draw_text(screen, "Custom Card Maker", 40, 25, BLACK, big_font)

    draw_saved_card_loader(screen)

    for box in always_text_boxes:
        box.draw(screen)

    draw_visible_stat_boxes(screen)

    draw_text(screen, "Usable Characters", 40, 495, BLACK, font)

    for character_name, button in character_buttons.items():
        button.color = LIGHT_GREEN if usable_characters[character_name] else GRAY
        button.draw(screen)

    per_character_button.text = "Per Character: Yes" if per_character_enabled else "Per Character: No"
    per_character_button.color = ORANGE if per_character_enabled else GRAY
    per_character_button.draw(screen)

    if per_character_enabled:
        variant_archer_button.color = LIGHT_GREEN if current_variant_character == "Archer" else GRAY
        variant_warrior_button.color = LIGHT_GREEN if current_variant_character == "Warrior" else GRAY
        variant_archer_button.draw(screen)
        variant_warrior_button.draw(screen)

    draw_text(screen, "Move / Charge / Shove Direction", 40, 580, BLACK, font)

    for direction, button in direction_buttons.items():
        button.color = LIGHT_GREEN if direction == move_direction else GRAY
        button.draw(screen)

    trap_snare_button.text = "Trap Snare: Yes" if trap_snares else "Trap Snare: No"
    trap_snare_button.color = LIGHT_GREEN if trap_snares else GRAY
    trap_snare_button.draw(screen)

    draw_card_preview(screen, card_data)
    draw_grid(screen)

    draw_text(screen, "Add Effects", 800, 455, BLACK, big_font)

    for button in effect_buttons:
        button.draw(screen)

    draw_wrapped_text(
        screen,
        "Description variables: {damage}, {block}, {draw}, {discard}, {range}, {move_distance}, {shove_distance}, {trap_duration}, {trap_radius}",
        40,
        790,
        84,
        BLACK,
        small_font,
        18
    )

    save_button.draw(screen)
    clear_effects_button.draw(screen)
    draw_effect_order(screen)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_current_variant_values()
            running = False

        for box in get_all_visible_text_boxes():
            box.handle_event(event)

        if save_button.clicked(event):
            save_card()

        if clear_effects_button.clicked(event):
            effect_order.clear()

        if prev_saved_button.clicked(event):
            if saved_card_files:
                selected_saved_card_index -= 1
                if selected_saved_card_index < 0:
                    selected_saved_card_index = len(saved_card_files) - 1

        if next_saved_button.clicked(event):
            if saved_card_files:
                selected_saved_card_index += 1
                if selected_saved_card_index >= len(saved_card_files):
                    selected_saved_card_index = 0

        if load_saved_button.clicked(event):
            load_selected_saved_card()

        if new_card_button.clicked(event):
            reset_editor_to_new_card()

        if refresh_saved_button.clicked(event):
            refresh_saved_card_files()

        for character_name, button in character_buttons.items():
            if button.clicked(event):
                usable_characters[character_name] = not usable_characters[character_name]

        if per_character_button.clicked(event):
            if not per_character_enabled:
                character_values["Archer"] = {
                    "damage": damage_box.text,
                    "block": block_box.text,
                    "draw": draw_box.text,
                    "discard": discard_box.text,
                    "move_distance": move_distance_box.text,
                    "shove_distance": shove_distance_box.text,
                    "trap_duration": trap_duration_box.text,
                    "trap_radius": trap_radius_box.text,
                }
                character_values["Warrior"] = character_values["Archer"].copy()
                current_variant_character = "Archer"
            else:
                save_current_variant_values()

            per_character_enabled = not per_character_enabled

            if per_character_enabled:
                load_variant_values(current_variant_character)

        if per_character_enabled and variant_archer_button.clicked(event):
            switch_variant_character("Archer")

        if per_character_enabled and variant_warrior_button.clicked(event):
            switch_variant_character("Warrior")

        for direction, button in direction_buttons.items():
            if button.clicked(event):
                move_direction = direction

        if trap_snare_button.clicked(event):
            trap_snares = not trap_snares

        for button in effect_buttons:
            if button.clicked(event):
                if button.text == "Add Damage":
                    add_effect("damage")
                elif button.text == "Add Block":
                    add_effect("block")
                elif button.text == "Add Draw":
                    add_effect("draw")
                elif button.text == "Add Discard":
                    add_effect("discard")
                elif button.text == "Add Move":
                    add_effect("move")
                elif button.text == "Add Charge":
                    add_effect("charge")
                elif button.text == "Add Shove":
                    add_effect("shove")
                elif button.text == "Add Trap":
                    add_effect("trap")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_effect_order_click(event.pos):
                continue

            square = get_grid_square_from_mouse(event.pos)

            if square is not None:
                if event.button == 1:
                    if square in selected_tiles:
                        selected_tiles.remove(square)
                    else:
                        selected_tiles.add(square)

                elif event.button == 3:
                    player_tile = square

pygame.quit()