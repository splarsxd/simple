import os
import sys
import time
import inspect
from random import random, randint, uniform, choices, sample
import rich
from rich.markup import escape

if os.name == "nt":
    import msvcrt
else:
    import select
    import termios
    import tty

VERSION = "2.0"

cls = lambda: os.system("cls" if os.name == "nt" else "clear")


def setup_terminal():
    if os.name == "nt":
        os.system(f"title Heroes Quest v{VERSION}")


def wait(seconds=None):
    rich.print("\n[bright_black]Press any key to continue...[/]")
    if os.name == "nt":
        end = None if seconds is None else time.time() + seconds
        while end is None or time.time() < end:
            if msvcrt.kbhit():
                msvcrt.getwch()
                return
            time.sleep(0.02)
        return
    if not sys.stdin.isatty():
        return
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        if select.select([sys.stdin], [], [], seconds)[0]:
            os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def ask():
    rich.print("\n[bold cyan]>>[/] ", end="")
    return input().strip().lower()


def bar(current, maximum, color, width=24):
    filled = round(width * max(0, current) / maximum) if maximum else 0
    filled = min(width, filled)
    return f"[{color}]{'█' * filled}[/][bright_black]{'░' * (width - filled)}[/]"


CLASSES = {
    "a": {
        "id": "warrior", "name": "Warrior", "color": "red",
        "hp": 130, "str": 10, "defense": 8, "crit": 5, "crit_mult": 1.75,
        "lore": "A veteran of a hundred sieges who only gets angrier as the fight drags on.",
        "play": "Builds Rage by hitting and being hit, then spends it on brutal finishers.",
    },
    "b": {
        "id": "sorcerer", "name": "Sorcerer", "color": "magenta",
        "hp": 90, "str": 13, "defense": 3, "crit": 5, "crit_mult": 1.75,
        "lore": "A scholar of the burning arts, expelled from the Academy for asking the wrong questions.",
        "play": "Fragile, but controls the fight with fire, frost and healing magic.",
    },
    "c": {
        "id": "ninja", "name": "Ninja", "color": "green",
        "hp": 95, "str": 11, "defense": 4, "crit": 25, "crit_mult": 2.0,
        "lore": "A shadow from the eastern isles. Nobody hears the first strike.",
        "play": "High crit chance, stacking poison and dodges. Hit hard, never get hit.",
    },
    "d": {
        "id": "guardian", "name": "Guardian", "color": "yellow",
        "hp": 125, "str": 8, "defense": 9, "crit": 5, "crit_mult": 1.75,
        "lore": "An oathbound knight who carries the souls of every foe they have laid to rest.",
        "play": "Grows stronger with every kill and punishes enemies that strike into Rebuke.",
    },
}

ABILITIES = {
    "warrior": [
        {"id": "aegis", "name": "Aegis", "cd": 5, "desc": "shield worth 25% max HP for 2 turns"},
        {"id": "bash", "name": "Shield Bash", "cd": 3, "rage": 20, "desc": "1.2x damage, stuns heavy or charged attacks"},
        {"id": "execute", "name": "Execute", "cd": 0, "rage": 40, "desc": "1.6x damage, 3x below 35% HP"},
    ],
    "sorcerer": [
        {"id": "fireball", "name": "Fireball", "cd": 0, "mana": 25, "desc": "1.7x damage + burn for 3 turns"},
        {"id": "frost", "name": "Frost Lance", "cd": 2, "mana": 15, "desc": "halves the next enemy hit, breaks charges"},
        {"id": "cure", "name": "Mightycure", "cd": 3, "mana": 40, "desc": "heal 35% max HP and cleanse"},
        {"id": "chant", "name": "Chant", "cd": 5, "desc": "restore 60 mana and heal 8%"},
    ],
    "ninja": [
        {"id": "alpha", "name": "Alpha Strike", "cd": 3, "desc": "4 hits of 0.55x, each can crit"},
        {"id": "smoke", "name": "Smoke Bomb", "cd": 4, "desc": "dodge the next enemy action, next hit crits"},
        {"id": "venom", "name": "Venom Blade", "cd": 2, "desc": "0.7x damage + 2 poison stacks"},
    ],
    "guardian": [
        {"id": "judgement", "name": "Judgement", "cd": 2, "desc": "1.3x damage, +0.08x per soul"},
        {"id": "sanctuary", "name": "Sanctuary", "cd": 4, "desc": "heal 18% max HP + 12% shield"},
        {"id": "rebuke", "name": "Rebuke", "cd": 3, "desc": "block 60% of hits this turn and reflect them"},
    ],
}
ABILITY_BY_ID = {ab["id"]: ab for abilities in ABILITIES.values() for ab in abilities}

INTENTS = {
    "strike": ("attack", "bright_white"),
    "heavy": ("heavy attack", "bold red"),
    "rend": ("attack that leaves you wounded", "red"),
    "drain": ("life-draining attack", "magenta"),
    "multi": ("three quick hits", "red"),
    "curse": ("weakens your attacks", "magenta"),
    "charge": ("gathering power, unleashes next turn", "bold yellow"),
    "unleash": ("DEVASTATING attack: guard, interrupt or dodge", "bold red"),
    "defend": ("bracing, your damage is halved", "cyan"),
    "heal": ("healing itself", "green"),
    "enrage": ("about to grow stronger", "bold red"),
}

ENEMY_MULTS = {"strike": 1.0, "heavy": 2.0, "unleash": 3.2, "drain": 0.8, "rend": 0.7}

