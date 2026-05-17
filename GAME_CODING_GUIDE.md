# How To Code This Game

This is a hands-on coding guide for this exact project. It is not a modding guide. The goal is that you can open the code, find the right place, change a mechanic, and understand what other files may need to change with it.

Use this like a Google Docs manual. Read the chapter for the thing you want to change, then follow the checklist.

## Table Of Contents

- Chapter 1: How The Project Is Organized
- Chapter 2: How To Read The Code Without Getting Lost
- Chapter 3: Python Basics This Game Uses
- Chapter 4: The Game Loop And Screen States
- Chapter 5: The Grid And Board System
- Chapter 6: Card Creation
- Chapter 7: Card Effects And Result Dictionaries
- Chapter 8: Card Ranges, Hitboxes, And Preview Tiles
- Chapter 9: Movement Cards, Shove Cards, And Path Planning
- Chapter 10: Characters, Character-Specific Cards, And Starting Decks
- Chapter 11: Energy, Drawing, Discarding, And Deck Piles
- Chapter 12: Sleeves And Card Upgrades
- Chapter 13: Enemies
- Chapter 14: Enemy Attacks, Timers, And Attack Warnings
- Chapter 15: Enemy Movement
- Chapter 16: Traps, Fire, Poison, And Lingering Effects
- Chapter 17: Status Effects
- Chapter 18: Shielding
- Chapter 19: Reactions
- Chapter 20: Rewards
- Chapter 21: Map Generation And Map Navigation
- Chapter 22: Drawing, UI, Popups, And Windows
- Chapter 23: Assets, Sprites, Animations, And Sounds
- Chapter 24: Debugging And Common Breaks
- Chapter 25: Build Recipes For Bigger Ideas

---

# Chapter 1: How The Project Is Organized

Think of the project as several teams. Each file has a job.

## The Main Flow Team

### `main.py`

`main.py` is the conductor. It owns the live game state and decides what happens every frame.

Use `main.py` for:

- Clicking buttons.
- Pressing keys.
- Changing screens.
- Starting battles.
- Ending turns.
- Playing cards.
- Opening popups.
- Confirming movement.
- Confirming shove.
- Handling reactions.
- Moving from battle to rewards to map.

Important live variables in `main.py`:

```python
current_state
current_turn
party
selected_character_index
selected_character
player_grid_data
enemy_grid_data
enemies
player_deck
draw_pile
player_hand
discard_pile
selected_card_index
max_energy
current_energy
movement_mode
shove_mode
reaction_mode
reward_mode
map_layers
```

If something changes the flow of play, start in `main.py`.

## The Data Team

### `cards/card_library.py`

All hand-coded cards live here.

Use it for:

- Adding a new card.
- Changing cost.
- Changing damage.
- Changing range.
- Changing rarity.
- Changing card art.
- Making a card character-specific.

### `Characters/archer.py` and `Characters/warrior.py`

Character data lives here.

Use these files for:

- HP.
- Starting board position.
- Tags.
- Passives.
- Character-specific cards.
- Sprite paths.
- Attack/death animation paths.

### `battle_setup.py`

Enemy and battle room data lives here.

Use it for:

- Adding enemies.
- Spawning battle rooms.
- Enemy attack patterns.
- Enemy movement helper functions.
- Traps.
- Fire.
- Enemy splitting.
- Enemy healing.

## The Rules Team

### `cards/card_effects.py`

This is where cards do real gameplay.

Use it for:

- Dealing damage.
- Applying block.
- Drawing cards.
- Discarding cards.
- Applying statuses.
- Starting shove.
- Placing traps.
- Character restrictions.

### `cards/card_targeting.py`

This is where card preview tiles are calculated.

Use it for:

- Blue attack highlights.
- Hitbox preview.
- Range preview.
- Making previews match the actual effect.

### `battle_turn_logic.py`

This is where enemy turn flow is organized.

Use it for:

- Enemy movement queue.
- Enemy countdown timers.
- Choosing which enemies move.
- Handling enemy split/heal before movement.

### `movement.py`

This is the safe movement helper.

Use it for:

- Moving a unit.
- Checking if a tile is legal.
- Preventing board mixing.
- Preventing units sharing a tile.

## The Drawing Team

### `battle_renderer.py`

Draws battle UI and units.

Use it for:

- HP and block display.
- Energy display.
- Player sprites.
- Enemy sprites.
- Enemy tooltip.
- Status icons.
- Shield button.
- Enemy attack counter.

### `battle_grid.py`

Draws the board squares and creates grid data.

Use it for:

- Attack warning colors.
- Trap/floor effect visuals.
- Movement preview visuals.
- Board tile dictionary shape.

### `cards/card_renderer.py`

Draws cards.

Use it for:

- Card template.
- Card art placement.
- Card name.
- Cost circle.
- Description text.
- Sleeve outline.

### `screens/reward_screen.py`

Draws reward popup.

### `screens/map_screen.py`

Draws map screen and handles map node clicking.

### `screens/pile_screen.py`

Draws deck and discard pile popups.

## The Loading Team

### `loaders/asset_paths.py`

Use this to load assets with relative paths:

```python
asset_path("assets/...")
```

### `loaders/battle_assets.py`

Loads battle background, enemy sprites, arrow image, and counter image.

### `loaders/animation_loader.py`

Slices sprite sheets into frames.

### `loaders/sound_assets.py`

Loads and plays sounds.

---

# Chapter 2: How To Read The Code Without Getting Lost

When you want to change something, do not start by reading all of `main.py`. Start with the thing you want.

## If You Want To Change A Card

Search the card effect name.

Example:

```bash
rg "pierce_row"
```

That shows you:

- Card data in `cards/card_library.py`.
- Effect function in `cards/card_effects.py`.
- Preview logic in `cards/card_targeting.py`.
- Description logic in `cards/card_renderer.py`.

## If You Want To Change An Enemy

Search the enemy type.

Example:

```bash
rg '"orc"'
```

That shows you:

- Spawn data in `battle_setup.py`.
- Attack pattern in `battle_setup.py`.
- Movement logic in `battle_setup.py`.
- Movement queue in `battle_turn_logic.py`.
- Asset loading in `loaders/battle_assets.py`.
- Tooltip text in `battle_renderer.py`.

## If You Want To Change A Screen

Search the state.

Example:

```bash
rg "REWARD"
```

That shows you:

- Imports in `main.py`.
- Click handling in `main.py`.
- Drawing in `main.py`.
- Reward drawing in `screens/reward_screen.py`.

## If You Want To Change A Button

Search the button name.

Example:

```bash
rg "play_card_button"
```

You will find:

- Button creation near the top of `main.py`.
- Click handling in the event loop.
- Drawing in `battle_renderer.py`.

## If You Want To Know Where A Variable Changes

Use search.

Example:

```bash
rg "current_energy"
```

Then read only the places where it is assigned:

```python
current_energy = max_energy
current_energy -= card["cost"]
current_energy += card_result["gain_energy"]
```

## Useful Search Patterns

Find functions:

```bash
rg "^def " main.py
```

Find a card:

```bash
rg "deep_breath"
```

Find an enemy type:

```bash
rg '"skeleton"'
```

Find places that draw something:

```bash
rg "draw_"
```

Find click handling:

```bash
rg "MOUSEBUTTONDOWN" main.py
```

Find keyboard handling:

```bash
rg "KEYDOWN" main.py
```

Find a state:

```bash
rg "current_state == BATTLE"
```

## The "Data, Rule, Preview, Draw" Pattern

Most features use this pattern:

1. Data: What is it?
2. Rule: What does it do?
3. Preview: What does the player see before doing it?
4. Draw: How is it displayed?

Example card:

- Data: `cards/card_library.py`
- Rule: `cards/card_effects.py`
- Preview: `cards/card_targeting.py`
- Draw: `cards/card_renderer.py`

Example enemy:

- Data: `battle_setup.py`
- Rule: `battle_setup.py` and `battle_turn_logic.py`
- Preview: `battle_setup.py` movement/attack helper functions
- Draw: `battle_renderer.py` and `loaders/battle_assets.py`

If a feature is broken, ask which side is wrong:

- Data missing?
- Rule missing?
- Preview wrong?
- Drawing missing?

---

# Chapter 3: Python Basics This Game Uses

This chapter is for reading the code itself.

## Dictionaries

Most game objects are dictionaries.

Example:

```python
enemy = {
    "name": "Skeleton",
    "type": "skeleton",
    "row": 0,
    "col": 2,
    "hp": 30
}
```

Read a required value:

```python
enemy["hp"]
```

Change a value:

```python
enemy["hp"] -= 5
```

Read an optional value:

```python
enemy.get("fire_stacks", 0)
```

That means:

```text
If fire_stacks exists, use it.
If it does not exist, use 0.
```

Use `[]` for values that must exist.

Use `.get()` for optional mechanics.

## Lists

Lists hold multiple things.

```python
enemies = []
player_hand = []
discard_pile = []
```

Add:

