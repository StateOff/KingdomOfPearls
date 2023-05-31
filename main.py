# -*- coding: utf-8 -*-

"""
Kindom of Pearls
- A text based adventure -

©2023 StateOffGames

Music: David Renda & David Fesliyan
Royalty free music from https://www.FesliyanStudios.com

Went overboard when doing programming exercises with my son.

Installation:
- Depends on/tested with Python 3.10
- External modules: regex
    pip install regex
- Launch via:
    main.py

This games uses standard Unicode symbols. The console/font used greatly changes the experience.
Tested with Kitty Terminal.
"""

import copy
import json
import math
import os
import random
import sys

import regex

WITH_MUSIC = True
CUSTOM_DRAWING = False

MUSIC = {
    'home': 'music/2019-08-25_-_8bit-Smooth_Presentation_-_David_Fesliyan.mp3',
    'adventure': 'music/2019-12-09_-_Retro_Forest_-_David_Fesliyan.mp3',
    'boss': 'music/slow-2021-08-30_-_Boss_Time_-_www.FesliyanStudios.com.mp3',
    'epilogue': 'music/2021-08-17_-_8_Bit_Nostalgia_-_www.FesliyanStudios.com.mp3',
    'gameover': 'music/stinger-2021-08-17_-_8_Bit_Nostalgia_-_www.FesliyanStudios.com.mp3',
    'success': 'music/stinger-2021-10-19_-_Funny_Bit_-_www.FesliyanStudios.com.mp3',
}

if CUSTOM_DRAWING:
    from terminal import print, input, clear
else:
    def clear():
        # for windows
        if os.name == 'nt':
            _ = os.system('cls')

        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')


if WITH_MUSIC:
    try:
        import pygame
    except ModuleNotFoundError:
        input("Music could not be loaded - pygame module missing.\n(Press Enter to continue without music)")
        WITH_MUSIC = False
    else:
        pygame.init()
        pygame.mixer.init()

        def play_music(name, repeat=-1, force=False):
            global music
            if name == music and not force:
                return
            music = name

            pygame.mixer.music.stop()
            pygame.mixer.music.load(MUSIC[name])
            pygame.mixer.music.play(repeat)

if not WITH_MUSIC:
    def play_music(name, repeat=-1, force=False):
        pass

# -----------------------------------------------------------------------------
# -- DEBUG
# -----------------------------------------------------------------------------
VERSION = "0.18a"
DEBUG_START_LEVEL = 1
DEBUG_SHOW_COMPLETE_MAP = False #True
DEBUG_LARGE_INVENTORY = False #True
DEBUG_START_PEARL_COUNT = 0
DEBUG_START_COINS = 0
DEBUG_MONSTERS_CLEARED = False
DEBUG_BOSSES_CLEARED = False

# -----------------------------------------------------------------------------
# -- ITEMS
# -----------------------------------------------------------------------------
I_EMPTY = "_"
I_SWORD = "🗡️"
I_SHIELD = "🛡️"
I_GLOVES = "🧤"
I_SHOES = "🥾"
I_COIN = "🟡"
I_POTION = "🧪"
I_BOMB = "💣"
I_BOW = "🏹"
I_BATTLE_AXE = "🪓"
I_RING = "💍"
I_CROWN = "👑"
I_BANDAGE = "🩹"
I_PEARL = "🔮"
I_WAND = "🪄"
I_SPELLBOOK = "📕"
I_COFFIN = "⚰️"
I_PICKAXE = "⛏️"
I_BUCKET = "🪣"
I_AMULET = "📿"

I_NOT_DROPABLE = f"{I_COFFIN}{I_PEARL}{I_PICKAXE}{I_AMULET}"

# Modes
BACKPACK_ONLY = 1
EQUIPPED_ONLY = 2
BACKPACK_OR_EQUIPPED = 3


PRICES = {
    I_SWORD: 3,
    I_GLOVES: 3,
    I_BUCKET: 3,
    I_BOW: 5,
    I_BATTLE_AXE: 10,
    I_SHIELD: 10,
    I_SHOES: 1,
    I_BOMB: 3,
    I_POTION: 2,
    I_BANDAGE: 2,
    I_PICKAXE: 3,
}

# TYPES
T_CARRY = 0
T_L_HAND = 1
T_R_HAND = 2
T_ARMS = 3
T_FEET = 4
T_FINGERS = 5
T_HEAD = 6

ITEM_TYPES = {
    I_SWORD: [T_L_HAND, T_R_HAND],
    I_SHIELD: [T_R_HAND, T_L_HAND],
    I_GLOVES: [T_ARMS],
    I_SHOES: [T_FEET],
    I_BOW: [T_L_HAND, T_R_HAND],
    I_BATTLE_AXE: [T_L_HAND, T_R_HAND],
    I_PICKAXE: [T_L_HAND, T_R_HAND],
    I_RING: [T_FINGERS],
    I_CROWN: [T_HEAD],
    I_AMULET: [T_FINGERS],
    I_BUCKET: [T_HEAD],
    I_PEARL: [T_FINGERS],
    I_WAND: [T_L_HAND, T_R_HAND],
    I_SPELLBOOK: [T_L_HAND, T_R_HAND]
}


D_GREEN = "🟩"
D_RED = "🟥"
D_BLUE = "🟦"
D_YELLOW = "🟨"
D_PURPLE = "🟪"
D_BLACK = "⬛"

S_HEART = "❤️"
S_HEART_EMPTY = "🖤"
S_SKULL = "💀"
S_HIT = "💥"
S_BLOCKED = "⛔"
S_MISS = "💨"
S_MAGIC = "🔥"
S_MAGIC_MISS = "✨"
S_FIGHT = "⚔️"
S_WELL = "⛲"
S_TALK = "💬"
S_NORTH = "⬆️"
S_EAST = "➡️"
S_SOUTH = "⬇️"
S_WEST = "⬅️"
S_COMPASS = "🧭"
S_BUY = "💰"
S_DROP = "🗑️"
S_RETREAT = "🏳️"
S_ACTION = "⚡"
S_INVENTORY = "📦"
S_MAP = "🗺️"
S_STATUS = "📜"
S_DONE = "↩️"
S_NEW = "⚔️🆕"
S_SAVE = "💾⬅️"
S_LOAD = "💾⤵️"
S_QUIT = "🚪"
S_OPTIONS = "⚙️"

DEFAULT_ITEM_EFFECT = D_GREEN * 2
ITEM_EFFECTS = {
    I_SWORD: D_RED,
    I_GLOVES: D_BLUE,
    I_BUCKET: D_BLUE,
    I_RING: D_YELLOW,

    I_BOW: (D_BLUE + D_GREEN),
    I_PICKAXE: (D_RED + D_GREEN),

    I_BATTLE_AXE: (D_RED * 2),
    I_SHIELD: (2 * D_BLUE),
    I_CROWN: (D_YELLOW + D_BLUE),

    I_SPELLBOOK: (D_YELLOW * 1),
    I_WAND: (D_YELLOW * 2),
    I_PEARL: (D_YELLOW * 3),
}

# -----------------------------------------------------------------------------
# -- Locations
# -----------------------------------------------------------------------------
L_CASTLE = "🏰 CASTLE"
L_BRIDGE = "🏞️ BRIDGE"
L_FOREST = "🌲 FOREST"
L_SHOP = "🛍️ SHOP"
L_CATHEDRAL = "⛪ CATHEDRAL"
L_HUT = "🛖 HUT"
L_BLACKSMITH = "⚒️ BLACKSMITH"
L_MINES = "⛏️ MINES"
L_SWAMP = "🌿 SWAMP"
L_RUINS = "🏛️ RUINS"
L_DESERT = "🏜️ DESERT"
L_CAVE = "⛰️ CAVE"
L_BEACH = "🏝️ BEACH"
L_SHIP = "⛵ SHIP"
L_OCEAN = "🌊 OCEAN"
L_VULCANO = "🌋 VULCANO"
L_GRAVEYARD = "🪦 GRAVEYARD"
L_TOMB = "🕍 TOMB"
L_LAIR = "⚰️ LAIR"
L_PORTAL = "🌀 PORTAL"
L_GRAVEDIGGER = "🏚️ GRAVEDIGGER'S HOUSE"

# -----------------------------------------------------------------------------
# -- Stats
# -----------------------------------------------------------------------------
MAX_LEVEL = 10
LEVELS = {
    "xp":       [0, 500, 1000, 2500, 5000, 10000, 15000, 25000, 40000, 50000, math.inf],
    "backpack": [9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
    "health":   [5, 6, 6, 7, 7,  8,  8,  9,  9,  10],
    "slots": [
        # Level 1
        {
            T_L_HAND: 1,
            T_R_HAND: 0,
            T_ARMS: 1,
            T_FEET: 1,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 2
        {
            T_L_HAND: 1,
            T_R_HAND: 1,
            T_ARMS: 1,
            T_FEET: 1,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 3
        {
            T_L_HAND: 2,
            T_R_HAND: 1,
            T_ARMS: 1,
            T_FEET: 1,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 4
        {
            T_L_HAND: 2,
            T_R_HAND: 2,
            T_ARMS: 1,
            T_FEET: 1,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 5
        {
            T_L_HAND: 2,
            T_R_HAND: 2,
            T_ARMS: 2,
            T_FEET: 1,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 6
        {
            T_L_HAND: 2,
            T_R_HAND: 2,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 1,
            T_HEAD: 1,
        },
        # Level 7
        {
            T_L_HAND: 2,
            T_R_HAND: 2,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 2,
            T_HEAD: 1,
        },
        # Level 8
        {
            T_L_HAND: 2,
            T_R_HAND: 2,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 3,
            T_HEAD: 1,
        },
        # Level 9
        {
            T_L_HAND: 3,
            T_R_HAND: 2,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 3,
            T_HEAD: 1,
        },
        # Level 10
        {
            T_L_HAND: 3,
            T_R_HAND: 3,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 3,
            T_HEAD: 1,
        },
        # Level 11
        {
            T_L_HAND: 3,
            T_R_HAND: 3,
            T_ARMS: 2,
            T_FEET: 2,
            T_FINGERS: 3,
            T_HEAD: 1,
        },
    ]
}

# -----------------------------------------------------------------------------
# -- Damage Callbacks
# -----------------------------------------------------------------------------

def _default_damage(rolled_dice: list) -> int:
    return False, rolled_dice


def __type_damage_only(rolled_dice: list, only_type: list, effect: list = [I_SWORD]) -> int:
    removed_damage = False
    new_result = []
    for die, throw in rolled_dice:
        if die not in only_type:
            value = ""
            if throw in effect:
                removed_damage = True
                new_result.append((die, S_MAGIC_MISS))
            else:
                new_result.append((die, throw))
        else:
            new_result.append((die, throw))
    return removed_damage, new_result


def _magic_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_YELLOW])

def _no_magic_effect(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_GREEN, D_BLUE, D_RED], [I_SWORD, I_SHIELD])

def _green_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_GREEN])

def _blue_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_BLUE])

def _red_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_RED])

CURRENT_DAMAGE = []
def _random_damage(rolled_dice: list) -> int:
    global CURRENT_DAMAGE
    CURRENT_DAMAGE = [random.choice([D_GREEN, D_BLUE, D_RED, D_YELLOW])]
    return __type_damage_only(rolled_dice, CURRENT_DAMAGE, [I_SWORD, I_SHIELD])

def _random_damage_message() -> str:
    global CURRENT_DAMAGE
    return "Changing abilities: Silenced all throws, except " + "".join(CURRENT_DAMAGE)

def _reduced_to_count(rolled_dice: list, count: int, affect_types: list = [], effect: list = [I_SWORD]) -> int:
    removed_damage = False
    new_result = []
    counter = 0
    for die, throw in rolled_dice:
        if len(affect_types) == 0 or die not in affect_types:
            if throw in effect:
                counter += 1
                if counter > count:
                    removed_damage = True
                    new_result.append((die, S_MAGIC_MISS))
                else:
                    new_result.append((die, throw))
            else:
                new_result.append((die, throw))
        else:
            new_result.append((die, throw))
    return removed_damage, new_result