ACTS = [
    {
        "name": "Act I: The Whisperwood",
        "intro": "Ancient oaks lean close and murmur in a tongue older than kings. Something large moves between them, and the moss is wet with more than dew.",
        "grave": "The Whisperwood grows a little greener where you fell.",
        "pool": [
            {"name": "Werewolf", "desc": "Half man, half hunger. Its eyes catch the moonlight like coins.",
             "hp": 78, "str": 12, "moves": [("strike", "Bite", 4), ("rend", "Savage Claws", 3), ("heavy", "Pounce", 2)]},
            {"name": "Stone Golem", "desc": "Moss-covered and patient. It has guarded these woods since before there were roads.",
             "hp": 110, "str": 10, "moves": [("strike", "Stone Fist", 3), ("defend", "Granite Skin", 2), ("charge", "Earthshatter", 2)]},
            {"name": "Bog Slime", "desc": "A quivering heap of swamp, and of everything the swamp has eaten.",
             "hp": 84, "str": 10, "moves": [("strike", "Engulf", 4), ("curse", "Acid Spit", 2), ("heal", "Reform", 2)]},
        ],
        "boss": {"name": "The Slime King", "desc": "A gelatinous tyrant wearing the crowns of every knight it has swallowed.",
                 "hp": 200, "str": 13, "enrage": "Royal Tantrum",
                 "moves": [("strike", "Royal Slam", 3), ("multi", "Spawn Slimelings", 2), ("charge", "Crushing Decree", 2),
                           ("heal", "Absorb", 1), ("curse", "Corrosive Ooze", 1)]},
    },
    {
        "name": "Act II: The Crimson Crypts",
        "intro": "Beneath the ruined abbey, candles still burn for the dead. The dead do not appreciate it.",
        "grave": "Your name is carved on a crypt wall, among a thousand others.",
        "pool": [
            {"name": "Vampire", "desc": "An old noble in an older coat. It smiles with far too many teeth.",
             "hp": 143, "str": 18, "moves": [("strike", "Claw", 3), ("drain", "Crimson Kiss", 3), ("curse", "Mesmerize", 1), ("defend", "Mist Form", 1)]},
            {"name": "Reaper", "desc": "A robe, a scythe, and a ledger with your name already written in it.",
             "hp": 130, "str": 21, "moves": [("strike", "Scythe", 3), ("heavy", "Harvest", 3), ("charge", "Death Sentence", 1)]},
            {"name": "Ghoul", "desc": "It used to be a gravedigger. Now it just digs.",
             "hp": 156, "str": 17, "moves": [("strike", "Gnaw", 3), ("rend", "Rotting Claws", 3), ("multi", "Frenzy", 2)]},
        ],
        "boss": {"name": "Red Crimson Demon", "desc": "Chained beneath the abbey for three centuries. The chains broke this morning.",
                 "hp": 390, "str": 23, "enrage": "Demonic Ascension",
                 "moves": [("strike", "Hellfire Claw", 3), ("heavy", "Brimstone Fist", 2), ("charge", "Inferno", 2),
                           ("drain", "Soul Siphon", 1), ("rend", "Searing Chains", 1)]},
    },
    {
        "name": "Act III: The Ashen Peaks",
        "intro": "These mountains have burned for a hundred years. Ash falls like snow, and the wind carries the sound of enormous wings.",
        "grave": "The ash settles over you like a blanket. The peaks keep burning.",
        "pool": [
            {"name": "Wraith", "desc": "A cold spot in the shape of a person, still mourning something it cannot remember.",
             "hp": 195, "str": 26, "moves": [("strike", "Chill Touch", 3), ("curse", "Wail", 2), ("drain", "Life Tap", 2), ("defend", "Fade", 1)]},
            {"name": "Wyvern", "desc": "A smaller cousin of the dragons, and much angrier about it.",
             "hp": 228, "str": 27, "moves": [("strike", "Tail Lash", 3), ("multi", "Raking Talons", 2), ("charge", "Venom Dive", 2)]},
            {"name": "Ash Elemental", "desc": "The mountain's fury, given legs and a grudge.",
             "hp": 214, "str": 26, "moves": [("strike", "Cinder Fist", 3), ("rend", "Ember Burn", 2), ("defend", "Harden", 1), ("heavy", "Magma Burst", 2)]},
        ],
        "boss": {"name": "Titan", "desc": "The last of the giants who built the world. It would like it back.",
                 "hp": 559, "str": 32, "enrage": "Titanic Wrath",
                 "moves": [("strike", "Colossal Swing", 2), ("heavy", "Mountain Breaker", 3), ("charge", "Cataclysm", 2),
                           ("defend", "Stone Bulwark", 2)]},
    },
    {
        "name": "Act IV: The Shattered Heavens",
        "intro": "A stair of broken starlight climbs into the wound in the sky. Up here, the angels have forgotten whose side they were on.",
        "grave": "You fall from the heavens like a star. Nobody below makes a wish.",
        "pool": [
            {"name": "Fallen Seraphim", "desc": "Six wings, all of them tarnished. It still hums a hymn, slightly off-key.",
             "hp": 286, "str": 35, "moves": [("strike", "Tarnished Blade", 3), ("multi", "Wings of Knives", 2), ("heal", "Stolen Grace", 1)]},
            {"name": "Void Herald", "desc": "It speaks for the emptiness between stars, and the emptiness has a lot to say.",
             "hp": 299, "str": 36, "moves": [("curse", "Whispers of the Void", 2), ("drain", "Unmake", 2), ("heavy", "Null Lance", 2), ("strike", "Void Touch", 2)]},
            {"name": "Celestial Sentinel", "desc": "A guardian of the gates, built from constellations and bad intentions.",
             "hp": 338, "str": 34, "moves": [("strike", "Halberd of Orion", 3), ("defend", "Shield of Stars", 2), ("charge", "Judgement Ray", 2)]},
        ],
        "boss": {"name": "The Celestial Entity", "desc": "The wound in the sky opens its eye. Every star you have ever wished on is part of it.",
                 "hp": 806, "str": 42, "enrage": "Ascension",
                 "moves": [("strike", "Starfall", 2), ("heavy", "Collapse", 2), ("charge", "Supernova", 2),
                           ("multi", "Shattered Light", 2), ("curse", "Gaze of Eternity", 1), ("heal", "Drink the Stars", 1)]},
    },
]

