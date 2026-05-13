
# Archer character data.
# specific_cards are mixed with neutral cards by player_deck.py.
archer = {
    "name": "Archer",
    "max_hp": 25,
    "current_hp": 25,
    "starting_row": 1,
    "starting_col": 0,
    "tags": ["ranged"],
    "passive": "reaction_bonus",
    "basic_attack_shape": "row_shot",
    "attack_draw_offset_x": 41,
    "idle_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Archer/Archer/Archer-Idle.png"
        ),
        "frame_width": 100,
        "frame_height": 100
    },
    "attack_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Archer/Archer/Archer-Attack01.png"
        ),
        "frame_width": 100,
        "frame_height": 100,
        "stable_normalize": True,
        "sprite_scale": 2.1
    },
    "death_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Archer/Archer/Archer-Death.png"
        ),
        "frame_width": 100,
        "frame_height": 100
    },
    # Character-specific cards are mixed with neutral cards by player_deck.py.
    "specific_cards": [
        "pierce_shot",
        "pierce_shot"
    ]
}