def _reduce_all_damage_to_two(rolled_dice: list):
    return _reduced_to_count(rolled_dice, 2)

def _reduce_all_damage_to_four(rolled_dice: list):
    return _reduced_to_count(rolled_dice, 4)

# -----------------------------------------------------------------------------
# -- Enemies
# -----------------------------------------------------------------------------

E_OCTOPUS = "🐙 OCTOPUS"
E_SNAKE = "🐍 SNAKE"
E_DRAGON = "🐉 DRAGON"
E_RAT = "🐀 RAT"
E_GHOST = "👻 GHOST"
E_ZOMBIE = "🧟‍️ ZOMBIE"
E_BAT = "🦇 MEGABAT"
E_TOAD = "🐸 GIANT TOAD"
E_SPIDER = "🕷️ SPIDER"
E_SCORPION = "🦂 LARGE SCORPION"
E_TROLL = "🧌 TROLL"
E_VAMPIRE = "🧛 VAMPIRE"
E_SKELETON = "💀 SKELETON"
E_DEMON = "👹 DEMON"
E_CRAB = "🦀 MONSTER CRAB"
E_SHARK = "🦈 SHARK"
E_MERMAID = "🧜 MERMAID"
E_JINN = "🧞 JINN"
E_SORCERER = "🧙 EVIL SORCERER"

MONSTERS = {
    # Purple Dice, Black Dice, Health, XP, LOOT, damage_callback
    E_RAT: (1, 0, 1, 50, "", _default_damage, ""),
    E_SNAKE: (3, 0, 2, 100, I_COIN * 1, _default_damage, ""),

    E_TROLL: (4, 0, 6, 250, I_COIN * 3, _default_damage, ""),

    E_TOAD: (3, 1, 5, 150, I_COIN * 1, _default_damage, ""),
    E_SPIDER: (0, 4, 4, 200, f"{I_POTION}", _default_damage, ""),

    E_SKELETON: (2, 3, 3, 250, f"{I_POTION * 1}", _default_damage, ""),
    E_ZOMBIE: (3, 1, 4, 350, f"{I_COIN * 1}", _green_damage_only, f"Only {D_GREEN} basic attacks are effective against Zombies"),
    E_GHOST: (0, 5, 3, 400, f"{I_POTION * 1}", _reduce_all_damage_to_two,
              f"{S_MISS} Hard to hit. Ghosts only receive the first two hits!"),

    E_SCORPION: (3, 6, 5, 400, f"{I_COIN}", _default_damage, ""),
    E_BAT: (7, 5, 5, 500, "", _default_damage, ""),

    E_CRAB: (4, 7, 7, 500, f"{I_COIN * 3}", _default_damage, ""),
    E_OCTOPUS: (2, 8, 12, 600, I_COIN * 2, _default_damage, ""),
    E_SHARK: (2, 4, 5, 700, f"{I_COIN}", _blue_damage_only, f"Only {D_BLUE} attacks are effective against sharks!"),


    E_DEMON: (0, 14, 10, 1000, I_COIN * 1, _magic_damage_only, f"Only {D_YELLOW} magic is effective against Demons!"),
    E_JINN: (2, 12, 5, 1000, I_COIN * 1, _magic_damage_only, f"Only {D_YELLOW} magic is effective against Jinns!"),


    E_MERMAID: (2, 6, 12, 2500, f"{I_RING}{I_PEARL}", _blue_damage_only, f"Only {D_BLUE} attacks are effective against Mermaids!"),
    E_VAMPIRE: (1, 6, 8, 2500, f"{I_COIN * 6}{I_PEARL}", _reduce_all_damage_to_four, f"Vampire is quick! Only the first four attacks hit."),
    E_DRAGON: (8, 8, 25, 15000, f"{I_COIN * 6}{I_CROWN}{I_PEARL}", _no_magic_effect, f"Dragon is immune to {D_YELLOW}"),

    E_SORCERER: (3, 3, 15, 20000, f"{I_COIN}", _random_damage, _random_damage_message),
}

MONSTER_ZONES = {
    L_CASTLE: [E_RAT],
    L_FOREST: [E_RAT, E_SNAKE, E_SNAKE, E_SNAKE],
    L_BRIDGE: [E_TROLL],
    L_SWAMP: [E_TOAD, E_TOAD, E_TOAD, E_SNAKE],
    L_RUINS: [E_SPIDER],
    L_GRAVEYARD: [E_ZOMBIE, E_ZOMBIE, E_ZOMBIE, E_ZOMBIE, E_ZOMBIE, E_SKELETON, E_GHOST],
    L_TOMB: [E_SKELETON, E_GHOST, E_GHOST],
    L_LAIR: [E_VAMPIRE],
    L_DESERT: [E_SCORPION],
    L_BEACH: [E_CRAB],
    L_SHIP: [E_OCTOPUS, E_SHARK],
    L_OCEAN: [E_MERMAID],
    L_CAVE: [E_BAT],
    L_MINES: [E_DEMON, E_JINN],
    L_VULCANO: [E_DRAGON],
    L_PORTAL: [E_SORCERER],
}

BOSS_MONSTER = 1
MONSTER_CLEARED = {
    L_CASTLE: 5,
    L_FOREST: 5,
    L_BRIDGE: 2,
    L_SWAMP: 5,
    L_RUINS: 5,
    L_BEACH: 5,
    L_GRAVEYARD: 5,
    L_TOMB: 3,
    L_LAIR: BOSS_MONSTER,
    L_DESERT: 5,
    L_SHIP: 5,
    L_OCEAN: BOSS_MONSTER,
    L_CAVE: 5,
    L_MINES: 5,
    L_VULCANO: BOSS_MONSTER,
    L_PORTAL: BOSS_MONSTER,
}
BOSSES = (E_VAMPIRE, E_MERMAID, E_DRAGON, E_SORCERER)

# -----------------------------------------------------------------------------
# -- Effects
# -----------------------------------------------------------------------------

DICE = {
    D_GREEN:  f"{I_SWORD * 2}{I_SHIELD * 2}  ",
    D_RED:    f"{I_SWORD * 3}{I_SHIELD * 1}  ",
    D_BLUE:   f"{I_SWORD * 1}{I_SHIELD * 3}  ",
    D_YELLOW: f"{I_SWORD * 4}{I_SHIELD * 0}  ",
    D_PURPLE: f"{I_SWORD * 2}{I_SHIELD * 1}   ",
    D_BLACK:  f"{I_SWORD * 3}{I_SHIELD * 2} ",
}

ACTIONS = {
    'attack': ('a', f"{S_FIGHT} [a]ttack"),
    'retreat': ('r', f"{S_RETREAT} [r]etreat"),
    'potion': ('p', f"{I_POTION} Drink [p]otion"),
    'bandage': ('h', f"{I_BANDAGE} Apply [h]ealing bandage"),
    'bomb': ('b', f"{I_BOMB} Throw a [b]omb ({3 * S_HIT} to target & {S_HIT} to you)"),
}


# -----------------------------------------------------------------------------
# -- Story
# -----------------------------------------------------------------------------

