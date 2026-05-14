import pygame
import os
import json

DEV_MENU_OPEN = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (70, 70, 70)
RED = (220, 70, 70)
GREEN = (80, 200, 130)
BLUE = (90, 140, 230)
YELLOW = (230, 210, 80)

FONT = None
SMALL_FONT = None


def setup_dev_menu_fonts():
    global FONT
    global SMALL_FONT

    if FONT is None:
        FONT = pygame.font.SysFont(None, 28)
        SMALL_FONT = pygame.font.SysFont(None, 22)


def draw_text(screen, text, x, y, color=BLACK, font=None):
    setup_dev_menu_fonts()

    if font is None:
        font = FONT

    image = font.render(str(text), True, color)
    screen.blit(image, (x, y))


class DevButton:
    def __init__(self, x, y, w, h, text, action, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        draw_text(screen, self.text, self.rect.x + 8, self.rect.y + 8, BLACK, SMALL_FONT)

    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def toggle_dev_menu():
    global DEV_MENU_OPEN
    DEV_MENU_OPEN = not DEV_MENU_OPEN


def dev_menu_is_open():
    return DEV_MENU_OPEN


def get_custom_card_ids():
    card_ids = []

    folders = [
        "custom_cards",
        os.path.join("cards", "custom_cards")
    ]

    for folder in folders:
        if not os.path.exists(folder):
            continue

        for file_name in os.listdir(folder):
            if file_name.endswith(".json"):
                card_ids.append(file_name.replace(".json", ""))

    card_ids.sort()
    return card_ids


def get_battle_room_files():
    room_files = []

    folder = "battle_rooms"

    if not os.path.exists(folder):
        return room_files

    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            room_files.append(file_name)

    room_files.sort()
    return room_files


def instant_kill_all_enemies(enemies):
    for enemy in enemies:
        enemy["hp"] = 0


def instant_kill_first_enemy(enemies):
    if enemies:
        enemies[0]["hp"] = 0


def add_card_to_hand(card_id, player_hand, card_library):
    if card_id not in card_library:
        print("Card not found:", card_id)
        return

    player_hand.append(card_library[card_id].copy())
    print("Added to hand:", card_id)


def add_card_to_deck(card_id, player_deck, card_library):
    if card_id not in card_library:
        print("Card not found:", card_id)
        return

    player_deck.append(card_library[card_id].copy())
    print("Added to deck:", card_id)


def draw_dev_menu(
    screen,
    enemies,
    player_hand,
    player_deck,
    card_library,
    selected_dev_card_index,
    selected_battle_index
):
    setup_dev_menu_fonts()

    panel = pygame.Rect(40, 40, 620, 650)
    pygame.draw.rect(screen, WHITE, panel)
    pygame.draw.rect(screen, BLACK, panel, 4)

    draw_text(screen, "DEV MENU", panel.x + 20, panel.y + 15, BLACK)
    draw_text(screen, "Alt + 7 to close", panel.x + 430, panel.y + 18, DARK_GRAY, SMALL_FONT)

    y = panel.y + 65

    buttons = []

    buttons.append(DevButton(panel.x + 20, y, 180, 38, "Kill First Enemy", "kill_first", RED))
    buttons.append(DevButton(panel.x + 220, y, 180, 38, "Kill All Enemies", "kill_all", RED))

    y += 60

    custom_cards = get_custom_card_ids()

    draw_text(screen, "Custom Cards", panel.x + 20, y, BLACK)
    y += 30

    if custom_cards:
        selected_dev_card_index %= len(custom_cards)
        selected_card_id = custom_cards[selected_dev_card_index]

        draw_text(screen, "Selected: " + selected_card_id, panel.x + 20, y, BLACK, SMALL_FONT)

        buttons.append(DevButton(panel.x + 20, y + 30, 40, 34, "<", "prev_card", GRAY))
        buttons.append(DevButton(panel.x + 70, y + 30, 40, 34, ">", "next_card", GRAY))
        buttons.append(DevButton(panel.x + 130, y + 30, 180, 34, "Add To Hand", "add_hand", GREEN))
        buttons.append(DevButton(panel.x + 330, y + 30, 180, 34, "Add To Deck", "add_deck", BLUE))
    else:
        draw_text(screen, "No custom cards found.", panel.x + 20, y, RED, SMALL_FONT)

    y += 100

    battle_rooms = get_battle_room_files()

    draw_text(screen, "Saved Battle Rooms", panel.x + 20, y, BLACK)
    y += 30

    if battle_rooms:
        selected_battle_index %= len(battle_rooms)
        selected_room = battle_rooms[selected_battle_index]

        draw_text(screen, "Selected: " + selected_room, panel.x + 20, y, BLACK, SMALL_FONT)

        buttons.append(DevButton(panel.x + 20, y + 30, 40, 34, "<", "prev_battle", GRAY))
        buttons.append(DevButton(panel.x + 70, y + 30, 40, 34, ">", "next_battle", GRAY))
        buttons.append(DevButton(panel.x + 130, y + 30, 220, 34, "Load This Battle", "load_battle", YELLOW))
    else:
        draw_text(screen, "No battle_rooms JSON files found.", panel.x + 20, y, RED, SMALL_FONT)

    y += 105

    draw_text(screen, "Enemies", panel.x + 20, y, BLACK)
    y += 30

    if enemies:
        for enemy in enemies[:8]:
            text = enemy.get("name", enemy.get("type", "enemy")) + " HP: " + str(enemy.get("hp", "?"))
            draw_text(screen, text, panel.x + 20, y, BLACK, SMALL_FONT)
            y += 24
    else:
        draw_text(screen, "No enemies alive.", panel.x + 20, y, DARK_GRAY, SMALL_FONT)

    for button in buttons:
        button.draw(screen)

    return buttons