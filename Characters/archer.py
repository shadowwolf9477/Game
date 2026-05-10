
# Archer character data.
# specific_cards are mixed with neutral cards by player_deck.py.
archer = {
    "name": "Archer",
    "max_hp": 5,
    "current_hp": 5,
    "starting_row": 1,
    "starting_col": 2,
    "tags": ["ranged"],
    "basic_attack_shape": "row_shot",
    "idle_animation": {
        "sheet_path": "assests/Eris Esra's Character Template 4.1/16x32/16x32 Idle-Sheet.png",
        "frame_width": 32,
        "frame_height": 32,
        "row": 1,
        "frame_count": 4
    },
    # Character-specific cards are mixed with neutral cards by player_deck.py.
    "specific_cards": [
        "pierce_shot",
        "pierce_shot"
    ]
}