LORE = lambda: {
    L_OCEAN: {
        'music': 'adventure',
        'quest': {
            I_BOMB: [
                f"""You drop the bomb into the ocean. The explosion creates a huge wave.

Soon after various dead sea creatures raise from the ocean.
You can hear a loud scream. It pierces your ears - it is unbearable.

You might have enraged the queen of the sea."""
            ],
        },
        'cleared': [
            """\"She is dead! She is dead!\" screams Captain Ghur at you in joy.

He puts down his hat and looks sadly into the water. 

\"I will miss her singing.\"
"""
        ],
        'story': [
            f"""You sail towards the open ocean.
There is not much to see at this point, but an endless blue of water.

How possibly will you find the pearl out here, you ask yourself."""
        ]
    },
    L_GRAVEDIGGER: {
        'music': 'home',
        'obstacle': {
            I_PICKAXE: [
                f"""The gravedigger looks at you with a scared look.

"I can not let you have this, until the lord of these monsters is defeated."

He seems to be needing the pickaxe to defend himself."""
            ],
        },
        'talk': {
            'gravedigger': [
                f"""You ask if he is indeed Vernal, brother of Nordil the monk.

"Yes, it is me. Nordil and I were raised in the village near by, before it was turned into ashes.
Let him know that I am alive and he still ows me three coins from our last gamble."""
            ]
        },
        'story': [
            f"""You enter a somewhat damaged old stonehouse.

Inside, the Gravedigger looks at you in terror.

"If you are not one of these creatures, you can stay a while and listen."

He begins to tell you his story. He introduces himself as Vernal, the gravedigger.
It seems that a dangerous monster, that only acts at night, is commanding all the undead creatures in this area.

Vernal has seen it hiding in its lair, somewhere within the tomb. But he does not know the exact location.

"Save us all", he cries.
"Defeat this unholy creature, {name}!"
"""
        ]
    },
    L_RUINS: {
        'music': 'adventure',
        'obstacle': {
            L_GRAVEYARD: [
                f"""The spiders are in your way."""
            ],
        },
        'cleared': [
            """The scream of the last defeated spider fades in the distance. It looks like you did it."""
        ],
        'story': [
            """This must have been a village, not very long ago.
The ashes of some of the houses are still warm. You look for something
useful, but there is not much that can be salvaged.

What is this? A sticky web and cocoons. Are these the remains of the people that lived here?

While inspecting, you hear a high-pitched sound coming closer.
You expect the worst.
"""
        ]
    },
    L_GRAVEYARD: {
        'music': 'adventure',
        'obstacle': {
            L_GRAVEDIGGER: [
                f"""A small stonehouse is next to the graveyard. You see a candle lit, but you can not reach it, with all these undead monsters around."""
            ],
            L_TOMB: [
                f"""In the center of the graveyard, lies a large tomb. The undead seem to be protecting it."""
            ],
        },
        'cleared': [
            """It does not seem to stop. More undead are approaching, but at least you decimated them enough to be able to pass."""
        ],
        'story': [
            """A thick fog surrounds your feet as you enter the village's graveyard.
The moment you step foot on it - hands break through the graves and undead creatures raise coming for you.

You see other structures near by, but how will you reach them?
"""
        ]
    },
    L_LAIR: {
        'music': 'adventure',
        'obstacle': {
            I_COFFIN: [
                f"""You try to take the coffin, but the vampire is blocking you."""
            ],
        },
        'cleared': [
            """The vampire turns into ashes. What's left is some of his gold and one of the pearls you seek.

        The moment you touch the pearl you feel its magical power surrounding you. But how can you unleash it?"""
        ],
        'story': [
            """A dark place of evil. I has barely any light - only some moonlight shining through the crack in the
ceiling onto the coffin in the middle of the room. But what lies within?

Your amulet clearly points at the coffin. You approach it and slowly open the lid.
The vampire king is sleeping inside the coffin. What will you do?"""
        ]
    },
    L_TOMB: {
        'music': 'adventure',
        'obstacle': {
            L_LAIR: [
                f"""The amulet seems to show you the way to the evil's lair, but the surrounding monsters do not let you through."""
            ],
        },
        'cleared': [
            """The last scream of the undead souls echoes in the chambers of the tomb."""
        ],
        'story': [
            """This is a dark place. Whatever calls it home must be an evil spirit.

You can not see any monsters, but you feel their dead presence.
Beyond those walls, you can sense an even more devilish force waiting for you. But you will need something to help you uncover its location.
"""
        ]
    },
    L_FOREST: {
        'music': 'adventure',
        'obstacle': {
            L_BRIDGE: [
                f"""The snakes are in your way."""
            ],
        },
        'cleared': [
            """The forest looks passable now."""
        ],
        'story': [
            """It is hard for you to believe, that 
these are the same woods you passed by before.
The trees look dried out and twisted in pain.

The deeper you go, the darker it gets. You start to
hear suspicious sounds. Squeaking and hissing.

There is no safe passage through the forest, without ridden it first of its beasts.
"""
        ]
    },
    L_PORTAL: {
        'music': 'adventure',
        'cleared': [
            """With your hit the sorcerer falls to the ground. You have defeated the evil force.
            The lights in the room seem to diminish. Victory! It is time to break the evil spell and revive the king.
A bright light emerges from the sorcerer's body. You have to cover your eyes.

"Did you think you could defeat me this easily?!" his voice becomes deeper while his body ascends from the ground.
He seems to grow in size. You start to recognize his shape - he turned into a black dragon.""",

            """\"You shall burst into flames, human!\" He takes a big breath - a red fire can be seen as he opens his mouth towards you.
            You try to find cover but there is nothing around that could protect you.
           
            A burst of flames brightens the room. But it is not his fire. Out of nothing, Ghur the red dragon appeared. It immediately attacked the black dragon.
            
            \"May this be a lesson for you.\" exclaims Ghur after the black dragon turns to ashes. A most powerful light brigthen the space.
            
            You pass out."""
        ],
        'story': [
            """You enter what seems to be a secret space - it's black with small points of light in the distance.
Could these be stars?

\"Who let you in?\" the sorcerer approaches you.

"I must have underestimated the power of the pearls. How foolish of me. Well, I might as well get rid of you here. Would you be so kind to hand over the pearls of power?"

He reaches his hand towards you and mumbles some words. You are no longer in possession of the pearls. The portal closed.

"Fear not - you will perish either way."
"""
        ],
    },
    L_VULCANO: {
        'music': 'adventure',
        'obstacle': {
            L_BRIDGE: [
                f"""The snakes are in your way."""
            ],
        },
        'cleared': [
            """A loud scream echoes in the chambers.

\"Good! Take the artifact.\" screams Hhror, the dragon at you. He spits something out.
\"The wizard broke his promise. I shall not forget.\"

Hhror jumps through the ceiling of the vulcano. A hot stream of lava follows him.
Time to leave!
"""
        ],
        'story': [
            """You enter a large chamber lit by hot lava flowing in streams throughout the walls.
You start sweating - but not beacuse of the heat. The chamber is occupied by the largest creature you have seen in this realm: A red dragon.
It breaths slowly, exhausting smoke. It immediately spotted your presence.

\"A visitor? Since you came past my guards you will be a worthy snack for Hhror. I hope the wizard sent his best.\"

The dragon stands up and now you can clearly see its full size! It spreads his wings. A single step makes the vulcano shake and dust falls off the cave's ceiling.

"Find your courage!" you say to yourself.
"""
        ]
    },
    L_BRIDGE: {
        'music': 'adventure',
        'obstacle': {
            L_SWAMP: [
                f"""There is not a chance you can sneak by a Troll."""
            ],
        },
        'cleared': [
            """The last Troll falls off the bridge. The bridge is clear for your passage."""
        ],
        'story': [
            """The bridge is near. It is the only safe way to pass the river. Yet something does not seem right.

The moment you set foot on it two large shadows emerge from the other side. Their footsteps make the ground tremble.

Can it be the bridge is guarded by trolls? Indeed, these strong but not very clever monsters enter your sight.

"You not pass!" screams the first.
"You come, we eat you!" adds the other. Both look at each other and start to grin.
"""
        ]
    },
    L_SWAMP: {
        'music': 'adventure',
        'obstacle': {
            L_HUT: [
                f"""The hut is within a small lake. Without a boat\nof some kind, you will not be able to reach it."""
            ],
            L_RUINS: [
                f"""You can see the ruins, but the toads are blocking your way."""
            ],
            L_DESERT: [
                f"""The swamp seems to end behind a pack of toads."""
            ],
        },
        'cleared': [
            """It seems like all the monsters have been defeated. The path is clear."""
        ],
        'story': [
            """The endless fields with golden ripe crops have vanished.
  In its place a wet and stinking swamp terrorizes who wants to pass it.
  
  But the smell is the least of your problems. What you fail to see is that you are not alone. Large eyes cut through the puddles and observe every of your moves. You know these creatures! Toads, as large as humans! And who knows which other creatures hide here.
  
  You have to be on you guard if you want to make it through the swamps alive.
  """
        ]
    },
    L_DESERT: {
        'music': 'adventure',
        'obstacle': {
            L_BEACH: [
                f"""The beach seems near, but the monsters do not let you through."""
            ],
        },
        'cleared': [
            """The last scorpion is defeated. Maybe it is time to escape the desert."""
        ],
        'story': [
            """You clothes dried quickly. The celebration does not hold for long, as the ground gets dry and starts to slowly yield to seemingly endless piles of sand.
  
  The sky clears and while the sun pierces your skin with its rays of fire you start to realize, that you landed in the desert.
  
  You can not tell where it ends - but strange and spikey poles catch your gaze in the distance. As these poles start to move in a random dance, you begin to realize that these are not poles, but the deadly tails of scorpions. This very special kind, however, is larger than anything you have seen before. What kind of dark magic surfaced monsters like these? There is no way, you think, to avoid combat here other than turning around.
  """
        ]
    },
    L_CAVE: {
        'music': 'adventure',
        'obstacle': {
            L_MINES: [
                f"""There seems to be a passage, but it is blocked. With the right tool and no creatures around you might get through."""
            ],
        },
        'cleared': [
            """The bats seem to not bother you anymore."""
        ],
        'story': [
            """You enter a dark cave. You can barely see your next step. But high-pitched sounds make you uncomfortable.
Is this cave even going anywhere?"""
        ]
    },
    L_BLACKSMITH: {
        'music': 'home',
        'story': [
            """You sneak by one of the tunnels following a light. It leads to a magically sealed door. You knock.
To your surprise a voice answers:

"Who is it?" The door opens and reveals a dwarven blacksmith by the name of Thudur. He escaped the fate of his fellows with magic and has been living in these parts of the mines perfecting his craft.
"""
        ]
    },
    L_MINES: {
        'music': 'adventure',
        'obstacle': {
            L_VULCANO: [
                f"""You feel a powerful presence behind these walls. But in order to reveal it you have to get past these magical creatures."""
            ],
        },
        'cleared': [
            """The magical voices silenced. You can clearly hear a slow and loud breathing."""
        ],
        'story': [
            """With the help of the pickaxe you clear the entrance behind the cave. It seems to lead to tunnels. Man-made but small.
These must be old dwarfen mines. They seem abandoned and soon you realize why. Devilish magical creatures have infested the tunnels."""
        ]
    },
    L_SHIP: {
        'music': 'adventure',
        'obstacle': {
            L_OCEAN: [
                f"""You can not sail with the sea monsters endangering your voyage."""
            ],
        },
        'cleared': [
            """\"It won't be easy but I think I can navigate past the creatures now. Of course, since I am Captain Ghur!\""""
        ],
        'story': [
            """You board an old ship that anchored close to the shore.
The captain greets you.

"I am captain Ghur! Yes, THE captain Ghur. You are welcome to tell my stories."
He smiles revealing teath of silver. 

"I wish I could help your travels, but since a terrible sea creature started its reign over the sea we can not move.
Monsters of incredible size hinder us from save sailing. They seem to serve their queen of terror. At nights you can hear her singing ... not bad at times, if you ask me.\""""
        ]
    },
    L_BEACH: {
        'music': 'adventure',
        'obstacle': {
            L_SHIP: [
                f"""You need a boat and a clear path to board the ship."""
            ],
            L_CAVE: [
                f"""The entrance to to cave is blocked by crabs."""
            ],
        },
        'cleared': [
            """The beach is safe now. The remaining crabs are fleeing into the ocean."""
        ],
        'story': [
            """Finally you start hearing the pleasing concert of waves breaking over and over again.

You have reached the beaches. Far ahead you see an ship anchoring at the bay.
But in order to come closer to the shore, you need to fight your way through monster crabs.
"""
        ]
    },
    L_SHOP: {
        'music': 'home',
        'story': [
            """As you enter the castle's shop, the merchant immediately approaches you.
Stroking his long beard and mustering you from head to toe, he asks:
"Yes, yes. What can I do for you?"
"""
        ]
    },
    L_HUT: {
        'music': 'home',
        'story': [
            """You put the coffin onto the lake and jump in. It may not be a boat but it seems like a common way to
travel in swamps."""
        ]
    },
    L_CATHEDRAL: {
        'music': 'home',
        'story': [
            f"""The tallest building in the center of the castle is an old cathedral.
The moment you enter you smell herbs and incense. You approach the altar, next to a large well.

The monk comes in from a side door and seeks your contact. 
"You must be {name}. The king was expecting you. Yet no one could expect his fate."
You nod.

"I am Nordil, monk overseeing this holy place. Is it true" he asks, "that you are going to defeat the evil?"

"Bring back the three pearls, as they are the only thing that can save our king."

He smiles, but he seems troubled."""
        ],
        'talk': {
            'monk': [
                f"""The monk greets you. He does not dare to meet you gaze when saying:
"{name}, I have a favor to ask.
Should you travel our lands, please visit the village north of the plains.

My brother, Vernal is the local gravedigger. Please, if you find him, report back.
Some reports came in that undead creates were spotted in that area. I am sick of worry.

Let me at least heal your wounds. If you spot him, please let me know and I will make sure that your effort will be rewarded beyond that.\""""
            ],
            'brother': [
                f"""You report of Vernal's wellbeing.

"Forgive me, but I am not sure I can believe you." replied Nordil in sadness.

When asked if he remembers to pay his brother back three coins from their last gamble the monks eyes light up.

"Indeed! Vernal is alive! Here take this! It a talisman that can find undead evil."

He moves away, turns back and hands you three coins.
"Take these, and make sure they end up with my brother."
He smiles, nods and leaves."""
            ]
        }
    },
    L_CASTLE: {
        'music': 'home',
        'obstacle': {
            L_FOREST: [
                f"""You can not pass before the drawbridge is lowered."""
            ],
        },
        'cleared': [
            """The rats have been decimated. The drawbridge is functional again. You should talk to the commander."""
        ],
        'epilogue': [
            f"""You wake up back in the castle. The king and Nordil are sitting next to your bed. You can barely remember what happened.
\"The hero is awake. {name}! Welcome back\" says the king, while holding your shoulder.

\"I owe you my kingdom. I owe you my life. From here on you shall be known as the third dragon.\"

The group is led towards the castle's balcony, where the people from all the land gathered to celebrate your victory.
And far out in the sky you can see the silhouette of a red dragon passing by. It may not be over yet ...        
"""
        ],
        'talk': {
            "king": [f"""The second you make a step the three pearls light up.
             The king's statue starts to glow. Will it be able to break the spell?

            But before you know it a dark shadow appears. The sorcerer enters and stops the glowing with a sudden move and some mumbling that you can not fully comprehend. 

            \"{name}, is it? You seem to have fought well. But this will not bring back your king. I am the ruler of this world now!\"

            He sends a powerful blast your direction - you can barely dodge it. The sorcerer is gone, but in his place stands a shining portal of some sort. It seems that having the pearls in reach keeps the portal open.

            You feel that there might be no escape from where this portal leads. You better be prepared before entering.
            """
                     ],
            'rats': [
                f"""You tell the commander that the rats are decimated by your actions.

"Well done! Now passage outside the castle is possible again. I do not recommend leaving to anyone but the most courageous.
We heard reports of monsters blocking the path to the east.

Take this - may it be of help on your journey.\""""
            ],
        },
        'story': [
            f"""The castle drawbridge is lowered at your arrival. The guards already expect you, {name} - the famous adventurer. They escort you to the throne room, where the anxious king Balaar, ruler of the Kingdom of Pearls awaits you.
           He explains his worries. The evil sorcerer, Xonius, threatened the king! He plans to takeover the rule. But even with his best man at the guard, the king fears for his life. Xonius is a powerful mage, who has the forbidden knowledge of dark magic. He can spawn an army of monsters, if only he would get hold of the king's magical crown, that hosts three pearls. 
These pearls are known to have special powers, but the knowledge to unlock it has been lost.

Within that moment, the glass windows of the throne room shattered. A dark cloud emerged, and Xonius stepped our of the cloud. """,
            f""""Guards!" shouted the king, but it was too late, as the sorcerer already spoke his magic spell and turned the king to stone, while hastily taking the crown off his majesty's head. The moment you tried to step in, Xonius disappeared again in the dark cloud.

The magic lifted - and all that was left, is a king made of stone and shattered glass. But this should only be the beginning of the tragedy in the lands of the kingdom.

Reports of monster hordes came in. Even the castle was not spared - as a plague of rats infested the castle's cellar.

"We can't lower the castle's drawbridge, if we do not get rid of the rats.", explained the guard's commander.
"The rats infested the winch. If we could only lower their numbers."

Who will be brave enough to face the evil sorcerer, rescue the lands from the monsters and bring back the three magical pearls to break the kings spell?
"""
        ]
    }
}
# -----------------------------------------------------------------------------
# -- Global state
# -----------------------------------------------------------------------------
name = ""
backpack = ""
level = 0
backpack_size = 0
location = ""
visited = []
max_health = 0
health = 0
xp = 0
music = ""
equiped = [
    ['l', "🇱 Left Hand", ""],
    ['r', "🇷 Right Hand", ""],
    ['a', "🖐️ Arms/Hands", ""],
    ['f', "🦶 Feet", ""],
    ['j', "🫳 Jewellery", ""],
    ['h', "🧑 Head", ""],
]
quests = {
    'king': 0,
    # 1 - Tried to revive him (portal opens)
    'rats': 0, # 0 - Commander is about to give you money if rats are cleared
    # 1 - You got the reward
    'monk': 0, # 0 - Not talked to monk
    # 1 - Quest to find brother
    # 2 - Talked to brother
    'ocean': 0,  # 0 - No boss
    # 1 - Dropped bomb, boss appears
}


