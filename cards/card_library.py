# Card definitions are the source data for building decks and rewards.
# Each card copy can later be modified by sleeves/upgrades during a run.
CARD_LIBRARY = {
    "quick_step": {
        "name": "Quick Step",
        "cost": 1,
        "thickness": 0.5,
        "type": "movement",
        "rarity": "common",
        # effect tells card_effects.py which function should resolve the card.
        "effect": "move",
        "move_range": 2,
        "description": "Move up to 2 tiles.",
        "image_path": "assets/card_templtes/card art/quick_dash.jpg"
    },

    "basic_attack": {
        "name": "Basic Attack",
        "cost": 1,
        "rarity": "common",
        "thickness": 0.5,
        "type": "attack",
        "effect": "basic_attack",
        "damage": 5,
        "usable_tags": ["ranged", "melee"],
        # Characters read the same range differently: Archer shoots a row, Warrior slashes lanes.
        "range": 2,
        "character_damage": {
            "Archer": 4,
            "Warrior": 7
        },
        "description": "Use this character's basic attack shape.",
        "image_path": "assets/card_templtes/card art/bow_shot.jpg",
        "character_image_paths": {
            "Archer": "assets/card_templtes/card art/bow_shot.jpg",
            "Warrior": "assets/card_templtes/card art/axe swing.jpg"
        },
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
        "damage": 9,
        "rarity": "rare",
        # Pierce hits more than one enemy, but still respects the player's row.
        "max_targets": 2,
        "range": 3,
        "usable_characters": ["Archer"],
        "description": "Pierce 3 tiles in your row. Hit up to 2 enemies.",
        "image_path": "assets/card_templtes/card art/bow_shot.jpg"
    },

    "cleave": {
        "rarity": "rare",
        "name": "Cleave",
        "cost": 2,
        "thickness": 0.5,
        "type": "attack",
        "effect": "cleave_column",
        "damage": 15,
        "usable_characters": ["Warrior"],
        "description": "Choose left or right. Split this card's damage across enemies in the swing.",
        "image_path": "assets/card_templtes/card art/Cleave.jpg"
    },

    "guarded_step": {
        "name": "Guarded Step",
        "cost": 0,
        "thickness": 0.5,
        "type": "movement",
        "rarity": "common",
        "effect": "move",
        "move_range": 1,
        "block": 10,
        "description": "Move 1 tile. Gain 10 block.",
        "image_path": "assets/card_templtes/card art/gaurd_step.webp"
    },

    "deep_breath": {
        "name": "Deep Breath",
        "cost": 0,
        "thickness": 0.5,
        "type": "skill",
        "rarity": "common",
        "effect": "deep_breath",
        "gain_energy": 1,
        "draw_cards": 1,
        "discard_cards": 1,
        "description": "Gain 1 energy. Discard 1 card. Draw 1 card.",
        "image_path": "assets/card_templtes/card art/deep_breaths.webp"
    },

    "shove": {
        "name": "Shove",
        "cost": 1,
        "thickness": 0.5,
        "type": "skill",
        "rarity": "uncommon",
        "effect": "shove",
        "push_range": 2,
        "description": "Push the enemy directly ahead 2 tiles.",
        "image_path": "assets/card_templtes/card art/Shove.webp"
    },

    "snare_trap": {
        "name": "Snare Trap",
        "cost": 2,
        "thickness": 0.5,
        "type": "skill",
        "rarity": "uncommon",
        "effect": "trap",
        "trap_damage": 1,
        "trap_duration": 4,
        "trap_radius": 1,
        "description": "Set a trap on the enemy board. Radius 1. Lasts 4 turns.",
        "image_path": "assets/card_templtes/card art/Snare_trap.png"
    }

}
from cards.custom_card_loader import load_custom_cards

CARD_LIBRARY.update(load_custom_cards())