```python
enemies.append(enemy)
```

Remove:

```python
enemies.remove(enemy)
```

Clear:

```python
enemies.clear()
```

Loop:

```python
for enemy in enemies:
    enemy["hp"] -= 2
```

Loop with an index:

```python
for index, card in enumerate(player_hand):
    print(index, card["name"])
```

Loop through a copy if you might remove things:

```python
for enemy in enemies[:]:
    if enemy["hp"] <= 0:
        enemies.remove(enemy)
```

## Tuples

Grid tiles are usually stored as:

```python
(row, col)
```

Example:

```python
preview_tiles.append((row, col))
```

Check if an enemy is on a preview tile:

```python
if (enemy["row"], enemy["col"]) in preview_tiles:
    damage_enemy(enemy, 5, hits)
```

## For Loops

Loop through every row and column:

```python
for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        print(row, col)
```

Use this for:

- Drawing every board square.
- Finding all legal tiles.
- Clearing all warnings.
- Checking every trap.
- Building attack patterns.

Loop through card range:

```python
for distance in range(1, card["range"] + 1):
    target_col = selected_character["col"] + distance
```

Why `+ 1`?

Python stops before the last number.

```python
range(1, 4)
```

means:

```text
1, 2, 3
```

## If / Elif / Else

Use `if` when checking a condition:

```python
if enemy["hp"] <= 0:
    enemies.remove(enemy)
```

Use `elif` when only one branch should happen:

```python
if enemy["type"] == "orc":
    choose_orc_attack(enemy, player_grid_data)
elif enemy["type"] == "skeleton":
    choose_skeleton_attack(enemy, player_grid_data)
else:
    choose_goblin_attack(enemy, player_grid_data)
```

Use separate `if` statements when multiple things can happen:

```python
if card_result.get("gain_energy", 0) > 0:
    current_energy += card_result["gain_energy"]

if card_result.get("draw_cards", 0) > 0:
    draw_cards(draw_pile, discard_pile, player_hand, card_result["draw_cards"])
```

## Functions

A function packages code under a name.

```python
def damage_enemy(enemy, damage, hits):
    enemy["hp"] -= damage
    hits.append({
        "target": enemy,
        "damage": damage
    })
```

Call it:

```python
damage_enemy(enemy, 5, hits)
```

Use a function when:

- You repeat logic.
- You want to name a mechanic.
- You want different files to use the same rule.

## Return Values

Functions can give data back.

```python
def get_direction_step(start_value, target_value):
    if target_value > start_value:
        return 1

    if target_value < start_value:
        return -1

    return 0
```

Use it:

```python
row_change = get_direction_step(enemy["row"], target["row"])
```

## Result Dictionaries

Cards return dictionaries to `main.py`.

Example:

```python
return {
    "hits": hits,
    "draw_cards": 1,
    "discard_cards": 1
}
```

Then `main.py` reads those keys:

```python
handle_card_feedback(card_result, acting_character)
apply_card_utility_result(card_result)
```

Use result dictionaries when a card does multiple things.

## Globals In `main.py`

If a function inside `main.py` changes a variable that was created outside that function, it needs `global`.

Example:

```python
def spend_energy(amount):
    global current_energy
    current_energy -= amount
```

Without `global`, Python may think you are trying to create a new local variable.

Only use `global` inside `main.py` functions that change `main.py` state.

---

# Chapter 4: The Game Loop And Screen States

The game loop is in `main.py`.

Every frame:

1. Pygame collects events.
2. The code handles keyboard and mouse.
3. Timers and animations update.
4. The screen draws.
5. Pygame flips the display.

## Screen States

The game screen is decided by:

```python
current_state
```

Common checks:

```python
if current_state == HOME_MENU:
    ...

if current_state == BATTLE:
    ...

if current_state == MAP:
    ...

if current_state == REWARD:
    ...
```

## Player Turn vs Enemy Turn

Combat side is decided by:

```python
current_turn
```

Player-only input usually checks:

```python
if current_state == BATTLE and current_turn == PLAYER_TURN:
    ...
```

Enemy turn logic checks:

```python
if current_turn == ENEMY_TURN:
    ...
```

## Event Types

Mouse click:

```python
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    # left click
```

Right click:

```python
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
    # right click
```

Keyboard:

```python
if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_e:
        confirm_selected_card()
```

Quit window:

```python
if event.type == pygame.QUIT:
    running = False
```

Important:

Only mouse events have `event.pos`.

Bad:

```python
if event.key == pygame.K_e:
    print(event.pos)
```

Good:

```python
if event.type == pygame.MOUSEBUTTONDOWN:
    print(event.pos)
```

## Modal Modes

Modal modes are states inside the battle screen that block other input.

Current modal modes:

```python
movement_mode
shove_mode
reaction_mode
discard_choice_mode
swing_choice_mode
pile_view_title is not None
pending_reward_after_deaths
```

Why they matter:

If a discard popup is open, clicking should discard a card, not play a card.

Example pattern:

```python
if discard_choice_mode:
    clicked_card_index = get_clicked_card_index(player_hand, event.pos)
    choose_discard_card(clicked_card_index)
    continue
```

The `continue` means:

```text
Stop handling this event. Do not let it fall into normal battle clicks.
```

## Add A New Modal Mode

Example: a target-selection popup.

Step 1: Add state near the other state variables in `main.py`.

```python
target_choice_mode = False
target_choice_card = None
```

Step 2: Start it from card play.

```python
target_choice_mode = True
target_choice_card = selected_card
```

Step 3: Handle clicks before normal battle clicks.

```python
if target_choice_mode:
    clicked_enemy = get_clicked_enemy(enemies, event.pos)

    if clicked_enemy is not None:
        finish_target_choice(clicked_enemy)

    continue
```

Step 4: Draw the popup.

```python
if target_choice_mode:
    draw_target_choice_popup(screen, font)
```

Step 5: Reset it on cancel and battle start.

```python
target_choice_mode = False
target_choice_card = None
```

---

# Chapter 5: The Grid And Board System

The game has two separate boards:

```python
player_grid_data = create_grid_data("player")
enemy_grid_data = create_grid_data("enemy")
```

Each board is a 3 row by 5 column grid.

Rows:

```text
0 top
1 middle
2 bottom
```

Columns:

```text
0 left
1
2
3
4 right
```

## Tile Data

Tiles are created in `battle_grid.py`:

```python
tile = {
    "board": board_name,
    "unit": None,
    "effect": None,
    "incoming_attack": None
}
```

Meaning:

- `board`: player or enemy.
- `unit`: character/enemy on this tile.
- `effect`: floor effect like trap or fire.
- `incoming_attack`: enemy attack warning.

## Logical Position vs Screen Position

Logical position:

```python
enemy["row"] = 1
enemy["col"] = 3
```

Screen position:

```python
x = ENEMY_GRID_X + enemy["col"] * (GRID_SIZE + GRID_GAP)
y = GRID_Y + enemy["row"] * (GRID_SIZE + GRID_GAP)
```

Mouse click to grid tile:

```python
clicked_tile = get_clicked_grid_tile(event.pos, ENEMY_GRID_X)
```

That returns:

```python
(row, col)
```

or:

```python
None
```

## Placing Units

Place enemy:

```python
enemy_grid_data[enemy["row"]][enemy["col"]]["unit"] = enemy
```

Place player:

```python
player_grid_data[character["row"]][character["col"]]["unit"] = character
```

Usually use helper functions:

```python
add_enemy_to_grid(enemy, enemies, enemy_grid_data)
place_party_on_grid(party, player_grid_data)
```

## Moving Units

Always use:

```python
move_unit(unit, grid_data, row_change, col_change)
```

Examples:

```python
move_unit(character, player_grid_data, -1, 0) # up
move_unit(character, player_grid_data, 1, 0)  # down
move_unit(character, player_grid_data, 0, -1) # left
move_unit(character, player_grid_data, 0, 1)  # right
```

Enemy:

```python
move_unit(enemy, enemy_grid_data, 0, -1)
```

Never move an enemy on `player_grid_data`.

Never move a character on `enemy_grid_data`.

## Checking Legal Landings

```python
can_land_on_tile(enemy_grid_data, row, col, enemy)
```

This checks:

- In bounds.
- Correct board.
- Tile empty or occupied by the same unit.

## Making A Shape On The Board

A shape is usually a list of `(row, col)` tuples.

Example: all tiles:

```python
tiles = []

for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        tiles.append((row, col))
```

Example: same row:

```python
tiles = []
target_row = selected_character["row"]

for col in range(GRID_COLS):
    tiles.append((target_row, col))
```

Example: radius 1 square:

```python
tiles = []
center_row = 1
center_col = 2

for row in range(center_row - 1, center_row + 2):
    for col in range(center_col - 1, center_col + 2):
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            tiles.append((row, col))
```

## If The Grid Breaks

If units overlap:

- Check spawn positions.
- Check `move_unit`.
- Check `can_land_on_tile`.
- Check you are passing the right grid.

