# -*- coding: utf-8 -*-
import math

import regex

# TODO:
# [X] Limit Backpack size
# [X] Potion: Adds a random dice during fight
# [X] 💣 Bomb: 2 Damage to Monster + 1 Damage to self
# [ ] 🩹 Heals 3 heart
# [ ] Turns: 3 Moves per Turn
# [ ] Limit items in shop
# [ ] Shoes: One more Move per Turn + Two Shoes = two more moves.
# [ ] Moon Phase: 🌑 🌘 🌗 🌖 🌕 = After 5 Turns Big Monster attacks the castle
# [ ] 🐴 Horse: 3 Moves per turn + 3 Space in Backpack (replaces Shoes)
# [ ] 🔨 🟥 🟩
# [X] 🪓 🟥 🟥
# [X] 🏹  🟦 🟩
# [ ] 🧤 🟦
# [ ] 👑 🟨
# [ ] 💍 🟨
# [ ] Add monsters to specific locations
# [ ] Only move past location if there are no monsters
# [ ] GHOSTS in RUINS
# [X] ZOMBIE: On hit gets heart back
# [ ] FROG 🐸
# [ ] SPIDER 🕷️
# [ ] BATS 🦇
# [ ] SKELETON
# [ ] TROLL
# [ ] ZOMBIE only green dice
# [ ] SHARK
# [ ] Mermaid
# [ ] EVIL SORCERER 🧙
# [ ] Princess 👸 3x 🔮

# GOAL:
# - Defeat Vampire
# - Defeat Mermaid
# - Defeat Dragon
# ---> Defeat Sorcerer
# MAP
# ---
#        G-T-K+
#        |
# *C-F-B-S-E-B-U-C+
#     \    |
#      +-C-D-m-T+
#
# Graveyard (ZOMBIES)
# Tomb (GHOST)
# Kings Lair (VAMPIRE)
# Castle START (RATS)
# Forest (SNAKE)
# Bridge (TROLL)
# Swamp (FROG)
# Entrance (SPIDER)
# Cave (BAT)
# Dungeon (SKELETONS)
# mines (DEMONS)
# Mountain [T]op (DRAGON)
# BEACH (SHARK)
# UNDERWATER (OCTOPUS)
# UNDERWATER-CITY (MERMAID)

import os
import random
import sys

I_EMPTY = "_"
I_SWORD = "🗡️"
I_SHIELD = "🛡️"
I_SHOE = "🥾"
I_COIN = "🟡"
I_POTION = "🧪"
I_BOMB = "💣"
I_BOW = "🏹"
I_BATTLE_AXE = "🪓"

E_OCTOPUS = "🐙"
E_SNAKE = "🐍"
E_DRAGON = "🐉"
E_RAT = "🐀"
E_GHOST = "👻"
E_ZOMBIE = "🧟‍️"

E_TROLL = "🧌"
E_VAMPIRE = "🧛"
E_DEMON = "👹"

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
S_MISS = "💨"
S_MAGIC_MISS = "✨"


L_CASTLE = "🏰 Castle"
L_FOREST = "🌲 Forest"
L_SHOP = "🛍️ Shop"

MAX_LEVEL = 10
LEVELS = {
    "xp":       [0, 500, 1000, 2500, 5000, 10000, 15000, 30000, 45000, 60000, math.inf],
    "backpack": [8, 10, 12, 14, 16, 18, 20, 22, 24, 26],
    "health":   [5, 6, 6, 7, 7,  8,  8,  9,  9,  10],
}

def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def pause(text):
    input(text + " (Press Enter to continue)")


clear()
print("PAWELS ADVENTURE GAME")
name = input("What is the name of the hero? ")
if len(name) > 20:
    name = name[:20]
    pause(f"That's a long name. I will call you {name}")

print("Welcome", name, "on your great adventure!")
backpack = f"{I_POTION}{I_COIN * 2}"
backback_size = LEVELS['backpack'][0]
equipment = ""
location = L_CASTLE
max_health = LEVELS['health'][0]
health = max_health
xp = 0
level = 1

prices = {
    I_SWORD: 4,
    I_BOW: 6,
    I_BATTLE_AXE: 10,
    I_SHIELD: 4,
    I_SHOE: 1,
    I_BOMB: 3,
    I_POTION: 2,
}


def _default_damage(rolled_dice: list) -> int:
    return False, rolled_dice


def __type_damage_only(rolled_dice: list, only_type: list) -> int:
    removed_damage = False
    new_result = []
    for die, throw in rolled_dice:
        if die not in only_type:
            value = ""
            if throw == I_SWORD:
                removed_damage = True
                new_result.append((die, S_MAGIC_MISS))
            else:
                new_result.append((die, throw))
        else:
            new_result.append((die, throw))
    return removed_damage, new_result


