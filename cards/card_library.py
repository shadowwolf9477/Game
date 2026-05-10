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

    "basic_attack": {
        "name": "Basic Attack",
        "cost": 1,
        "thickness": 0.5,
        "type": "attack",
        "effect": "basic_attack",
        "damage": 1,
        "usable_tags": ["ranged", "melee"],
        # Characters read the same range differently: Archer shoots a row, Warrior slashes lanes.
        "range": 2,
        "description": "Use this character's basic attack shape.",
        "character_names": {
            "Archer": "Bow Shot",
            "Warrior": "Axe Slash"
        }
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
        "usable_characters": ["Archer"],
        "description": "Pierce your row. Hit up to 2 enemies.",
        "image_path": "cards/card_assets/pierce shot.png"
    },

    "cleave": {
        "name": "Cleave",
        "cost": 2,
        "thickness": 0.5,
        "type": "attack",
        "effect": "cleave_column",
        "damage": 2,
        "usable_characters": ["Warrior"],
        "description": "Cleave a column. Hit every enemy in that column."
    }

}
