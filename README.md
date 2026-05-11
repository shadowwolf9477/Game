<<<<<<< ours

=======
# Roguelike Card Game Learning Project

This repo is for building a small visual roguelike card game while learning C# step by step.

The goal is **not** to paste in a finished game. Each milestone below gives you a focused feature, the C# idea you will learn, and the kind of file where your own code should go.

## Engine direction

You said you do **not** want MonoGame and you want a game with assets, not a text-only console game. A good first choice is one of these:

| Engine | Why it fits | Notes |
| --- | --- | --- |
| **Godot with C#/.NET** | Free, lightweight, good for 2D UI/card games, scene-based workflow. | Use the .NET build of Godot. C# editor support inside Godot is limited, so use VS Code, Rider, or Visual Studio for scripts. |
| **Unity 2D** | Very common C# learning path, lots of card-game and UI tutorials. | Bigger editor and more services than we need for a first small game. |

Recommended starting point: **Godot C#** unless you already know you want Unity. It keeps the project small and lets us focus on C# fundamentals plus game structure.

## First playable target

Build a tiny vertical slice before designing every card:

1. A main menu opens a battle scene.
2. The player sees a hand of 3 cards with art placeholders.
3. Clicking a card spends energy and damages an enemy.
4. The enemy attacks at end of turn.
5. Winning gives a simple reward choice.
6. The player moves to the next randomly chosen encounter.

That is enough to prove the roguelike card loop without overbuilding.

## Suggested project structure

If using Godot, create folders like this inside the Godot project:

```text
Game/
  scenes/
    MainMenu.tscn
    Battle.tscn
    CardView.tscn
    EnemyView.tscn
  scripts/
    cards/
      CardData.cs
      CardView.cs
      Deck.cs
    battle/
      BattleController.cs
      PlayerState.cs
      EnemyState.cs
      TurnManager.cs
    run/
      RunState.cs
      EncounterGenerator.cs
  assets/
    art/
      cards/
      enemies/
      ui/
    audio/
```

Do not create every file at once. Add a file only when the current lesson needs it.

## How I will teach you C# in this project

When we work on a feature, I will use this format:

1. **What you are building** - the visible game feature.
2. **C# idea** - the programming concept behind it.
3. **Where to create the file** - the exact folder and file name.
4. **Small example** - a short snippet, not the whole finished solution.
5. **Your task** - what you should type yourself.
6. **How to test it** - what should happen in the game.

Example style:

```csharp
public int Damage = 6;

public void Play()
{
    // Later this will damage the enemy.
}
```

Where it would go: `scripts/cards/CardData.cs`, inside a class that represents one card's rules.

What this teaches: fields, methods, and how game data can live in a class.

## Milestone roadmap

### Milestone 1: Project setup and first scene

**Feature:** Open the game and show a blank battle table with a background image.

**C# you learn:** What a class is, what a method is, and how scripts attach to scene objects.

**Likely files:**

- `scenes/Battle.tscn`
- `scripts/battle/BattleController.cs`
- `assets/art/ui/battle_background.png`

### Milestone 2: Card data

**Feature:** Define one card named `Strike` with cost and damage.

**C# you learn:** Classes, fields/properties, constructors, and simple data modeling.

**Likely file:**

- `scripts/cards/CardData.cs`

Example concept only:

```csharp
public class CardData
{
    public string Name;
    public int Cost;
    public int Damage;
}
```

You would use this in battle code when the player clicks a card.

### Milestone 3: Drawing cards

**Feature:** Start combat with 3 cards in hand.

**C# you learn:** Lists, loops, and separating deck/hand/discard piles.

**Likely files:**

- `scripts/cards/Deck.cs`
- `scripts/battle/BattleController.cs`

### Milestone 4: Card visuals

**Feature:** Each card appears as a visual asset with name, cost, and art.

**C# you learn:** Connecting code to UI nodes and updating labels/images.

**Likely files:**

- `scenes/CardView.tscn`
- `scripts/cards/CardView.cs`
- `assets/art/cards/strike.png`

### Milestone 5: Turns and energy

**Feature:** Player has energy, cards spend energy, and the end-turn button starts the enemy turn.

**C# you learn:** Booleans, conditions, methods that return success/failure, and basic state machines.

**Likely files:**

- `scripts/battle/TurnManager.cs`
- `scripts/battle/PlayerState.cs`

### Milestone 6: Enemy actions

**Feature:** Enemy shows intent and attacks after the player ends turn.

**C# you learn:** Encapsulation, method parameters, and keeping player/enemy state separate.

**Likely files:**

- `scripts/battle/EnemyState.cs`
- `scripts/battle/BattleController.cs`

### Milestone 7: Roguelike run loop

**Feature:** After winning, choose a reward and go to the next encounter.

**C# you learn:** Random numbers, saving temporary run state, and passing data between scenes.

**Likely files:**

- `scripts/run/RunState.cs`
- `scripts/run/EncounterGenerator.cs`

## Asset plan

Start with placeholders so programming does not get blocked:

- Card art: simple colored rectangles or free placeholder icons.
- Enemy art: one static image per enemy.
- UI: readable fonts, clear buttons, simple energy/health icons.

Replace placeholders after the first playable battle works.

## Details to decide later

When you are ready, give me these details and we will turn them into the first milestone:

1. Engine choice: Godot C# or Unity 2D?
2. Theme: fantasy, sci-fi, horror, cute, etc.?
3. Player character: one hero or multiple classes?
4. Core resources: energy only, or energy plus mana/block/status effects?
5. Cards: attack/defense only at first, or special card types too?
6. Visual style: pixel art, hand-drawn, clean UI, dark gothic, etc.?

## Learning rule for this repo

I should guide you and give small examples, but you should write the final code yourself. If I suggest code, I will also say exactly which file it belongs in and what part of the game will use it.
>>>>>>> theirs