If highlights are offset:

- Check `PLAYER_GRID_X`, `ENEMY_GRID_X`, `GRID_Y`.
- Check `get_clicked_grid_tile`.
- Check preview tile math.

If enemies cross to player board:

- Check unit has `"board": "enemy"`.
- Check enemy movement uses `enemy_grid_data`.

---

# Chapter 6: Card Creation

This is the big card chapter. Most new cards start here.

## Card Creation Checklist

For a new card, ask:

1. Can it use an existing effect?
2. Does it need a new effect function?
3. Does it need a preview shape?
4. Does it need special input like choosing a tile, choosing a card, or choosing left/right?
5. Does it need a new animation/sound?
6. Does it need a special card description?
7. Should it appear in rewards?
8. Should it appear in starting deck?
9. Is it character-specific?
10. Can sleeves upgrade it correctly?

## Basic Card Template

File:

```text
cards/card_library.py
```

Example:

```python
"new_card_id": {
    "name": "New Card",
    "cost": 1,
    "thickness": 0.5,
    "type": "attack",
    "rarity": "common",
    "effect": "basic_attack",
    "damage": 5,
    "description": "Deal 5 damage.",
    "image_path": "assets/card_templtes/card art/bow_shot.jpg"
}
```

Card id:

```python
"new_card_id"
```

is what code uses.

Card name:

```python
"name": "New Card"
```

is what player sees.

## Change Card Cost

File:

```text
cards/card_library.py
```

Change:

```python
"cost": 1
```

to:

```python
"cost": 2
```

If the card has a custom description that mentions cost, update that too.

## Change Card Damage

File:

```text
cards/card_library.py
```

Change:

```python
"damage": 5
```

to:

```python
"damage": 8
```

If it is a character-specific damage card, check:

```python
"character_damage": {
    "Archer": 4,
    "Warrior": 7
}
```

If `character_damage` exists, the normal `"damage"` may not be what gets used.

## Change Card Range

File:

```text
cards/card_library.py
```

Change:

```python
"range": 3
```

Then check:

- `cards/card_effects.py`: does the effect read `card["range"]`?
- `cards/card_targeting.py`: does preview read `card["range"]`?
- `cards/card_renderer.py`: does description show the range?

## Change Card Rarity

File:

```text
cards/card_library.py
```

```python
"rarity": "common"
```

Options:

```python
"common"
"uncommon"
"rare"
"legendary"
```

Rewards use rarity in:

```text
cards/card_rewards.py
```

## Make A Card Character-Specific

Only Archer:

```python
"usable_characters": ["Archer"]
```

Only Warrior:

```python
"usable_characters": ["Warrior"]
```

Any ranged character:

```python
"usable_tags": ["ranged"]
```

Any melee character:

```python
"usable_tags": ["melee"]
```

Checked in:

```python
character_can_use_card(character, card)
```

File:

```text
cards/card_effects.py
```

## Make One Card Act Differently Per Character

Example from Basic Attack:

```python
"character_damage": {
    "Archer": 4,
    "Warrior": 7
},
"character_image_paths": {
    "Archer": "assets/card_templtes/card art/bow_shot.jpg",
    "Warrior": "assets/card_templtes/card art/axe swing.jpg"
},
"character_names": {
    "Archer": "Bow Shot",
    "Warrior": "Axe Slash"
}
```

If you add character-specific values for a new stat:

```python
"character_values": {
    "Archer": {
        "damage": 5,
        "range": 4
    },
    "Warrior": {
        "damage": 8,
        "range": 1
    }
}
```

Then your effect must read those values.

Example helper pattern:

```python
def get_character_value(card, character, key, default):
    character_values = card.get("character_values", {})
    character_name = character["name"]

    if character_name in character_values:
        if key in character_values[character_name]:
            return character_values[character_name][key]

    return card.get(key, default)
```

Use it:

```python
damage = get_character_value(card, selected_character, "damage", card.get("damage", 0))
```

## Add A Card That Uses An Existing Effect

Example: stronger Archer pierce.

File:

```text
cards/card_library.py
```

```python
"heavy_pierce": {
    "name": "Heavy Pierce",
    "cost": 3,
    "thickness": 0.5,
    "type": "attack",
    "rarity": "uncommon",
    "effect": "pierce_row",
    "damage": 14,
    "max_targets": 2,
    "range": 3,
    "usable_characters": ["Archer"],
    "description": "Pierce 3 tiles. Hit up to 2 enemies.",
    "image_path": "assets/card_templtes/card art/bow_shot.jpg"
}
```

Because it uses:

```python
"effect": "pierce_row"
```

you do not need a new effect function.

It automatically uses:

- `play_pierce_row` in `cards/card_effects.py`.
- `pierce_row` preview in `cards/card_targeting.py`.

## Add A Card With A New Effect

Example: `poison_stab`.

Step 1: Add card data.

File:

```text
cards/card_library.py
```

```python
"poison_stab": {
    "name": "Poison Stab",
    "cost": 1,
    "thickness": 0.5,
    "type": "attack",
    "rarity": "uncommon",
    "effect": "poison_stab",
    "damage": 4,
    "poison_damage": 2,
    "poison_turns": 3,
    "range": 1,
    "usable_characters": ["Warrior"],
    "description": "Deal 4 damage and poison.",
    "image_path": "assets/card_templtes/card art/axe swing.jpg"
}
```

Step 2: Add effect function.

File:

```text
cards/card_effects.py
```

```python
def play_poison_stab(card, selected_character, enemies):
    hits = []
    target_col = selected_character["col"] + 1

    if get_character_attack_direction(selected_character) == "back":
        target_col = selected_character["col"] - 1

    for enemy in enemies:
        if enemy["row"] == selected_character["row"] and enemy["col"] == target_col:
            damage_enemy(enemy, card["damage"], hits)
            enemy["poison_turns"] = max(enemy.get("poison_turns", 0), card.get("poison_turns", 3))
            enemy["poison_damage"] = max(enemy.get("poison_damage", 0), card.get("poison_damage", 2))
            break

    return {
        "hits": hits
    }
```

Step 3: Register effect.

File:

```text
cards/card_effects.py
```

```python
CARD_EFFECTS = {
    ...
    "poison_stab": play_poison_stab
}
```

Step 4: Add preview.

File:

```text
cards/card_targeting.py
```

```python
if card["effect"] == "poison_stab":
    target_col = selected_character["col"] + 1

    if get_character_attack_direction(selected_character) == "back":
        target_col = selected_character["col"] - 1

    if 0 <= target_col < GRID_COLS:
        return [(selected_character["row"], target_col)]

    return []
```

Step 5: Add card description.

File:

```text
cards/card_renderer.py
```

```python
if card["effect"] == "poison_stab":
    return "Deal " + str(card["damage"]) + " damage. Poison for " + str(card["poison_turns"]) + " turns."
```

Step 6: Add poison ticking.

See Chapter 16.

---

# Chapter 7: Card Effects And Result Dictionaries

Card effects happen in `cards/card_effects.py`.

The core function is:

```python
play_card(card, selected_character, enemies, current_energy)
```

It does:

1. Check character can use card.
2. Check energy.
3. Find effect in `CARD_EFFECTS`.
4. Spend energy.
5. Apply character-specific attack changes.
6. Run the effect function.
7. Return success, energy, and result.

## The Effect Registry

File:

```text
cards/card_effects.py
```

```python
CARD_EFFECTS = {
    "basic_attack": play_basic_attack,
    "pierce_row": play_pierce_row,
    "cleave_column": play_cleave_column,
    "move": start_move_card,
    "deep_breath": play_deep_breath,
    "shove": start_shove_card,
    "trap": place_trap_card
}
```

If your card's `"effect"` is not in this dictionary, the card will not play.

## Basic Damage Result

```python
def play_simple_hit(card, selected_character, enemies):
    hits = []

    for enemy in enemies:
        if enemy["row"] == selected_character["row"]:
            damage_enemy(enemy, card["damage"], hits)
            break

    return {
        "hits": hits
    }
```

`main.py` uses `"hits"` to:

- Start attack animation.
- Show damage numbers.
- Start projectile if Archer.
- Play sound.
- Queue enemy death animation.

## Draw And Discard Result

```python
return {
    "gain_energy": 1,
    "discard_cards": 1,
    "draw_cards": 1,
    "discard_prompt": "Discard a card"
}
```

Handled by:

```python
apply_card_utility_result(card_result)
```

## Random Discard Result

```python
return {
    "discard_cards": 1,
    "random_discard": True
}
```

This discards without asking the player.

## Shove Result

```python
return {
    "shove_target": target,
    "push_range": 2
}
```

Handled by:

```python
start_shove_mode(card_result, acting_character)
```

## Trap Result

One trap:

```python
return {
    "trap": {
        "row": selected_character["row"],
        "col": selected_character["col"],
        "damage": 2,
        "duration": 4,
        "radius": 1
    }
}
```

Multiple traps:

```python
return {
    "traps": [
        {"row": 0, "col": 1, "damage": 2, "duration": 3, "radius": 0},
        {"row": 2, "col": 4, "damage": 2, "duration": 3, "radius": 0}
    ]
}
```

Handled by:

```python
place_trap_on_enemy_grid(trap, enemy_grid_data)
```

## When To Edit `main.py` For A Card

You need `main.py` if the card needs a new player choice.

Examples:

- Choose a card from hand.
- Choose an enemy manually.
- Choose a tile.
- Choose left/right.
- Wait for an animation before resolving.
- Open a popup.

If the card can immediately calculate everything from selected character and enemies, keep it in `cards/card_effects.py`.

---

# Chapter 8: Card Ranges, Hitboxes, And Preview Tiles

The most important rule:

```text
If a card has a hitbox, card_effects.py and card_targeting.py must agree.
```

`cards/card_effects.py` decides who actually gets hit.

`cards/card_targeting.py` decides what gets highlighted.

## Row Attack

Effect logic:

```python
def get_row_attack_tiles(selected_character, attack_range):
    tiles = []
    attack_direction = get_character_attack_direction(selected_character)

    for distance in range(1, attack_range + 1):
        if attack_direction == "back":
            col = selected_character["col"] - distance
        else:
            col = selected_character["col"] + distance

        if 0 <= col < GRID_COLS:
            tiles.append((selected_character["row"], col))

    return tiles
```

Damage:

```python
target_tiles = get_row_attack_tiles(selected_character, card["range"])

for enemy in enemies:
    if (enemy["row"], enemy["col"]) in target_tiles:
        damage_enemy(enemy, card["damage"], hits)
        break
```

Preview:

```python
return get_row_attack_tiles(selected_character, card["range"])
```

## 2x2 Area

```python
def get_2x2_tiles(start_row, start_col):
    tiles = []

    for row in range(start_row, start_row + 2):
        for col in range(start_col, start_col + 2):
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                tiles.append((row, col))

    return tiles
```

## Plus Pattern

```python
def get_plus_tiles(center_row, center_col):
    tiles = []

    for row in range(GRID_ROWS):
        tiles.append((row, center_col))

    for col in range(GRID_COLS):
        tiles.append((center_row, col))

    return list(dict.fromkeys(tiles))
```

## X Pattern

```python
def get_x_tiles(center_row, center_col):
    tiles = []
    offsets = [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)]

    for row_offset, col_offset in offsets:
        row = center_row + row_offset
        col = center_col + col_offset

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            tiles.append((row, col))

    return tiles
```

## C Shape

This is Warrior Cleave style.

```text
[][]
x []
[][]
```

The current helper:

```python
get_warrior_swing_tiles(selected_character, swing_direction)
```

Important:

The shape should not change based on left/right swing. Left/right swing should only change hit order.

So:

- Shape helper decides valid tiles.
- Sort helper decides who takes damage first.

Damage order:

```python
sort_enemies_for_swing(enemies, selected_character, swing_direction)
```

Split damage:

```python
split_degrading_damage(card["damage"], len(targets))
```

## Debug Preview Problems

If the blue highlight is right but damage is wrong:

```text
cards/card_effects.py is wrong.
```

If damage is right but highlight is wrong:

```text
cards/card_targeting.py is wrong.
```

If both are wrong:

```text
The shared shape idea is wrong.
Make a helper and use the same math in both files.
```

---

# Chapter 9: Movement Cards, Shove Cards, And Path Planning

Movement and shove are special because the player first plans a path, then confirms.

## Normal Movement Card

Card data:

```python
"quick_step": {
    "effect": "move",
    "move_range": 2,
    "cost": 1,
    "type": "movement"
}
```

Flow:

1. Select card.
2. Select character.
3. Confirm card.
4. `movement_mode = True`.
5. Click adjacent tiles or use WASD.
6. Confirm with right click, `E`, or Play Card.
7. Spend energy.
8. Move character.
9. Discard card.

Important functions in `main.py`:

```python
card_uses_movement_preview(card)
get_card_movement_range(card, character)
start_movement_preview(card_index, character)
add_movement_preview_step(row_change, col_change)
click_movement_preview_tile(clicked_tile)
get_movement_preview_tiles()
confirm_movement_card()
```

## Make A Movement Card Go Farther

File:

```text
cards/card_library.py
```

```python
"move_range": 3
```

## Make A Movement Card Give Block

```python
"block": 10
```

`confirm_movement_card()` already applies:

```python
gain_block(acting_character, selected_card.get("block", 0))
```

## Shove Card

Card data:

```python
"shove": {
    "name": "Shove",
    "cost": 1,
    "type": "skill",
    "effect": "shove",
    "push_range": 2
}
```

Flow:

1. Play card.
2. Card effect finds an enemy directly ahead.
3. `main.py` starts `shove_mode`.
4. Player draws shove path on enemy board.
5. Confirm.
6. Enemy moves along path one tile at a time.
7. Traps trigger after movement.

Important functions:

```python
start_shove_card(card, selected_character, enemies)
start_shove_mode(card_result, acting_character)
add_shove_preview_step(row_change, col_change)
click_shove_preview_tile(clicked_tile)
get_shove_preview_tiles()
confirm_shove()
finish_shove(enemy_that_was_shoved)
```

## Change Shove Targeting

Current target:

```python
get_enemy_directly_ahead(selected_character, enemies)
```

If you want shove to target any enemy in range:

1. Change preview in `cards/card_targeting.py`.
2. Change target-finding in `cards/card_effects.py`.
3. If player must choose the enemy, add a modal mode in `main.py`.

## Debug Movement

If movement preview appears but confirm does nothing:

- Is `movement_preview_path` empty?
- Can the unit land on final tile?
- Is there enough energy?
- Does `play_card` return true?

If movement spends energy too early:

- Check `start_movement_preview`.
- Energy should only spend in `confirm_movement_card`.

If shove path will not draw:

- Check `can_land_on_tile(enemy_grid_data, next_row, next_col, shove_target)`.
- Check target tile is adjacent.
- Check `shove_steps_left`.

---

# Chapter 10: Characters, Character-Specific Cards, And Starting Decks

## Character Data

Example:

```python
warrior = {
    "name": "Warrior",
    "max_hp": 40,
    "current_hp": 40,
    "starting_row": 2,
    "starting_col": 0,
    "tags": ["melee", "tank"],
    "passive": "guardian",
    "basic_attack_shape": "vertical_slash",
    "specific_cards": ["cleave", "cleave"]
}
```

## Change Starting Position

File:

```text
Characters/archer.py
Characters/warrior.py
```

Change:

```python
"starting_row": 1,
"starting_col": 0
```

Characters are placed by:

```python
place_party_on_grid(party, player_grid_data)
```

## Change HP

```python
"max_hp": 35,
"current_hp": 35
```

If the character is already alive in a run, changing the file will affect new runs only.

## Add Character-Specific Starting Cards

File:

```text
Characters/archer.py
```

```python
"specific_cards": [
    "pierce_shot",
    "pierce_shot",
    "heavy_pierce"
]
```

Deck building:

```python
build_starting_deck(party)
```

File:

```text
cards/player_deck.py
```

## Change Neutral Starting Cards

File:

```text
cards/player_deck.py
```

```python
NEUTRAL_STARTING_CARDS = [
    "quick_step",
    "quick_step",
    "basic_attack",
    "basic_attack"
]
```

## Add A New Character Later

Files to change:

- `Characters/new_character.py`
- `party_manager.py`
- `cards/card_library.py` if new specific cards exist
- `loaders/battle_assets.py` only if asset loading helper needs changes
- `cards/card_effects.py` if the character has special rules
- `battle_renderer.py` if the UI must show something new

Pattern:

```python
from Characters.new_character import new_character
```

In `make_party()`:

```python
new_character_copy = new_character.copy()
new_character_copy["idle_frames"] = load_character_idle_frames(new_character_copy)
...
return [archer_character, warrior_character, new_character_copy]
```

Because your design is currently 2 characters max, adding a third playable character would require UI decisions too.

---

# Chapter 11: Energy, Drawing, Discarding, And Deck Piles

## Energy

In `main.py`:

```python
max_energy = 3
current_energy = 3
```

At start of player turn:

```python
next_current_energy = max_energy
```

Cards spend energy in:

```python
play_card(card, selected_character, enemies, current_energy)
```

Do not spend energy manually unless you are making a special mechanic.

## Add More Max Energy

Change:

```python
max_energy = 4
current_energy = 4
```

Energy UI can draw extra bars if current energy goes above max.

## Draw Cards

Function:

```python
draw_cards(draw_pile, discard_pile, player_hand, 5)
```

It reshuffles discard into draw pile when needed.

## Discard Hand At End Of Turn

In `finish_enemy_actions()`:

```python
discard_pile.extend(player_hand)
player_hand.clear()
draw_cards(draw_pile, discard_pile, player_hand, 5)
```

## Chosen Discard

Use:

