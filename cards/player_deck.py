import random
from cards.card_library import CARD_LIBRARY


def build_starting_deck(character):
    # Turn starting deck IDs into separate card copies for this run.
    deck = []

    for card_id in character["starting_deck"]:
        # copy() matters: sleeves should change one card, not every library copy.
        card = CARD_LIBRARY[card_id].copy()

        deck.append(card)

    return deck


def shuffle_deck(deck):
    # Shuffle a copy so callers can keep their original pile/list if needed.
    shuffled_deck = deck.copy()
    random.shuffle(shuffled_deck)
    return shuffled_deck


def draw_cards(draw_pile, discard_pile, hand, amount):
    # Draw one at a time so an empty draw pile can reshuffle mid-draw.
    for draw_count in range(amount):
        if len(draw_pile) == 0 and len(discard_pile) > 0:
            # This supports "draw 4 with only 2 left": draw 2, reshuffle, draw 2.
            draw_pile.extend(shuffle_deck(discard_pile))
            discard_pile.clear()

        if len(draw_pile) == 0:
            return

        card = draw_pile.pop(0)
        hand.append(card)
