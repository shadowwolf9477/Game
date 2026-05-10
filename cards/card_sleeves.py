# Sleeve definitions describe which cards a sleeve can modify.
# The actual stat changes live in sleeve_effects.py.
CARD_SLEEVES = {
    "premium_sleeve": {
        "name": "Premium Sleeve",
        "description": "+1 damage, +1 cost, +0.5 thickness.",
        # Keep movement cards invalid until movement-specific sleeves exist.
        "valid_card_types": ["attack"],
        "effect": "premium_sleeve"
    }
}