PERKS = {
    "vitality": ("Vitality", "+15 max HP"),
    "might": ("Might", "+3 strength"),
    "fortitude": ("Fortitude", "+3 defense"),
}
CLASS_PERKS = {
    "warrior": ("bulwark", "Bulwark", "Aegis shields 20% stronger"),
    "sorcerer": ("arcana", "Arcane Well", "+20 max mana"),
    "ninja": ("edge", "Keen Edge", "+5% crit chance"),
    "guardian": ("soulbind", "Soul Bind", "+1 soul"),
}

SHOP = [
    ("potion", "Healing Potion", "restores 40% HP", 25, 0),
    ("whetstone", "Dwarven Whetstone", "+2 strength", 40, 15),
    ("plating", "Mithril Plating", "+2 defense", 40, 15),
    ("crystal", "Heart Crystal", "+15 max HP", 40, 15),
]
MAX_POTIONS = 5


class Hero:
    def __init__(self, name, class_letter):
        c = CLASSES[class_letter]
        self.name = name
        self.key = c["id"]
        self.title = c["name"]
        self.color = c["color"]
        self.level = 1
        self.max_hp = self.hp = c["hp"]
        self.strength = c["str"]
        self.defense = c["defense"]
        self.crit = c["crit"]
        self.crit_mult = c["crit_mult"]
        self.max_mana = 100
        self.souls = 0
        self.aegis_mult = 1.0
        self.potions = 2
        self.gold = 0
        self.prices = {item[0]: item[3] for item in SHOP}
        self.stats = {"slain": 0, "turns": 0, "dealt": 0, "taken": 0, "potions": 0, "gold": 0}
        self.reset_battle()

    def reset_battle(self):
        self.rage = 0
        self.mana = self.max_mana
        self.shield = 0
        self.shield_turns = 0
        self.guarding = False
        self.rebuke = False
        self.dodge = False
        self.sure_crit = False
        self.weaken = 0
        self.wound = 0
        self.wound_dmg = 0
        self.cooldowns = {}

    def heal(self, amount):
        amount = max(0, min(round(amount), self.max_hp - self.hp))
        self.hp += amount
        return amount

    def add_soul(self):
        self.souls += 1
        self.max_hp += 5
        self.hp += 5


class Enemy:
    def __init__(self, template, boss=False):
        self.name = template["name"]
        self.desc = template["desc"]
        self.max_hp = self.hp = template["hp"]
        self.strength = template["str"]
        self.moves = template["moves"]
        self.enrage_name = template.get("enrage", "Fury")
        self.boss = boss
        self.enraged = False
        self.charged = None
        self.stunned = False
        self.chilled = False
        self.burn = 0
        self.burn_dmg = 0
        self.poison = 0
        self.last_kind = None


