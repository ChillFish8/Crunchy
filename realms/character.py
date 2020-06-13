import random
import json
import time

from utils.id_maker import get_id

BASE_HEARTS = 5
BASE_FOOD = 5
BASE_TREATS = 5

class CharacterRef:
    with open(r"resources/archieve/main_characters.json", "r") as file:
        references = json.load(file)

    @classmethod
    def get_character(cls, name):
        for character in cls.references:
            if character['name'].lower() == name.lower():
                return character

class Responses:
    FOOD_RESP_NO_COMMENT = [
        'God im hungry! Can we get something to eat?',
        "I heard there's a new restaurant open, maybe we should check it out?",
        'If you dont have food, dont talk to me!',
    ]

    FOOD = [
        'pizza',
        'fish',
        'cake'
    ]

    LOVE = [
        "You're amazing!",
        "You're the best!",
        "Glad to see you."
    ]

    MOOD = [
        'Bored',
        'Tired',
        'Grumpy',
        'Sad',
        'Happy',
        'Excited'
    ]

    @classmethod
    def get_food_resp(cls):
        if random.randint(0, 1):
            comment = random.choice(cls.FOOD_RESP_NO_COMMENT)
        else:
            FOOD_RESP_COMMENT = [
                f'I could really go for some {random.choice(cls.FOOD)} right now.',
            ]
            comment = random.choice(FOOD_RESP_COMMENT)
        return comment

    @classmethod
    def get_love_resp(cls):
        return random.choice(cls.LOVE)

    @classmethod
    def random_mood(cls):
        return random.choice(cls.MOOD)


class Feelings:
    def get_emotion(self) -> str:
        if self.food <= 2:
            return f'**Thinking** - "{Responses.get_food_resp()}"'
        elif self.hearts > 4:
            return f'**Thinking** - "{Responses.get_love_resp()}"'
        else:
            return f'**Feeling** - "{self.mood}"'


class CharactersChoice:
    def __init__(self):
        self._treat = self.treat
        self._hearts = self.hearts
        self._food = self.food
        self._mood = self.mood

    def choice(self, activity: str):
        if activity == "snack":
            if self._food >= BASE_FOOD:
                return False, "FOOD-FULL"
            else:
                return True, None
        elif activity == "fun":
            if self._food <= BASE_FOOD - 3:
                return False, "FOOD-NEEDED"
            elif self._mood.lower() in ['tired', 'grumpy']:
                return False, "NOT-IN-MOOD"
            else:
                return True, None


class Character(Feelings, CharactersChoice):
    def __init__(self, name=None, icon=None, base_power=None, defense=None, attack=None):
        self.name = name
        self.icon = icon
        self.id = get_id()
        self.modifiers = {}
        self.last_active = time.time()
        self.mood = Responses.random_mood()

        self._base_power = base_power
        self._base_defense = defense
        self._base_attack = attack

        self._hearts = 1
        self._food = 3
        self._treat = 0
        super().__init__()

    def _unload_self(self) -> dict:
        items = self.__dict__
        export = {}
        for key, value in items.items():
            export[key] = value
        return export

    def _load_unknown(self):
        if any([item is None for item in [self._base_power, self._base_defense, self._base_attack]]):
            ref = CharacterRef.get_character(self.name)
            if ref is None:
                raise ValueError("No Character reference for this character!")

            self._base_power = self._base_power if self._base_power is not None else ref['base_power']
            self._base_defense = self._base_defense if self._base_defense is not None else ref['defense']
            self._base_attack = self._base_attack if self._base_attack is not None else ref['attack']

    def to_dict(self) -> dict:
        return self._unload_self()

    def from_dict(self, character_dict: dict):
        for key, value in character_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.check_mood()
        return self

    def check_mood(self):
        if time.time() > self.last_active + 300:
            self.mood = Responses.random_mood()

    def render_modifiers(self):
        string = ""
        for key, value in self.modifiers.items():
            string += f"• {key} - `{value}`\n"
        return string if string != "" else "No Mods"

    def render_character_info(self):
        hearts = "💔" * BASE_HEARTS
        hearts = f"**[ Hearts ]** `{hearts.replace('💔', '❤️', self.hearts)}`\n"

        food = " " * BASE_HEARTS
        food = f"**[ Food & Drink ]** `{food.replace(' ', '🍔', self.food)}`\n"

        treats = " " * BASE_HEARTS
        treats = f"**[ Treats ]** `{treats.replace(' ', '🍬', self.treat)}`\n"
        return f"{hearts}\n{food}\n{treats}\n"

    @property
    def power(self) -> int:
        if self._base_power is None:
            self._load_unknown()
        export_power = 0
        for key, value in self.modifiers.items():
            mod = value.get("num_modifier", "0")
            if mod.startswith("-"):
                export_power - int(mod[1:])
            elif mod.startswith("+"):
                export_power + int(mod[1:])
        export_power += self._base_power
        return export_power

    @property
    def attack(self):
        return self._base_attack

    @property
    def defense(self):
        return self._base_defense

    @property
    def hearts(self):
        return self._hearts

    @property
    def food(self):
        return self._food

    @property
    def treat(self):
        return self._treat