# -----------------------------------------------------------------------------
# -- Display
# -----------------------------------------------------------------------------
def wrap(text, length=50):
    new_text = []
    for line in text.split('\n'):
        if len(line) > length:
            cur_length = 0
            split_line = line.split()
            start = 0
            for i, word in enumerate(split_line):
                cur_length += len(word) + 1
                if cur_length > length:
                    new_text.append(" ".join(split_line[start:i+1]))
                    start = i+1
                    cur_length = 0
            new_text.append(" ".join(split_line[start:]))
        else:
            new_text.append(line)
    return "\n".join(new_text)


def lore(location, new_location=None, category='story', title='You entered the '):

    if not location in LORE().keys():
        return
    if category not in LORE()[location].keys():
        return
    all_story_elements = LORE()[location][category]
    if new_location != None:
        all_story_elements = all_story_elements[new_location]
    for i, story in enumerate(all_story_elements):
        clear()
        print("""
O---------------------------------------------------------------O
""" + f"{title}{location}".center(64) +
              """\nO---------------------------------------------------------------O
""")
        if i > 0:
            print("    [...]\n")
        #print("    " + textwrap.fill(story, 55, replace_whitespace=False, drop_whitespace=False, break_on_hyphens=False).replace('\n', '\n    '))
        print("    " + wrap(story).replace('\n', '\n    '))
        if i < len(all_story_elements) -1:
            print("\n    [...]")
        pause("\n")




def pause(text):
    input(text + " (Press Enter to continue)")


def intro():
    print("""
                     _   __ _____  _   _  _____ ______  _____ ___  ___    _____ ______  
                    | | / /|_   _|| \ | ||  __ \|  _  \|  _  ||  \/  |   |  _  ||  ___| 
                    | |/ /   | |  |  \| || |  \/| | | || | | || .  . |   | | | || |_    
                    |    \   | |  | . ` || | __ | | | || | | || |\/| |   | | | ||  _|   
                    | |\  \ _| |_ | |\  || |_\ \| |/ / \ \_/ /| |  | |   \ \_/ /| |     
                    \_| \_/ \___/ \_| \_/ \____/|___/   \___/ \_|  |_/    \___/ \_|     
                                                                                      
                                                                                      
                                ______  _____   ___  ______  _      _____               
                                | ___ \|  ___| / _ \ | ___ \| |    /  ___|              
                                | |_/ /| |__  / /_\ \| |_/ /| |    \ `--.               
                                |  __/ |  __| |  _  ||    / | |     `--. \              
                                | |    | |___ | | | || |\ \ | |____/\__/ /              
                                \_|    \____/ \_| |_/\_| \_|\_____/\____/               
    """)
    print(29 * ' ' +"""\033[49m                        \033[38;2;96;204;227;49m▄▄▄\033[49m                       \033[m
    \033[49m                    \033[38;2;251;242;56;49m▄\033[49m \033[38;2;99;185;203;49m▄\033[38;2;88;141;152;48;2;96;204;227m▄\033[48;2;99;185;203m \033[38;2;99;185;203;48;2;248;248;248m▄\033[38;2;202;218;252;48;2;248;248;248m▄\033[38;2;248;248;248;48;2;96;204;227m▄\033[38;2;96;204;227;49m▄\033[49m \033[38;2;251;242;56;49m▄\033[49m                   \033[m
    \033[49m                   \033[49;38;2;251;242;56m▀\033[49m \033[48;2;195;162;30m \033[38;2;100;154;255;48;2;99;185;203m▄\033[38;2;92;110;224;48;2;88;141;152m▄\033[38;2;100;154;255;48;2;99;185;203m▄\033[38;2;88;141;152;48;2;99;185;203m▄\033[48;2;99;185;203m \033[38;2;99;185;203;48;2;202;218;252m▄\033[48;2;96;204;227m \033[48;2;251;242;56m \033[49m \033[49;38;2;251;242;56m▀\033[49m                  \033[m
    \033[49m         \033[38;2;96;204;227;49m▄\033[38;2;99;185;203;48;2;96;204;227m▄\033[38;2;248;248;248;48;2;96;204;227m▄▄\033[38;2;96;204;227;49m▄\033[49m        \033[49;38;2;195;162;30m▀\033[38;2;195;162;30;48;2;100;154;255m▄\033[38;2;100;154;255;48;2;92;110;224m▄\033[48;2;100;154;255m \033[38;2;100;154;255;48;2;88;141;152m▄\033[38;2;251;242;56;48;2;99;185;203m▄\033[49;38;2;251;242;56m▀\033[49m         \033[38;2;96;204;227;49m▄\033[38;2;99;185;203;48;2;96;204;227m▄\033[38;2;248;248;248;48;2;96;204;227m▄▄\033[38;2;96;204;227;49m▄\033[49m       \033[m
    \033[49m     \033[38;2;251;242;56;49m▄\033[49;38;2;251;242;56m▀\033[38;2;195;162;30;49m▄\033[48;2;99;185;203m \033[48;2;88;141;152m \033[48;2;99;185;203m  \033[38;2;99;185;203;48;2;202;218;252m▄\033[38;2;202;218;252;48;2;248;248;248m▄\033[48;2;96;204;227m \033[38;2;251;242;56;49m▄\033[49;38;2;251;242;56m▀\033[38;2;251;242;56;49m▄\033[49m   \033[38;2;95;73;68;49m▄\033[49m \033[49;38;2;195;162;30m▀\033[38;2;145;122;36;48;2;195;162;30m▄\033[38;2;145;122;36;48;2;251;242;56m▄\033[38;2;195;162;30;48;2;251;242;56m▄\033[49;38;2;251;242;56m▀\033[49m      \033[38;2;251;242;56;49m▄\033[49;38;2;251;242;56m▀\033[38;2;195;162;30;49m▄\033[48;2;99;185;203m \033[48;2;88;141;152m \033[48;2;99;185;203m  \033[38;2;99;185;203;48;2;202;218;252m▄\033[38;2;202;218;252;48;2;248;248;248m▄\033[48;2;96;204;227m \033[38;2;251;242;56;49m▄\033[49;38;2;251;242;56m▀\033[38;2;251;242;56;49m▄\033[49m   \033[m
    \033[49m       \033[49;38;2;195;162;30m▀\033[38;2;195;162;30;48;2;100;154;255m▄\033[38;2;100;154;255;48;2;92;110;224m▄\033[38;2;92;110;224;48;2;100;154;255m▄\033[38;2;100;154;255;48;2;88;141;152m▄\033[38;2;88;141;152;48;2;99;185;203m▄\033[48;2;99;185;203m \033[38;2;251;242;56;48;2;96;204;227m▄\033[49;38;2;251;242;56m▀\033[49m    \033[38;2;89;87;83;48;2;95;73;68m▄\033[38;2;131;125;134;48;2;95;73;68m▄\033[49m       \033[38;2;95;73;68;49m▄\033[48;2;95;73;68m \033[49m     \033[49;38;2;195;162;30m▀\033[38;2;195;162;30;48;2;100;154;255m▄\033[38;2;100;154;255;48;2;92;110;224m▄\033[38;2;92;110;224;48;2;100;154;255m▄\033[38;2;100;154;255;48;2;88;141;152m▄\033[38;2;88;141;152;48;2;99;185;203m▄\033[48;2;99;185;203m \033[38;2;251;242;56;48;2;96;204;227m▄\033[49;38;2;251;242;56m▀\033[49m     \033[m
    \033[49m         \033[48;2;195;162;30m \033[38;2;195;162;30;48;2;100;154;255m▄\033[38;2;251;242;56;48;2;100;154;255m▄▄\033[48;2;251;242;56m \033[49m      \033[48;2;89;87;83m \033[48;2;131;125;134m \033[38;2;131;125;134;48;2;120;113;123m▄\033[38;2;131;125;134;49m▄\033[38;2;154;172;182;49m▄▄\033[38;2;95;73;68;49m▄\033[38;2;89;87;83;49m▄\033[38;2;95;73;68;49m▄\033[48;2;131;125;134m \033[38;2;131;125;134;48;2;154;172;182m▄\033[49m       \033[48;2;195;162;30m \033[38;2;195;162;30;48;2;100;154;255m▄\033[38;2;251;242;56;48;2;100;154;255m▄▄\033[48;2;251;242;56m \033[49m       \033[m
    \033[49m          \033[49;38;2;145;122;36m▀▀\033[49;38;2;195;162;30m▀\033[49m       \033[38;2;89;87;83;48;2;95;73;68m▄\033[48;2;89;87;83m \033[38;2;131;125;134;48;2;113;107;116m▄\033[38;2;113;107;116;48;2;131;125;134m▄\033[38;2;131;125;134;48;2;113;107;116m▄\033[48;2;131;125;134m \033[38;2;131;125;134;48;2;120;113;123m▄\033[38;2;113;107;116;48;2;120;113;123m▄\033[38;2;89;87;83;48;2;95;73;68m▄\033[38;2;131;125;134;48;2;120;113;123m▄\033[48;2;154;172;182m \033[49m        \033[49;38;2;145;122;36m▀▀\033[49;38;2;195;162;30m▀\033[49m        \033[m
    \033[49m                    \033[48;2;89;87;83m \033[48;2;95;73;68m \033[38;2;113;107;116;48;2;131;125;134m▄\033[48;2;131;125;134m \033[38;2;61;55;51;48;2;131;125;134m▄\033[38;2;61;55;51;48;2;89;87;83m▄\033[38;2;89;87;83;48;2;120;113;123m▄\033[48;2;120;113;123m \033[38;2;113;107;116;48;2;89;87;83m▄\033[48;2;131;125;134m \033[38;2;113;107;116;48;2;131;125;134m▄\033[49m                   \033[m
    \033[49m                 \033[38;2;83;76;41;49m▄\033[38;2;61;89;95;49m▄▄\033[38;2;61;89;95;48;2;95;73;68m▄\033[38;2;61;89;95;48;2;89;87;83m▄\033[38;2;61;89;95;48;2;131;125;134m▄▄\033[38;2;95;62;85;48;2;61;55;51m▄▄\033[38;2;116;76;59;48;2;61;55;51m▄\033[38;2;61;89;95;48;2;120;113;123m▄\033[38;2;88;141;152;48;2;113;107;116m▄\033[38;2;83;76;41;48;2;131;125;134m▄\033[38;2;88;141;152;48;2;131;125;134m▄\033[38;2;61;89;95;49m▄\033[38;2;88;141;152;49m▄\033[38;2;76;105;50;49m▄\033[49m                \033[m
    \033[49m        \033[38;2;83;76;41;49m▄▄▄\033[38;2;57;74;41;49m▄▄\033[38;2;57;74;41;48;2;83;76;41m▄▄▄\033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;57;74;41m \033[38;2;71;95;49;48;2;83;76;41m▄\033[38;2;83;76;41;48;2;61;89;95m▄\033[38;2;83;76;41;48;2;102;60;52m▄\033[38;2;116;76;59;48;2;76;105;50m▄\033[38;2;102;60;52;48;2;76;105;50m▄▄\033[38;2;102;60;52;48;2;95;62;85m▄\033[38;2;102;60;52;48;2;116;76;59m▄\033[38;2;102;60;52;48;2;142;87;61m▄\033[38;2;116;76;59;48;2;61;89;95m▄\033[38;2;116;76;59;48;2;83;76;41m▄\033[48;2;76;105;50m \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;85;123;50m   \033[38;2;85;123;50;48;2;102;152;56m▄▄\033[38;2;85;123;50;49m▄▄▄\033[38;2;102;152;56;49m▄\033[49m          \033[m
    \033[49m \033[38;2;83;76;41;49m▄▄\033[38;2;57;74;41;48;2;83;76;41m▄\033[48;2;57;74;41m     \033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;57;74;41m \033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;71;95;49m \033[38;2;71;95;49;48;2;57;74;41m▄\033[38;2;116;76;59;48;2;71;95;49m▄\033[38;2;116;76;59;48;2;102;60;52m▄▄\033[38;2;62;81;42;48;2;102;60;52m▄\033[38;2;62;81;42;48;2;116;76;59m▄▄▄\033[38;2;76;105;50;48;2;116;76;59m▄▄\033[38;2;76;105;50;48;2;142;87;61m▄\033[38;2;76;105;50;48;2;116;76;59m▄\033[48;2;76;105;50m      \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;76;105;50m  \033[38;2;85;123;50;48;2;76;105;50m▄\033[38;2;76;105;50;48;2;85;123;50m▄▄▄\033[38;2;85;123;50;48;2;76;105;50m▄\033[48;2;85;123;50m \033[48;2;76;105;50m \033[38;2;76;105;50;48;2;85;123;50m▄▄\033[38;2;85;123;50;48;2;102;152;56m▄\033[38;2;85;123;50;49m▄\033[38;2;102;152;56;49m▄\033[49m    \033[m
    \033[48;2;57;74;41m   \033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;57;74;41m \033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;71;95;49m    \033[38;2;57;74;41;48;2;71;95;49m▄\033[48;2;71;95;49m  \033[38;2;71;95;49;48;2;57;74;41m▄\033[48;2;71;95;49m \033[38;2;62;81;42;48;2;102;60;52m▄\033[38;2;62;81;42;48;2;116;76;59m▄▄\033[38;2;102;60;52;48;2;116;76;59m▄\033[38;2;142;87;61;48;2;116;76;59m▄\033[48;2;116;76;59m \033[38;2;142;87;61;48;2;116;76;59m▄\033[48;2;116;76;59m \033[38;2;142;87;61;48;2;116;76;59m▄\033[48;2;116;76;59m  \033[38;2;116;76;59;48;2;102;60;52m▄▄▄\033[38;2;116;76;59;48;2;76;105;50m▄▄▄▄\033[38;2;142;87;61;48;2;76;105;50m▄▄\033[48;2;76;105;50m  \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;76;105;50m \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;76;105;50m \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;76;105;50m \033[38;2;85;123;50;48;2;76;105;50m▄\033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;76;105;50m  \033[38;2;76;105;50;48;2;85;123;50m▄\033[48;2;85;123;50m \033[38;2;76;105;50;48;2;85;123;50m▄\033[m""".replace('\n', '\n' + ' ' * 25))
    print(f"©2023 StateOffGames - v{VERSION}".center(110))
    if WITH_MUSIC:
        print("Royalty free music from https://www.FesliyanStudios.com".center(110))

