
import random
from cards.card_library import CARD_LIBRARY
from cards.card_effects import character_can_use_card

def party_can_use_card(party, card):
    for character in party:
        if character_can_use_card(character, card):
            return True

    return False

RARITY_WEIGHTS = {
    "common": 70,
    "uncommon": 25,
    "rare": 5
}

BOSS_RARITY_WEIGHTS = {
    "rare": 70,
    "legendary": 30
}

def get_reward_rarity(include_legendary=False):
    rarities = ["common", "uncommon", "rare"]
    weights = [70, 25, 5]
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    return chosen_rarity
   
def get_valid_card_ids(party, rarity, excluded_card_ids, include_legendary=False):
    valid_card_ids = []

    for card_id, card in CARD_LIBRARY.items():
        if card["rarity"] != rarity:
            continue

        if card_id in excluded_card_ids:
            continue

        if card["rarity"] == "legendary" and not include_legendary:
            continue

        if party_can_use_card(party, card):
            valid_card_ids.append(card_id)

    return valid_card_ids

def get_any_valid_card_ids(party, excluded_card_ids, include_legendary=False):
    valid_card_ids = []

    for card_id, card in CARD_LIBRARY.items():
        if card_id in excluded_card_ids:
            continue

        if card["rarity"] == "legendary" and not include_legendary:
            continue

        if party_can_use_card(party, card):
            valid_card_ids.append(card_id)
    return valid_card_ids
def generate_card_rewards(party, amount=3, include_legendary=False):
    chosen_card_ids = []

    for reward_number in range(amount):
        rarity = get_reward_rarity(include_legendary)

        valid_card_ids = get_valid_card_ids(
            party,
            rarity,
            chosen_card_ids,
            include_legendary
        )

        if len(valid_card_ids) == 0:
            valid_card_ids = get_any_valid_card_ids(
                party,
                chosen_card_ids,
                include_legendary
            )

        if len(valid_card_ids) == 0:
            break

        chosen_card_id = random.choice(valid_card_ids)
        chosen_card_ids.append(chosen_card_id)

    reward_cards = []

    for card_id in chosen_card_ids:
        reward_cards.append(CARD_LIBRARY[card_id].copy())

    return reward_cards









     


    



    