class Battle:
    def __init__(self, hero, template, boss=False):
        self.hero = hero
        self.enemy = Enemy(template, boss)
        hero.reset_battle()
        self.log = []
        self.turn = 1
        self.intent = None
        self.damaging = False
        self.next_intent()

    @property
    def en(self):
        return f"[bold red]{self.enemy.name}[/]"

    def say(self, text):
        self.log.append(text)

    def next_intent(self):
        e = self.enemy
        if e.charged:
            self.intent = ("unleash", e.charged)
            e.charged = None
        elif e.boss and not e.enraged and e.hp <= e.max_hp / 2:
            self.intent = ("enrage", e.enrage_name)
            e.enraged = True
        else:
            options = [
                m for m in e.moves
                if not (m[0] == "heal" and e.hp > e.max_hp * 0.6)
                and not (m[0] in ("defend", "charge", "heal", "curse") and m[0] == e.last_kind)
            ]
            move = choices(options, weights=[m[2] for m in options])[0]
            self.intent = (move[0], move[1])
        e.last_kind = self.intent[0]

    def check(self, ab):
        h = self.hero
        cd = h.cooldowns.get(ab["id"], 0)
        if cd:
            return False, f"{cd} turn{'s' if cd > 1 else ''}"
        if h.rage < ab.get("rage", 0):
            return False, f"needs {ab['rage']} rage"
        if h.mana < ab.get("mana", 0):
            return False, f"needs {ab['mana']} mana"
        return True, ""

    def actions(self):
        h = self.hero
        acts = [("a", "attack"), ("b", "guard"), ("c", "potion")]
        acts += [(letter, ab["id"]) for letter, ab in zip("defg", ABILITIES[h.key])]
        return acts

    def strike(self, mult, label, crit_ok=True, quiet=False):
        h, e = self.hero, self.enemy
        dmg = h.strength * mult * uniform(0.9, 1.1)
        crit = crit_ok and (h.sure_crit or random() * 100 < h.crit)
        if crit:
            dmg *= h.crit_mult
        if h.weaken:
            dmg *= 0.7
        if self.intent[0] == "defend":
            dmg *= 0.5
        dmg = max(1, round(dmg))
        e.hp = max(0, e.hp - dmg)
        h.stats["dealt"] += dmg
        self.damaging = True
        if not quiet:
            tag = " [bold yellow]CRIT![/]" if crit else ""
            self.say(f"Your [bold]{label}[/] hits {self.en} for [bold]{dmg}[/].{tag}")
        return dmg, crit

    def gain_rage(self, amount):
        h = self.hero
        if h.key == "warrior":
            h.rage = min(100, h.rage + amount)

    def player_turn(self, letter):
        h, e = self.hero, self.enemy
        acts = dict(self.actions())
        if letter not in acts:
            self.say("[yellow]That's not a valid action.[/]")
            return False
        action = acts[letter]
        self.damaging = False

        if action == "attack":
            self.strike(1.0, "Attack")
            self.gain_rage(12)
        elif action == "guard":
            h.guarding = True
            extra = ""
            if h.key == "warrior":
                self.gain_rage(15)
                extra = " [red]+15 rage[/]"
            elif h.key == "sorcerer":
                h.mana = min(h.max_mana, h.mana + 25)
                extra = " [blue]+25 mana[/]"
            self.say(f"You raise your guard.{extra}")
        elif action == "potion":
            if not h.potions:
                self.say("[yellow]You have no potions left.[/]")
                return False
            h.potions -= 1
            h.stats["potions"] += 1
            healed = h.heal(h.max_hp * 0.4)
            h.wound = 0
            self.say(f"You drink a healing potion. [green]+{healed} HP[/]")
        else:
            ab = ABILITY_BY_ID[action]
            ok, why = self.check(ab)
            if not ok:
                self.say(f"[yellow]{ab['name']} is not ready ({why}).[/]")
                return False
            h.rage -= ab.get("rage", 0)
            h.mana -= ab.get("mana", 0)
            if ab["cd"]:
                h.cooldowns[action] = ab["cd"]
            getattr(self, f"ab_{action}")()

        if self.damaging:
            h.sure_crit = False
        return True

    def ab_aegis(self):
        h = self.hero
        amount = round(h.max_hp * 0.25 * h.aegis_mult)
        h.shield = max(h.shield, amount)
        h.shield_turns = 2
        self.say(f"A wall of golden light rises before you. [cyan]{amount} shield[/]")

    def ab_bash(self):
        self.strike(1.2, "Shield Bash")
        if self.intent[0] in ("heavy", "charge", "unleash"):
            self.enemy.stunned = True
            self.say(f"You catch {self.en} mid-swing. It reels, [yellow]stunned[/]!")

    def ab_execute(self):
        e = self.enemy
        low = e.hp <= e.max_hp * 0.35
        self.strike(3.0 if low else 1.6, "Execute")

    def ab_fireball(self):
        h, e = self.hero, self.enemy
        self.strike(1.7, "Fireball")
        e.burn = 3
        e.burn_dmg = max(1, round(h.strength * 0.35))
        self.say(f"{self.en} is [bold red]burning[/].")

    def ab_frost(self):
        e = self.enemy
        self.strike(1.0, "Frost Lance")
        e.chilled = True
        self.say(f"Frost creeps over {self.en}. Its next action is [cyan]chilled[/].")

    def ab_cure(self):
        h = self.hero
        healed = h.heal(h.max_hp * 0.35)
        h.weaken = 0
        h.wound = 0
        self.say(f"Mightycure washes over you. [green]+{healed} HP[/], ailments cleansed.")

    def ab_chant(self):
        h = self.hero
        before = h.mana
        h.mana = min(h.max_mana, h.mana + 60)
        healed = h.heal(h.max_hp * 0.08)
        self.say(f"You chant the old words. [blue]+{h.mana - before} mana[/] [green]+{healed} HP[/]")

    def ab_alpha(self):
        hits = [self.strike(0.55, "Alpha Strike", quiet=True) for _ in range(4)]
        parts = [f"[bold yellow]{d}![/]" if c else str(d) for d, c in hits]
        self.say(f"[bold]Alpha Strike[/] lands four blows on {self.en}: {', '.join(parts)} = [bold]{sum(d for d, _ in hits)}[/]")

    def ab_smoke(self):
        h = self.hero
        h.dodge = True
        h.sure_crit = True
        self.say("You vanish in a cloud of smoke. Your next hit will [bold yellow]crit[/].")

    def ab_venom(self):
        e = self.enemy
        self.strike(0.7, "Venom Blade")
        e.poison = min(8, e.poison + 2)
        self.say(f"{self.en} is poisoned. [green]{e.poison} stacks[/]")

    def ab_judgement(self):
        h = self.hero
        self.strike(1.3 + 0.08 * h.souls, "Judgement")

    def ab_sanctuary(self):
        h = self.hero
        healed = h.heal(h.max_hp * 0.18)
        amount = round(h.max_hp * 0.12)
        h.shield = max(h.shield, amount)
        h.shield_turns = 2
        self.say(f"Holy ground blooms beneath you. [green]+{healed} HP[/] [cyan]{amount} shield[/]")

    def ab_rebuke(self):
        self.hero.rebuke = True
        self.say("You plant your feet and raise your shield. [yellow]Rebuke[/] is ready.")

    def hit_hero(self, mult):
        h, e = self.hero, self.enemy
        dmg = e.strength * mult * uniform(0.9, 1.1)
        if e.chilled:
            dmg *= 0.5
        dmg *= 100 / (100 + 2 * h.defense)
        if h.guarding:
            dmg *= 0.5
        reflected = 0
        if h.rebuke:
            reflected = max(1, round(dmg))
            dmg *= 0.4
            e.hp = max(0, e.hp - reflected)
            h.stats["dealt"] += reflected
        dmg = max(1, round(dmg))
        absorbed = min(h.shield, dmg)
        h.shield -= absorbed
        dmg -= absorbed
        h.hp = max(0, h.hp - dmg)
        h.stats["taken"] += dmg
        self.gain_rage(12)
        return dmg, absorbed, reflected

    def describe_hit(self, dmg, absorbed, reflected):
        text = f"you take [bold red]{dmg}[/]"
        if absorbed:
            text += f" [cyan]({absorbed} absorbed)[/]"
        if reflected:
            text += f", Rebuke reflects [bold yellow]{reflected}[/]"
        return text

    def enemy_turn(self):
        h, e = self.hero, self.enemy
        kind, move = self.intent

        if e.stunned:
            e.stunned = False
            e.chilled = False
            self.say(f"{self.en} is stunned, and [bold]{move}[/] never comes.")
            return

        if kind == "charge":
            if e.chilled:
                self.say(f"Frost locks {self.en}'s limbs. [bold]{move}[/] is broken!")
            else:
                e.charged = move
                self.say(f"{self.en} gathers power for [bold yellow]{move}[/]...")
        elif kind == "defend":
            self.say(f"{self.en} uses [bold]{move}[/] and braces itself.")
        elif kind == "heal":
            amount = min(round(e.max_hp * 0.12), e.max_hp - e.hp)
            e.hp += amount
            self.say(f"{self.en} uses [bold]{move}[/]. [green]+{amount} HP[/]")
        elif kind == "enrage":
            e.strength *= 1.25
            self.say(f"{self.en} unleashes [bold red]{move}[/]! Its strength rises to [bold]{round(e.strength)}[/].")
        elif kind == "curse":
            if h.dodge:
                self.say(f"{self.en} uses [bold]{move}[/], but you are already gone.")
            else:
                h.weaken = 3
                self.say(f"{self.en} uses [bold]{move}[/]. You are [magenta]weakened[/] for 2 turns.")
        elif h.dodge:
            self.say(f"{self.en} uses [bold]{move}[/], but strikes only smoke.")
        elif kind == "multi":
            hits = [self.hit_hero(0.45) for _ in range(3)]
            total = [sum(x) for x in zip(*hits)]
            self.say(f"{self.en} uses [bold]{move}[/], three hits: {self.describe_hit(*total)}.")
        else:
            dmg, absorbed, reflected = self.hit_hero(ENEMY_MULTS[kind])
            line = f"{self.en} uses [bold]{move}[/]: {self.describe_hit(dmg, absorbed, reflected)}."
            if kind == "drain" and dmg:
                gained = min(dmg, e.max_hp - e.hp)
                e.hp += gained
                line += f" It drinks [green]{gained} HP[/]."
            if kind == "rend" and dmg:
                h.wound = 3
                h.wound_dmg = max(1, round(e.strength * 0.3))
                line += " You are [red]wounded[/]."
            self.say(line)
        e.chilled = False

    def end_round(self):
        h, e = self.hero, self.enemy
        if e.hp > 0 and e.burn:
            e.hp = max(0, e.hp - e.burn_dmg)
            h.stats["dealt"] += e.burn_dmg
            e.burn -= 1
            self.say(f"{self.en} burns for [bold red]{e.burn_dmg}[/].")
        if e.hp > 0 and e.poison:
            dmg = max(1, round(e.poison * 0.15 * h.strength))
            e.hp = max(0, e.hp - dmg)
            h.stats["dealt"] += dmg
            self.say(f"Poison eats at {self.en} for [bold green]{dmg}[/].")
        if h.hp > 0 and h.wound:
            dmg = min(h.wound_dmg, h.hp)
            h.hp -= dmg
            h.stats["taken"] += dmg
            h.wound -= 1
            self.say(f"Your wounds bleed for [bold red]{dmg}[/].")

        h.weaken = max(0, h.weaken - 1)
        h.cooldowns = {k: v - 1 for k, v in h.cooldowns.items() if v > 1}
        if h.shield_turns:
            h.shield_turns -= 1
            if not h.shield_turns:
                h.shield = 0
        h.guarding = h.rebuke = h.dodge = False
        if h.key == "sorcerer":
            h.mana = min(h.max_mana, h.mana + 8)
        self.turn += 1
        h.stats["turns"] += 1
        if e.hp > 0 and h.hp > 0:
            self.next_intent()

    def result(self):
        if self.enemy.hp <= 0:
            return "win"
        if self.hero.hp <= 0:
            return "lose"
        return None

    def play_round(self, letter):
        if not self.player_turn(letter):
            return False
        if not self.result():
            self.enemy_turn()
            if not self.result():
                self.end_round()
        return True


