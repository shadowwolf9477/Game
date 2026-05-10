import random
from cards.card_library import CARD_LIBRARY


def build_starting_deck(character):
    # Turn the character's card IDs into real card data from CARD_LIBRARY.
    deck = []

    for card_id in character["starting_deck"]:
        card = CARD_LIBRARY[card_id]
        deck.append(card)

    return deck


def shuffle_deck(deck):
    # Make a shuffled copy so the original starting deck order is not changed.
    shuffled_deck = deck.copy()
    random.shuffle(shuffled_deck)
    return shuffled_deck


def draw_cards(draw_pile, discard_pile, hand, amount):
    # Move cards from draw_pile into hand.
    # If the draw pile runs out, reshuffle the discard pile into a new draw pile.
    for draw_count in range(amount):
        if len(draw_pile) == 0 and len(discard_pile) > 0:
            draw_pile.extend(shuffle_deck(discard_pile))
            discard_pile.clear()

        if len(draw_pile) == 0:
            return

        card = draw_pile.pop(0)
        hand.append(card)