# -----------------------------------------------------------------------------
# -- Game
# -----------------------------------------------------------------------------

def main_menu():

    play_music('home')

    while True:
        clear()
        intro()
        options = get_main_options(with_new_game=True, with_save=False)
        try:
            action = get_action(options, "", "", False)
            options[action][2]()
        except InvalidSelection:
            pause("I do not understand.")
        else:
            try:
                loop()
            except GameEnded:
                play_music('home', force=True)
                pass



def game_over(text):
    play_music('gameover', 1)
    print("""
     _______  _______  __   __  _______    _______  __   __  _______  ______   
    |       ||   _   ||  |_|  ||       |  |       ||  | |  ||       ||    _ |  
    |    ___||  |_|  ||       ||    ___|  |   _   ||  |_|  ||    ___||   | ||  
    |   | __ |       ||       ||   |___   |  | |  ||       ||   |___ |   |_||_ 
    |   ||  ||       ||       ||    ___|  |  |_|  ||       ||    ___||    __  |
    |   |_| ||   _   || ||_|| ||   |___   |       | |     | |   |___ |   |  | |
    |_______||__| |__||_|   |_||_______|  |_______|  |___|  |_______||___|  |_|
            """)
    pause(text.center(77) + "\n")
    raise GameEnded


def new_game():
    global name, backpack, level, backpack_size, location, visited, max_health, health, xp

    clear()
    intro()

    name = ""
    while name.strip() == "":
        name = input("What is the name of the hero? ")

    if len(name) > 20:
        name = name[:20]
        pause(f"That's a long name. I will call you {name}")

    print("Welcome", name, "on your great adventure!")
    backpack = f"{I_POTION}{I_COIN * 2}" + (f"{I_BATTLE_AXE}{I_CROWN}{I_SHIELD}{I_BATTLE_AXE}{I_BOMB}{I_COIN * DEBUG_START_COINS}{I_PEARL * DEBUG_START_PEARL_COUNT}" if DEBUG_LARGE_INVENTORY else "")
    level = DEBUG_START_LEVEL
    backpack_size = LEVELS['backpack'][level - 1]
    location = ""
    visited = []
    max_health = LEVELS['health'][level - 1]
    health = max_health
    xp = LEVELS['xp'][level - 1]

    goto(L_CASTLE)


def save():
    state = {}
    state['name'] = name
    state['backpack'] = backpack
    state['level'] = level
    state['location'] = location
    state['visited'] = visited
    state['health'] = health
    state['xp'] = xp
    state['equiped'] = equiped
    state['QUESTS'] = quests
    state['MONSTER_CLEARED'] = MONSTER_CLEARED

    with open('kop.sav', 'w') as fh:
        json.dump(state, fh)

    pause("Game Saved")


def save_exists():
    return os.path.isfile('kop.sav')


def load():
    print('LOAD"$",8,1')
    global name, backpack, level, location, visited, health, backpack_size, max_health, xp, equiped, quests, MONSTER_CLEARED
    state = {}
    with open('kop.sav', 'r') as fh:
        state = json.load(fh)

    name = state['name']
    backpack = state['backpack']
    level = state['level']
    visited = state['visited']
    health = state['health']
    xp = state['xp']
    # Else we would overwrite labels
    for i, e in enumerate(state['equiped']):
        equiped[i][2] = e[2]

    backpack_size = LEVELS['backpack'][level - 1]
    max_health = LEVELS['health'][level - 1]
    quests = state['QUESTS']
    MONSTER_CLEARED = state['MONSTER_CLEARED']
    pause("Game Loaded")
    goto(state['location'])


def increment_quest(name):
    global quests
    quests[name] += 1


def pickup(item, condition=None):
    global backpack, location
    available = True
    if condition:
        available = condition()

    if available:
        backpack += item
    else:
        lore(location, item, 'obstacle', 'You are stuck at the ')


def goto(new_location, condition=None):
    global location, visited
    available = True
    if condition:
        available = condition()

    if available:
        location = new_location
        play_music(LORE()[location]['music'])
        if location not in visited:
            lore(location)
            visited.append(new_location)
    else:
        lore(location, new_location, 'obstacle', 'You are stuck at the ')


def heal(added_health):
    global health
    health = min(max_health, health + added_health)
    pause("You feel refreshed!")


def money():
    global backpack
    return backpack.count(I_COIN)


def withdraw(count, item=I_COIN, mode=BACKPACK_ONLY):
    global backpack, equiped
    if mode in (BACKPACK_ONLY, BACKPACK_OR_EQUIPPED):
        old_len = regex.findall(r'\X', backpack).count(item)
        backpack = backpack.replace(item, '', count)
        new_len = regex.findall(r'\X', backpack).count(item)
        count -= (old_len - new_len)
    if mode in (EQUIPPED_ONLY, BACKPACK_OR_EQUIPPED):
        for e in equiped:
            old_len = regex.findall(r'\X', e[2]).count(item)
            e[2] = e[2].replace(item, '', count)
            new_len = regex.findall(r'\X', e[2]).count(item)
            count -= (old_len - new_len)



def buy(item, condition=None):
    global PRICES, backpack
    available = True
    if condition:
        available = condition()

    if available:
        price = PRICES[item]
        if money() < price:
            pause("☹️ Sorry! You don't have enough coins")
        else:
            withdraw(price)
            backpack += item
            pause(f"You added a {item} to your backpack.")
    else:
        lore(location, item, 'obstacle', 'Can not buy at the ')


def roll(dice):
    result = []
    for die in dice:
        throw = random.choice(regex.findall(r'\X', DICE[die]))
        result.append((die, throw))

    return result


def gain_xp(added_xp):
    global xp, backpack_size, max_health, level, health
    old_xp = xp
    xp += added_xp

    for new_level, level_xp in enumerate(LEVELS['xp']):
        if xp >= level_xp and new_level + 1 > level:
            backpack_size = LEVELS['backpack'][new_level]
            max_health = LEVELS['health'][new_level]
            health = max_health
            level = new_level + 1
            pause(f"{S_NORTH} YOU REACHED LEVEL {level}! You feel stronger!")
            break



def max_potions_usable():
    global level
    return (level+1) // 2



