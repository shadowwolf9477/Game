# Card definitions are the source data for building decks and rewards.
# Each card copy can later be modified by sleeves/upgrades during a run.
CARD_LIBRARY = {
    "quick_step": {
        "name": "Quick Step",
        "cost": 1,
        "thickness": 0.5,
        "type": "movement",
        # effect tells card_effects.py which function should resolve the card.
        "effect": "move",
        "move_range": 2,
        "description": "Move up to 2 tiles.",
        "image_path": "cards/card_assets/Quick dash.png"
    },

    "bow_shot": {
        "name": "Bow Shot",
        "cost": 1,
        "thickness": 0.5,
        "type": "attack",
        "effect": "bow_shot",
        "damage": 1,
        # Bow Shot uses this as enemy-board spaces starting from the player's column.
        "range": 2,
        "description": "Shoot up to 2 tiles ahead. Hit 1 enemy.",
        "image_path": "cards/card_assets/bow shot.png"
    },

    "pierce_shot": {
        "name": "Pierce Shot",
        "cost": 2,
        "thickness": 0.5,
        "type": "attack",
        "effect": "pierce_row",
        "damage": 2,
        # Pierce hits more than one enemy, but still respects the player's row.
        "max_targets": 2,
        "range": "player_row",
        "description": "Pierce your row. Hit up to 2 enemies.",
        "image_path": "cards/card_assets/pierce shot.png"
    }

}