```python
start_discard_choice(discard_count, prompt, draw_after_discard)
```

Example card result:

```python
return {
    "discard_cards": 1,
    "draw_cards": 1,
    "discard_prompt": "Discard a card"
}
```

## Random Discard

Example card result:

```python
return {
    "discard_cards": 1,
    "random_discard": True
}
```

## Deck And Discard Viewer

Files:

```text
main.py
screens/pile_screen.py
```

Click handling:

```python
clicked_pile_button = get_clicked_pile_button(event.pos)
```

Deck viewer uses:

```python
pile_view_cards = shuffle_deck(draw_pile)
```

This hides exact draw order.

Discard viewer uses:

```python
pile_view_cards = discard_pile.copy()
```

---

# Chapter 12: Sleeves And Card Upgrades

Sleeves are card modifiers.

Two files:

```text
cards/card_sleeves.py
cards/sleeve_effects.py
```

## Sleeve Data

File:

```text
cards/card_sleeves.py
```

```python
"premium_sleeve": {
    "name": "Premium Sleeve",
    "description": "+1 damage, +1 cost, +0.5 thickness.",
    "valid_card_types": ["attack"],
    "effect": "premium_sleeve"
}
```

## Sleeve Effect

File:

```text
cards/sleeve_effects.py
```

```python
def apply_premium_sleeve(card):
    card["damage"] += 5
    card["cost"] += 1
    card["thickness"] += 0.5
    card.setdefault("sleeves", []).append("Premium Sleeve")
```

Register:

```python
SLEEVE_EFFECTS = {
    "premium_sleeve": apply_premium_sleeve
}
```

## Add A New Sleeve

Example: range sleeve.

`cards/card_sleeves.py`:

```python
"range_sleeve": {
    "name": "Long Sleeve",
    "description": "+1 range, +0.5 thickness.",
    "valid_card_types": ["attack"],
    "effect": "range_sleeve"
}
```

`cards/sleeve_effects.py`:

```python
def apply_range_sleeve(card):
    card["range"] = card.get("range", 1) + 1
    card["thickness"] += 0.5
    card.setdefault("sleeves", []).append("Long Sleeve")
```

Register:

```python
SLEEVE_EFFECTS = {
    "premium_sleeve": apply_premium_sleeve,
    "range_sleeve": apply_range_sleeve
}
```

## Make Sleeve Only Apply To Cards With Range

```python
def can_apply_sleeve(sleeve, card):
    if card["type"] not in sleeve["valid_card_types"]:
        return False

    if sleeve["effect"] == "range_sleeve" and "range" not in card:
        return False

    return True
```

## If Sleeve Changes Damage

Check:

- `cards/card_effects.py`: damage uses `card["damage"]`.
- `cards/card_renderer.py`: description shows new damage.

## If Sleeve Changes Range

Check:

- `cards/card_effects.py`: effect reads `card["range"]`.
- `cards/card_targeting.py`: preview reads `card["range"]`.
- `cards/card_renderer.py`: description shows new range.

---

# Chapter 13: Enemies

Enemies are dictionaries in `battle_setup.py`.

## Enemy Template

```python
def build_slime(row, col):
    return {
        "name": "Slime",
        "type": "slime",
        "board": "enemy",
        "row": row,
        "col": col,
        "hp": 20,
        "max_hp": 20,
        "attack_damage": 5,
        "attack_interval": 1,
        "turns_until_attack": 1,
        "flip_x": True
    }
```

Required:

- `name`
- `type`
- `board`
- `row`
- `col`
- `hp`
- `max_hp`
- `attack_damage`
- `attack_interval`
- `turns_until_attack`

## Spawn Enemy In A Room

```python
def start_slime_battle(enemies, enemy_grid_data):
    slime = build_slime(1, 2)
    add_enemy_to_grid(slime, enemies, enemy_grid_data)
```

Do not just do:

```python
enemies.append(slime)
```

Use:

```python
add_enemy_to_grid(slime, enemies, enemy_grid_data)
```

because that also marks the grid tile as occupied.

## Add Enemy Assets

File:

```text
loaders/battle_assets.py
```

```python
slime_assets = load_tiny_rpg_asset("Slime", "Attack01", 1.25)
```

Then:

```python
enemy_assets = {
    ...
    "slime": {
        **slime_assets
    }
}
```

The key must match:

```python
"type": "slime"
```

## Add Enemy Tooltip Text

File:

```text
battle_renderer.py
```

Add to:

```python
get_enemy_pattern_text(enemy)
get_enemy_move_text(enemy)
get_enemy_applied_status_text(enemy)
get_enemy_active_status_text(enemy)
```

Example:

```python
if enemy_type == "slime":
    return "Attacks its matching tile."
```

## Add Enemy To Random Battle Rooms

File:

```text
battle_setup.py
```

Add room id:

```python
RANDOM_BATTLE_ROOMS = ["orc_goblins", "bone_pack", "web_ambush", "slime_battle"]
```

Add branch:

```python
if battle_room == "slime_battle":
    start_slime_battle(enemies, enemy_grid_data)
```

---

# Chapter 14: Enemy Attacks, Timers, And Attack Warnings

Enemy attacks are warnings stored on the player grid.

Attack warnings are created by:

```python
add_incoming_attack(player_grid_data, row, col, enemy)
```

## Attack Data Shape

```python
incoming_attack = {
    "damage": total_damage,
    "attacks": [
        {
            "damage": damage,
            "source": enemy
        }
    ]
}
```

Multiple enemies can attack the same tile. That is why `"attacks"` is a list.

## Enemy Timers

Each enemy has:

```python
"attack_interval": 2,
"turns_until_attack": 2
```

Meaning:

- `turns_until_attack == 1`: the attack is shown and will happen this enemy turn.
- After attacking, it resets to `attack_interval`.
- If not attacking, it counts down.

## Add Attack Pattern To Enemy Type

File:

```text
battle_setup.py
```

In `prepare_enemy_attacks`:

```python
elif enemy["type"] == "slime":
    choose_slime_attack(enemy, player_grid_data)
```

Then:

```python
def choose_slime_attack(enemy, player_grid_data):
    add_incoming_attack(
        player_grid_data,
        enemy["row"],
        enemy["col"],
        enemy
    )
```

## Full Row Attack

```python
def choose_full_row_attack(enemy, player_grid_data):
    target_row = random.randint(0, GRID_ROWS - 1)

    for col in range(GRID_COLS):
        add_incoming_attack(player_grid_data, target_row, col, enemy)
```

## Random Tiles Attack

```python
def choose_two_random_tiles(enemy, player_grid_data):
    all_tiles = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            all_tiles.append((row, col))

    chosen_tiles = random.sample(all_tiles, 2)

    for row, col in chosen_tiles:
        add_incoming_attack(player_grid_data, row, col, enemy)
```

## 2x2 Attack

```python
def choose_2x2_attack(enemy, player_grid_data):
    start_row = random.randint(0, GRID_ROWS - 2)
    start_col = random.randint(0, GRID_COLS - 2)

    for row in range(start_row, start_row + 2):
        for col in range(start_col, start_col + 2):
            add_incoming_attack(player_grid_data, row, col, enemy)
```

## Attack That Applies Status

```python
add_incoming_attack(
    player_grid_data,
    row,
    col,
    enemy,
    status_effect="snared",
    status_duration=1
)
```

The status is applied after damage in:

```python
apply_attack_status(character, incoming_attack)
```

## One Enemy Attacks At A Time

`main.py` uses:

```python
attacking_enemy_index = get_next_attacking_enemy_index(enemies, -1)
```

After an enemy animation finishes:

```python
resolve_enemy_incoming_attacks(attacking_enemy, party, player_grid_data)
clear_enemy_incoming_attacks(attacking_enemy, player_grid_data)
attacking_enemy_index = get_next_attacking_enemy_index(enemies, attacking_enemy_index)
```

That is why one enemy's highlighted squares disappear before the next enemy attacks.

---

# Chapter 15: Enemy Movement

Enemy movement has two parts:

1. Possible movement preview when the player clicks an enemy.
2. Actual movement queue during enemy turn.

## Possible Movement Preview

File:

```text
battle_setup.py
```

Function:

```python
get_enemy_possible_movement_tiles(enemy, enemy_grid_data, party)
```

Add new type:

```python
if enemy["type"] == "slime":
    return get_slime_possible_movement_tiles(enemy, enemy_grid_data)
```

Helper:

```python
def get_slime_possible_movement_tiles(enemy, enemy_grid_data):
    possible_tiles = []

    for row_change, col_change in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        row = enemy["row"] + row_change
        col = enemy["col"] + col_change

        if can_land_on_tile(enemy_grid_data, row, col, enemy):
            possible_tiles.append((row, col))

    return possible_tiles
```

## Actual Movement Queue

File:

```text
battle_turn_logic.py
```

Function:

```python
build_enemy_movement_queue(enemies, enemy_grid_data, party)
```

Add:

```python
elif enemy["type"] == "slime":
    movement_queue.extend(get_slime_movement_steps(enemy, enemy_grid_data))
```

Then import `get_slime_movement_steps`.

## Movement Step Data

One movement step:

```python
{
    "enemy": enemy,
    "row_change": 0,
    "col_change": 1,
    "is_final_step": True
}
```

Multi-step path:

```python
[
    {"enemy": enemy, "row_change": -1, "col_change": 0, "is_final_step": False},
    {"enemy": enemy, "row_change": -1, "col_change": 0, "is_final_step": False},
    {"enemy": enemy, "row_change": 0, "col_change": 1, "is_final_step": True}
]
```

## Move Randomly One Tile

```python
def get_slime_movement_steps(enemy, enemy_grid_data):
    possible_tiles = get_slime_possible_movement_tiles(enemy, enemy_grid_data)

    if not possible_tiles:
        return []

    target_row, target_col = random.choice(possible_tiles)

    return [{
        "enemy": enemy,
        "row_change": target_row - enemy["row"],
        "col_change": target_col - enemy["col"],
        "is_final_step": True
    }]
```

## Move Toward Player

```python
def get_chaser_movement_steps(enemy, enemy_grid_data, party):
    target = get_closest_living_character(enemy, party)

    if target is None:
        return []

    row_change = get_direction_step(enemy["row"], target["row"])
    col_change = get_direction_step(enemy["col"], target["col"])

    possible_steps = [
        (0, col_change),
        (row_change, 0)
    ]

    for step_row, step_col in possible_steps:
        if step_row == 0 and step_col == 0:
            continue

        next_row = enemy["row"] + step_row
        next_col = enemy["col"] + step_col

        if can_land_on_tile(enemy_grid_data, next_row, next_col, enemy):
            return [{
                "enemy": enemy,
                "row_change": step_row,
                "col_change": step_col,
                "is_final_step": True
            }]

    return []
```

## Move Like A Chess Knight

The Orc uses:

```python
get_orc_knight_movement_steps(enemy, enemy_grid_data)
```

It chooses a final knight tile, then builds one-square steps using:

```python
build_step_path(enemy, row_change, col_change, row_first)
```

That makes reactions possible because the enemy moves step by step.

---

# Chapter 16: Traps, Fire, Poison, And Lingering Effects

Lingering effects usually live on a grid tile or on a unit.

## Floor Effects

Stored on:

```python
enemy_grid_data[row][col]["effect"]
```

Placed by:

```python
place_trap_on_enemy_grid(trap, enemy_grid_data)
```

## Basic Trap

Trap data:

```python
{
    "row": row,
    "col": col,
    "damage": 5,
    "duration": 3,
    "radius": 1
}
```

Trigger:

```python
trigger_enemy_traps(enemy, enemy_grid_data)
```

Duration:

```python
tick_traps(enemy_grid_data)
```

## Fire Floor

Fire data:

```python
{
    "kind": "fire_floor",
    "row": row,
    "col": col,
    "duration": 3,
    "entry_damage": 2,
    "stay_damage": 2,
    "fire_stacks_on_enter": 1
}
```

Entering fire is handled in:

```python
trigger_enemy_traps(enemy, enemy_grid_data)
```

Standing in fire is handled in:

```python
process_enemy_end_of_turn_fire(enemies, enemy_grid_data)
```

## Poison On Enemy

Add poison keys:

```python
enemy["poison_turns"] = max(enemy.get("poison_turns", 0), 3)
enemy["poison_damage"] = max(enemy.get("poison_damage", 0), 2)
```

Tick poison:

```python
def tick_enemy_poison(enemy):
    if enemy.get("poison_turns", 0) <= 0:
        return None

    damage = enemy.get("poison_damage", 2)
    enemy["hp"] -= damage
    enemy["poison_turns"] -= 1

    return {
        "target": enemy,
        "damage": damage
    }
```

Call it in an end-of-turn effect function:

```python
poison_hit = tick_enemy_poison(enemy)

if poison_hit is not None:
    hits.append(poison_hit)
```

Then `main.py` should:

```python
add_damage_popups_from_hits(hits, "enemy")
queue_enemy_death_animations(enemies, enemy_death_animations)
handle_enemy_deaths(enemies, enemy_grid_data)
```

## Example: Fire Card That Damages And Creates Fire

Card data:

```python
"hellfire": {
    "name": "Hellfire",
    "cost": 2,
    "thickness": 0.5,
    "type": "attack",
    "rarity": "rare",
    "effect": "hellfire",
    "damage": 8,
    "fire_tile_count": 2,
    "fire_duration": 3,
    "fire_entry_damage": 2,
    "fire_stay_damage": 2,
    "fire_stacks": 2,
    "description": "Damage a 2x2 area and create fire.",
    "image_path": "assets/card_templtes/card art/Snare_trap.png"
}
```

Effect:

```python
def play_hellfire(card, selected_character, enemies):
    hits = []
    damage_tiles = get_hellfire_damage_tiles(selected_character)

    for enemy in enemies:
        if (enemy["row"], enemy["col"]) in damage_tiles:
            damage_enemy(enemy, card["damage"], hits)
            enemy["fire_stacks"] = enemy.get("fire_stacks", 0) + card.get("fire_stacks", 2)

    possible_fire_tiles = []

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            possible_fire_tiles.append((row, col))

    chosen_fire_tiles = random.sample(possible_fire_tiles, card.get("fire_tile_count", 2))
    traps = []

    for row, col in chosen_fire_tiles:
        traps.append({
            "kind": "fire_floor",
            "row": row,
            "col": col,
            "duration": card.get("fire_duration", 3),
            "entry_damage": card.get("fire_entry_damage", 2),
            "stay_damage": card.get("fire_stay_damage", 2),
            "fire_stacks_on_enter": card.get("fire_stacks", 2)
        })

    return {
        "hits": hits,
        "traps": traps
    }
```

This mixes:

- Area damage.
- Random floor effects.
- Entry damage.
- End-turn damage.
- Status damage.

---

# Chapter 17: Status Effects

Statuses are usually dictionary keys with numbers.

Examples:

```python
character["snared"] = 1
character["reaction_locked"] = 2
enemy["poison_turns"] = 3
```

## Player Statuses

Current player statuses:

- `snared`
- `reaction_locked`
- `random_discard_next_turn`
- `weak_attacks`

Where they are used:

- `snared`: movement and move cards.
- `reaction_locked`: reactions.
- `random_discard_next_turn`: start of next player turn.
- `weak_attacks`: next attacks deal less damage.

## Add New Player Status

Example: `silenced`, cannot play skill cards.

Step 1: Apply it.

```python
add_incoming_attack(
    player_grid_data,
    row,
    col,
    enemy,
    status_effect="silenced",
    status_duration=1
)
```

Step 2: Make it block skills.

File:

```text
cards/card_effects.py
```

```python
if card["type"] == "skill" and character.get("silenced", 0) > 0:
    return False
```

Step 3: Tick it down.

File:

```text
party_manager.py
```

```python
status_keys = ["snared", "silenced"]
```

Step 4: Reset at battle start.

```python
character["silenced"] = 0
```

Step 5: Draw icon.

File:

```text
battle_renderer.py
```

Add to `STATUS_DEFINITIONS`.

## Enemy Statuses

Enemy statuses are read in:

```python
get_enemy_active_status_text(enemy)
```

File:

```text
battle_renderer.py
```

Add:

```python
if enemy.get("poison_turns", 0) > 0:
    statuses.append("poison " + str(enemy["poison_turns"]))
```

---

# Chapter 18: Shielding

Shielding is a relationship between the two characters.

If Warrior shields Archer:

```python
warrior["shielding"] = archer
```

Important files:

- `party_manager.py`
- `battle_setup.py`
- `battle_renderer.py`
- `main.py`

## Shield Button

Button rectangle:

```python
get_shield_button_rect(party, selected_character)
```

Draw:

```python
draw_shield_button(screen, font, party, selected_character)
```

Click:

```python
if shield_button_rect.collidepoint(event.pos):
    shield_target = get_shield_target(party, selected_character)
    clear_party_shields(party)
    selected_character["shielding"] = shield_target
```

## Damage Redirection

In `battle_setup.py`:

```python
damage_target = get_shielding_character(party, character)
```

If someone shields the hit character, the shielder takes damage.

## Warrior Passive

```python
if damage_target["name"] == "Warrior":
    reduced_damage = int(damage * 0.75)
```

## Break Shield On Movement

After movement:

```python
clear_shields_involving_character(party, selected_character)
remove_broken_shields(party)
```

If shielding behaves wrong, check:

- Is selected character the shielder?
- Are the two characters adjacent?
- Did movement break it?
- Did `clear_party_shields` remove old shields?

---

# Chapter 19: Reactions

Reactions happen during enemy movement.

Rule:

```text
If a moving enemy steps onto a tile threatened by an attack card in hand,
the player may play that card during enemy turn.
```

## Reaction Cost

File:

```text
cards/card_effects.py
```