def fight(zone):
    global health, backpack, MONSTER_ZONES, MONSTER_CLEARED, equiped

    potions_used = 0
    monster = random.choice(MONSTER_ZONES[zone])

    if monster in BOSSES:
        play_music('boss')

    values = MONSTERS[monster]
    monster_dice = f"{values[0] * D_PURPLE}{values[1] * D_BLACK}"
    monster_max_health = values[2]
    monster_health = values[2]
    monster_xp = values[3]
    if MONSTER_CLEARED[zone] == 0:
        monster_xp = monster_xp // 10

    monster_loot = values[4]
    damage_callback = values[5]
    damage_message = values[6]
    damage_message_callback = None
    if callable(damage_message):
        damage_message_callback = damage_message
        damage_message = "PLACEHOLDER o_O"

    player_dice = get_player_dice()

    while monster_health > 0 and health > 0:

        status(
            f"{monster} in sight! {values[0] * D_PURPLE}{values[1] * D_BLACK} | " + S_HEART * monster_health + S_HEART_EMPTY * (
                    monster_max_health - monster_health))

        attack = list(ACTIONS['attack'])
        attack[1] += f" {player_dice}"
        options = [
            attack,
        ]
        shoe_count = 0
        for pack in equiped:
            shoe_count += pack[2].count(I_SHOES)
        if monster != E_SORCERER and (shoe_count >= 2 and monster in BOSSES) or (shoe_count >= 1 and monster not in BOSSES):
            options.append(ACTIONS['retreat'])
        if I_POTION in backpack and potions_used < max_potions_usable():
            options.append(ACTIONS['potion'])
        if I_BANDAGE in backpack:
            options.append(ACTIONS['bandage'])
        if I_BOMB in backpack:
            options.append(ACTIONS['bomb'])

        print(SEPARATOR_DO[1])
        valid_options = []
        for option in options:
            valid_options.append(option[0])
            print(f"{option[0]} {option[1]}")

        try:
            cmd = input("\nYour selection: ")
            if cmd not in valid_options:
                raise ValueError
        except ValueError:
            pause("I do not understand.")
        else:
            if cmd == ACTIONS['attack'][0]:
                clear()
                status(f"{monster} ready to attack {values[0] * D_PURPLE}{values[1] * D_BLACK} | " + S_HEART * monster_health + S_HEART_EMPTY * (monster_max_health - monster_health), "ATTACKING!")
                print("PLAYER THROWS:")
                player_roll = roll(player_dice)
                altered, player_roll = damage_callback(player_roll)
                for die, throw in player_roll:
                    if die == D_YELLOW:
                        throw = throw.replace(I_SWORD, S_MAGIC)
                    print(f"{die} {throw}")

                print("MONSTER THROWS:")
                monster_roll = roll(monster_dice)
                for die, throw in monster_roll:
                    print(f"{die} {throw}")

                player_sum = "".join([throw for die, throw in player_roll])
                monster_sum = "".join([throw for die, throw in monster_roll])
                player_damage = max(0, monster_sum.count(I_SWORD) - player_sum.count(I_SHIELD))
                monster_damage = max(0, player_sum.count(I_SWORD) - monster_sum.count(I_SHIELD))
                print(f"PLAYER {player_damage * S_HIT or S_MISS}")
                print(f"MONSTER {monster_damage * S_HIT or S_MISS}")
                if altered and damage_message:
                    if damage_message_callback:
                        damage_message = damage_message_callback()
                    print(damage_message)

                monster_health = max(0, monster_health - monster_damage)
                health = max(0, health - player_damage)

                if monster == E_VAMPIRE and monster_health > 0 and monster_health < monster_max_health and player_damage > 0:
                    monster_health = min(monster_max_health, monster_health + 1)
                    print(f"The {E_VAMPIRE} regained {S_HEART} health by drinking your blood.")

                pause("")
            elif cmd == ACTIONS['retreat'][0]:
                # Retreat!
                play_music(LORE()[location]['music'])
                return
            elif cmd == ACTIONS['potion'][0]:
                potions_used += 1
                backpack = backpack.replace(I_POTION, "", 1)
                potion_die = D_GREEN
                player_dice += potion_die
                limit_message = f"\n{S_BLOCKED} You can not use more potions at this level" if potions_used >= max_potions_usable() else ""
                pause(f"You feel stronger. A {potion_die} was added." + limit_message)
            elif cmd == ACTIONS['bandage'][0]:
                apply_bandage()
            elif cmd == ACTIONS['bomb'][0]:
                msg = "The bomb exploded"
                monster_damage = 3
                if monster == E_SORCERER:
                    monster_damage = 0
                    msg = "The sorcerer is not affected by the bomb."
                player_damage = 1
                monster_health = max(0, monster_health - monster_damage)
                health = max(0, health - player_damage)
                backpack = backpack.replace(I_BOMB, "", 1)
                print(f"PLAYER {player_damage * S_HIT}")
                print(f"MONSTER {monster_damage * S_HIT}")
                pause(msg)
            else:
                pause("I do not understand.")

    if health == 0:
        game_over(f"{S_SKULL * 3} YOU WERE DEFEATED {S_SKULL * 3}")
    if monster_health == 0:
        old_clear_count = MONSTER_CLEARED[zone]
        MONSTER_CLEARED[zone] = max(0, MONSTER_CLEARED[zone] - 1)
        if monster in BOSSES:
            play_music('success', 1)
        pause(f'THE MONSTER IS DEFEATED{". YOU FOUND " if monster_loot else ""}{monster_loot}. GAINED {monster_xp} XP')
        gain_xp(monster_xp)
        backpack += monster_loot
        if old_clear_count > 0 and MONSTER_CLEARED[zone] == 0:
            play_music('success', 1)
            lore(location, None, 'cleared', 'You cleared the ')

        play_music(LORE()[location]['music'])



def get_player_dice():
    global equiped
    player_dice = DEFAULT_ITEM_EFFECT
    for pack in equiped:
        for item in regex.findall(r'\X', pack[2]):
            if item in ITEM_EFFECTS:
                player_dice += ITEM_EFFECTS[item]
    return player_dice


def apply_bandage():
    global backpack, health
    backpack = backpack.replace(I_BANDAGE, "", 1)
    health = min(max_health, health + 2)
    pause(f"You feel better {S_HEART * 2}")


SEPARATOR_LEN = 50
SEPARATOR_GO = (None, '\n' + f'{{ {S_COMPASS} GO }}'.center(SEPARATOR_LEN, '-'))
SEPARATOR_DO = (None, '\n' + f'{{ {S_ACTION} DO }}'.center(SEPARATOR_LEN, '-'))
SEPARATOR_BUY = (None, '\n' + f'{{ {S_BUY} BUY }}'.center(SEPARATOR_LEN, '-'))
SEPARATOR_STATUS = (None, '\n' + f'{{ {S_STATUS} STATUS }}'.center(SEPARATOR_LEN, '-'))
SEPARATOR_OPTIONS = (None, '\n' + f'{{ {S_OPTIONS} OPTIONS }}'.center(SEPARATOR_LEN, '-'))


def monsters_cleared(zone):
    if MONSTER_CLEARED[zone] == BOSS_MONSTER:
        if DEBUG_BOSSES_CLEARED:
            return True
    elif DEBUG_MONSTERS_CLEARED:
            return True
    return MONSTER_CLEARED[zone] == 0



def has_items(item_counts, mode=BACKPACK_ONLY):
    global backpack, equiped
    has_all = True
    for item_count in item_counts:
        count, item = item_count
        backpack_count = 0
        if mode == BACKPACK_ONLY or mode == BACKPACK_OR_EQUIPPED:
            backpack_count += backpack.count(item)
        equiped_count = 0
        if mode == EQUIPPED_ONLY or mode == BACKPACK_OR_EQUIPPED:
            for pack in equiped:
                equiped_count += pack[2].count(item)
        if backpack_count + equiped_count < count:
            has_all = False

    return has_all

def talk(location, person, talk_callback=None):
    lore(location, person, 'talk', "Discussion at the ")
    if talk_callback is not None:
        talk_callback()