def gain_rewards(hero, act_index, boss):
    gold = 50 + 25 * act_index if boss else randint(15, 25) + 10 * act_index
    hero.gold += gold
    hero.stats["gold"] += gold
    hero.stats["slain"] += 1
    potion = boss or random() < 0.25
    if potion and hero.potions < MAX_POTIONS:
        hero.potions += 1
    else:
        potion = False
    if hero.key == "guardian":
        hero.add_soul()
    hero.level += 1
    hero.max_hp += 8
    hero.heal(8)
    hero.strength += 1
    return gold, potion


def perk_options(hero):
    pool = list(PERKS.items()) + [(CLASS_PERKS[hero.key][0], CLASS_PERKS[hero.key][1:])]
    return sample(pool, 3)


def apply_perk(hero, perk):
    if perk == "vitality":
        hero.max_hp += 15
        hero.heal(15)
    elif perk == "might":
        hero.strength += 3
    elif perk == "fortitude":
        hero.defense += 3
    elif perk == "bulwark":
        hero.aegis_mult += 0.2
    elif perk == "arcana":
        hero.max_mana += 20
    elif perk == "edge":
        hero.crit += 5
    elif perk == "soulbind":
        hero.add_soul()


def rest(hero):
    return hero.heal(hero.max_hp * 0.35)


