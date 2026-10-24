<p align="center">
  <img src="HeroesQuest.png" width="160" alt="Heroes Quest icon">
</p>

<h1 align="center">Heroes Quest</h1>

<p align="center">A turn-based fantasy RPG for the terminal.</p>

---

The sky has cracked. From the wound above the world, the Celestial Entity whispers to every beast and shade below, and they answer. The kingdom has one hero left. It is you.

Fight your way through four acts and twelve battles, from the haunted Whisperwood to the Shattered Heavens. Read your enemies, outplay them and grow stronger with every victory.

## Download

**No Python needed:** grab `Heroes Quest.exe` from the [Releases](../../releases) page and double-click it.

**Run from source:**
```
python "Heroes Quest.py"
```

Supports: Python Crossplatform (Windows, MacOS and Linux.)

## How to play

Every turn the enemy shows its **intent**, meaning what it will do next. That's the key to winning.

| Intent | What it means | How to answer |
|---|---|---|
| Attack | A normal hit | Attack back |
| Heavy attack | Hits twice as hard | Guard, shield up or interrupt |
| Gathering power | Next turn it unleashes a devastating blow | Interrupt it, or prepare to guard or dodge |
| Bracing | Your damage is halved this turn | Heal, guard or set up instead |
| Healing | It restores its health | Hit hard before it recovers |
| Curse | Weakens your attacks for 2 turns | Dodge it, or cleanse it |

Bosses grow stronger once they drop below half health.

### Controls

| Key | Action |
|---|---|
| `A` | Attack |
| `B` | Guard: take half damage and regain Rage or Mana |
| `C` | Drink a potion: heal 40% HP and stop bleeding |
| `D` to `G` | Class abilities |
| `Enter` | Repeat your last action |
| Any key | Skip pause screens |
| `Ctrl+C` | Quit |

## Classes

### ⚔️ Warrior
A veteran of a hundred sieges who only gets angrier as the fight drags on. Builds **Rage** by hitting and being hit. The most forgiving class.
- **Aegis:** a shield worth 25% of your max HP for 2 turns
- **Shield Bash:** catches heavy or charged attacks mid-swing and stuns the enemy
- **Execute:** a finisher that triples in power on low-health enemies

### 🔥 Sorcerer
A scholar of the burning arts. Fragile, but controls the fight with **Mana**. The hardest class.
- **Fireball:** big damage and sets the enemy on fire
- **Frost Lance:** halves the next enemy hit and breaks charged attacks
- **Mightycure:** heals 35% HP and cleanses ailments
- **Chant:** instantly restores 60 Mana

### 🗡️ Ninja
A shadow from the eastern isles. Lands **critical hits** a quarter of the time.
- **Alpha Strike:** four quick blows that can each crit
- **Smoke Bomb:** dodge the enemy's next action, and your next hit is a guaranteed crit
- **Venom Blade:** stacks poison that hurts every turn

### 🛡️ Guardian
An oathbound knight who carries the souls of the fallen. Gains a **soul** from every kill, growing tougher as the journey goes on.
- **Judgement:** a holy strike that gets stronger with every soul
- **Sanctuary:** heals and shields you
- **Rebuke:** blocks most of a hit and reflects it back at the attacker

## The journey

| Act | Region | Boss |
|---|---|---|
| I | The Whisperwood | The Slime King |
| II | The Crimson Crypts | Red Crimson Demon |
| III | The Ashen Peaks | Titan |
| IV | The Shattered Heavens | The Celestial Entity |

Each act has two battles against random monsters, then a boss. After every victory you level up and **choose a blessing**: more health, strength, defense or a class perk.

Between battles the road splits, and you pick one:
- **Campfire:** rest and recover 35% HP
- **Merchant:** spend gold on potions, strength, defense or max HP
- **Shrine:** pray to the old gods for a blessing, gold or a full heal. They aren't always in a good mood.

Beating a boss fully heals you before the next act.

## Tips

- Never ignore *gathering power*. An unleashed attack can take half your health.
- Save your interrupt or dodge for big hits instead of using it on cooldown.
- An enemy that's bracing is a free turn to heal or build Rage and Mana.
- Potions are limited (you can carry 5). The Merchant and boss drops are your main supply.

## Changelog

**v2.0**
- Full rework: 4 acts, 12 battles, enemy intents, status effects, bosses with enrage phases
- Reworked every class and ability for balance, and gave the Guardian real abilities
- Level-up blessings, merchant, campfire and shrine
- Cleaner colored output using rich
- Fixed the game slowly breaking over time, plus many ability bugs
- Removed the forced 10–30 second waits

**v1:** the original version.
---
Made by splars#1252