def apply_premium_sleeve(card):
    # Premium Sleeve makes one attack card stronger but heavier to play/draw.
    card["damage"] += 1
    card["cost"] += 1
    card["thickness"] += 0.5


# Maps sleeve effect IDs from card_sleeves.py to the function that applies them.
SLEEVE_EFFECTS = {
    "premium_sleeve": apply_premium_sleeve
}


def can_apply_sleeve(sleeve, card):
    # UI and click logic both use this so invalid cards draw gray and do nothing.
    return card["type"] in sleeve["valid_card_types"]


def apply_sleeve(sleeve, card):
    # Return False instead of changing invalid cards.
    if not can_apply_sleeve(sleeve, card):
        return False

    effect_name = sleeve["effect"]
    effect_function = SLEEVE_EFFECTS[effect_name]
    effect_function(card)

    return True