def buy(hero, item_id):
    item = next(i for i in SHOP if i[0] == item_id)
    price = hero.prices[item_id]
    if hero.gold < price:
        return False, f"You can't afford the {item[1]}."
    if item_id == "potion" and hero.potions >= MAX_POTIONS:
        return False, f"You can't carry more than {MAX_POTIONS} potions."
    hero.gold -= price
    hero.prices[item_id] += item[4]
    if item_id == "potion":
        hero.potions += 1
    elif item_id == "whetstone":
        hero.strength += 2
    elif item_id == "plating":
        hero.defense += 2
    elif item_id == "crystal":
        hero.max_hp += 15
        hero.heal(15)
    return True, f"You bought the {item[1]}."


def pray(hero):
    roll = random()
    if roll < 0.35:
        boon = randint(1, 3)
        if boon == 1:
            hero.strength += 3
            return "[bold green]The old gods smile.[/] [bright_white]+3 strength[/]"
        if boon == 2:
            hero.defense += 3
            return "[bold green]The old gods smile.[/] [bright_white]+3 defense[/]"
        hero.max_hp += 20
        hero.heal(20)
        return "[bold green]The old gods smile.[/] [bright_white]+20 max HP[/]"
    if roll < 0.6:
        healed = hero.heal(hero.max_hp)
        return f"[bold green]Warm light fills you.[/] [bright_white]Fully healed (+{healed} HP)[/]"
    if roll < 0.8:
        gold = randint(30, 60)
        hero.gold += gold
        hero.stats["gold"] += gold
        return f"[bold yellow]Coins glitter in the offering bowl.[/] [bright_white]+{gold} gold[/]"
    lost = min(hero.hp - 1, round(hero.max_hp * 0.2))
    hero.hp -= lost
    return f"[bold red]The old gods are displeased.[/] [bright_white]-{lost} HP[/]"


def header(act, extra=""):
    rich.print(f"[bold red]HEROES QUEST[/] [bright_black]·[/] [bright_white]{act['name']}[/]{extra}\n")


def hero_line(hero):
    return f"[bold {hero.color}]{escape(hero.name)}[/] [bright_black]the[/] [{hero.color}]{hero.title}[/]  [bright_white]Lv {hero.level}[/]"


def stat_line(hero):
    line = (f"[bright_white]STR[/] [bold]{round(hero.strength)}[/]  [bright_white]DEF[/] [bold]{hero.defense}[/]  "
            f"[bright_white]CRIT[/] [bold]{hero.crit}%[/]  [bright_black]|[/]  "
            f"[bright_white]Potions[/] [bold green]{hero.potions}[/]  [bright_white]Gold[/] [bold yellow]{hero.gold}[/]")
    if hero.key == "guardian":
        line += f"  [bright_white]Souls[/] [bold yellow]{hero.souls}[/]"
    return line


def render_battle(battle, act, fight_no, total):
    h, e = battle.hero, battle.enemy
    cls()
    header(act, f" [bright_black]· Battle {fight_no}/{total} · Turn {battle.turn}[/]")

    rich.print(hero_line(h))
    shield = f"  [cyan]+{h.shield} shield[/]" if h.shield else ""
    rich.print(f"[bright_white]HP  [/] {bar(h.hp, h.max_hp, 'green')} [bold]{h.hp}[/]/{h.max_hp}{shield}")
    if h.key == "warrior":
        rich.print(f"[bright_white]Rage[/] {bar(h.rage, 100, 'red')} [bold]{h.rage}[/]/100")
    elif h.key == "sorcerer":
        rich.print(f"[bright_white]Mana[/] {bar(h.mana, h.max_mana, 'blue')} [bold]{h.mana}[/]/{h.max_mana}")
    rich.print(stat_line(h))
    status = []
    if h.weaken:
        status.append(f"[magenta]Weakened ({h.weaken})[/]")
    if h.wound:
        status.append(f"[red]Wounded ({h.wound})[/]")
    if h.sure_crit:
        status.append("[yellow]Next hit crits[/]")
    if status:
        rich.print("[bright_white]Status:[/] " + "  ".join(status))

    rich.print("\n[bright_black]──────────────── vs ────────────────[/]\n")

    tag = " [bold yellow]BOSS[/]" if e.boss else ""
    rich.print(f"[bold red]{e.name}[/]{tag}  [bright_white]STR[/] [bold]{round(e.strength)}[/]")
    rich.print(f"[bright_white]HP  [/] {bar(e.hp, e.max_hp, 'red')} [bold]{e.hp}[/]/{e.max_hp}")
    status = []
    if e.burn:
        status.append(f"[red]Burning ({e.burn})[/]")
    if e.poison:
        status.append(f"[green]Poison x{e.poison}[/]")
    if e.stunned:
        status.append("[yellow]Stunned[/]")
    if e.chilled:
        status.append("[cyan]Chilled[/]")
    if status:
        rich.print("[bright_white]Status:[/] " + "  ".join(status))
    kind, move = battle.intent
    hint, style = INTENTS[kind]
    rich.print(f"[bright_white]Intent:[/] [{style}]{move}[/] [bright_black]({hint})[/]")

    rich.print("\n[bright_black]────────────────────────────────────[/]\n")
    rich.print(f"[bold cyan]A)[/] [bright_white]Attack[/]   [bold cyan]B)[/] [bright_white]Guard[/]   "
               f"[bold cyan]C)[/] [bright_white]Potion[/] [bright_black]({h.potions})[/]")
    for letter, ab in zip("DEFG", ABILITIES[h.key]):
        ok, why = battle.check(ab)
        cost = f"{ab['rage']} rage" if ab.get("rage") else f"{ab['mana']} mana" if ab.get("mana") else ""
        name = f"{ab['name']:<13}"
        if ok:
            rich.print(f"[bold cyan]{letter})[/] [bright_white]{name}[/] [yellow]{cost:<14}[/] [bright_black]{ab['desc']}[/]")
        else:
            rich.print(f"[bright_black]{letter}) {name} {why:<14} {ab['desc']}[/]")

    if battle.log:
        rich.print()
        for line in battle.log:
            rich.print(f"[bright_black]›[/] {line}")