```python
def get_reaction_cost(card):
    return card["cost"] + 1
```

## Archer Reaction Bonus

```python
if selected_character["name"] == "Archer" and "damage" in reaction_card:
    boosted_damage = int(reaction_card["damage"] * 1.25)
```

## Reaction Detection

File:

```text
main.py
```

Important function:

```python
get_reaction_character_for_card(card, party, moving_enemy, current_energy)
```

It checks:

- Energy.
- Card is attack.
- Character can use card.
- Character is not shielding.
- Character is not reaction locked.
- Enemy is standing in the card preview tiles.

## Change What Cards Can React

Currently:

```python
if card["type"] != "attack":
    continue
```

If you want skill reactions later, change that rule.

## Debug Reactions

If reaction does not trigger:

- Is enemy moving one tile at a time?
- Is card type `"attack"`?
- Is current energy enough for reaction cost?
- Is character reaction locked?
- Does `get_card_preview_tiles` include the moving enemy tile?
- Is character shielding someone?

---

# Chapter 20: Rewards

After battle:

```python
queue_reward_after_battle()
```

Reward state:

```python
current_state = REWARD
reward_mode = "choose_reward"
```

Reward modes:

```python
"choose_reward"
"choose_new_card"
"choose_sleeve_card"
```

## Card Rewards

Generated by:

```python
generate_card_rewards(party, 3)
```

File:

```text
cards/card_rewards.py
```

Rarity weights:

```python
RARITY_WEIGHTS = {
    "common": 70,
    "uncommon": 25,
    "rare": 5
}
```

Currently `get_reward_rarity` uses fixed lists:

```python
rarities = ["common", "uncommon", "rare"]
weights = [70, 25, 5]
```

To use `RARITY_WEIGHTS`, you could write:

```python
def get_reward_rarity(include_legendary=False):
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    return random.choices(rarities, weights=weights, k=1)[0]
```

## No Duplicate Card Rewards

Handled by:

```python
chosen_card_ids
excluded_card_ids
```

If a card already got chosen, it is skipped.

## Reward Click Flow

In `main.py`:

```python
if reward_choice == "new_card":
    card_reward_choices = generate_card_rewards(party, 3)
    reward_mode = "choose_new_card"
```

Click card:

```python
player_deck.append(clicked_card.copy())
current_state = MAP
```

Sleeve:

```python
selected_sleeve = CARD_SLEEVES["premium_sleeve"]
reward_mode = "choose_sleeve_card"
```

Click deck card:

```python
apply_sleeve(selected_sleeve, clicked_card)
current_state = MAP
```

---

# Chapter 21: Map Generation And Map Navigation

This chapter is for understanding how the map works through code.

Files:

```text
maps/map_loader.py
screens/map_screen.py
main.py
```

## What Map Data Looks Like

The map is a list of layers.

```python
map_layers = [
    [node],
    [node, node, node],
    [node, node],
    ...
]
```

Each node is a dictionary:

```python
node = {
    "connections": [],
    "type": "battle",
    "layer": layer,
    "index": index,
    "x": get_node_x(index, nodes_in_layer),
    "y": 80 + layer * 70,
    "completed": False,
    "available": False
}
```

## Generate The Map

File:

```text
maps/map_loader.py
```

Function:

```python
generate_map()
```

It does:

1. Choose how many nodes each layer has.
2. Create node dictionaries.
3. Choose node types.
4. Add connections.
5. Mark start completed.
6. Mark connected layer 1 nodes available.

## Number Of Layers

```python
LAYER_COUNT = 12
```

Change to:

```python
LAYER_COUNT = 15
```

for longer run.

## Number Of Nodes Per Layer

Function:

```python
generate_nodes_per_layer(layer_count)
```

Current:

```python
if layer == 0:
    nodes_per_layer.append(1)
elif layer == layer_count - 1:
    nodes_per_layer.append(1)
else:
    nodes_per_layer.append(random.randint(3, 5))
```

Meaning:

- Start has 1 node.
- Boss has 1 node.
- Middle layers have 3 to 5 nodes.

## Node Types

Function:

```python
choose_node_type(layer, shops_placed, events_placed)
```

Current idea:

```python
possible_types = [
    "battle",
    "battle",
    "battle",
    "battle",
    "upgrade"
]
```

More copies means more likely.

To make shops more common:

```python
possible_types.append("shop")
possible_types.append("shop")
```

To make battles less common:

```python
possible_types = [
    "battle",
    "battle",
    "upgrade",
    "shop",
    "event"
]
```

## Guaranteed Rest Layers

```python
if layer % 5 == 0:
    return "rest", shops_placed, events_placed
```

Change to every 4th stop:

```python
if layer % 4 == 0:
    return "rest", shops_placed, events_placed
```

But be careful: layer 0 is start. If you only want rest after the start:

```python
if layer != 0 and layer % 4 == 0:
    return "rest", shops_placed, events_placed
```

## Connections

Connections live on each node:

```python
node["connections"] = [0, 2]
```

That means:

```text
From this node, player can go to next layer's node index 0 or 2.
```

Connections are added by:

```python
add_spire_style_connections(map_layers)
```

Extra splits:

```python
add_extra_splits(map_layers)
```

No unreachable nodes:

```python
make_every_next_node_reachable(map_layers)
```

## How Clicking A Map Node Works

File:

```text
screens/map_screen.py
```

Function:

```python
get_clicked_map_node(map_layers, mouse_pos)
```

It only returns nodes that are available.

In `main.py`:

```python
clicked_node = get_clicked_map_node(map_layers, event.pos)

if clicked_node is not None:
    complete_map_node(map_layers, clicked_node)
    current_map_layer = clicked_node["layer"]
```

## Completing A Node

File:

```text
screens/map_screen.py
```

Function:

```python
complete_map_node(map_layers, clicked_node)
```

It should:

1. Mark clicked node completed.
2. Mark clicked node unavailable.
3. Look at clicked node connections.
4. Make connected next-layer nodes available.

Concept:

```python
clicked_node["completed"] = True
clicked_node["available"] = False

next_layer_index = clicked_node["layer"] + 1

for connected_index in clicked_node["connections"]:
    map_layers[next_layer_index][connected_index]["available"] = True
```

## Starting A Battle From Map

In `main.py`:

```python
if clicked_node["type"] == "battle" or clicked_node["type"] == "boss":
    player_grid_data = create_grid_data("player")
    enemy_grid_data = create_grid_data("enemy")
    enemies.clear()

    place_party_on_grid(party, player_grid_data)

    battle_number += 1
    last_battle_room = start_map_battle(enemies, enemy_grid_data, last_battle_room)
    apply_enemy_assets(enemies, enemy_assets)
    prepare_enemy_attacks(enemies, player_grid_data)

    draw_pile = shuffle_deck(player_deck)
    draw_cards(draw_pile, discard_pile, player_hand, 5)

    current_turn = PLAYER_TURN
    current_energy = max_energy
    current_state = BATTLE
```

## Adding A New Node Type

Example: treasure node.

Step 1: Add to map generation.

File:

```text
maps/map_loader.py
```

```python
possible_types.append("treasure")
```

Step 2: Add icon.

File:

```text
screens/map_screen.py
```

```python
ICON_PATHS = {
    ...
    "treasure": "assets/Map_Icons/treasure.png"
}
```

Step 3: Handle click.

File:

```text
main.py
```

```python
if clicked_node["type"] == "treasure":
    player_deck.append(CARD_LIBRARY["some_card"].copy())
```

Step 4: Decide if it should open a popup.

If yes:

```python
current_state = REWARD
reward_mode = "choose_treasure"
```

Then draw/handle that mode in reward screen.

## Debug Map Problems

If nodes are not clickable:

- Is `node["available"]` true?
- Is the click position correct?
- Does `get_clicked_map_node` return only available nodes?

If map has dead ends:

- Check `make_every_next_node_reachable`.
- Check every current node has at least one connection.

If map lines cross too much:

- Check `remove_crossing_connections`.

If all nodes are battles:

- Check `possible_types`.
- Check `guarantee_battle_in_layer`.

---

# Chapter 22: Drawing, UI, Popups, And Windows

Drawing happens after updates.

The battle drawing order:

1. Background.
2. Grids.
3. Characters and enemies.
4. HP/counters/status.
5. Death/projectile/damage popups.
6. Enemy hover tooltip.
7. Reaction red edges.
8. Swing/discard popups.
9. Hand cards.
10. Pile buttons.
11. Pile viewer.
12. Game over popup.
13. Dev menu.

If something is hidden, draw it later.

If something covers too much, draw it earlier or move it.

## Add A New Popup

Step 1: State in `main.py`.

```python
my_popup_open = False
```

Step 2: Draw function in a screen file.

```python
def draw_my_popup(screen, font):
    popup_rect = pygame.Rect(250, 150, 700, 500)
    pygame.draw.rect(screen, (30, 30, 40), popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 2)
```

Step 3: Open it.