def _magic_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_YELLOW])


def _green_damage_only(rolled_dice: list) -> int:
    return __type_damage_only(rolled_dice, [D_GREEN])

monsters = {
    # Purple Dice, Black Dice, Health, XP, LOOT, damage_callback
    E_RAT: (1, 0, 1, 50, I_COIN, _default_damage, ""),
    E_SNAKE: (3, 0, 2, 100, I_COIN * 1, _default_damage, ""),
    E_OCTOPUS: (2, 0, 3, 200, I_COIN * 2, _default_damage, ""),
    E_GHOST: (0, 2, 3, 300, f"{I_POTION * 2}", _magic_damage_only, f"Only {D_YELLOW} magic is effective against Ghosts!"),
    E_ZOMBIE: (4, 0, 4, 600, f"{I_POTION * 2}", _green_damage_only, f"Only {D_GREEN} basic attacks are effective against Zombies!"),
    E_DRAGON: (2, 2, 15, 2500, f"{I_COIN * 8}{I_BOMB}", _default_damage, ""),
}



DICE = {
    D_GREEN:  f"{I_SWORD * 2}{I_SHIELD * 2}  ",
    D_RED:    f"{I_SWORD * 3}{I_SHIELD * 1}  ",
    D_BLUE:   f"{I_SWORD * 1}{I_SHIELD * 3}  ",
    D_YELLOW: f"{I_SWORD * 3}{I_SHIELD * 3}",
    D_PURPLE: f"{I_SWORD * 2}{I_SHIELD * 1}   ",
    D_BLACK:  f"{I_SWORD * 3}{I_SHIELD * 2} ",
}




def goto(new_location):
    global location
    location = new_location

def heal(added_health):
    global health
    health = min(max_health, health + added_health)

def money():
    global backpack
    return backpack.count(I_COIN)

def withdraw(count):
    global backpack
    backpack = backpack.replace(I_COIN, '', count)

def buy(what):
    global prices, backpack
    price = prices[what]
    if money() < price:
        pause("☹️ Sorry! You don't have enough coins")
    else:
        withdraw(price)
        backpack += what


def roll(dice):
    result = []
    for die in dice:
        throw = random.choice(regex.findall(r'\X', DICE[die]))
        result.append((die, throw))

    return result

def gain_xp(added_xp):
    global xp, backback_size, max_health, level, health
    old_xp = xp
    xp += added_xp

    for new_level, level_xp in enumerate(LEVELS['xp']):
        if xp >= level_xp and new_level + 1 > level:
            backback_size = LEVELS['backpack'][new_level]
            max_health = LEVELS['health'][new_level]
            health = max_health
            level = new_level + 1
            pause(f"YOU REACHED LEVEL {level}! You feel stronger!")
            break


def fight():
    global health, backpack

    monster = random.choice(list(monsters.keys()))
    values = monsters[monster]
    monster_dice = f"{values[0] * D_PURPLE}{values[1] * D_BLACK}"
    monster_max_health = values[2]
    monster_health = values[2]
    monster_xp = values[3]
    monster_loot = values[4]
    damage_callback = values[5]
    damage_message = values[6]

    player_dice = D_GREEN * 2

    player_dice += D_RED * backpack.count(I_SWORD)

    player_dice += D_BLUE * backpack.count(I_BOW)
    player_dice += D_GREEN * backpack.count(I_BOW)

    player_dice += D_RED * backpack.count(I_BATTLE_AXE) * 2

    player_dice += D_BLUE * backpack.count(I_SHIELD)

    while monster_health > 0 and health > 0:

        status(
            f"{monster} in sight! {values[0] * D_PURPLE}{values[1] * D_BLACK} | " + S_HEART * monster_health + S_HEART_EMPTY * (
                    monster_max_health - monster_health))

        ACTIONS = {
            'attack': f"Attack {player_dice}",
            'retreat': f"Retreat",
            'potion': f"Drink Potion",
            'bomb': f"Throw a bomb (2 {S_HIT} to target & 1 {S_HIT} to you)"
        }

        options = [
            ACTIONS['attack'],
            ACTIONS['retreat']
        ]
        if I_POTION in backpack:
            options.append(ACTIONS['potion'])
        if I_BOMB in backpack:
            options.append(ACTIONS['bomb'])

        for i, option in enumerate(options):
            print(f"{i + 1} {option}")

        try:
            action = int(input("Your selection: "))
            if action < 1 or action > len(options):
                raise ValueError
        except ValueError:
            pause("I do not understand.")
        else:
            action_text = options[action - 1]
            if action_text == ACTIONS['attack']:
                clear()
                status(f"{monster} ready to attack {values[0] * D_PURPLE}{values[1] * D_BLACK} | " + S_HEART * monster_health + S_HEART_EMPTY * (monster_max_health - monster_health), "ATTACKING!")
                print("PLAYER THROWS:")
                player_roll = roll(player_dice)
                altered, player_roll = damage_callback(player_roll)
                for die, throw in player_roll:
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
                    print(damage_message)

                monster_health = max(0, monster_health - monster_damage)
                health = max(0, health - player_damage)

                pause("")
            elif action_text == ACTIONS['retreat']:
                # Retreat!
                return
            elif action_text == ACTIONS['potion']:
                backpack = backpack.replace(I_POTION, "", 1)
                potion_die = random.choice([D_RED, D_BLUE, D_GREEN])
                player_dice += potion_die
                pause(f"You feel stronger. A {potion_die} was added.")
            elif action_text == ACTIONS['bomb']:
                monster_damage = 2
                player_damage = 1
                monster_health = max(0, monster_health - monster_damage)
                health = max(0, health - player_damage)
                backpack = backpack.replace(I_BOMB, "", 1)
                print(f"PLAYER {player_damage * S_HIT}")
                print(f"MONSTER {monster_damage * S_HIT}")
                pause("The bomb exploded")


    if health == 0:
        pause(f"YOU WERE DEFEATED {S_SKULL}")
        sys.exit(0)
    if monster_health == 0:
        pause(f'THE MONSTER IS DEFEATED. YOU FOUND {monster_loot} AND GAINED {monster_xp} XP')
        gain_xp(monster_xp)
        backpack += monster_loot