def fight(hero, template, boss, act, fight_no, total):
    battle = Battle(hero, template, boss)
    cls()
    header(act)
    tag = "[bold yellow]BOSS[/] " if boss else ""
    rich.print(f"{tag}[bold red]{template['name']}[/] [bright_white]appears![/]\n")
    rich.print(f"[italic bright_black]{template['desc']}[/]")
    wait()

    last = None
    while not battle.result():
        render_battle(battle, act, fight_no, total)
        if last:
            rich.print(f"\n[bright_black]Enter: repeat last action[/]", end="")
        choice = ask()
        if not choice:
            if not last:
                continue
            choice = last
        battle.log = []
        if battle.play_round(choice):
            last = choice

    render_battle(battle, act, fight_no, total)
    if battle.result() == "win":
        rich.print(f"\n[bold green]The {template['name']} falls![/]")
    else:
        rich.print("\n[bold red]You collapse...[/]")
    wait()
    return battle.result() == "win"


def reward_screen(hero, act, act_index, boss):
    gold, potion = gain_rewards(hero, act_index, boss)
    cls()
    header(act)
    rich.print("[bold green]Victory![/]\n")
    rich.print(f"[bright_white]Gold:[/] [bold yellow]+{gold}[/]")
    if potion:
        rich.print("[bright_white]Found a[/] [bold green]Healing Potion[/]")
    if hero.key == "guardian":
        rich.print(f"[bright_white]A soul joins you.[/] [bold yellow]{hero.souls} souls[/] [bright_black](+5 max HP)[/]")
    rich.print(f"\n[bold cyan]Level up![/] [bright_white]You are now level {hero.level}.[/] [bright_black](+8 max HP, +1 strength)[/]")

    options = perk_options(hero)
    rich.print("\n[bright_white]Choose a blessing:[/]\n")
    for letter, (pid, (name, desc)) in zip("abc", options):
        rich.print(f"[bold cyan]{letter.upper()})[/] [bright_white]{name:<12}[/] [bright_black]{desc}[/]")
    while True:
        choice = ask()
        picks = dict(zip("abc", options))
        if choice in picks:
            apply_perk(hero, picks[choice][0])
            return


def campfire(hero, act):
    healed = rest(hero)
    cls()
    header(act)
    rich.print("[bold yellow]You make camp.[/] [bright_white]The fire crackles, and for a while the world feels small and safe.[/]\n")
    rich.print(f"[green]+{healed} HP[/] [bright_black]({hero.hp}/{hero.max_hp})[/]")
    wait()


def merchant(hero, act):
    message = "[italic bright_black]\"Rare goods for a rare customer. Mind the cart, it bites.\"[/]"
    while True:
        cls()
        header(act)
        rich.print("[bold yellow]A wandering merchant[/] [bright_white]waves you over.[/]\n")
        rich.print(message + "\n")
        rich.print(f"[bright_white]Gold:[/] [bold yellow]{hero.gold}[/]   [bright_white]Potions:[/] [bold green]{hero.potions}/{MAX_POTIONS}[/]\n")
        for letter, item in zip("abcd", SHOP):
            price = hero.prices[item[0]]
            color = "bright_white" if hero.gold >= price else "bright_black"
            rich.print(f"[bold cyan]{letter.upper()})[/] [{color}]{item[1]:<18}[/] [yellow]{price:>3}g[/]  [bright_black]{item[2]}[/]")
        rich.print("\n[bold cyan]Q)[/] [bright_white]Leave[/]")
        choice = ask()
        if choice in ("q", ""):
            return
        items = dict(zip("abcd", SHOP))
        if choice in items:
            ok, text = buy(hero, items[choice][0])
            message = f"[green]{text}[/]" if ok else f"[yellow]{text}[/]"


def shrine(hero, act):
    cls()
    header(act)
    rich.print("[bold magenta]A crumbling shrine[/] [bright_white]to gods whose names have worn off the stone.[/]\n")
    rich.print("[bright_white]You kneel and pray...[/]\n")
    rich.print(pray(hero))
    rich.print(f"\n[bright_black]HP {hero.hp}/{hero.max_hp}  ·  Gold {hero.gold}[/]")
    wait()