```python
my_popup_open = True
```

Step 4: Handle clicks before normal battle clicks.

```python
if my_popup_open:
    if close_rect.collidepoint(event.pos):
        my_popup_open = False

    continue
```

Step 5: Draw it.

```python
if my_popup_open:
    draw_my_popup(screen, font)
```

Step 6: Reset it at battle start if needed.

```python
my_popup_open = False
```

## Draw A Button

Buttons use `Button`.

Create:

```python
my_button = Button(500, 300, 200, 70, "Text")
```

Draw:

```python
my_button.draw(screen, font)
```

Click:

```python
if my_button.is_clicked(event.pos):
    print("clicked")
```

---

# Chapter 23: Assets, Sprites, Animations, And Sounds

## Relative Asset Paths

Always use:

```python
asset_path("assets/...")
```

Never use:

```python
"/home/corbin/Desktop/Game/assets/..."
```

## Card Art

In card data:

```python
"image_path": "assets/card_templtes/card art/new_art.png"
```

Card art is loaded by:

```python
cards/card_renderer.py
```

## Enemy Sprites

File:

```text
loaders/battle_assets.py
```

Load:

```python
slime_assets = load_tiny_rpg_asset("Slime", "Attack01", 1.25)
```

Scale is the last number.

Bigger:

```python
slime_assets = load_tiny_rpg_asset("Slime", "Attack01", 1.7)
```

## Character Sprites

Files:

```text
Characters/archer.py
Characters/warrior.py
```

Attack scale:

```python
"sprite_scale": 2.1
```

## Flip Direction

Use:

```python
"flip_x": True
```

or:

```python
"flip_x": False
```

For players, pressing `R` flips selected character.

## Animation Speeds

In `main.py`:

```python
enemy_animation_speed = 16
enemy_attack_speed = 6
player_animation_speed = 16
```

Lower number means faster.

In `battle_animations.py`:

```python
PLAYER_ATTACK_FRAME_SPEED = 4
PLAYER_DEATH_FRAME_SPEED = 9
ENEMY_DEATH_FRAME_SPEED = 8
PROJECTILE_SPEED = 0.13
```

## Damage Numbers

File:

```text
damage_numbers.py
```

Change popup duration:

```python
"duration": 38
```

Change float speed:

```python
draw_y = popup["y"] - int(popup["timer"] * 1.3) - height // 2
```

## Sounds

File:

```text
loaders/sound_assets.py
```

Load:

```python
sound = load_sound("assets/sound effects/my_sound.wav", 0.5)
```

Play:

```python
random.choice(possible_sounds).play()
```

Current attack sounds are played in:

```python
handle_card_feedback(card_result, acting_character)
```

---

# Chapter 24: Debugging And Common Breaks

## Run A Syntax Check

```bash
python3 -m py_compile main.py
```

All files:

```bash
python3 -m py_compile $(find . -name "*.py")
```

## Read Tracebacks

Look at the bottom line first.

Example:

```text
KeyError: 'idle_frames_flipped'
```

Means code tried:

```python
enemy["idle_frames_flipped"]
```

but that enemy dictionary did not have the key.

Likely fix:

- Assets were not applied.
- New enemy type missing from `enemy_assets`.
- Split enemy did not copy assets.

## Card Shows Highlight But Does Not Hit

Check:

```text
cards/card_effects.py
```

Damage shape is wrong.

## Card Hits But Does Not Highlight

Check:

```text
cards/card_targeting.py
```

Preview shape is missing/wrong.

## Card Does Nothing

Check:

- Is the effect registered in `CARD_EFFECTS`?
- Does character pass `character_can_use_card`?
- Is energy enough?
- Is a modal active?
- Is card type valid?

## Enemy Is Invisible

Check:

- Enemy type has assets in `loaders/battle_assets.py`.
- `apply_enemy_assets(enemies, enemy_assets)` ran after spawning.
- Sprite path exists.
- Sprite scale is not too small.

## Enemy Movement Wrong

Check:

- Possible tiles in `battle_setup.py`.
- Actual queue in `battle_turn_logic.py`.
- `can_land_on_tile`.
- Correct grid.

## Map Node Not Clickable

Check:

- `node["available"]`
- `get_clicked_map_node`
- `complete_map_node`
- node position from `get_node_screen_pos`

## Keyboard Crash

Only mouse events have `event.pos`.

Make sure `event.pos` is inside:

```python
if event.type == pygame.MOUSEBUTTONDOWN:
    ...
```

---

# Chapter 25: Build Recipes For Bigger Ideas

These are examples of mixing systems.

## Recipe 1: Card That Hits Area And Leaves Poison Cloud

Files:

- `cards/card_library.py`
- `cards/card_effects.py`
- `cards/card_targeting.py`
- `battle_setup.py`
- `battle_grid.py`
- `battle_renderer.py`

Data:

```python
"poison_cloud": {
    "name": "Poison Cloud",
    "cost": 2,
    "thickness": 0.5,
    "type": "attack",
    "rarity": "rare",
    "effect": "poison_cloud",
    "damage": 4,
    "poison_damage": 2,
    "poison_turns": 3,
    "cloud_duration": 3,
    "description": "Damage an area and leave poison.",
    "image_path": "assets/card_templtes/card art/Snare_trap.png"
}
```

Effect idea:

```python
def play_poison_cloud(card, selected_character, enemies):
    hits = []
    tiles = get_poison_cloud_tiles(selected_character)

    for enemy in enemies:
        if (enemy["row"], enemy["col"]) in tiles:
            damage_enemy(enemy, card["damage"], hits)
            enemy["poison_turns"] = max(enemy.get("poison_turns", 0), card["poison_turns"])
            enemy["poison_damage"] = max(enemy.get("poison_damage", 0), card["poison_damage"])

    traps = []

    for row, col in tiles:
        traps.append({
            "kind": "poison_cloud",
            "row": row,
            "col": col,
            "duration": card["cloud_duration"],
            "poison_turns": card["poison_turns"],
            "poison_damage": card["poison_damage"]
        })

    return {
        "hits": hits,
        "traps": traps
    }
```

Then:

- `trigger_enemy_traps` applies poison when enemy enters cloud.
- end-turn effect ticks poison.
- `battle_grid.py` draws poison cloud color.
- `battle_renderer.py` shows poison in tooltip.

## Recipe 2: Enemy That Charges Across A Row

Files:

- `battle_setup.py`
- `battle_turn_logic.py`
- `battle_renderer.py`

Enemy data:

```python
def build_charger(row, col):
    return {
        "name": "Charger",
        "type": "charger",
        "board": "enemy",
        "row": row,
        "col": col,
        "hp": 35,
        "max_hp": 35,
        "attack_damage": 8,
        "attack_interval": 2,
        "turns_until_attack": 2,
        "flip_x": True
    }
```

Attack:

```python
def choose_charger_attack(enemy, player_grid_data):
    for col in range(GRID_COLS):
        add_incoming_attack(player_grid_data, enemy["row"], col, enemy)
```

Movement:

```python
def get_charger_movement_steps(enemy, enemy_grid_data):
    steps = []

    for step_index in range(2):
        next_col = enemy["col"] - (step_index + 1)

        if not can_land_on_tile(enemy_grid_data, enemy["row"], next_col, enemy):
            break

        steps.append({
            "enemy": enemy,
            "row_change": 0,
            "col_change": -1,
            "is_final_step": False
        })

    if steps:
        steps[-1]["is_final_step"] = True

    return steps
```

Then add it to `build_enemy_movement_queue`.

## Recipe 3: Reward That Gives Gold

Files:

- `main.py`
- `screens/reward_screen.py`

State:

```python
gold = 0
```

Reward click:

```python
if reward_choice == "gold":
    gold += 25
    current_state = MAP
```

Draw:

```python
gold_text = font.render("Gold: " + str(gold), True, WHITE)
screen.blit(gold_text, (20, 110))
```

If shop later spends gold:

```python
if gold >= card_price:
    gold -= card_price
    player_deck.append(card.copy())
```

## Recipe 4: New Map Node That Opens Upgrade Screen

Files:

- `maps/map_loader.py`
- `screens/map_screen.py`
- `main.py`
- maybe `screens/reward_screen.py`

Add node type:

```python
possible_types.append("upgrade")
```

Handle click:

```python
if clicked_node["type"] == "upgrade":
    selected_sleeve = CARD_SLEEVES["premium_sleeve"]
    reward_mode = "choose_sleeve_card"
    current_state = REWARD
```

This reuses the sleeve upgrade UI.

## Final Rule

When you change a thing, look for its matching thing.

```text
Card data -> card effect -> card preview -> card description
Enemy data -> enemy attack -> enemy movement -> enemy assets -> enemy tooltip
Status applied -> status ticks -> status blocks something -> status icon
Map node created -> map node drawn -> map node clicked -> map node reward/action
Popup state -> popup drawing -> popup click handling -> popup reset
```

That is the whole game in one sentence: data, rules, preview, drawing, reset.
