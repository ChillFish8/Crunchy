import json

from random import randint, choice


BASE_HP = (20, 50)  # min, max
BASE_AC = 10

def get_stats():
    hp = randint(*BASE_HP)
    dex = randint(10, 20)
    strength = randint(10, 20)
    loot = {
        'platinum': randint(0, 5),
        'gold': randint(1, 200),
        'copper': randint(50, 500)
    }
    armour = randint(0, 3)
    return hp, dex, strength, loot, armour


class Monster:
    def __init__(self, **stats):
        self.name = None
        self.cr = None
        for key, item in stats.items():
            setattr(self, key, item)

    @property
    def format_name(self):
        return f"{self.name} - [ CR {self.cr} ]"




with open(r'realms/generation/monster_name.json', 'r') as file:
    random_names = json.load(file)


class MonsterManual:
    def __init__(self):
        pass

    @staticmethod
    def get_random_monster(challenge_rating):
        hp, dex, strength, loot, armour = get_stats()
        hp = hp * (challenge_rating + randint(0, 2)) / 2

        dex_mod = (dex - 10) // 2
        str_mod = (strength - 10) // 2

        ac = BASE_AC + dex_mod + armour + (challenge_rating // 3)

        if challenge_rating in range(1, 6):
            loot['platinum'] = 0
            loot['gold'] = randint(1, 20)
            loot['copper'] = randint(50, 200)

        elif challenge_rating in range(6, 11):
            loot['platinum'] = randint(1, 5)
            loot['gold'] = randint(10, 100)
            loot['copper'] = randint(50, 500)

        elif challenge_rating in range(11, 16):
            loot['platinum'] = randint(1, 25)
            loot['gold'] = randint(100, 250)
            loot['copper'] = randint(50, 500)

        else:
            loot['platinum'] = randint(1, 50)
            loot['gold'] = randint(150, 350)
            loot['copper'] = randint(50, 500)

        return Monster(**{
            'name': choice(random_names),
            'cr': challenge_rating,
            'ac': ac,
            'hp': hp,
            'dex': dex,
            'dex_mod': dex_mod,
            'strength': strength,
            'str_mod': str_mod,
            'loot': loot,
            'armour': armour
        })