def crossroads(hero, act):
    while True:
        cls()
        header(act)
        rich.print(hero_line(hero))
        rich.print(f"[bright_white]HP  [/] {bar(hero.hp, hero.max_hp, 'green')} [bold]{hero.hp}[/]/{hero.max_hp}")
        rich.print(stat_line(hero))
        rich.print("\n[bright_white]The path splits ahead.[/]\n")
        rich.print("[bold cyan]A)[/] [bright_white]Campfire[/]  [bright_black]rest and heal 35% HP[/]")
        rich.print("[bold cyan]B)[/] [bright_white]Merchant[/]  [bright_black]spend your gold[/]")
        rich.print("[bold cyan]C)[/] [bright_white]Shrine  [/]  [bright_black]pray to the old gods, if you dare[/]")
        choice = ask()
        if choice == "a":
            return campfire(hero, act)
        if choice == "b":
            return merchant(hero, act)
        if choice == "c":
            return shrine(hero, act)


def act_cleared(hero, act):
    hero.hp = hero.max_hp
    cls()
    header(act)
    rich.print(f"[bold green]{act['name']} is cleared.[/]\n")
    rich.print("[bright_white]You take a long rest before moving on.[/] [green]Fully healed.[/]")
    wait()


def summary(hero):
    s = hero.stats
    rich.print(inspect.cleandoc(f"""
        {hero_line(hero)}
        [bright_white]Enemies slain:[/] [bold]{s['slain']}[/]   [bright_white]Turns fought:[/] [bold]{s['turns']}[/]
        [bright_white]Damage dealt:[/] [bold]{s['dealt']}[/]   [bright_white]Damage taken:[/] [bold]{s['taken']}[/]
        [bright_white]Potions drunk:[/] [bold]{s['potions']}[/]   [bright_white]Gold earned:[/] [bold yellow]{s['gold']}[/]
    """))


def game_over(hero, act):
    cls()
    rich.print("[bold red]YOU HAVE DIED[/]\n")
    rich.print(f"[italic bright_black]{act['grave']}[/]\n")
    summary(hero)
    wait()


def victory_screen(hero):
    cls()
    rich.print("[bold yellow]VICTORY[/]\n")
    rich.print(inspect.cleandoc(f"""
        [bright_white]The Celestial Entity comes apart like a dropped mirror, and the wound in the sky
        knits itself shut. For the first time in years, the stars are just stars.

        Far below, the kingdom wakes to a quiet morning, and to the legend of[/] [bold {hero.color}]{escape(hero.name)}[/][bright_white].[/]
    """) + "\n")
    summary(hero)
    wait()


def act_intro(act):
    cls()
    header(act)
    rich.print(f"[italic bright_white]{act['intro']}[/]")
    wait()


def title_screen():
    while True:
        cls()
        rich.print(inspect.cleandoc(f"""
            [bold red]HEROES QUEST[/] [bright_black]v{VERSION}[/]

            [italic bright_white]The sky has cracked. From the wound above the world, the Celestial Entity
            whispers to every beast and shade below, and they answer. The kingdom has
            one hero left. It is you.[/]

            [bold cyan]A)[/] [bright_white]New journey[/]
            [bold cyan]Q)[/] [bright_white]Quit[/]
        """))
        choice = ask()
        if choice == "a":
            return True
        if choice == "q":
            return False


def create_hero():
    name = ""
    while not name:
        cls()
        rich.print("[bold red]HEROES QUEST[/]\n")
        rich.print("[bright_white]What is your name, hero?[/]")
        name = input_name()
    while True:
        cls()
        rich.print(f"[bold red]HEROES QUEST[/]\n\n[bright_white]Choose your path,[/] [bold]{escape(name)}[/][bright_white]:[/]\n")
        for letter, c in CLASSES.items():
            names = ", ".join(ab["name"] for ab in ABILITIES[c["id"]])
            rich.print(inspect.cleandoc(f"""
                [bold cyan]{letter.upper()})[/] [bold {c['color']}]{c['name']}[/]  [bright_black]HP {c['hp']} · STR {c['str']} · DEF {c['defense']} · CRIT {c['crit']}%[/]
                   [italic bright_white]{c['lore']}[/]
                   [bright_black]{c['play']}[/]
                   [bright_black]Abilities: {names}[/]
            """) + "\n")
        choice = ask()
        if choice in CLASSES:
            return Hero(name, choice)


def input_name():
    rich.print("\n[bold cyan]>>[/] ", end="")
    return input().strip()[:16]


def play(hero):
    for act_index, act in enumerate(ACTS):
        act_intro(act)
        foes = sample(act["pool"], 2) + [act["boss"]]
        for fight_index, foe in enumerate(foes):
            boss = fight_index == len(foes) - 1
            if not fight(hero, foe, boss, act, fight_index + 1, len(foes)):
                game_over(hero, act)
                return
            if boss and act_index == len(ACTS) - 1:
                hero.stats["slain"] += 1
                victory_screen(hero)
                return
            reward_screen(hero, act, act_index, boss)
            if boss:
                act_cleared(hero, act)
            else:
                crossroads(hero, act)


def main():
    setup_terminal()
    try:
        while title_screen():
            play(create_hero())
    except (KeyboardInterrupt, EOFError):
        print()
    rich.print("[bright_white]Farewell, hero.[/]")

    main()