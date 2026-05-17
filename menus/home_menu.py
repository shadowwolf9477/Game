from button import Button


def create_home_menu_buttons():
    return {
        "start": Button(500, 220, 220, 70, "Start"),
        "card_editor": Button(500, 310, 220, 70, "Card Editor"),
        "quit": Button(500, 400, 220, 70, "Quit")
    }


def draw_home_menu(screen, font, start_button, quit_button, card_editor_button):
    start_button.draw(screen, font)
    quit_button.draw(screen, font)
    card_editor_button.draw(screen, font)