LOCATION_OPTIONS = {
    L_CASTLE: [
        SEPARATOR_GO,
        ('n', f"{S_NORTH} [n]orth to the shop", lambda: goto(L_SHOP)),
        ('e', f"{S_EAST} [e]ast to the forest", lambda: goto(L_FOREST, lambda: quests['rats'] == 1 and monsters_cleared(L_CASTLE)), lambda: quests['rats'] == 1 and monsters_cleared(L_CASTLE)),
        ('s', f"{S_SOUTH} [s]outh through portal", lambda: [goto(L_PORTAL, lambda: has_items([(3, I_PEARL)], EQUIPPED_ONLY)), withdraw(3, I_PEARL, BACKPACK_OR_EQUIPPED)], lambda: quests['king'] == 1 and has_items([(3, I_PEARL)], EQUIPPED_ONLY), True),
        SEPARATOR_DO,
        ('k', f"{I_CROWN} Revive the [k]ing", lambda: [talk(L_CASTLE, 'king', lambda: has_items([(3, I_PEARL)], EQUIPPED_ONLY)), increment_quest('king')], lambda: quests['king'] == 0 and has_items([(3, I_PEARL)], EQUIPPED_ONLY), True),
        ('t', f"{S_TALK} [t]alk to the commander", lambda: talk(L_CASTLE, 'rats', lambda: [pickup(f"{I_COIN * 2}"), increment_quest('rats')]), lambda: quests['rats'] == 0 and monsters_cleared(L_CASTLE), True),
        ('f', f"{S_FIGHT} [f]ight rats in cellar", lambda: fight(L_CASTLE), lambda: not monsters_cleared(L_CASTLE), True),
    ],
    L_CATHEDRAL: [
        SEPARATOR_GO,
        ('s', f"{S_SOUTH} [s]outh to the shop", lambda: goto(L_SHOP)),
        SEPARATOR_DO,
        ('t', f"{S_TALK} [t]alk to the monk", lambda: talk(L_CATHEDRAL, 'monk', lambda: increment_quest('monk')), lambda: quests['monk'] == 0, True),
        ('t', f"{S_TALK} [t]alk to the monk", lambda: talk(L_CATHEDRAL, 'brother', lambda: [pickup(f"{I_AMULET}{I_COIN * 3}"), increment_quest('monk')]), lambda: quests['monk'] == 2, True),
        ('h', f"{S_WELL} [h]eal at the well", lambda: heal(max_health), lambda: quests['monk'] >= 1, True),
    ],
    L_SHOP: [
        SEPARATOR_GO,
        ('n', f"{S_NORTH} [n]orth to the cathedral", lambda: goto(L_CATHEDRAL)),
        ('s', f"{S_SOUTH} [s]outh to the castle", lambda: goto(L_CASTLE)),
        SEPARATOR_BUY,
        ('S', f"{I_SWORD} Buy a [S]word (Effect: {ITEM_EFFECTS[I_SWORD]} Cost: {PRICES[I_SWORD]})", lambda: buy(I_SWORD)),
        ('G', f"{I_GLOVES} Buy [G]loves (Effect: {ITEM_EFFECTS[I_GLOVES]} Cost: {PRICES[I_GLOVES]})", lambda: buy(I_GLOVES)),
        ('H', f"{I_BANDAGE} Buy [H]ealing bandages (Effect: {S_HEART * 2} Cost: {PRICES[I_BANDAGE]})", lambda: buy(I_BANDAGE)),
        ('E', f"{I_SHOES} Buy Sho[E] (Effect: 1x{I_SHOES} = {S_RETREAT} Monsters, 2x{I_SHOES} = {S_RETREAT} Bosses, Cost: {PRICES[I_SHOES]})",
         lambda: buy(I_SHOES), lambda: not has_items([(2, I_SHOES)], BACKPACK_OR_EQUIPPED), True),
    ],
    L_FOREST: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the castle", lambda: goto(L_CASTLE)),
        ('e', f"{S_EAST} [e]ast to the bridge", lambda: goto(L_BRIDGE, lambda: monsters_cleared(L_FOREST) ), lambda: monsters_cleared(L_FOREST)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_FOREST), lambda: not monsters_cleared(L_FOREST), True),
    ],
    L_BRIDGE: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the forest", lambda: goto(L_FOREST)),
        ('e', f"{S_EAST} [e]ast to the swamp", lambda: goto(L_SWAMP, lambda: monsters_cleared(L_BRIDGE) ), lambda: monsters_cleared(L_BRIDGE)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_BRIDGE), lambda: not monsters_cleared(L_BRIDGE), True),
    ],
    L_SWAMP: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the bridge", lambda: goto(L_BRIDGE)),
        ('s', f"{S_SOUTH} [s]outh to the hut", lambda: goto(L_HUT, lambda: I_COFFIN in backpack), lambda: I_COFFIN in backpack),
        ('n', f"{S_NORTH} [n]orth to the ruins", lambda: goto(L_RUINS, lambda: monsters_cleared(L_SWAMP)), lambda: monsters_cleared(L_SWAMP)),
        ('e', f"{S_EAST} [e]ast to the desert", lambda: goto(L_DESERT, lambda: monsters_cleared(L_SWAMP)), lambda: monsters_cleared(L_SWAMP)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_SWAMP), lambda: not monsters_cleared(L_SWAMP), True),
    ],
    L_HUT: [
        SEPARATOR_GO,
        ('n', f"{S_NORTH} [n]orth to the swamp", lambda: goto(L_SWAMP)),
        SEPARATOR_BUY,
        ('B', f"{I_BOW} Buy a [B]ow (Effect: {ITEM_EFFECTS[I_BOW]} Cost: {PRICES[I_BOW]})", lambda: buy(I_BOW)),
        ('P', f"{I_POTION} Buy a [P]otion (Effect: 1 Random Dice Cost: {PRICES[I_POTION]})", lambda: buy(I_POTION)),
        ('O', f"{I_BOMB} Buy a B[O]mb (Effect: {3 * S_HIT} + {S_HIT} to self, Cost: {PRICES[I_BOMB]})", lambda: buy(I_BOMB)),
    ],
    L_RUINS: [
        SEPARATOR_GO,
        ('s', f"{S_SOUTH} [s]outh to the swamp", lambda: goto(L_SWAMP)),
        ('e', f"{S_EAST} [e]ast to the graveyard", lambda: goto(L_GRAVEYARD, lambda: monsters_cleared(L_RUINS)), lambda: monsters_cleared(L_RUINS)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_RUINS), lambda: not monsters_cleared(L_RUINS), True),
    ],
    L_GRAVEYARD: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]west to the ruins", lambda: goto(L_RUINS)),
        ('n', f"{S_NORTH} [n]orth to the tomb", lambda: goto(L_TOMB, lambda: monsters_cleared(L_GRAVEYARD)), lambda: monsters_cleared(L_GRAVEYARD)),
        ('e', f"{S_EAST} [e]ast to the gravedigger's house", lambda: goto(L_GRAVEDIGGER, lambda: monsters_cleared(L_GRAVEYARD)), lambda: monsters_cleared(L_GRAVEYARD)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_GRAVEYARD)),
    ],
    L_GRAVEDIGGER: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]west to the graveyard", lambda: goto(L_GRAVEYARD)),
        SEPARATOR_DO,
        ('t', f"{S_TALK} [t]alk to the gravedigger", lambda: talk(L_GRAVEDIGGER, 'gravedigger', lambda: increment_quest('monk')), lambda: quests['monk'] == 1, True),
        SEPARATOR_BUY,
        #('P', f"{I_PICKAXE} Buy [P]ickaxe ()", lambda: pickup(I_PICKAXE, lambda: monsters_cleared(L_LAIR)),
        ('B', f"{I_BUCKET} Buy [B]ucket (Effect: {ITEM_EFFECTS[I_BUCKET]} Cost: {PRICES[I_BUCKET]})", lambda: buy(I_BUCKET), lambda: not has_items([(1, I_BUCKET)], BACKPACK_OR_EQUIPPED), True),
        ('P', f"{I_PICKAXE} Buy [P]ickaxe (Effect: Digging Cost: {PRICES[I_PICKAXE]})",
         lambda: buy(I_PICKAXE, lambda: monsters_cleared(L_LAIR)), lambda: not has_items([(1, I_PICKAXE)], BACKPACK_OR_EQUIPPED), True),
    ],
    L_TOMB: [
        SEPARATOR_GO,
        ('s', f"{S_SOUTH} [s]outh to the graveyard", lambda: goto(L_GRAVEYARD)),
        ('e', f"{S_EAST} [e]ast to the lair", lambda: goto(L_LAIR, lambda: monsters_cleared(L_TOMB)), lambda: has_items([(1, I_AMULET)], EQUIPPED_ONLY) or L_LAIR in visited, True),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_TOMB), lambda: not monsters_cleared(L_TOMB), True),
    ],
    L_LAIR: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]west to the tomb", lambda: goto(L_TOMB)),
        SEPARATOR_DO,
        ('C', f"{I_COFFIN} pickup [C]offin", lambda: pickup(I_COFFIN, lambda: monsters_cleared(L_LAIR)), lambda: I_COFFIN not in backpack, True),
        ('f', f"{S_FIGHT} [f]ight Boss", lambda: fight(L_LAIR), lambda: not monsters_cleared(L_LAIR), True),
    ],
    L_DESERT: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the swamp", lambda: goto(L_SWAMP)),
        ('e', f"{S_EAST} [e]ast to the beach", lambda: goto(L_BEACH, lambda: monsters_cleared(L_DESERT)), lambda: monsters_cleared(L_DESERT)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_DESERT), lambda: not monsters_cleared(L_DESERT), True),
    ],
    L_BEACH: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the desert", lambda: goto(L_DESERT)),
        ('e', f"{S_EAST} [e]ast to board a ship", lambda: goto(L_SHIP, lambda: monsters_cleared(L_BEACH) and I_COFFIN in backpack), lambda: monsters_cleared(L_BEACH) and I_COFFIN in backpack),
        ('s', f"{S_SOUTH} [s]outh to enter cave", lambda: goto(L_CAVE, lambda: monsters_cleared(L_BEACH)), lambda: monsters_cleared(L_BEACH)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_BEACH), lambda: not monsters_cleared(L_BEACH), True),
    ],
    L_SHIP: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to go to the beach", lambda: goto(L_BEACH)),
        ('e', f"{S_EAST} [e]ast to sail the ocean", lambda: goto(L_OCEAN, lambda: monsters_cleared(L_SHIP)), lambda: monsters_cleared(L_SHIP)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_SHIP)),
    ],
    L_OCEAN: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to sail back", lambda: goto(L_SHIP)),
        SEPARATOR_DO,
        ('b', f"{I_BOMB} Drop [b]omb into ocean", lambda: [increment_quest('ocean'), withdraw(1, I_BOMB), lore(L_OCEAN, I_BOMB, 'quest', 'Sailing in the ')], lambda: I_BOMB in backpack and quests['ocean'] == 0, True),
        ('f', f"{S_FIGHT} [f]ight Boss", lambda: fight(L_OCEAN), lambda: not monsters_cleared(L_OCEAN) and quests['ocean'] == 1, True),
    ],
    L_CAVE: [
        SEPARATOR_GO,
        ('n', f"{S_NORTH} [n]orth to the beach", lambda: goto(L_BEACH)),
        ('s', f"{S_SOUTH} [s]outh to the mines", lambda: goto(L_MINES, lambda: monsters_cleared(L_CAVE)), lambda: monsters_cleared(L_CAVE) and (has_items([(1, I_PICKAXE)], EQUIPPED_ONLY) or L_MINES in visited), lambda: not has_items([(1, I_PICKAXE)], EQUIPPED_ONLY)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_CAVE)),
    ],
    L_MINES: [
        SEPARATOR_GO,
        ('n', f"{S_NORTH} [n]orth to the cave", lambda: goto(L_CAVE)),
        ('w', f"{S_WEST} [w]est to the blacksmith", lambda: goto(L_BLACKSMITH)),
        ('e', f"{S_EAST} [e]ast to the vulcano", lambda: goto(L_VULCANO, lambda: monsters_cleared(L_MINES)), lambda: monsters_cleared(L_MINES)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Monster", lambda: fight(L_MINES)),
    ],
    L_VULCANO: [
        SEPARATOR_GO,
        ('w', f"{S_WEST} [w]est to the mines", lambda: goto(L_MINES)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Boss", lambda: fight(L_VULCANO), lambda: not monsters_cleared(L_VULCANO), True),
    ],
    L_BLACKSMITH: [
        SEPARATOR_GO,
        ('e', f"{S_EAST} [e]east to the mines", lambda: goto(L_MINES)),
        SEPARATOR_BUY,
        ('X', f"{I_BATTLE_AXE} Buy a battle-a[X]e (Effect: {ITEM_EFFECTS[I_BATTLE_AXE]} Cost: {PRICES[I_BATTLE_AXE]})",
         lambda: buy(I_BATTLE_AXE)),
        ('D', f"{I_SHIELD} Buy a shiel[D] (Effect: {ITEM_EFFECTS[I_SHIELD]} Cost: {PRICES[I_SHIELD]})", lambda: buy(I_SHIELD)),
    ],
    L_PORTAL: [
        #SEPARATOR_GO,
        #('n', f"{S_NORTH} [n]orth to the castle", lambda: goto(L_CASTLE)),
        SEPARATOR_DO,
        ('f', f"{S_FIGHT} [f]ight Evil Sorcerer", lambda: [fight(L_PORTAL), play_music('epilogue'), lore(L_CASTLE, None, 'epilogue', 'Epilogue at the '), game_over("A new adventure awaits ...")], lambda: not monsters_cleared(L_PORTAL), True),
    ]
}

def get_equiped(with_empty=False):
    global equiped
    item_in_use = []
    for i, pack in enumerate(equiped):
        items_to_add = ""
        if pack[2]:
            items_to_add += pack[2]
        if with_empty:
             items_to_add += f"{I_EMPTY} " * (LEVELS['slots'][level][i+1] - len(regex.findall(r'\X', pack[2])))
        item_in_use.append(items_to_add)

    return item_in_use


def status(event="", question="What would you like to do?"):
    clear()
    backpack_item_count = len(regex.findall(r'\X', backpack))
    print(f"""
{'*' * SEPARATOR_LEN}
{location.center(SEPARATOR_LEN)}
{'*' * SEPARATOR_LEN}
{S_STATUS} {name}
🎒 Backpack: {backpack}{(backpack_size - backpack_item_count) * I_EMPTY} ({backpack_item_count} / {backpack_size} | {backpack.count(I_COIN)}x{I_COIN})
{" | ".join(get_equiped(True))}
{get_player_dice()}
HEALTH: {health * S_HEART}{(max_health -  health) * S_HEART_EMPTY} ({int(0.5 + (health / max_health) * 100.0)}%)
LEVEL: {level}
XP: {xp} / {LEVELS['xp'][level]}
{'*' * SEPARATOR_LEN}
{event}""")
    print(f"+-{'-' * len(question)}-+".center(50))
    print(f"| {question} |".center(50))
    print(f"+-{'-' * len(question)}-+".center(50))


def drop_from_backpack(exit_condition=None, message="Too much load"):
    global backpack

    condition = exit_condition
    if exit_condition is None:
        condition = lambda: True

    while condition():
        status(message, "What to drop from your backpack?")

        print(SEPARATOR_DO[1])

        for i, item in enumerate(regex.findall(r'\X', backpack)):
            print(i+1, f"Drop {item}")

        if exit_condition is None:
            print(f'x {S_DONE} e[x]it backpack')

        try:
            cmd = input("\nYour selection: ")
            if exit_condition is None and cmd == 'x':
                return

            action = int(cmd)
            if action > len(backpack):
                raise IndexError
        except (IndexError, ValueError):
            pause("I do not understand.")
        else:
            new_backpack = ""
            for i, item in enumerate(regex.findall(r'\X', backpack)):
                if i == action - 1:
                    if not item in I_NOT_DROPABLE:
                        continue
                    else:
                        pause("You can not drop this special item.")
                new_backpack += item
            backpack = new_backpack

def equip_part(part, x):

    while True:
        available_items = _get_available_items(part)

        if len(available_items) == 0 and len(equiped[part-1][2]) == 0:
            pause("Nothing in the backpack that could fit.")
            return

        options = []
        # For each level available slot
        items = regex.findall(r'\X', equiped[part - 1][2])
        for i in range(LEVELS['slots'][level][part]):
            item = I_EMPTY + " " if len(items) <= i else items[i]
            options.append((str(i+1), item))

        options.append(('x', f'{S_DONE} e[x]it equipment'))
        try:
            action = get_action(options, f"Equip items in {equiped[part-1][1]}", "Which slot would you like to equip?")
        except InvalidSelection:
            pause("I do not know about this slot.")
            continue
        else:
            cmd = options[action][0]
            if cmd == 'x':
                return
            slot_index = options[action][0]
            if equip_slot(part, int(cmd) - 1):
                return


def _get_available_items(slot):
    available_items = []
    for item in regex.findall(r'\X', backpack):
        if not item in ITEM_TYPES:
            continue

        if slot in ITEM_TYPES[item]:
            available_items.append(item)
    return available_items


def unequip(part, slot):
    global equiped, backpack
    all_slots = regex.findall(r'\X', equiped[part - 1][2])
    backpack += all_slots[slot]
    all_slots[slot] = ""
    equiped[part - 1][2] = "".join(all_slots)


def equip_slot(part, slot):
    global backpack

    while True:
        options = []
        available_items = _get_available_items(part)
        for i, item in enumerate(available_items):
            options.append((str(i+1), item))

        currently_equiped = ""
        if len(regex.findall(r'\X', equiped[part-1][2])) > slot:
            currently_equiped = regex.findall(r'\X', equiped[part - 1][2])[slot]
            options.append(('u', f'{currently_equiped} [u]unequip slot'))

        options.append(('x', f'{S_DONE} e[x]it slots'))
        try:
            action = get_action(options, f"Equip items in {equiped[part-1][1]} - {slot+1}.Slot", "What to equip in the slot?")
        except InvalidSelection:
            pause("I do not know about this.")
            continue
        else:
            cmd = options[action][0]
            if cmd == 'x':
                return False
            if cmd == 'u':
                unequip(part, slot)
                return True
            else:
                to_equip = available_items[int(cmd)-1]
                if currently_equiped:
                    unequip(part, slot)
                withdraw(1, to_equip)
                equiped[part-1][2] += to_equip;
                return True

def equip_items():

    while True:

        slots = copy.deepcopy(equiped)
        for i in range(0, len(slots)):
            equiped_slots = regex.findall(r'\X', slots[i][2])
            equiped_slots += [(I_EMPTY + " ")] * (LEVELS['slots'][level][i+1] - len(equiped_slots))
            slots[i] = (slots[i][0], "".join(equiped_slots).ljust(6) + slots[i][1].ljust(14))

        options = [
            SEPARATOR_DO
        ] + slots + [('x', f'{S_DONE} e[x]it inventory')]
        try:
            action = get_action(options, "Equip items", "What would you like to equip?")
        except InvalidSelection:
            pause("I do not understand this equipment action")
            continue
        else:
            cmd = options[action][0]
            if cmd == 'x':
                return
            else:
                equip_part(action, options[action])

        # for i, item in enumerate(equiped):
        #     description, slot = item
        #     print(i + 1, description.ljust(12), slot)
        #
        # print(f'x {S_DONE} e[x]it inventory')
        #
        # action = input("\nYour selection: ")
        # if action == 'x':
        #     return
        # try:
        #     slot = int(action)
        # except (ValueError, IndexError):
        #     pause("I do not understand")
        # else:
        #     pause("You selected ", slot)



def show_inventory():
    options = [
        SEPARATOR_DO,
        ('e', f'{S_ACTION} [e]quip items'),
        ('d', f'{S_DROP} [d]rop items from backpack'),
        ('x', f'{S_DONE} e[x]it inventory'),
    ]
    if I_BANDAGE in backpack:
        options.append(ACTIONS['bandage'])

    option = ''
    while option != 'x':
        status("Inspecting your inventory")
        cmd = get_action(options)
        option = options[cmd][0]
        if option == 'd':
            drop_from_backpack(message="Freeing space in backpack")
        elif option == 'h':
            apply_bandage()
        elif option == 'e':
            equip_items()


#        R-G-T-K+ (Crown)
#        |
# *C-F-B-S-D-B-U-C+ (Ring)
#        |   |
#        H   C-D-m-T+
#                |
#                B
MAP = {
    L_CASTLE: {
        f'{S_NORTH}': L_SHOP,
        f'{S_EAST}': L_FOREST,
    },
    L_SHOP: {
        f'{S_SOUTH}': L_CASTLE,
        f'{S_NORTH}': L_CATHEDRAL,
    },
    L_CATHEDRAL: {
        f'{S_SOUTH}': L_SHOP,
    },
    L_FOREST: {
        f'{S_WEST}': L_CASTLE,
        f'{S_EAST}': L_BRIDGE,
    },
    L_BRIDGE: {
        f'{S_WEST}': L_FOREST,
        f'{S_EAST}': L_SWAMP,
    },
    L_SWAMP: {
        f'{S_WEST}': L_BRIDGE,
        f'{S_NORTH}': L_RUINS,
        f'{S_EAST}': L_DESERT,
        f'{S_SOUTH}': L_HUT,
    },
    L_HUT: {
        f'{S_NORTH}': L_SWAMP,
    },
    L_RUINS: {
        f'{S_SOUTH}': L_SWAMP,
        f'{S_EAST}': L_GRAVEYARD,
    },
    L_GRAVEYARD: {
        f'{S_WEST}': L_RUINS,
        f'{S_NORTH}': L_TOMB,
        f'{S_EAST}': L_GRAVEDIGGER,
    },
    L_GRAVEDIGGER: {
        f'{S_WEST}': L_GRAVEYARD,
    },
    L_TOMB: {
        f'{S_SOUTH}': L_GRAVEYARD,
        f'{S_EAST}': L_LAIR,
    },
    L_LAIR: {
        f'{S_WEST}': L_TOMB,
    },
    L_DESERT: {
        f'{S_WEST}': L_SWAMP,
        f'{S_EAST}': L_BEACH,
    },
    L_BEACH: {
        f'{S_WEST}': L_DESERT,
        f'{S_EAST}': L_SHIP,
        f'{S_SOUTH}': L_CAVE,
    },
    L_SHIP: {
        f'{S_WEST}': L_BEACH,
        f'{S_EAST}': L_OCEAN,
    },
    L_OCEAN: {
        f'{S_WEST}': L_SHIP,
    },
    L_CAVE: {
        f'{S_NORTH}': L_BEACH,
        f'{S_SOUTH}': L_MINES,
    },
    L_MINES: {
        f'{S_NORTH}': L_CAVE,
        f'{S_EAST}': L_VULCANO,
        f'{S_WEST}': L_BLACKSMITH,
    },
    L_BLACKSMITH: {
        f'{S_EAST}': L_MINES,
    },
    L_VULCANO: {
        f'{S_WEST}': L_MINES,
    },
}

MAP_WIDTH = 18
MAP_HEIGHT = 13
def show_map():
    global location
    clear()

    status("Looking at map", "KINGDOM OF PEARLS")

    tiles = ['  '] * MAP_WIDTH * MAP_HEIGHT
    pos = [2, 6]
    handled_locations = []

    add_map_location(L_CASTLE, pos, tiles, handled_locations)

    for i, c in enumerate(tiles):
        x = i % MAP_WIDTH
        y = i // MAP_WIDTH

        if x == 0:
            print("")

        if y == 0 or y == MAP_HEIGHT - 1:
            print('--', end="")
        elif x == 0:
            print('|', end="")
        elif x == MAP_WIDTH - 1:
            print('  |', end="")
        else:
            print(c, end="")


    # for i, x in enumerate(tiles):
    #     if x.strip() != 'XX':
    #         print(i % 64, i // 64, x)

    pause("\n\n")

def add_map_location(cur_loc, pos, tiles, handled_locations):
    global visited, location

    if cur_loc in handled_locations:
        return

    handled_locations.append(cur_loc)

    tiles[pos[1] * MAP_WIDTH + pos[0]] = regex.findall(r'\X', cur_loc)[0]

    distance = (2, 2)

    for dir, loc in MAP[cur_loc].items():

        if not DEBUG_SHOW_COMPLETE_MAP:
            if loc not in visited:
                continue

        new_pos = [] + pos
        connection = ""
        if dir == f'{S_NORTH}':
            new_pos[1] -= distance[1]
            connection = "| "
        elif dir == f'{S_SOUTH}':
            new_pos[1] += distance[1]
            connection = "| "
        elif dir == f'{S_WEST}':
            new_pos[0] -= distance[0]
            connection = "-"
        elif dir == f'{S_EAST}':
            new_pos[0] += distance[0]
            connection = "-"

        for move_y in range(min(new_pos[1], pos[1]), max(new_pos[1], pos[1])+1):
            for move_x in range(min(pos[0], new_pos[0]), 1+max(pos[0], new_pos[0])):
                if not tiles[move_y * MAP_WIDTH + move_x].strip():
                    pass
                    # tiles[move_y * MAP_WIDTH + move_x] = connection

        tiles[new_pos[1] * MAP_WIDTH + new_pos[0]] = regex.findall(r'\X', loc)[0]
        if loc == location:
            tiles[(new_pos[1] + 1) * MAP_WIDTH + (new_pos[0])] = '^^'

        add_map_location(loc, new_pos, tiles, handled_locations)


class InvalidSelection(Exception):
    pass

class GameEnded(Exception):
    pass


def raise_game_ended():
    raise GameEnded

def get_main_options(with_new_game=False, with_save=True, sys_exit=True):
    options = [
        SEPARATOR_OPTIONS,
    ]
    if with_new_game:
        options.append(
            ('NEW', f' {S_NEW} [NEW] game', lambda: new_game()),
        )

    if with_save:
        options.append(
            ('SAVE', f'{S_SAVE} [SAVE] game', lambda: save())
        )

    quit_cb = lambda: sys.exit(0)
    if not sys_exit:
        quit_cb = raise_game_ended
    return options + [
        ('LOAD', f'{S_LOAD} [LOAD] game', lambda: load(), lambda: save_exists(), True),
        ('QUIT', f'{S_QUIT}   [QUIT] game', quit_cb),
    ]

def get_character_options():
    options = [
        SEPARATOR_STATUS,
        ('i', f'{S_INVENTORY} [i]nventory', lambda: show_inventory()),
        ('m', f'{S_MAP} [m]map', lambda: show_map()),
    ]

    return options


def get_action(options, event="", question="What would you like to do?", with_status=True):
    if len(backpack) > backpack_size:
        drop_from_backpack(lambda: len(regex.findall(r'\X', backpack)) > backpack_size)

    if with_status:
        status(event, question)

    valid_options = []
    for option in options:

        valid_options.append([option[0], True])

        # Separator etc
        if option[0] is None:
            valid_options[-1][1] = False
            print(option[1])
            continue

        if len(option) > 3:
            # Have condition
            if not option[3]():
                if len(option) > 4:
                    hidden = option[4]
                    if callable(option[4]):
                        hidden = option[4]()
                    if hidden:
                        valid_options[-1][1] = False
                        continue
                print(option[0], option[1] + f" ({S_BLOCKED} BLOCKED)")
                continue

        print(option[0], option[1])

    for valid_option in valid_options:
        if valid_option[0] is None or valid_option[1] == False:
            continue
        if valid_options.count(valid_option) > 1:
            raise AssertionError("Already have option for '{}'", valid_option)


    action = input("\nYour selection: ")
    try:
        return valid_options.index([action, True])
    except:
        raise InvalidSelection()


def loop():
    while True:
        options = LOCATION_OPTIONS[location] + get_character_options() + get_main_options(sys_exit=False)
        try:
            action = get_action(options)
            # Display error on secret option selection
            if len(options[action]) > 4 and not options[action][3]() and ( (callable(options[action][4] and not options[action][4]())) or not options[action][4]):
                    raise InvalidSelection
            options[action][2]()
        except InvalidSelection:
            pause("I do not understand.")


if __name__ == '__main__':
    main_menu()


