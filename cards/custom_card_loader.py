import json
import os


def load_custom_cards(folders=None):
    custom_cards = {}

    if folders is None:
        folders = [
            "custom_cards",
            os.path.join("cards", "custom_cards")
        ]

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            continue

        for file_name in os.listdir(folder):
            if not file_name.endswith(".json"):
                continue

            file_path = os.path.join(folder, file_name)

            with open(file_path, "r") as file:
                card = json.load(file)

            card_id = card["id"]
            card["effect"] = "custom_card"
            custom_cards[card_id] = card

    return custom_cards