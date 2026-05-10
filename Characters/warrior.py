# Warrior character data.
# The warrior shares the run deck, but has melee tags and a different basic attack.
warrior = {
    "name": "Warrior",
    "max_hp": 8,
    "current_hp": 8,
    "starting_row": 2,
    "starting_col": 2,
    "tags": ["melee", "tank"],
    "basic_attack_shape": "vertical_slash",
    "idle_animation": {
        "sheet_path": "assests/sample(idle&walk)./idle/sprite sheets/idle.png",
        "frame_width": 46,
        "frame_height": 55,
        "row": 0,
        "frame_count": 10
    },
    "flip_x": True,
    "specific_cards": [
        "cleave",
        "cleave"
    ]
}
