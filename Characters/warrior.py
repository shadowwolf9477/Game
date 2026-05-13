# Warrior character data.
# The warrior shares the run deck, but has melee tags and a different basic attack.
warrior = {
    "name": "Warrior",
    "max_hp": 40,
    "current_hp": 40,
    "starting_row": 2,
    "starting_col": 0,
    "tags": ["melee", "tank"],
    "passive": "guardian",
    "basic_attack_shape": "vertical_slash",
    "idle_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Knight/Knight/Knight-Idle.png"
        ),
        "frame_width": 100,
        "frame_height": 100
    },
    "attack_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Knight/Knight/Knight-Attack01.png"
        ),
        "frame_width": 100,
        "frame_height": 100
    },
    "death_animation": {
        "strip_path": (
            "assets/Tiny RPG Character Asset Pack v1.03b -Full 20 Characters/"
            "Tiny RPG Character Asset Pack v1.03 -Full 20 Characters/"
            "Characters(100x100)/Knight/Knight/Knight-Death.png"
        ),
        "frame_width": 100,
        "frame_height": 100
    },
    "flip_x": False,
    "specific_cards": [
        "cleave",
        "cleave"
    ]
}