options = {
    L_CASTLE: [
        ("Go to the shop", lambda: goto(L_SHOP)),
        ("Heal at the well", lambda: heal(max_health)),
        ("Leave the castle", lambda: goto(L_FOREST))
    ],
    L_SHOP: [
        ("Go back to the castle", lambda: goto(L_CASTLE)),
        (f"{I_SWORD} Buy a sword (Cost: {prices[I_SWORD]})", lambda: buy(I_SWORD)),
        (f"{I_BOW} Buy a bow (Cost: {prices[I_BOW]})", lambda: buy(I_BOW)),
        (f"{I_BATTLE_AXE} Buy a battle-axe (Cost: {prices[I_BATTLE_AXE]})", lambda: buy(I_BATTLE_AXE)),
        (f"{I_SHIELD} Buy a shield (Cost: {prices[I_SHIELD]})", lambda: buy(I_SHIELD)),
        (f"{I_SHOE} Buy boots (Cost: {prices[I_SHOE]})", lambda: buy(I_SHOE)),
        (f"{I_BOMB} Buy a bomb (Cost: {prices[I_BOMB]})", lambda: buy(I_BOMB)),
        (f"{I_POTION} Buy a potion (Cost: {prices[I_POTION]})", lambda: buy(I_POTION)),
    ],
    L_FOREST: [
        ("Go back to the castle", lambda: goto(L_CASTLE)),
        (f"Fight Monster", lambda: fight())
    ]
}

def status(event="", question="What would you like to do?"):
    clear()
    print(f"""
******************************
🗺️ {name}'s location: {location}
🎒 Backpack: {backpack}{(backback_size-len(backpack)) * I_EMPTY} ({len(backpack)} / {backback_size})
Health: {health * S_HEART}{(max_health -  health) * S_HEART_EMPTY} ({int(0.5 + (health / max_health) * 100.0)}%)
LEVEL: {level}
XP: {xp} / {LEVELS['xp'][level]}
******************************
{event}
+-{'-' * len(question)}-+
| {question} |
+-{'-' * len(question)}-+
""")


def backpack_full():
    global backpack

    while len(backpack) > backback_size:
        status("Too much load", "What to drop from your backpack?")

        for i, item in enumerate(regex.findall(r'\X', backpack)):
            print(i+1, f"Drop {item}")

        try:
            action = int(input("Your selection: "))
            if action > len(backpack):
                raise IndexError
        except (IndexError, ValueError):
            pause("I do not understand.")
        else:
            new_backpack = ""
            for i, item in enumerate(regex.findall(r'\X', backpack)):
                if i == action - 1:
                    continue
                new_backpack += item
            backpack = new_backpack


def get_action():
    if len(backpack) > backback_size:
        backpack_full()

    status()
    for i, option in enumerate(options[location]):
        print(i+1, option[0])

    action = input("Your selection: ")
    return int(action)

while True:
    try:
        options[location][get_action()-1][1]()
    except (IndexError, ValueError):
        pause("I do not understand.")




